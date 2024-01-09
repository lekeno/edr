from edri18n import _, _c, _edr
import edrlog
from edtime import EDTime

EDRLOG = edrlog.EDRLog()

class EDRSystemSettlementCheck(object):

    def __init__(self):
        self.max_distance = 50
        self.max_sc_distance = 1500
        self.name = None
        self.hint = None
        self.systems_counter = 0
        self.settlements_counter = 0
        self.dlc_name = None


    def set_dlc(self, name):
        self.dlc_name = name

    def check_system(self, system):
        self.systems_counter = self.systems_counter + 1
        if not system:
            return False
        
        if system.get('distance', None) is None:
            return False
        
        return system['distance'] <= self.max_distance

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking SysSettl: {}".format(settlement['name']), "DEBUG")
        if not settlement:
            EDRLOG.log("Failed SysSettlCheck: nothing", "DEBUG")
            return False
        
        EDRLOG.log("Checking: {}".format(settlement['name']), "DEBUG")

        EDRLOG.log(settlement, "DEBUG")
        if "settlement" not in settlement.get("type", "").lower():
            EDRLOG.log("no settlement", "DEBUG")
            return False
        
        self.settlements_counter = self.settlements_counter + 1
        if settlement.get('distanceToArrival', None) is None:
            EDRLOG.log("no distance", "DEBUG")
            return False

        EDRLOG.log("Dist: {} vs {}".format(settlement['distanceToArrival'], self.max_sc_distance), "DEBUG")
        return settlement['distanceToArrival'] < self.max_sc_distance
    
    def is_ambiguous(self, settlement, system_name=None):
        
        timestamps = settlement.get("updateTime", None)
        if not timestamps:
            return True
        
        reference = timestamps.get("information", None)
        if not reference:
            return True
        
        limit = EDTime()
        limit.rewind(60*60*24*5)
        info = EDTime()
        info.from_edsm_timestamp(reference)
        too_old = info <= limit
        return too_old
    

class EDRSystemOdySettlementCheck(EDRSystemSettlementCheck):

    def __init__(self):
        super(EDRSystemOdySettlementCheck, self).__init__()

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking SysOdySettl: {}".format(settlement['name']), "DEBUG")
        backup = self.settlements_counter
        if not super(EDRSystemOdySettlementCheck, self).check_settlement(settlement):
            EDRLOG.log("failed check from SystemOdySettlementCheck", "DEBUG")
            return False
        
        if settlement.get("type", "").lower() != "odyssey settlement":
            self.settlements_counter = backup
            EDRLOG.log("not an odyssey settlement", "DEBUG")
            return False
    
        return True
    
