import os

from edtime import EDTime # EDR_INTERNAL
from edrconfig import EDR_CONFIG # EDR_INTERNAL
from lrucache import LRUCache # EDR_INTERNAL
from edrlog import EDR_LOG # EDR_INTERNAL
from edentities import EDPlayerOne # EDR_INTERNAL
from edrserver import CommsJammedError # EDR_INTERNAL


class EDRCmdrs:
    #TODO these should be player and/or squadron specific
    EDR_CMDRS_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache', 'cmdrs.v8.p')
    EDR_INARA_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache', 'inara.v8.p')
    EDR_SQDRDEX_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache', 'sqdrdex.v2.p')

    def __init__(self, edrserver):
        """
        Initializes EDRCmdrs.

        Args:
            edrserver (EDRServer): The EDR server interface.
        """
        self.server = edrserver
        self._player = EDPlayerOne()
        self.heartbeat_timestamp = None

        edr_config = EDR_CONFIG
        self._edr_heartbeat = edr_config.edr_heartbeat()

        self.cmdrs_cache = LRUCache.load(
            file_path=self.EDR_CMDRS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.cmdrs_max_age()
        )

        self.inara_cache = LRUCache.load(
            file_path=self.EDR_INARA_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.inara_max_age()
        )

        self.sqdrdex_cache = LRUCache.load(
            file_path=self.EDR_SQDRDEX_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.sqdrdex_max_age()
        )

    @property
    def player(self):
        """
        Returns the player object.

        Returns:
            EDPlayerOne: The player object.
        """
        return self._player

    def player_name(self):
        """
        Returns the player's commander name.

        Returns:
            str: The player's commander name.
        """
        return self._player.name

    def set_player_name(self, new_player_name):
        """
        Sets the player's commander name.

        Args:
            new_player_name (str): The new commander name.
        """
        if new_player_name != self._player.name:
            self._player.force_new_name(new_player_name)
            self.__update_squadron_info(force_update=True)

    def player_pledged_to(self, power, time_pledged=0):
        """
        Update player's pledge status.

        Args:
            power (str): The power pledged to.
            time_pledged (int): Timestamp of pledge.

        Returns:
            bool: True if updated, False otherwise.
        """
        edr_config = EDR_CONFIG
        delta = time_pledged - self._player.time_pledged if self._player.time_pledged else time_pledged
        if power == self._player.power and delta <= edr_config.noteworthy_pledge_threshold():
            EDR_LOG.debug("Skipping pledged_to (not noteworthy): current vs. proposed {} vs. {}; {} vs {}".format(self._player.power, power, self._player.time_pledged, time_pledged))
            return False
        self._player.pledged_to(power, time_pledged)
        since = self._player.pledged_since()
        try:
            return self.server.pledged_to(power, since)        
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to update pledge status to EDR.")
            return False

    def __squadron_id(self):
        self.__update_squadron_info()
        info = self._player.squadron_info()
        return info["squadronId"] if info else None

    def __update_squadron_info(self, force_update=False):
        if self.server.is_anonymous():
            return
        mark_twain_flag = int((EDTime.js_epoch_now() - self.heartbeat_timestamp)/1000) >= self._edr_heartbeat if self.heartbeat_timestamp else True
        if force_update or mark_twain_flag:
            info = None
            try:
                info = self.server.heartbeat()
            except CommsJammedError:
                EDR_LOG.warning("Comms jammed: Failed to get heartbeat from EDR.")
                info = None

            if info:
                self.heartbeat_timestamp = info["heartbeat"] if "heartbeat" in info else EDTime.js_epoch_now()
                self._player.squadron_member(info) if "squadronId" in info else self._player.lone_wolf()
            else:
                self.heartbeat_timestamp = EDTime.js_epoch_now()
                self._player.lone_wolf()

    def persist(self):
        """Saves caches to disk."""
        if self.cmdrs_cache:
            self.cmdrs_cache.save(self.EDR_CMDRS_CACHE)

        if self.inara_cache:
            self.inara_cache.save(self.EDR_INARA_CACHE)

        if self.sqdrdex_cache:
            self.sqdrdex_cache.save(self.EDR_SQDRDEX_CACHE)

    def evict(self, cmdr):
        """
        Evicts a commander from caches.

        Args:
            cmdr (str): Commander name.
        """
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
                sq_cmdr_key = "{}:{}".format(sqdr_id, cmdr.lower())
                del self.sqdrdex_cache[sq_cmdr_key]
        except KeyError:
            pass

    def __edr_cmdr(self, cmdr_name, autocreate):
        key = cmdr_name.lower()
        registered = self.cmdrs_cache.has_key(key)
        profile = self.cmdrs_cache.peek(key)
        stale = self.cmdrs_cache.is_stale(key)
        if registered and not stale:
            if profile:
                EDR_LOG.debug(f"Cmdr {cmdr_name} is in the EDR cache (FRESH)")
                return profile
            else:
                EDR_LOG.debug(f"Cmdr {cmdr_name} is unknown to EDR (FRESH dummy entry)")
                return None

        try:
            updated_profile = self.server.cmdr(cmdr_name, autocreate)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed. Failed to fetch cmdr profile from EDR server.")
            updated_profile = None
        except Exception as e: # Catch other, unexpected exceptions
            EDR_LOG.exception(f"Unexpected exception during call to EDR server cmdr: {e}")
            updated_profile = None

        if not updated_profile:
            if registered:
                self.cmdrs_cache.refresh(key)
                EDR_LOG.debug("Server failed. Refreshing old profile")
                return profile
            else:
                self.cmdrs_cache.set(key, None)
                EDR_LOG.debug("No server match/fallback. Setting temporary None entry.")
                return None
        
        dex_profile = None
        try:
            dex_profile = self.server.cmdrdex(updated_profile.cid)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to fetch cmdr dex from EDR server.")
            dex_profile = None

        if dex_profile:
            EDR_LOG.debug("EDR CmdrDex entry found for {cmdr}: {id}".format(cmdr=cmdr_name, id=profile.cid))
            updated_profile.dex(dex_profile)
        
        self.cmdrs_cache.set(key, updated_profile)
        EDR_LOG.debug("Cached EDR profile {cmdr}: {id}".format(cmdr=cmdr_name, id=updated_profile.cid))
        return updated_profile
    
    def __edr_sqdrdex(self, cmdr_name, autocreate):
        sqdr_id = self.__squadron_id()
        if not sqdr_id:
            return None
        key = "{}:{}".format(sqdr_id, cmdr_name.lower())
        profile = self.sqdrdex_cache.get(key)
        if profile:
            EDR_LOG.debug("Cmdr {cmdr} is in the EDR IFF cache for squadron {sqid} with key {key}".format(cmdr=cmdr_name, sqid=sqdr_id, key=key))
            return profile

        profile = self.__edr_cmdr(cmdr_name, autocreate)
        if not profile:
            return None

        sqdrdex_dict = None
        try:
            sqdrdex_dict = self.server.sqdrdex(sqdr_id, profile.cid)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to fetch squadron dex from EDR server.")
            sqdrdex_dict = None

        if sqdrdex_dict:
            EDR_LOG.debug("EDR SqdrDex {sqid} entry found for {cmdr}@{cid}".format(sqid=sqdr_id, cmdr=cmdr_name, cid=profile.cid))
            profile.sqdrdex(sqdrdex_dict)
        self.sqdrdex_cache.set("{}:{}".format(sqdr_id, cmdr_name.lower()), profile)
        EDR_LOG.debug("Cached EDR SqdrDex {sqid} entry for {cmdr}@{cid}".format(sqid=sqdr_id, cmdr=cmdr_name, cid=profile.cid))
        return profile.sqdrdex_profile

    def __inara_cmdr(self, cmdr_name, check_inara_server):
        key = cmdr_name.lower()
        registered = self.inara_cache.has_key(key)
        profile = self.inara_cache.peek(key)
        stale = self.inara_cache.is_stale(key)
        if registered and not stale:
            if profile:
                EDR_LOG.debug(f"Cmdr {cmdr_name} is in the Inara cache (FRESH)")
                return profile
            else:
                EDR_LOG.debug(f"Cmdr {cmdr_name} is unknown to Inara (FRESH dummy entry)")
                return None

        if not check_inara_server:
            EDR_LOG.debug(f"Cmdr {cmdr_name} check vs. Inara cache: cached={registered}; stale={stale}.")
            return None

        updated_profile = None
        
        EDR_LOG.info(f"Inara API call for {cmdr_name}. Inara cache failed: stale={stale}; cached={registered}.")
        try:
            updated_profile = self.server.inara_cmdr(cmdr_name)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to fetch Inara profile via EDR server.")
            updated_profile = None
        except Exception as e:
            EDR_LOG.exception(f"Unexpected exception during call to Inara via EDR server: {e}")
            updated_profile = None

        if not updated_profile:
            if registered:
                self.inara_cache.refresh(key)
                EDR_LOG.debug("Inara server failed. Refreshing old profile")
                return profile
            else:
                self.inara_cache.set(key, None)
                EDR_LOG.debug("No Inara server match/fallback. Setting temporary None entry.")
                return None
        
        if updated_profile.name.lower() == cmdr_name.lower():
            self.inara_cache.set(key, updated_profile)
            EDR_LOG.debug("Cached fresh Inara profile {}.".format(cmdr_name))
            return updated_profile
        else:
            self.inara_cache.set(key, None)
            EDR_LOG.info("No strict match on Inara. Setting temporary None entry.")
            return None

    def cmdr(self, cmdr_name, autocreate=True, check_inara_server=False):
        """
        Retrieves a commander profile.

        Args:
            cmdr_name (str): Commander name.
            autocreate (bool): Create profile on server if missing. Defaults to True.
            check_inara_server (bool): Check Inara server if missing in cache. Defaults to False.

        Returns:
            EDRCmdrProfile: The commander profile.
        """
        profile = self.__edr_cmdr(cmdr_name, autocreate)
        inara_profile = self.__inara_cmdr(cmdr_name, check_inara_server)
    
        if profile is None:
            if inara_profile is None:
                EDR_LOG.error("Failed to retrieve/create cmdr {}".format(cmdr_name))
                return None
            else:
                return inara_profile

        if inara_profile:
            EDR_LOG.info("Combining info from EDR and Inara for cmdr {}".format(cmdr_name))
            profile.complement(inara_profile)
        
        squadron_profile = self.__edr_sqdrdex(cmdr_name, autocreate)
        if squadron_profile:
            EDR_LOG.info("Combining info from Squadron for cmdr {}".format(cmdr_name))
            profile.sqdrdex(squadron_profile.sqdrdex_dict())

        return profile

    def is_friend(self, cmdr_name):
        """
        Checks if a commander is a friend.

        Args:
            cmdr_name (str): Commander name.

        Returns:
            bool: True if friend, False otherwise.
        """
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            return False
        return profile.is_friend()

    def is_ally(self, cmdr_name):
        """
        Checks if a commander is an ally (squadron).

        Args:
            cmdr_name (str): Commander name.

        Returns:
            bool: True if ally, False otherwise.
        """
        sqdr_id = self.__squadron_id()
        if not sqdr_id:
            return False

        profile = self.__edr_sqdrdex(cmdr_name, False)
        if profile:
            return profile.is_ally()
        return False

    def tag_cmdr(self, cmdr_name, tag):
        """
        Tags a commander.

        Args:
            cmdr_name (str): Commander name.
            tag (str): Tag to apply.

        Returns:
            bool: True if successful, False otherwise.
        """
        if tag in ["enemy", "ally"]:
            return self.__squadron_tag_cmdr(cmdr_name, tag)
        return self.__tag_cmdr(cmdr_name, tag)

    def contracts(self):
        """
        Gets list of active contracts.

        Returns:
            list: List of contracts.
        """
        try:
            return self.server.contracts()
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to get contracts list.")
            return None

    def contract_for(self, cmdr_name):
        """
        Gets contract for a commander.

        Args:
            cmdr_name (str): Commander name.

        Returns:
            dict: The contract if found, False otherwise.
        """
        if not cmdr_name:
            return False

        profile = self.cmdr(cmdr_name)
        if not profile:
            return False

        try:
            return self.server.contract_for(profile.cid)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to get contract for {}.".format(cmdr_name))
            return False
    def place_contract(self, cmdr_name, reward):
        """
        Places a bounty contract on a commander.

        Args:
            cmdr_name (str): Commander name.
            reward (int): Reward amount.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not cmdr_name:
            return False
        
        if reward <= 0:
            return self.remove_contract(cmdr_name)

        profile = self.cmdr(cmdr_name)
        if not profile:
            return False
        
        try:
            return self.server.place_contract(profile.cid, {"cname": cmdr_name.lower(), "reward": reward})
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to place contract on {}.".format(cmdr_name))
            return False

    def remove_contract(self, cmdr_name):
        """
        Removes a contract on a commander.

        Args:
            cmdr_name (str): Commander name.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not cmdr_name:
            return False

        profile = self.cmdr(cmdr_name)
        if not profile:
            return False

        try:
            return self.server.remove_contract(profile.cid)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to remove contract on {}.".format(cmdr_name))
            return False

    def __tag_cmdr(self, cmdr_name, tag):
        EDR_LOG.debug("Tagging {} with {}".format(cmdr_name, tag))
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.debug("Couldn't find a profile for {}.".format(cmdr_name))
            return False

        tagged = profile.tag(tag)
        if not tagged:
            EDR_LOG.debug("Couldn't tag {} with {} (e.g. already tagged)".format(cmdr_name, tag))
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        EDR_LOG.debug("New dex state: {}".format(dex_dict))
        
        success = False
        try:
            success = self.server.update_cmdrdex(profile.cid, dex_dict)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to update EDR Dex for {}.".format(cmdr_name))
            success = False

        self.evict(cmdr_name)
        return success

    def __squadron_tag_cmdr(self, cmdr_name, tag):
        sqdr_id = self.__squadron_id() 
        if not sqdr_id:
            EDR_LOG.debug("Can't tag: not a member of a squadron")
            return False

        EDR_LOG.debug("Tagging {} with {} for squadron".format(cmdr_name, tag))
        profile = self.__edr_sqdrdex(cmdr_name, False)
        if profile is None:
            EDR_LOG.debug("Couldn't find a squadron profile for {}.".format(cmdr_name))
            return False

        tagged = profile.tag(tag)
        if not tagged:
            EDR_LOG.debug("Couldn't tag {} with {} (e.g. already tagged)".format(cmdr_name, tag))
            self.evict(cmdr_name)
            return False

        sqdrdex_dict = profile.sqdrdex_dict()
        EDR_LOG.debug("New dex state: {}".format(sqdrdex_dict))
        augmented_sqdrdex_dict = sqdrdex_dict
        augmented_sqdrdex_dict["level"] = self._player.squadron_info()["squadronLevel"]
        augmented_sqdrdex_dict["by"] = self._player.name
        
        success = False # Initialize success before the try block
        try:
            success = self.server.update_sqdrdex(sqdr_id, profile.cid, augmented_sqdrdex_dict)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to update Squadron Dex (tag) for {}.".format(cmdr_name))
            success = False

        self.evict(cmdr_name)
        return success
         
    def memo_cmdr(self, cmdr_name, memo):
        """
        Adds a memo/note to a commander.

        Args:
            cmdr_name (str): Commander name.
            memo (str): The memo content.

        Returns:
             bool: True if successful, False otherwise.
        """
        if memo is None:
            return self.clear_memo_cmdr(cmdr_name)
        EDR_LOG.debug("Writing a note about {}: {}".format(memo, cmdr_name))
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.debug("Couldn't find a profile for {}.".format(cmdr_name))
            return False

        noted = profile.memo(memo)
        if not noted:
            EDR_LOG.debug("Couldn't write a note about {}".format(cmdr_name))
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        
        success = False # Initialize success
        try:
            success = self.server.update_cmdrdex(profile.cid, dex_dict)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to update EDR Dex (memo) for {}.".format(cmdr_name))
            success = False

        self.evict(cmdr_name)
        return success

    def clear_memo_cmdr(self, cmdr_name):
        """
        Clears memo from a commander.

        Args:
            cmdr_name (str): Commander name.

        Returns:
            bool: True if successful, False otherwise.
        """
        EDR_LOG.debug("Removing a note from {}".format(cmdr_name))
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.debug("Couldn't find a profile for {}.".format(cmdr_name))
            return False

        noted = profile.remove_memo()
        if not noted:
            EDR_LOG.debug("Couldn't remove a note from {}".format(cmdr_name))
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        
        success = False # Initialize success
        try:
            success = self.server.update_cmdrdex(profile.cid, dex_dict)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to update EDR Dex (clear memo) for {}.".format(cmdr_name))
            success = False

        self.evict(cmdr_name)
        return success
    
    def untag_cmdr(self, cmdr_name, tag):
        """
        Removes a tag from a commander.

        Args:
            cmdr_name (str): Commander name.
            tag (str): Tag to remove.

        Returns:
            bool: True if successful, False otherwise.
        """
        if tag in ["enemy", "ally"]:
            return self.__squadron_untag_cmdr(cmdr_name, tag)
        return self.__untag_cmdr(cmdr_name, tag)

    def __untag_cmdr(self, cmdr_name, tag):
        EDR_LOG.debug("Removing {} tag from {}".format(tag, cmdr_name))
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.debug("Couldn't find a profile for {}.".format(cmdr_name))
            return False

        untagged = profile.untag(tag)
        if not untagged:
            EDR_LOG.debug("Couldn't untag {} (e.g. tag not present)".format(cmdr_name))
            self.evict(cmdr_name)
            return False

        dex_dict = profile.dex_dict()
        EDR_LOG.debug("New dex state: {}".format(dex_dict))
        
        success = False # Initialize success
        try:
            success = self.server.update_cmdrdex(profile.cid, dex_dict)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to update EDR Dex (untag) for {}.".format(cmdr_name))
            success = False

        self.evict(cmdr_name)
        return success

    def __squadron_untag_cmdr(self, cmdr_name, tag):
        sqdr_id = self.__squadron_id()
        if not sqdr_id:
            EDR_LOG.debug("Can't untag: not a member of a squadron")
            return False

        EDR_LOG.debug("Removing {} tag from {}".format(tag, cmdr_name))
        profile = self.__edr_cmdr(cmdr_name, False)
        if profile is None:
            EDR_LOG.debug("Couldn't find a profile for {}.".format(cmdr_name))
            return False

        untagged = profile.untag(tag)
        if not untagged:
            EDR_LOG.debug("Couldn't untag {} (e.g. tag not present)".format(cmdr_name))
            self.evict(cmdr_name)
            return False

        sqdrdex_dict = profile.sqdrdex_dict()
        EDR_LOG.debug("New dex state: {}".format(sqdrdex_dict))
        augmented_sqdrdex_dict = sqdrdex_dict
        augmented_sqdrdex_dict["level"] = self._player.squadron_info()["squadronLevel"]
        augmented_sqdrdex_dict["by"] = self._player.name
        
        success = False # Initialize success
        try:
            success = self.server.update_sqdrdex(sqdr_id, profile.cid, augmented_sqdrdex_dict)
        except CommsJammedError:
            EDR_LOG.warning("Comms jammed: Failed to update Squadron Dex (untag) for {}.".format(cmdr_name))
            success = False

        self.evict(cmdr_name)
        return success