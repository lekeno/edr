import os
import pickle
import edrconfig
import edrinara
import lrucache
import edrlog

EDRLOG = edrlog.EDRLog()

class EDRCmdrs(object):
    EDR_CMDRS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/cmdrs.v4.p')
    EDR_INARA_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/inara.v3.p')

    def __init__(self, server):
        self.server = server
        self.inara = edrinara.EDRInara()
 
        edr_config = edrconfig.EDRConfig()
 
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

    def persist(self):
        with open(self.EDR_CMDRS_CACHE, 'wb') as handle:
            pickle.dump(self.cmdrs_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INARA_CACHE, 'wb') as handle:
            pickle.dump(self.inara_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def evict(self, cmdr):
        try:
            del self.cmdrs_cache[cmdr]
        except KeyError:
            pass

        try:
            del self.inara_cache[cmdr]
        except KeyError:
            pass

    def __edr_cmdr(self, cmdr_name, autocreate):
        profile = self.cmdrs_cache.get(cmdr_name.lower())
        if not profile is None:
            EDRLOG.log(u"Cmdr {cmdr} is in the EDR cache with id={cid}".format(cmdr=cmdr_name,
                                                                           cid=profile.cid),
                       "DEBUG")
        else:
            profile = self.server.cmdr(cmdr_name, autocreate)

            if not profile is None:
                dex_profile = self.server.cmdrdex(profile.cid)
                if dex_profile:
                    EDRLOG.log(u"EDR CmdrDex entry found for {cmdr}: {id}".format(cmdr=cmdr_name,
                                                                id=profile.cid), "DEBUG")
                    profile.dex(dex_profile)
                self.cmdrs_cache.set(cmdr_name.lower(), profile)
                EDRLOG.log(u"Cached EDR profile {cmdr}: {id}".format(cmdr=cmdr_name,
                                                                id=profile.cid), "DEBUG")
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

        if profile is None and inara_profile is None:
            EDRLOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
            return None
        elif profile and inara_profile:
            EDRLOG.log(u"Combining info from EDR and Inara for cmdr {}".format(cmdr_name), "INFO")
            profile.complement(inara_profile)
            return profile
        return inara_profile if profile is None else profile

    def tag_cmdr(self, cmdr_name, tag):
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