class EDROdySettlementCheck(EDRSystemOdySettlementCheck):

    def __init__(self, edrsystems):
        super().__init__()
        self.economies = set()
        self.exclude_economies = set()
        
        self.governments = set()
        self.exclude_governments = set()

        self.bgs_states = set()
        self.exclude_bgs_states = set()
        # by default, exclude states linked to conflict zones
        self.exclude_bgs_states.add("war")
        self.exclude_bgs_states.add("civil war")

        self.allegiances = set()
        self.exclude_allegiances = set()

        self.edrsystems = edrsystems

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking Odyssey Settlement {}; details: {}".format(settlement['name'], settlement), "DEBUG")
        if not super().check_settlement(settlement):
            EDRLOG.log("Failed basic checks", "DEBUG")
            return False

        eco = settlement.get('economy', None)
        if self.economies:
            if not eco or eco.lower() not in self.economies:
                EDRLOG.log("Eco not matching any required state for the controlling faction: {} vs. {}".format(eco, self.economies), "DEBUG")
                return False
            
        if self.exclude_economies:
            if not eco or eco.lower() in self.exclude_economies:
                EDRLOG.log("Eco matching an exluded state for the controlling faction: {} vs. {}".format(eco, self.exclude_economies), "DEBUG")
                return False
    
        gvt = settlement.get('government', None)
        if self.governments:
            if not gvt or gvt.lower() not in self.governments:
                EDRLOG.log("Gvt not matching any required state for the controlling faction: {} vs. {}".format(gvt, self.governments), "DEBUG")
                return False
            
        if self.exclude_governments:
            if not gvt or gvt.lower() in self.exclude_governments:
                EDRLOG.log("Gvt matching an excluded state for the controlling faction: {} vs. {}".format(gvt, self.exclude_governments), "DEBUG")
                return False
                
        alg = settlement.get('allegiance', None)
        if self.allegiances:
            if not alg or alg.lower() not in self.allegiances:
                EDRLOG.log("Alg not matching any required state for the controlling faction: {} vs. {}".format(alg, self.allegiances), "DEBUG")
                return False
            
        if self.exclude_allegiances:
            if not alg or alg.lower() in self.exclude_allegiances:
                EDRLOG.log("Alg matching an excluded state for the controlling faction: {} vs. {}".format(alg, self.exclude_allegiances), "DEBUG")
                return False
        
        factionIDName = settlement.get("controllingFaction", { "id": -1, "name": ""})
        factionName = factionIDName.get("name", "")
        faction = self.edrsystems.faction_in_system(factionName, system_name)
        EDRLOG.log("Checking faction: {}".format(faction), "DEBUG")
        state = faction.state if faction else None
        
        if self.bgs_states:
            if not faction:
                EDRLOG.log("No faction info => can't match against BGS conditions", "DEBUG")
                return False
            
            if state not in self.bgs_states:
                EDRLOG.log("BGS not matching any required state for the controlling faction: {} vs. {}".format(state, self.bgs_states), "DEBUG")
                return False
            
        if self.exclude_bgs_states:
            if not faction:
                EDRLOG.log("No faction info => can't match against BGS exclusions", "DEBUG")
                return False
            
            if state in self.exclude_bgs_states:
                EDRLOG.log("BGS matching an excluded state for the controlling faction: {} vs. {}".format(state, self.exclude_bgs_states), "DEBUG")
                return False
        
        return True
    
    def is_ambiguous(self, settlement, system_name=None):
        if super().is_ambiguous(settlement):
            return True
        
        if not system_name:
            return True
        
        factionIDName = settlement.get("controllingFaction", { "id": -1, "name": ""})
        factionName = factionIDName.get("name", "")
        faction = self.edrsystems.faction_in_system(factionName, system_name)
        if not faction:
            return True
        
        reference = faction.timestamps["state"]
        if not reference:
            EDRLOG.log("Faction {} is ambiguous because its BGS state is unknown (no update timestamp)".format(factionName), "DEBUG")
            return True
        
        limit_BGS = EDTime()
        limit_BGS.rewind(60*60*24)
        too_old = reference <= limit_BGS.as_py_epoch()
        if too_old:
            EDRLOG.log("Faction {} is ambiguous because its last known BGS state is too old: {}".format(factionName, EDTime.t_minus_py(reference)), "DEBUG")
            return True
        
        return False
        


class EDRCZSettlementChecker(EDROdySettlementCheck):
    def __init__(self, system):
        super().__init__(system)
        self.bgs_states.add("civil war")
        self.bgs_states.add("war")
        self.exclude_bgs_states = set()

class EDRRetoreSettlementChecker(EDROdySettlementCheck):
    def __init__(self, system):
        super().__init__(system)
        self.bgs_states.add("civil unrest")
        self.bgs_states.add("lockdown")
        self.bgs_states.add("natural disaster")
        self.bgs_states.add("pirate attack")
        self.bgs_states.add("terrorist attack")
        self.bgs_states.add("blight")
        self.bgs_states.add("bust")
        self.bgs_states.add("famine")
        self.bgs_states.add("infrastructure failure")
        self.bgs_states.add("outbreak")

