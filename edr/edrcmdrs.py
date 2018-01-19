import os
import pickle
import edrcmdrsdex
import edrconfig
import edrinara
import lrucache
import edrlog

EDRLOG = edrlog.EDRLog()

class EDRCmdrs(object):
    EDR_CMDRS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/cmdrs.p')
    EDR_INARA_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/inara.p')

    def __init__(self, server):
        self.server = server
        self.inara = edrinara.EDRInara()
 
        edr_config = edrconfig.EDRConfig()
 
        try:
            with open(self.EDR_CMDRS_CACHE, 'rb') as handle:
                self.cmdrs_cache = pickle.load(handle)
        except:
            #TODO increase after there is a good set of cmdrs in the backend
            self.cmdrs_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                 edr_config.cmdrs_max_age())

        try:
            with open(self.EDR_INARA_CACHE, 'rb') as handle:
                self.inara_cache = pickle.load(handle)
        except:
            self.inara_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                 edr_config.inara_max_age())
        
        self.cmdrs_dex = edrcmdrsdex.EDRCmdrsDex()

    def persist(self):
        with open(self.EDR_CMDRS_CACHE, 'wb') as handle:
            pickle.dump(self.cmdrs_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INARA_CACHE, 'wb') as handle:
            pickle.dump(self.inara_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        self.cmdrs_dex.persist()

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
        profile = self.cmdrs_cache.get(cmdr_name)
        if not profile is None:
            EDRLOG.log(u"Cmdr {cmdr} is in the EDR cache with id={cid}".format(cmdr=cmdr_name,
                                                                           cid=profile.cid),
                       "DEBUG")
        else:
            profile = self.server.cmdr(cmdr_name, autocreate)

            if not profile is None:
                self.cmdrs_cache.set(cmdr_name, profile)
                EDRLOG.log(u"Cached EDR profile {cmdr}: {id}".format(cmdr=cmdr_name,
                                                                id=profile.cid), "DEBUG")
        return profile

    def __inara_cmdr(self, cmdr_name, check_inara_server):
        inara_profile = self.inara_cache.get(cmdr_name)
        if not inara_profile is None:
            EDRLOG.log(u"Cmdr {} is in the Inara cache (name={})".format(cmdr_name,
                                                                         inara_profile.name),
                       "DEBUG")
        elif check_inara_server:
            EDRLOG.log(u"No match in Inara cache. Inara API call for {}.".format(cmdr_name), "INFO")
            inara_profile = self.inara.cmdr(cmdr_name)

            if not inara_profile is None:
                self.inara_cache.set(cmdr_name, inara_profile)
                EDRLOG.log(u"Cached Inara profile {}: {},{},{}".format(cmdr_name,
                                                                       inara_profile.name,
                                                                       inara_profile.squadron,
                                                                       inara_profile.role), "DEBUG")
            else:
                self.inara_cache.set(cmdr_name, None)
                EDRLOG.log(u"No match on Inara. Temporary entry to be nice on Inara's server.",
                           "INFO")

    def __dex_cmdr(self, cmdr_name):
        dex_profile = self.cmdrs_dex.get(cmdr_name)
        if dex_profile is None:
            EDRLOG.log(u"Cmdr {} is NOT in the CmdrsDex".format(cmdr_name), "DEBUG")
            return None
        EDRLOG.log(u"Found a dex entry for Cmdr {}: {}".format(cmdr_name, self.cmdrs_dex.short_profile(cmdr_name)), "DEBUG")
        return dex_profile

    def cmdr(self, cmdr_name, autocreate=True, check_inara_server=False):
        profile = self.__edr_cmdr(cmdr_name, autocreate)
        inara_profile = self.__inara_cmdr(cmdr_name, check_inara_server)
        dex_profile = self.__dex_cmdr(cmdr_name)
        profile.dex(dex_profile)

        if profile is None and inara_profile is None and dex_profile is None:
            EDRLOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
            return None
        elif profile and inara_profile:
            EDRLOG.log(u"Combining info from EDR and Inara for cmdr {}".format(cmdr_name), "INFO")
            profile.complement(inara_profile)
            return profile
        return inara_profile if profile is None else profile

    def tag_cmdr(self, cmdr_name, tag):
        tagged = self.cmdrs_dex.tag(cmdr_name, tag)
        if tagged:
            dex_json = self.cmdrs_dex.json(cmdr_name)
            self.server.cmdrsdex(cmdr_name, dex_json)
    
    def memo_cmdr(self, cmdr_name, memo):
        noted = self.cmdrs_dex.memo(cmdr_name, memo)
        if noted:
            dex_json = self.cmdrs_dex.json(cmdr_name)
            self.server.cmdrsdex(cmdr_name, dex_json)
    
    def untag_cmdr(self, cmdr_name, tag):
        untagged = self.cmdrs_dex.untag(cmdr_name, tag)
        if untagged:
            dex_json = self.cmdrs_dex.json(cmdr_name)
            self.server.cmdrsdex(cmdr_name, dex_json)