import os
import pickle
from edtime import EDTime
import edrconfig
import edrinara
import lrucache
import edrlog
from edentities import EDCmdr

EDRLOG = edrlog.EDRLog()

class EDRCmdrs(object):
    #TODO these should be player and/or squadron specific
    EDR_CMDRS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/cmdrs.v4.p')
    EDR_INARA_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/inara.v4.p')
    EDR_SQDRDEX_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/sqdrdex.v1.p')

    def __init__(self, edrserver, edrinara):
        self.server = edrserver
        self.inara = edrinara
        self._player = EDCmdr()
        self.heartbeat_timestamp = None
 
        edr_config = edrconfig.EDRConfig()
        self._edr_heartbeat = edr_config.edr_heartbeat()
 
        try:
            with open(self.EDR_CMDRS_CACHE, 'rb') as handle:
                self.cmdrs_cache = pickle.load(handle)
        except:
            self.cmdrs_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                 edr_config.cmdrs_max_age())

        try:
            with open(self.EDR_INARA_CACHE, 'rb') as handle:
                self.inara_cache = pickle.load(handle)
        except:
            self.inara_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                 edr_config.inara_max_age())
        
        try:
            with open(self.EDR_SQDRDEX_CACHE, 'rb') as handle:
                self.sqdrdex_cache = pickle.load(handle)
        except:
            self.sqdrdex_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                 edr_config.sqdrdex_max_age())

    @property
    def player(self):
        return self._player

    def player_name(self):
        return self._player.name

    def set_player_name(self, new_player_name):
        if (new_player_name != self._player.name):
            self._player.name = new_player_name
            self.inara.requester = new_player_name
            self.__update_squadron_info(force_update=True)
        self.inara.cmdr_name = new_player_name

    def player_pledged_to(self, power, time_pledged=0):
        delta = time_pledged - self._player.time_pledged if self._player.time_pledged else time_pledged
        if power == self._player.power and delta <= 60*60*6: #TODO parameterize
            EDRLOG.log(u"Skipping pledged_to (not noteworthy): current vs. proposed {} vs. {}; {} vs {}".format(self._player.power, power, self._player.time_pledged, time_pledged), "DEBUG")
            return False
        self._player.pledged_to(power, time_pledged)
        since = self._player.pledged_since()
        return self.server.pledged_to(power, since)        

    def __squadron_id(self):
        self.__update_squadron_info()
        info = self._player.squadron_info()
        return info["squadronId"] if info else None

    def __update_squadron_info(self, force_update=False):
        print "edrcmdrs heartbeat check"
        print force_update
        print self.heartbeat_timestamp
        mark_twain_flag = int((EDTime.js_epoch_now() - self.heartbeat_timestamp)/1000) >= self._edr_heartbeat if self.heartbeat_timestamp else True
        print mark_twain_flag
        if force_update or mark_twain_flag:
            info = self.server.heartbeat()
            self._player.squadron_member(info) if info else self._player.lone_wolf()
            self.heartbeat_timestamp = info["heartbeat"]

    def persist(self):
        with open(self.EDR_CMDRS_CACHE, 'wb') as handle:
            pickle.dump(self.cmdrs_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INARA_CACHE, 'wb') as handle:
            pickle.dump(self.inara_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_SQDRDEX_CACHE, 'wb') as handle:
            pickle.dump(self.sqdrdex_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def evict(self, cmdr):
        try:
            del self.cmdrs_cache[cmdr]
        except KeyError:
            pass

        try:
            del self.inara_cache[cmdr]
        except KeyError:
            pass

        try:
            del self.sqdrdex_cache[cmdr]
        except KeyError:
            pass

    def __edr_cmdr(self, cmdr_name, autocreate):
        profile = self.cmdrs_cache.get(cmdr_name.lower())
        if profile:
            EDRLOG.log(u"Cmdr {cmdr} is in the EDR cache with id={cid}".format(cmdr=cmdr_name,
                                                                           cid=profile.cid),
                       "DEBUG")
            return profile

        profile = self.server.cmdr(cmdr_name, autocreate)

        if not profile:
            return None
        dex_profile = self.server.cmdrdex(profile.cid)
        if dex_profile:
            EDRLOG.log(u"EDR CmdrDex entry found for {cmdr}: {id}".format(cmdr=cmdr_name,
                                                        id=profile.cid), "DEBUG")
            profile.dex(dex_profile)
        self.cmdrs_cache.set(cmdr_name.lower(), profile)
        EDRLOG.log(u"Cached EDR profile {cmdr}: {id}".format(cmdr=cmdr_name,
                                                        id=profile.cid), "DEBUG")
        return profile
    
    def __edr_sqdrdex(self, cmdr_name, autocreate):
        sqdr_id = self.__squadron_id()
        if not sqdr_id:
            return None
        profile = self.sqdrdex_cache.get(u"{}:{}".format(sqdr_id, cmdr_name.lower()))
        if profile:
            EDRLOG.log(u"Cmdr {cmdr} is in the EDR IFF cache for squadron {sqid}".format(cmdr=cmdr_name,
                                                                                    sqid=sqdr_id),
                                                                                    "DEBUG")
            return profile

        profile = self.__edr_cmdr(cmdr_name, autocreate)
        if not profile:
            return None

        sqdrdex_dict = self.server.sqdrdex(sqdr_id, profile.cid)
        if sqdrdex_dict:
            EDRLOG.log(u"EDR SqdrDex {sqid} entry found for {cmdr}@{cid}".format(sqid=sqdr_id,
                                                                    cmdr=cmdr_name, cid=profile.cid
                                                                    ), "DEBUG")
            profile.sqdrdex(sqdrdex_dict)
        self.sqdrdex_cache.set(u"{}:{}".format(sqdr_id, cmdr_name.lower()), profile)
        EDRLOG.log(u"Cached EDR SqdrDex {sqid} entry for {cmdr}@{cid}".format(sqid=sqdr_id,
                                                                cmdr=cmdr_name, cid=profile.cid), "DEBUG")
        return profile

    def __inara_cmdr(self, cmdr_name, check_inara_server):
        inara_profile = self.inara_cache.get(cmdr_name.lower())
        if inara_profile:
            EDRLOG.log(u"Cmdr {} is in the Inara cache (name={})".format(cmdr_name,
                                                                         inara_profile.name),
                       "DEBUG")
        elif check_inara_server:
            EDRLOG.log(u"No match in Inara cache. Inara API call for {}.".format(cmdr_name), "INFO")
            inara_profile = self.inara.cmdr(cmdr_name)

            if inara_profile and inara_profile.name.lower() == cmdr_name.lower():
                self.inara_cache.set(cmdr_name.lower(), inara_profile)
                EDRLOG.log(u"Cached Inara profile {}: {},{},{},{}".format(cmdr_name,
                                                                          inara_profile.name,
                                                                          inara_profile.squadron,
                                                                          inara_profile.role,
                                                                          inara_profile.powerplay), "DEBUG")
            else:
                inara_profile = None
                self.inara_cache.set(cmdr_name.lower(), None)
                EDRLOG.log(u"No match on Inara. Temporary entry to be nice on Inara's server.",
                           "INFO")
        return inara_profile

    def cmdr(self, cmdr_name, autocreate=True, check_inara_server=False):
        profile = self.__edr_cmdr(cmdr_name, autocreate)
        inara_profile = self.__inara_cmdr(cmdr_name, check_inara_server)
    
        if profile is None:
            if inara_profile is None:
                EDRLOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
                return None
            else:
                return inara_profile

        if inara_profile:
            EDRLOG.log(u"Combining info from EDR and Inara for cmdr {}".format(cmdr_name), "INFO")
            profile.complement(inara_profile)
        
        squadron_profile = self.__edr_sqdrdex(cmdr_name, autocreate)
        if squadron_profile:
            EDRLOG.log(u"Combining info from Squadron for cmdr {}".format(cmdr_name), "INFO")
            profile.sqdrdex(squadron_profile.sqdrdex_dict())

        return profile

    def tag_cmdr(self, cmdr_name, tag):
        if tag in ["enemy", "ally"]:
            return self.__squadron_tag_cmdr(cmdr_name, tag)
        else:
            return self.__tag_cmdr(cmdr_name, tag)

    def __tag_cmdr(self, cmdr_name, tag):
        EDRLOG.log(u"Tagging {} with {}".format(cmdr_name, tag), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDRLOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        tagged = profile.tag(tag)
        if not tagged:
            EDRLOG.log(u"Couldn't tag {} with {} (e.g. already tagged)".format(cmdr_name, tag), "DEBUG")
            return False

        dex_dict = profile.dex_dict()
        EDRLOG.log(u"New dex state: {}".format(dex_dict), "DEBUG")
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        if success:
            self.evict(cmdr_name)
        return success

    def __squadron_tag_cmdr(self, cmdr_name, tag):
        sqdr_id = self.__squadron_id() 
        if not sqdr_id:
            EDRLOG.log(u"Can't tag: not a member of a squadron", "DEBUG")
            return False

        EDRLOG.log(u"Tagging {} with {} for squadron".format(cmdr_name, tag), "DEBUG")
        profile = self.__edr_sqdrdex(cmdr_name, False)
        if profile is None:
            EDRLOG.log(u"Couldn't find a squadron profile for {}.".format(cmdr_name), "DEBUG")
            return False

        tagged = profile.tag(tag)
        if not tagged:
            EDRLOG.log(u"Couldn't tag {} with {} (e.g. already tagged)".format(cmdr_name, tag), "DEBUG")
            return False

        sqdrdex_dict = profile.sqdrdex_dict()
        EDRLOG.log(u"New dex state: {}".format(sqdrdex_dict), "DEBUG")
        success = self.server.update_sqdrdex(sqdr_id, profile.cid, sqdrdex_dict)
        if success:
            self.evict(cmdr_name)
        return success
         
    def memo_cmdr(self, cmdr_name, memo):
        if memo is None:
            return self.clear_memo_cmdr(cmdr_name)
        EDRLOG.log(u"Writing a note about {}: {}".format(memo, cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDRLOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        noted = profile.memo(memo)
        if not noted:
            EDRLOG.log(u"Couldn't write a note about {}".format(cmdr_name), "DEBUG")
            return False

        dex_dict = profile.dex_dict()
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        if success:
            self.evict(cmdr_name)
        return success

    def clear_memo_cmdr(self, cmdr_name):
        EDRLOG.log(u"Removing a note from {}".format(cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDRLOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        noted = profile.remove_memo()
        if not noted:
            EDRLOG.log(u"Couldn't remove a note from {}".format(cmdr_name), "DEBUG")
            return False

        dex_dict = profile.dex_dict()
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        if success:
            self.evict(cmdr_name)
        return success
    
    def untag_cmdr(self, cmdr_name, tag):
        if tag in ["enemy", "ally"]:
            return self.__squadron_untag_cmdr(cmdr_name, tag)
        else:
            return self.__untag_cmdr(cmdr_name, tag)

    def __untag_cmdr(self, cmdr_name, tag):
        EDRLOG.log(u"Removing {} tag from {}".format(tag, cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDRLOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        untagged = profile.untag(tag)
        if not untagged:
            EDRLOG.log(u"Couldn't untag {} (e.g. tag not present)".format(cmdr_name), "DEBUG")
            return False

        dex_dict = profile.dex_dict()
        EDRLOG.log(u"New dex state: {}".format(dex_dict), "DEBUG")
        success = self.server.update_cmdrdex(profile.cid, dex_dict)
        if success:
            self.evict(cmdr_name)
        return success

    def __squadron_untag_cmdr(self, cmdr_name, tag):
        sqdr_id = self.__squadron_id()
        if not sqdr_id:
            EDRLOG.log(u"Can't untag: not a member of a squadron", "DEBUG")
            return False

        EDRLOG.log(u"Removing {} tag from {}".format(tag, cmdr_name), "DEBUG")
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDRLOG.log(u"Couldn't find a profile for {}.".format(cmdr_name), "DEBUG")
            return False

        untagged = profile.untag(tag)
        if not untagged:
            EDRLOG.log(u"Couldn't untag {} (e.g. tag not present)".format(cmdr_name), "DEBUG")
            return False

        sqdrdex_dict = profile.sqdrdex_dict()
        EDRLOG.log(u"New dex state: {}".format(sqdrdex_dict), "DEBUG")
        success = self.server.update_sqdrdex(sqdr_id, profile.cid, sqdrdex_dict)
        if success:
            self.evict(cmdr_name)
        return success