class EDRSettlementCheckerFactory(object):
    COMBOS_LUT = {
        _("abandoned"): EDRRetoreSettlementChecker,
        _("restore"): EDRRetoreSettlementChecker,
        _("cz"): EDRCZSettlementChecker,
        _("combatzone"): EDRCZSettlementChecker,
    }
    
    GVT_LUT = {
        _("anarchy"): "anarchy",
        _("anar"): "anarchy",
        _("confederacy"): "confederacy",
        _("cooperative"): "cooperative",
        _("corporate"): "corporate",
        _("democracy"): "democracy",
        _("demo"): "democracy",
        _("dictatorship"): "dictatorship",
        _("feudal"): "feudal",
        _("patronage"): "patronage",
        _("prison"): "prison",
        _("prison colony"): "prison colony",
        _("theocracy"): "theocracy",
        _("engineer"): "workshop (engineer)", # not "engineer",
        _("communism"): "communism",
        # _("privateownership"): "fleetcarrier"
        # _("colony"): "colony", # Does not exist
    }

    ALG_LUT = {
        _("independent"): "independent",
        _("alliance"): "alliance",
        _("federal"): "federation",
        _("federation"): "federation",
        _("imperial"): "empire",
        _("empire"): "empire",
        _("pirate"): "pirate",
        _("pilotsfederation"): "pilots federation",
        _("thargoids"): "thargoids",
        _("guardians"): "guardians",
    }

    BGS_LUT = {
        _("blight"): "blight",
        _("bust"): "bust",
        _("boom"): "boom",
        _("civilliberty"): "civil liberty",
        _("civilunrest"): "civil unrest",
        _("coldwar"): "cold war", # may not exist
        _("civilwar"): "civil war",
        _("colonisation"): "colonisation", # may not exist
        _("drought"): "drought",
        _("elections"): "elections",
        _("expansion"): "expansion",
        _("famine"): "famine",
        _("historicevent"): "historic event", # may not exist
        _("incursion"): "incursion", # may not exist
        _("infested"): "infested", # may not exist
        _("infrastructurefailure"): "infrastructure failure",
        _("investment"): "investment",
        _("lockdown"): "lockdown",
        _("naturaldisaster"): "natural disaster",
        _("outbreak"): "outbreak",
        _("pirateattack"): "pirate attack",
        _("publicholiday"): "public holiday",
        _("retreat"): "retreat",
        _("revolution"): "revolution", # may not exist
        _("technologicalleap"): "technological leap", # may not exist
        _("terroristattack"): "terrorist attack",
        _("tradewar"): "trade war", # may not exist
        _("war"): "war",
    }

    ECO_LUT = {
        _("agriculture"): "agriculture",
        _("agri"): "agriculture",
        _("colony"): "colony",
        _("damaged"): "damaged", # may not exist
        _("engineer"): "engineer",
        _("extraction"): "extraction",
        _("extr"): "extraction",
        _("hightech"): "high tech",
        _("high"): "high tech",
        _("industrial"): "industrial",
        _("indu"): "industrial",
        _("military"): "military",
        _("mili"): "military",
        _("prison"): "prison",
        _("privateenterprise"): "fleet carrier",
        _("refinery"): "refinery",
        _("repair"): "repair", #  may not exist
        _("rescue"): "rescue",
        _("service"): "service",
        _("terraforming"): "terraforming",
        _("tourism"): "tourism",
        _("tour"): "tourism",
        _("underattack"): "under attack", # may not exist
    }

    @staticmethod
    def recognized_settlement(settlement_conditions):
        cconditions = settlement_conditions.lower().strip().replace(" ", "")
        cconditions = cconditions.split(",")

        all_supported_conditions = {
            **EDRSettlementCheckerFactory.COMBOS_LUT,
            **EDRSettlementCheckerFactory.GVT_LUT,
            **EDRSettlementCheckerFactory.ALG_LUT,
            **EDRSettlementCheckerFactory.ECO_LUT,
            **EDRSettlementCheckerFactory.BGS_LUT
        }
        
        for condition in cconditions:
            if condition in all_supported_conditions:
                return True
            
            if condition.startswith("-") and condition[1:] in all_supported_conditions:
                return True
        return False
    
    @staticmethod
    def get_checker(words_salad, override_sc_distance, edrsystems):
        words_salad = words_salad.lower().strip().replace(" ","")

        if words_salad in EDRSettlementCheckerFactory.COMBOS_LUT:
            checker = EDRSettlementCheckerFactory.COMBOS_LUT[words_salad](edrsystems)
            checker.max_sc_distance = override_sc_distance
            return checker
        
        words = words_salad.split(",")
        checker = EDROdySettlementCheck(edrsystems)
        checker.max_sc_distance = override_sc_distance

        irrelevant_salad = True
        for word in words:
            if word in EDRSettlementCheckerFactory.GVT_LUT:
                checker.governments.add(EDRSettlementCheckerFactory.GVT_LUT[word])
                checker.exclude_governments.discard(EDRSettlementCheckerFactory.GVT_LUT[word])
                irrelevant_salad = False
                continue

            if word.startswith("-") and word[1:] in EDRSettlementCheckerFactory.GVT_LUT:
                checker.exclude_governments.add(EDRSettlementCheckerFactory.GVT_LUT[word[1:]])
                checker.governments.discard(EDRSettlementCheckerFactory.GVT_LUT[word[1:]])
                irrelevant_salad = False
                continue
            

            if word in EDRSettlementCheckerFactory.ALG_LUT:
                checker.allegiances.add(EDRSettlementCheckerFactory.ALG_LUT[word])
                checker.exclude_allegiances.discard(EDRSettlementCheckerFactory.ALG_LUT[word])
                irrelevant_salad = False
                continue

            if word.startswith("-") and word[1:] in EDRSettlementCheckerFactory.ALG_LUT:
                checker.exclude_allegiances.add(EDRSettlementCheckerFactory.ALG_LUT[word[1:]])
                checker.allegiances.discard(EDRSettlementCheckerFactory.ALG_LUT[word[1:]])
                irrelevant_salad = False
                continue


            if word in EDRSettlementCheckerFactory.BGS_LUT:
                checker.bgs_states.add(EDRSettlementCheckerFactory.BGS_LUT[word])
                checker.exclude_bgs_states.discard(EDRSettlementCheckerFactory.BGS_LUT[word])
                irrelevant_salad = False
                continue

            if word.startswith("-") and word[1:] in EDRSettlementCheckerFactory.BGS_LUT:
                checker.exclude_bgs_states.add(EDRSettlementCheckerFactory.BGS_LUT[word[1:]])
                checker.bgs_states.discard(EDRSettlementCheckerFactory.BGS_LUT[word[1:]])
                irrelevant_salad = False
                continue


            if word in EDRSettlementCheckerFactory.ECO_LUT:
                checker.economies.add(EDRSettlementCheckerFactory.ECO_LUT[word])
                checker.exclude_economies.discard(EDRSettlementCheckerFactory.ECO_LUT[word])
                irrelevant_salad = False
                continue

            if word.startswith("-") and word[1:] in EDRSettlementCheckerFactory.ECO_LUT:
                checker.exclude_economies.add(EDRSettlementCheckerFactory.ECO_LUT[word[1:]])
                checker.economies.discard(EDRSettlementCheckerFactory.ECO_LUT[word[1:]])
                irrelevant_salad = False
                continue

            EDRLOG.log("unknown qualifier: {}".format(word), "DEBUG")

        if irrelevant_salad:
            return None
        return checker


    @staticmethod
    def recognized_candidates(words_salad):
        words_salad = words_salad.lower().strip()

        keys = list(EDRSettlementCheckerFactory.COMBOS_LUT.keys())
        matches = [k for k in keys if words_salad in k or k.startswith(words_salad)]
        
        words = words_salad.split(",")
        keys = list(EDRSettlementCheckerFactory.ALG_LUT.keys())
        keys.extend(list(EDRSettlementCheckerFactory.GVT_LUT.keys()))
        keys.extend(list(EDRSettlementCheckerFactory.ECO_LUT.keys()))
        keys.extend(list(EDRSettlementCheckerFactory.BGS_LUT.keys()))
        for word in words:
            matches.extend([k for k in keys if word in k or k.startswith(word)])
    
        return matches