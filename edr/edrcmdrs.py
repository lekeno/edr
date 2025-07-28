from __future__ import division

import os
import pickle

from edtime import EDTime
from edrconfig import EDRConfig
from lrucache import LRUCache
from edrlog import EDR_LOG
from edentities import EDPlayerOne




class EDRCmdrs(object):
    #TODO these should be player and/or squadron specific
    EDR_CMDRS_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache', 'cmdrs.v7.p')
    EDR_INARA_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache', 'inara.v7.p')
    EDR_SQDRDEX_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache', 'sqdrdex.v2.p')

    def __init__(self, edrserver):
        self.server = edrserver
        self._player = EDPlayerOne()
        self.heartbeat_timestamp = None
 
        edr_config = EDRConfig()
        self._edr_heartbeat = edr_config.edr_heartbeat()
 
        try:
            with open(self.EDR_CMDRS_CACHE, 'rb') as handle:
                self.cmdrs_cache = pickle.load(handle)
        except:
            self.cmdrs_cache = LRUCache(edr_config.lru_max_size(),
                                                 edr_config.cmdrs_max_age())

        try:
            with open(self.EDR_INARA_CACHE, 'rb') as handle:
                self.inara_cache = pickle.load(handle)
        except:
            self.inara_cache = LRUCache(edr_config.lru_max_size(),
                                                 edr_config.inara_max_age())
        
        try:
            with open(self.EDR_SQDRDEX_CACHE, 'rb') as handle:
                self.sqdrdex_cache = pickle.load(handle)
        except:
            self.sqdrdex_cache = LRUCache(edr_config.lru_max_size(),
                                                 edr_config.sqdrdex_max_age())

    @property
    def player(self):
        return self._player

    def player_name(self):
        return self._player.name

    def set_player_name(self, new_player_name):
        if (new_player_name != self._player.name):
            self._player.force_new_name(new_player_name)
            self.__update_squadron_info(force_update=True)

    def player_pledged_to(self, power, time_pledged=0):
        edr_config = EDRConfig()
        delta = time_pledged - self._player.time_pledged if self._player.time_pledged else time_pledged
        if power == self._player.power and delta <= edr_config.noteworthy_pledge_threshold():
            EDR_LOG.log(u"Skipping pledged_to (not noteworthy): current vs. proposed {} vs. {}; {} vs {}".format(self._player.power, power, self._player.time_pledged, time_pledged), "DEBUG")
            return False
        self._player.pledged_to(power, time_pledged)
        since = self._player.pledged_since()
        return self.server.pledged_to(power, since)        

    def __squadron_id(self):
        self.__update_squadron_info()
        info = self._player.squadron_info()
        return info["squadronId"] if info else None

    def __update_squadron_info(self, force_update=False):
        if self.server.is_anonymous():
            return
        mark_twain_flag = int((EDTime.js_epoch_now() - self.heartbeat_timestamp)/1000) >= self._edr_heartbeat if self.heartbeat_timestamp else True
        if force_update or mark_twain_flag:
            info = self.server.heartbeat()
            if info:
                self.heartbeat_timestamp = info["heartbeat"] if "heartbeat" in info else EDTime.js_epoch_now()
                self._player.squadron_member(info) if "squadronId" in info else self._player.lone_wolf()
            else:
                self.heartbeat_timestamp = EDTime.js_epoch_now()
                self._player.lone_wolf()

    def persist(self):
        with open(self.EDR_CMDRS_CACHE, 'wb') as handle:
            pickle.dump(self.cmdrs_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INARA_CACHE, 'wb') as handle:
            pickle.dump(self.inara_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_SQDRDEX_CACHE, 'wb') as handle:
            pickle.dump(self.sqdrdex_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def evict(self, cmdr):
        try:
            del self.cmdrs_cache[cmdr.lower()]
        except KeyError:
            pass

        try:
            del self.inara_cache[cmdr.lower()]
        except KeyError:
            pass

        try:
            sqdr_id = self.__squadron_id()
            if sqdr_id:
                sq_cmdr_key = u"{}:{}".format(sqdr_id, cmdr.lower())
                del self.sqdrdex_cache[sq_cmdr_key]
        except KeyError:
            pass

    def __edr_cmdr(self, cmdr_name, autocreate):
        profile = self.cmdrs_cache.get(cmdr_name.lower())
        cached = self.cmdrs_cache.has_key(cmdr_name.lower())
        if cached or profile:
            EDR_LOG.log(u"Cmdr {cmdr} is in the EDR cache with id={cid}".format(cmdr=cmdr_name,
                                                                           cid=profile.cid if profile else 'N/A'),
                       "DEBUG")
            return profile

        profile = self.server.cmdr(cmdr_name, autocreate)

        if not profile:
            self.cmdrs_cache.set(cmdr_name.lower(), None)
            EDR_LOG.log(u"No match on EDR. Temporary entry to be nice on EDR's server.", "DEBUG")
            return None
        dex_profile = self.server.cmdrdex(profile.cid)
        if dex_profile:
            EDR_LOG.log(u"EDR CmdrDex entry found for {cmdr}: {id}".format(cmdr=cmdr_name,
                                                        id=profile.cid), "DEBUG")
            profile.dex(dex_profile)
        self.cmdrs_cache.set(cmdr_name.lower(), profile)
        EDR_LOG.log(u"Cached EDR profile {cmdr}: {id}".format(cmdr=cmdr_name,
                                                        id=profile.cid), "DEBUG")
        return profile
    
    def __edr_sqdrdex(self, cmdr_name, autocreate):
        sqdr_id = self.__squadron_id()
        if not sqdr_id:
            return None
        key = u"{}:{}".format(sqdr_id, cmdr_name.lower())
        profile = self.sqdrdex_cache.get(key)
        if profile:
            EDR_LOG.log(u"Cmdr {cmdr} is in the EDR IFF cache for squadron {sqid} with key {key}".format(cmdr=cmdr_name,
                                                                                    sqid=sqdr_id, key=key),
                                                                                    "DEBUG")
            return profile

        profile = self.__edr_cmdr(cmdr_name, autocreate)
        if not profile:
            return None

        sqdrdex_dict = self.server.sqdrdex(sqdr_id, profile.cid)
        if sqdrdex_dict:
            EDR_LOG.log(u"EDR SqdrDex {sqid} entry found for {cmdr}@{cid}".format(sqid=sqdr_id,
                                                                    cmdr=cmdr_name, cid=profile.cid
                                                                    ), "DEBUG")
            profile.sqdrdex(sqdrdex_dict)
        self.sqdrdex_cache.set(u"{}:{}".format(sqdr_id, cmdr_name.lower()), profile)
        EDR_LOG.log(u"Cached EDR SqdrDex {sqid} entry for {cmdr}@{cid}".format(sqid=sqdr_id,
                                                                cmdr=cmdr_name, cid=profile.cid), "DEBUG")
        return profile.sqdrdex_profile

    def __inara_cmdr(self, cmdr_name, check_inara_server):
        inara_profile = None
        stale = self.inara_cache.is_stale(cmdr_name.lower())
        cached = self.inara_cache.has_key(cmdr_name.lower())
        if cached and not stale:
            inara_profile = self.inara_cache.get(cmdr_name.lower())
            EDR_LOG.log(u"Cmdr {} is in the Inara cache (name={})".format(cmdr_name,
                                                                         inara_profile.name if inara_profile else 'N/A'),
                       "DEBUG")
        elif check_inara_server:
            EDR_LOG.log(u"Stale {} or not cached {} in Inara cache. Inara API call for {}.".format(stale, cached, cmdr_name), "INFO")
            inara_profile = self.server.inara_cmdr(cmdr_name)

            if inara_profile and inara_profile.name.lower() == cmdr_name.lower():
                self.inara_cache.set(cmdr_name.lower(), inara_profile)
                EDR_LOG.log(u"Cached Inara profile {}: {},{},{},{}".format(cmdr_name,
                                                                          inara_profile.name,
                                                                          inara_profile.squadron,
                                                                          inara_profile.role,
                                                                          inara_profile.powerplay), "DEBUG")
            elif self.inara_cache.has_key(cmdr_name.lower()):
                inara_profile = self.inara_cache.peek(cmdr_name.lower())
                self.inara_cache.refresh(cmdr_name.lower())
                EDR_LOG.log(u"Refresh and re-use stale match in Inara cache.", "INFO")
            else:
                inara_profile = None
                self.inara_cache.set(cmdr_name.lower(), None)
                EDR_LOG.log(u"No match on Inara. Temporary entry to be nice on Inara's server.",
                           "INFO")
        return inara_profile

    def cmdr(self, cmdr_name, autocreate=True, check_inara_server=False):
        profile = self.__edr_cmdr(cmdr_name, autocreate)
        inara_profile = self.__inara_cmdr(cmdr_name, check_inara_server)
    
        if profile is None:
            if inara_profile is None:
                EDR_LOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
                return None
            else:
                return inara_profile

        if inara_profile:
            EDR_LOG.log(u"Combining info from EDR and Inara for cmdr {}".format(cmdr_name), "INFO")
            profile.complement(inara_profile)
        
        squadron_profile = self.__edr_sqdrdex(cmdr_name, autocreate)
        if squadron_profile:
            EDR_LOG.log(u"Combining info from Squadron for cmdr {}".format(cmdr_name), "INFO")
            profile.sqdrdex(squadron_profile.sqdrdex_dict())

        return profile

    def is_friend(self, cmdr_name):
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            return False
        return profile.is_friend()

    def is_ally(self, cmdr_name):
        sqdr_id = self.__squadron_id() 
        if not sqdr_id:
            return False

        profile = self.__edr_sqdrdex(cmdr_name, False)
        if profile:
            return profile.is_ally()
        return False

    def tag_cmdr(self, cmdr_name, tag):
        if tag in ["enemy", "ally"]:
            return self.__squadron_tag_cmdr(cmdr_name, tag)
        else:
            return self.__tag_cmdr(cmdr_name, tag)

    def contracts(self):
        return self.server.contracts()

    def contract_for(self, cmdr_name):
        if not cmdr_name:
            return False
        
        profile = self.cmdr(cmdr_name)
        if not profile:
            return False
        
        return self.server.contract_for(profile.cid)
    
    def place_contract(self, cmdr_name, reward):
        if not cmdr_name:
            return False
        
        if reward <= 0:
            return self.remove_contract(cmdr_name)

        profile = self.cmdr(cmdr_name)
        if not profile:
            return False
        
        return self.server.place_contract(profile.cid, {"cname": cmdr_name.lower(), "reward": reward})

    def remove_contract(self, cmdr_name):
        if not cmdr_name:
            return False
        
        profile = self.cmdr(cmdr_name)
        if not profile:
            return False
        
        return self.server.remove_contract(profile.cid)

    def __tag_cmdr(self, cmdr_name, tag):
        EDR_LOG.log(u"Tagging {} with {}".format(cmdr_name, tag), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        tagged = profile.tag(tag)
        if not tagged:
            EDR_LOG.log(u"Couldn't tag {} with {} (e.g. already tagged)".format(cmdr_name, tag), "DEBUG")
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        EDR_LOG.log(u"New dex state: {}".format(dex_dict), "DEBUG")
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        self.evict(cmdr_name)
        return success

    def __squadron_tag_cmdr(self, cmdr_name, tag):
        sqdr_id = self.__squadron_id() 
        if not sqdr_id:
            EDR_LOG.log(u"Can't tag: not a member of a squadron", "DEBUG")
            return False

        EDR_LOG.log(u"Tagging {} with {} for squadron".format(cmdr_name, tag), "DEBUG")
        profile = self.__edr_sqdrdex(cmdr_name, False)
        if profile is None:
            EDR_LOG.log(u"Couldn't find a squadron profile for {}.".format(cmdr_name), "DEBUG")
            return False

        tagged = profile.tag(tag)
        if not tagged:
            EDR_LOG.log(u"Couldn't tag {} with {} (e.g. already tagged)".format(cmdr_name, tag), "DEBUG")
            self.evict(cmdr_name)
            return False

        sqdrdex_dict = profile.sqdrdex_dict()
        EDR_LOG.log(u"New dex state: {}".format(sqdrdex_dict), "DEBUG")
        augmented_sqdrdex_dict = sqdrdex_dict
        augmented_sqdrdex_dict["level"] = self._player.squadron_info()["squadronLevel"]
        augmented_sqdrdex_dict["by"] = self._player.name
        success = self.server.update_sqdrdex(sqdr_id, profile.cid, augmented_sqdrdex_dict)
        self.evict(cmdr_name)
        return success
         
    def memo_cmdr(self, cmdr_name, memo):
        if memo is None:
            return self.clear_memo_cmdr(cmdr_name)
        EDR_LOG.log(u"Writing a note about {}: {}".format(memo, cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        noted = profile.memo(memo)
        if not noted:
            EDR_LOG.log(u"Couldn't write a note about {}".format(cmdr_name), "DEBUG")
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        self.evict(cmdr_name)
        return success

    def clear_memo_cmdr(self, cmdr_name):
        EDR_LOG.log(u"Removing a note from {}".format(cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        noted = profile.remove_memo()
        if not noted:
            EDR_LOG.log(u"Couldn't remove a note from {}".format(cmdr_name), "DEBUG")
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        self.evict(cmdr_name)
        return success
    
    def untag_cmdr(self, cmdr_name, tag):
        if tag in ["enemy", "ally"]:
            return self.__squadron_untag_cmdr(cmdr_name, tag)
        else:
            return self.__untag_cmdr(cmdr_name, tag)

    def __untag_cmdr(self, cmdr_name, tag):
        EDR_LOG.log(u"Removing {} tag from {}".format(tag, cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        untagged = profile.untag(tag)
        if not untagged:
            EDR_LOG.log(u"Couldn't untag {} (e.g. tag not present)".format(cmdr_name), "DEBUG")
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        EDR_LOG.log(u"New dex state: {}".format(dex_dict), "DEBUG")
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        self.evict(cmdr_name)
        return success

    def __squadron_untag_cmdr(self, cmdr_name, tag):
        sqdr_id = self.__squadron_id()
        if not sqdr_id:
            EDR_LOG.log(u"Can't untag: not a member of a squadron", "DEBUG")
            return False

        EDR_LOG.log(u"Removing {} tag from {}".format(tag, cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        untagged = profile.untag(tag)
        if not untagged:
            EDR_LOG.log(u"Couldn't untag {} (e.g. tag not present)".format(cmdr_name), "DEBUG")
            self.evict(cmdr_name)
            return False

        sqdrdex_dict = profile.sqdrdex_dict()
        EDR_LOG.log(u"New dex state: {}".format(sqdrdex_dict), "DEBUG")
        augmented_sqdrdex_dict = sqdrdex_dict
        augmented_sqdrdex_dict["level"] = self._player.squadron_info()["squadronLevel"]
        augmented_sqdrdex_dict["by"] = self._player.name
        success = self.server.update_sqdrdex(sqdr_id, profile.cid, augmented_sqdrdex_dict)
        self.evict(cmdr_name)
        return success