from __future__ import absolute_import, division

import os
import pickle
import math

from edrconfig import EDRConfig
from lrucache import LRUCache
from edri18n import _
from edtime import EDTime
import utils2to3
import edrlog

EDRLOG = edrlog.EDRLog()

class EDRMaterialOutcomes(object):
    def __init__(self):
        self.outcomes = {}
        
    def chances_of(self, material, grade, likelihood):
        self._combine(material, grade, likelihood, 1)

    def _combine(self, material, grade, likelihood, rolls):
        if self.outcomes.get(material.lower(), None):
            current_likelihood = self.outcomes[material.lower()]["likelihood"]
            current_grade = self.outcomes[material.lower()]["grade"]
            rolls = self.outcomes[material.lower()]["rolls"] + rolls
            base = current_likelihood + likelihood
            grade = current_grade * (current_likelihood // base) + grade * (likelihood // base)
            likelihood = 1.0 - (1.0 - current_likelihood)*(1.0 - likelihood)
        source_lut = {
            u"datamined wake exceptions": u"Distribution Center",
            u"exquisite focus crystals": u"Mission rewards"
        }
        source = source_lut.get(material, _(u"USS-HGE")) 
        self.outcomes[material.lower()] = {"likelihood": likelihood, "grade": grade, "rolls": rolls, "source": source}
        
    def merge(self, other):
        for material in other.outcomes:
            grade = other.outcomes[material]["grade"]
            likelihood = other.outcomes[material]["likelihood"]
            rolls = other.outcomes[material]["rolls"]
            self._combine(material, grade, likelihood, rolls) 
    
    def grade_and_likelihood(self, material):
        material = material.lower()
        if material not in self.outcomes:
            return None

        grade = self.outcomes[material]["grade"]
        likelihood = self.outcomes[material]["likelihood"] // len(self.outcomes)
        return (int(grade), likelihood)

class EDRFaction(object):
    def __init__(self, info):
        self.name = info.get("Name", None)
        if self.name and self.name.lower() == "$faction_none;":
            self.name = None
        self.allegiance = info.get("Allegiance", "").lower()
        self.influence = info.get("Influence", 0.0)
        self.state = EDRFaction._simplified_state(info.get("FactionState", "None"))
        self.active_states = set([self.state])
        active_states = info.get("ActiveStates", []) 
        for state in active_states:
            self.active_states.add(EDRFaction._simplified_state(state.get("State", "None")))
        self.pending_states = set()
        pending_states = info.get("PendingStates", []) 
        for state in pending_states:
            self.pending_states.add(EDRFaction._simplified_state(state.get("State", "None")))
            self.pending_states = set()
        recovering_states = info.get("RecoveringStates", []) 
        for state in recovering_states:
            self.recovering_states.add(EDRFaction._simplified_state(state.get("State", "None")))
        self.governemnt = info.get("Government", None)
        self.isPlayer = None
        edt = EDTime()
        if "timestamp" in info:
            edt.from_journal_timestamp(info["timestamp"])
        self.lastUpdated = edt.as_py_epoch()

    def chance_of_rare_mats(self):
        good_states = self.active_states.intersection(set(['outbreak', 'war', 'boom', 'civil unrest', 'war', 'civil war', 'famine', 'election', 'none']))
        if not good_states:
            return False

        relevant_states = good_states.intersection(set(['outbreak', 'boom', 'civil unrest', 'war', 'civil war', 'famine']))
        if self.allegiance in ['empire', 'federation']:
            if 'none' in good_states: 
                relevant_states.add('none')
            if 'election' in good_states:
                relevant_states.add('election')

        return len(relevant_states) > 0

    def hge_yield(self, security, population, spawning_state, inventory):
        if self.name is None:
            return [_(u"Unknown")]
        primary_state = spawning_state == self.state
        assessment = self._assess_hge(spawning_state, self.influence, self.allegiance, security, population, primary_state)
        return [u"{}".format(inventory.oneliner(material)) for material in assessment.outcomes.keys()]

    def ee_yield(self, security, population, spawning_state, inventory):
        if self.name is None:
            return [_(u"Private Data Beacon")]
        primary_state = spawning_state == self.state
        assessment = self._assess_ee(spawning_state, self.influence, self.allegiance, security, population, primary_state)
        return [u"{}".format(inventory.oneliner(material)) for material in assessment.outcomes.keys()]

    def assess(self, security, population):
        if not self.chance_of_rare_mats():
            return None
        
        overall_outcomes = EDRMaterialOutcomes()
        for state in self.active_states:
            primary_state = state == self.state
            outcomes = self._assess_state(state, self.influence, self.allegiance, security, population, primary_state)
            if outcomes:
                overall_outcomes.merge(outcomes)
        return overall_outcomes
    
    @staticmethod
    def _assess_state(state, influence, allegiance, security, population, primary_state=False):        
        grade = 2 if primary_state else 1
        bonus = 0
        if population >= 1000000:
            bonus = int(max(3, math.log10(population // 100000)))
        outcomes = EDRMaterialOutcomes()
        if state == 'outbreak':
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                grade += 1
            elif allegiance == 'empire':
                lgrade = grade + 1
                outcomes.chances_of('Imperial Shielding', lgrade+bonus, influence)
            outcomes.chances_of('Pharmaceutical Isolators', grade+bonus, influence)
        elif state in ['none', 'election']:
            if allegiance == 'empire':
                lgrade = grade + 1
                outcomes.chances_of('Imperial Shielding', lgrade+bonus, influence)
            if allegiance == 'federation':
                lgrade = grade + 1
                outcomes.chances_of('Core Dynamics Composites', lgrade+bonus, influence)
            if state == 'election' and allegiance in ['federation', 'empire']:
                outcomes.chances_of('Proprietary Composites', grade+bonus, influence)
        elif state == 'boom':
            outcomes.chances_of('Exquisite Focus Crystals', grade+bonus, influence)
            if allegiance in ['alliance', 'independent']:
                grade += 1
            outcomes.chances_of('Proto Light Alloys', grade+bonus, influence)
            outcomes.chances_of('Proto Heat Radiators', grade+bonus, influence)
            outcomes.chances_of('Proto Radiolic Alloys', grade+bonus, influence)
        elif state == 'civil unrest':
            if allegiance in ['alliance', 'independent']:
                grade += 1
            outcomes.chances_of('Improvised Components', grade+bonus, influence)
        elif state in ['war', 'civil war']:
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                grade += 1
            outcomes.chances_of('Military Grade Alloys', grade+bonus, influence)
            outcomes.chances_of('Military Supercapacitors', grade+bonus, influence)
        elif state == 'famine':
            outcomes.chances_of('Datamined Wake Exceptions', grade+bonus, influence)
        
        return outcomes

    @staticmethod
    def _assess_hge(state, influence, allegiance, security, population, primary_state=False):        
        grade = 2 if primary_state else 1
        bonus = 0
        if population >= 1000000:
            bonus = int(max(3, math.log10(population // 100000)))
        outcomes = EDRMaterialOutcomes()
        if state == 'outbreak':
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                grade += 1
            elif allegiance == 'empire':
                lgrade = grade + 1
                outcomes.chances_of('Imperial Shielding', lgrade+bonus, influence)
            outcomes.chances_of('Pharmaceutical Isolators', grade+bonus, influence)
        elif state in ['none', 'election']:
            if allegiance == 'empire':
                lgrade = grade + 1
                outcomes.chances_of('Imperial Shielding', lgrade+bonus, influence)
            if allegiance == 'federation':
                lgrade = grade + 1
                outcomes.chances_of('Core Dynamics Composites', lgrade+bonus, influence)
            if state == 'election' and allegiance in ['federation', 'empire']:
                outcomes.chances_of('Proprietary Composites', grade+bonus, influence)
        elif state == 'boom':
            if allegiance in ['alliance', 'independent']:
                grade += 1
            outcomes.chances_of('Proto Light Alloys', grade+bonus, influence)
            outcomes.chances_of('Proto Heat Radiators', grade+bonus, influence)
            outcomes.chances_of('Proto Radiolic Alloys', grade+bonus, influence)
        elif state == 'civil unrest':
            if allegiance in ['alliance', 'independent']:
                grade += 1
            outcomes.chances_of('Improvised Components', grade+bonus, influence)
        elif state in ['war', 'civil war']:
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                grade += 1
            outcomes.chances_of('Military Grade Alloys', grade+bonus, influence)
            outcomes.chances_of('Military Supercapacitors', grade+bonus, influence)
        return outcomes

    @staticmethod
    def _assess_ee(state, influence, allegiance, security, population, primary_state=False):        
        grade = 2 if primary_state else 1
        bonus = 0
        if population >= 1000000:
            bonus = int(max(3, math.log10(population // 100000)))
        outcomes = EDRMaterialOutcomes()
        if security == '$SYSTEM_SECURITY_low;':
            outcomes.chances_of('Configurable Components', grade+bonus, influence)
        elif security == '$SYSTEM_SECURITY_medium;':
            outcomes.chances_of('Compound Shielding', grade+bonus, influence)
            outcomes.chances_of('Chemical Manipulators', grade+bonus, influence)
            outcomes.chances_of('Refined Focus Crystals', grade+bonus, influence)
        elif security == '$SYSTEM_SECURITY_high;':
            outcomes.chances_of('Compound Shielding', grade+bonus, influence)
            outcomes.chances_of('Chemical Manipulators', grade+bonus, influence)
            outcomes.chances_of('Refined Focus Crystals', grade+bonus, influence)
            outcomes.chances_of('Private Data Beacon', grade+bonus, influence)
        elif security == '$GAlAXY_MAP_INFO_state_anarchy;':
            outcomes.chances_of('Conductive Polymers', grade+bonus, influence)
            outcomes.chances_of('Heat Vanes', grade+bonus, influence)
            outcomes.chances_of('Polymer Capacitors', grade+bonus, influence)
        
        return outcomes

    @staticmethod
    def _assess_convoy(state, influence, allegiance, security, population, primary_state=False):        
        grade = 2 if primary_state else 1
        bonus = 0
        if population >= 1000000:
            bonus = int(max(3, math.log10(population // 100000)))
        outcomes = EDRMaterialOutcomes()
        outcomes.chances_of('Thermic Alloys', grade+bonus, influence)
        if security == '$GAlAXY_MAP_INFO_state_anarchy;':
            lgrade = grade+1
            outcomes.chances_of("Polymer Capacitors", lgrade+bonus, influence)
        if state == 'election' and allegiance in ['federation', 'empire']:
            lgrade = grade+1
            outcomes.chances_of('Proprietary Composites', lgrade+bonus, influence)
        
        return outcomes

    @staticmethod
    def _simplified_state(internal_name):
        if internal_name is None:
            return None
        state = internal_name.lower()
        if state.endswith(u"_desc"):
            useless_suffix_length = len(u"_desc")
            state = state[:-useless_suffix_length]
        elif state.endswith(u"_desc;"):
            useless_suffix_length = len(u"_desc;")
            state = state[:-useless_suffix_length]
        elif state.endswith(u";"):
            state = state[:-1]
        if state.startswith(u"$"):
            state = state[1:]
        if state.startswith(u"factionstate_"):
            useless_prefix_length = len(u"factionstate_")
            state = state[useless_prefix_length:]
        LUT = {
            "": "none",
            "civilwar": "civil war",
            "civilunrest": "civil unrest",
            "civilliberty": "civil liberty"
        }
        return LUT.get(state, state)
    
class EDRFactionEDSM(EDRFaction):
    def __init__(self, info_edsm):
        self.name = info_edsm.get("name", None)
        if self.name and self.name.lower() == "$faction_none;":
            self.name = None
        self.allegiance = info_edsm.get("allegiance", "").lower()
        self.influence = info_edsm.get("influence", 0.0)
        self.state = EDRFaction._simplified_state(info_edsm.get("state", "None"))
        self.active_states = set([self.state])
        active_states = info_edsm.get("activeStates", []) 
        for state in active_states:
            self.active_states.add(EDRFaction._simplified_state(state.get("state", "None")))
        self.pending_states = set()
        pending_states = info_edsm.get("pendingStates", []) 
        for state in pending_states:
            self.pending_states.add(EDRFaction._simplified_state(state.get("state", "None")))
        self.recovering_states = set()
        recovering_states = info_edsm.get("recoveringStates", []) 
        for state in recovering_states:
            self.recovering_states.add(EDRFaction._simplified_state(state.get("state", "None")))
        self.governemnt = info_edsm.get("government", None)
        self.isPlayer = info_edsm.get("isPlayer", None)
        self.lastUpdated = info_edsm.get("lastUpdate", EDTime.py_epoch_now())

class EDRFactions(object):
    EDR_FACTIONS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edr_factions.v1.p')
    EDR_CONTROLLING_FACTIONS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edr_controlling_factions.v1.p')
    EDSM_FACTIONS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_factions.v1.p')

    def __init__(self, edsm_server):
        edr_config = EDRConfig()
        self.edsm_server = edsm_server

        try:
            with open(self.EDR_FACTIONS_CACHE, 'rb') as handle:
                self.factions_cache = pickle.load(handle)
        except:
            self.factions_cache = LRUCache(edr_config.lru_max_size(),
                                                   edr_config.factions_max_age())
            
        try:
            with open(self.EDR_CONTROLLING_FACTIONS_CACHE, 'rb') as handle:
                self.controlling_factions_cache = pickle.load(handle)
        except:
            self.controlling_factions_cache = LRUCache(edr_config.lru_max_size(),
                                                   edr_config.factions_max_age())
            
        try:
            with open(self.EDSM_FACTIONS_CACHE, 'rb') as handle:
                self.edsm_factions_cache = pickle.load(handle)
        except:
            self.edsm_factions_cache = LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_factions_max_age())
        
    def persist(self):
        with open(self.EDR_FACTIONS_CACHE, 'wb') as handle:
            pickle.dump(self.factions_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_CONTROLLING_FACTIONS_CACHE, 'wb') as handle:
            pickle.dump(self.controlling_factions_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_FACTIONS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_factions_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    
    def process(self, factions, star_system):
        factions_in_system = {}
        
        for faction in factions:
            factions_in_system[faction["Name"].lower()] = EDRFaction(faction)
        self.factions_cache.set(star_system.lower(), factions_in_system)

    
    def process_approach_event(self, entry, star_system):
        self.__process_station_settlement_event(entry, star_system)

    def process_docking_event(self, entry, star_system):
        self.__process_station_settlement_event(entry, star_system)

    def __process_station_settlement_event(self, entry, star_system):
        if entry["event"] not in ["Docked", "ApproachSettlement"]:
            return
        
        required = ["timestamp", "StationFaction", "StationAllegiance", "StationGovernment"]
        if not all(keys in required for keys in entry):
            return

        GVT_LUT = {
                "$government_Anarchy;": "Anarchy",
                "$government_Communism;": "Communism",
                "$government_Confederacy;": "Confederary",
                "$government_Cooperative;": "Cooperative",
                "$government_Corporate;": "Corporate",
                "$government_Dictatorship;": "Dictatorship",
                "$government_Democracy;": "Democracy",
                "$government_Engineer;": "Engineer",
                "$government_Feudal;": "Feudal",
                "$government_None;": "None",
                "$government_Patronage;": "Patronage",
                "$government_Prison;": "Prison",
                "$government_Theocracy;": "Theocracy"
        }

        name = entry["StationFaction"].get("Name", "")
        factions_in_system = self.get_all(star_system)
        if factions_in_system and name.lower() in factions_in_system:
            local_faction = factions_in_system[name.lower()]
            local_faction.government = GVT_LUT.get(entry["StationGovernment"], entry["StationGovernment"])
            local_faction.allegiance = entry["StationAllegiance"]
            edt = EDTime()
            edt.from_journal_timestamp(entry["timestamp"])
            local_faction.lastUpdated = edt.as_py_epoch()
            return
        
        art_info = {
            "Name": name,
            "Allegiance": entry["StationAllegiance"],
            "Government": entry["StationGovernment"],
            "timestamp": entry["timestamp"]
        }
        
        factions_in_system[name.lower()] = EDRFaction(art_info)
        

    def get(self, name, star_system):
        factions_in_system = self.get_all(star_system)
        if factions_in_system:
            return factions_in_system.get(name.lower(), None)
        return None

    def get_all(self, star_system):
        factions_in_system = self.factions_cache.get(star_system.lower()) or {}
        print(factions_in_system)
        controlling_faction_for_system = self.controlling_factions_cache.get(star_system.lower())
        if not self.are_factions_stale(star_system):
            return factions_in_system
        
        edsm_factions = self.__get_all_from_edsm(star_system)
        edsm_controlling_faction_name = edsm_factions["controllingFaction"]["name"] if "controllingFaction" in edsm_factions else None
        
        edsm_more_recent = True
        edsm_tracked = set()
        for faction in edsm_factions["factions"]:
            print(faction)
            edsm_tracked.add(faction["name"].lower())
            
            if faction["name"] == edsm_controlling_faction_name:
                if controlling_faction_for_system:
                    local_last_update = controlling_faction_for_system.lastUpdated
                    edsm_last_update = faction["lastUpdate"]
                    if edsm_last_update > local_last_update:
                        EDRLOG.log("Updating controlling faction with EDSM info: {}".format(faction["name"]), "DEBUG")
                        self.controlling_factions_cache.set(star_system.lower(), EDRFactionEDSM(faction))
                else:
                    EDRLOG.log("Setting controlling faction with EDSM info: {}".format(faction["name"]), "DEBUG")
                    self.controlling_factions_cache.set(star_system.lower(), EDRFactionEDSM(faction))

            if faction["name"].lower() in factions_in_system:
                local_faction = factions_in_system[faction["name"].lower()]
                local_last_update = local_faction.lastUpdated
                edsm_last_update = faction["lastUpdate"]
                if edsm_last_update <= local_last_update:
                    edsm_more_recent = False
                    EDRLOG.log("Skipping faction update from EDSM info: {} (timestamps: edsm={}, local={})".format(faction["name"], edsm_last_update, local_last_update), "DEBUG")
                    continue
            
            EDRLOG.log("Updating faction with EDSM info: {}".format(faction["name"]), "DEBUG")
            factions_in_system[faction["name"].lower()] = EDRFactionEDSM(faction)

        if edsm_more_recent and edsm_tracked != factions_in_system.keys():
            EDRLOG.log("Pruning some factions. Seen in EDSM info={}; Local cache={}".format(edsm_tracked, factions_in_system.keys()), "DEBUG")
            remaining_factions_in_system = {n: factions_in_system for n in edsm_tracked}
            EDRLOG.log("Updating local faction cache for {}".format(star_system), "DEBUG")
            self.factions_cache.set(star_system.lower(), remaining_factions_in_system)
        else:
            EDRLOG.log("Updating local faction cache for {}".format(star_system), "DEBUG")
            self.factions_cache.set(star_system.lower(), factions_in_system)

        return factions_in_system
        

    def assess(self, star_system, security, population):
        factions_in_system = self.get_all(star_system)
        assessments = {}
        for faction in factions_in_system:
            assessments[faction] = factions_in_system[faction].assess(security, population)
        return assessments

    def summarize_yields(self, star_system, security, population, inventory):
        assessment = self.assess(star_system, security, population)
        if not assessment:
            return None
        
        yields = {}
        for faction_name in assessment:
            if not assessment[faction_name]:
                continue
            faction = self.get(faction_name, star_system)
            faction_chance = faction.influence
            state_chance = 1.0/len(faction.active_states) if faction.active_states else 0.0
            chance = faction_chance*state_chance
            outcomes = assessment[faction_name].outcomes
            for material in outcomes:
                if yields.get(material, None) is None:
                    yields[material] = 0
                yields[material] += chance
        return [u"{:.0f}%: {}".format(chance*100.0, inventory.oneliner(material.title())) for (material, chance) in sorted(yields.items(), key=lambda x: x[1], reverse=True)]
    
    def are_factions_stale(self, star_system):
        if not star_system:
            return False
        
        return self.factions_cache.is_stale(star_system.lower())
    

    def __get_all_from_edsm(self, star_system):
        if not star_system:
            return None
        factions = self.edsm_factions_cache.get(star_system.lower())
        cached = self.edsm_factions_cache.has_key(star_system.lower())
        if cached or factions:
            EDRLOG.log(u"Factions for system {} are in the cache.".format(star_system), "DEBUG")
            return factions

        EDRLOG.log(u"Factions for system {} are NOT in the cache.".format(star_system), "DEBUG")
        factions = self.edsm_server.factions_in_system(star_system)
        if factions:
            self.edsm_factions_cache.set(star_system.lower(), factions)
            EDRLOG.log(u"Cached {}'s factions".format(star_system), "DEBUG")
            return factions

        self.edsm_factions_cache.set(star_system.lower(), None)
        EDRLOG.log(u"No match on EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        return None
    
    def faction_in_system(self, name, star_system):
        if not star_system or not name:
            return None
        
        cname = name.lower()
        factions = self.edsm_factions_cache.get(star_system.lower())
        cached = self.edsm_factions_cache.has_key(star_system.lower())
        if not(cached or factions):
            EDRLOG.log(u"Factions for system {} are NOT in the cache.".format(star_system), "DEBUG")
            factions = self.edsm_server.factions_in_system(star_system)
        
        if not cached:
            if factions:
                self.edsm_factions_cache.set(star_system.lower(), factions)
                EDRLOG.log(u"Cached {}'s factions".format(star_system), "DEBUG")
            else:
                self.edsm_factions_cache.set(star_system.lower(), None)
                EDRLOG.log(u"No match on EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        
        if factions:
            factionsInfo = factions.get("factions", [])
            for faction in factionsInfo:
                if cname == faction.get("name", "").lower():
                    return faction
        return None
    
    def getControllingFactionAllegiance(self, star_system):
        faction = self.__get_controlling_faction(star_system)
        if not faction:
            return None
        
        return faction.allegiance
    
    def getControllingFactionState(self, star_system):
        faction = self.__get_controlling_faction(star_system)
        if not faction:
            return (None, None)
        
        return (faction.state, faction.lastUpdated)
    
    def __get_controlling_faction(self, star_system):
        if not star_system:
            return None
        
        # TODO a bit much?
        factions = self.get_all(star_system)
        
        return self.controlling_factions_cache.get(star_system.lower())
