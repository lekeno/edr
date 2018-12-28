import edrconfig
import lrucache
import os
import pickle
import math
from edri18n import _

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
            grade = current_grade * (current_likelihood/base) + grade * (likelihood/base)
            likelihood = 1.0 - (1.0 - current_likelihood)*(1.0 - likelihood)
        source_lut = {
            "datamined wake exception": "Distribution Center",
            "exquisite focus crystals": "Mission rewards"
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
        likelihood = self.outcomes[material]["likelihood"] / len(self.outcomes)
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
        self.governemnt = info.get("Government", None)

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

    def hge_yield(self, security, population, spawning_state):
        if self.name is None:
            return [_(u"Unknown")]
        primary_state = spawning_state == self.state
        assessment = self._assess_hge(spawning_state, self.influence, self.allegiance, security, population, primary_state)
        return assessment.outcomes.keys()   

    def ee_yield(self, security, population, spawning_state):
        if self.name is None:
            return [_(u"Private Data Beacon")]
        primary_state = spawning_state == self.state
        assessment = self._assess_ee(spawning_state, self.influence, self.allegiance, security, population, primary_state)
        return assessment.outcomes.keys()  

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
            bonus = int(max(3, math.log10(population / 100000)))
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
            outcomes.chances_of('Proto Heat Radiator', grade+bonus, influence)
            outcomes.chances_of('Proto Radiolic Alloys', grade+bonus, influence)
        elif state == 'civil unrest':
            if allegiance in ['alliance', 'independent']:
                grade += 1
            outcomes.chances_of('Improvised Components', grade+bonus, influence)
        elif state in ['war', 'civil war']:
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                grade += 1
            outcomes.chances_of('Military Grade Alloy', grade+bonus, influence)
            outcomes.chances_of('Military Supercapacitors', grade+bonus, influence)
        elif state == 'famine':
            outcomes.chances_of('Datamined Wake Exception', grade+bonus, influence)
        
        return outcomes

    @staticmethod
    def _assess_hge(state, influence, allegiance, security, population, primary_state=False):        
        grade = 2 if primary_state else 1
        bonus = 0
        if population >= 1000000:
            bonus = int(max(3, math.log10(population / 100000)))
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
            outcomes.chances_of('Proto Heat Radiator', grade+bonus, influence)
            outcomes.chances_of('Proto Radiolic Alloys', grade+bonus, influence)
        elif state == 'civil unrest':
            if allegiance in ['alliance', 'independent']:
                grade += 1
            outcomes.chances_of('Improvised Components', grade+bonus, influence)
        elif state in ['war', 'civil war']:
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                grade += 1
            outcomes.chances_of('Military Grade Alloy', grade+bonus, influence)
            outcomes.chances_of('Military Supercapacitors', grade+bonus, influence)
        return outcomes

    @staticmethod
    def _assess_ee(state, influence, allegiance, security, population, primary_state=False):        
        grade = 2 if primary_state else 1
        bonus = 0
        if population >= 1000000:
            bonus = int(max(3, math.log10(population / 100000)))
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
            bonus = int(max(3, math.log10(population / 100000)))
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

class EDRFactions(object):
    EDR_FACTIONS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/edr_factions.v1.p')

    def __init__(self):
        edr_config = edrconfig.EDRConfig()

        try:
            with open(self.EDR_FACTIONS_CACHE, 'rb') as handle:
                self.factions_cache = pickle.load(handle)
        except:
            self.factions_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                   edr_config.factions_max_age())
        
    def persist(self):
        with open(self.EDR_FACTIONS_CACHE, 'wb') as handle:
            pickle.dump(self.factions_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    
    def process(self, factions, star_system):
        factions_in_system = {}
        for faction in factions:
            factions_in_system[faction["Name"].lower()] = EDRFaction(faction)
        self.factions_cache.set(star_system.lower(), factions_in_system)

    def get(self, name, star_system):
        factions_in_system = self.get_all(star_system)
        if factions_in_system:
            return factions_in_system.get(name.lower(), None)
        return None

    def get_all(self, star_system):
        return self.factions_cache.get(star_system.lower())

    def assess(self, star_system, security, population):
        factions_in_system = self.get_all(star_system)
        assessments = {}
        for faction in factions_in_system:
            assessments[faction] = factions_in_system[faction].assess(security, population)
        return assessments

    def summarize_yields(self, star_system, security, population):
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
        return ["{:.0f}%: {}".format(chance*100.0, material.title()) for (material, chance) in sorted(yields.items(), key=lambda x: x[1], reverse=True)]