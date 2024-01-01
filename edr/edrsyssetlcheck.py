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
            EDRLOG.log("Failed SysSettlCheck: nothing")
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
    
    def is_ambiguous(self, settlement):
        
        timestamps = settlement.get("updateTime", None)
        if not timestamps:
            print("no timestamp in settlement")
            return True
        
        reference = timestamps.get("information", None)
        if not reference:
            print("no info timestamp in settlement")
            return True
        
        limit = EDTime()
        limit.rewind(60*60*24*5)
        info = EDTime()
        info.from_edsm_timestamp(reference)
        too_old = info <= limit
        if too_old:
            print("too old: {}".format(settlement))
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
        self.exclude_bgs_states.add("war") # TODO other states to exclude?

        self.allegiances = set()
        self.exclude_allegiances = set()

        self.edrsystems = edrsystems

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking OdySettlEco: {}".format(settlement['name']), "DEBUG")
        if not super().check_settlement(settlement):
            EDRLOG.log("Failed settlementcheck", "DEBUG")
            return False

        eco = settlement.get('economy', None)
        EDRLOG.log("Eco: {}".format(eco), "DEBUG")
        if self.economies:
            if not eco or eco.lower() not in self.economies:
                EDRLOG.log("Eco not matching any required state for the controlling faction: {} with {}".format(settlement, eco), "DEBUG")
                return False
            
        if self.exclude_economies:
            if not eco or eco.lower() in self.exclude_economies:
                EDRLOG.log("Eco matching an exluded state for the controlling faction: {} with {}".format(settlement, eco), "DEBUG")
                return False
    
        gvt = settlement.get('government', None)
        EDRLOG.log("GVT: {}".format(gvt), "DEBUG")
        if self.governments:
            if not gvt or gvt.lower() not in self.governments:
                EDRLOG.log("Gvt not matching any required state for the controlling faction: {} with {}".format(settlement, gvt), "DEBUG")
                return False
            
        if self.exclude_governments:
            if not gvt or gvt.lower() in self.exclude_governments:
                EDRLOG.log("Gvt matching an excluded state for the controlling faction: {} with {}".format(settlement, gvt), "DEBUG")
                return False
                
        alg = settlement.get('allegiance', None)
        EDRLOG.log("ALG: {}".format(alg), "DEBUG")
        if self.allegiances:
            if not alg or alg.lower() not in self.allegiances:
                EDRLOG.log("Alg not matching any required state for the controlling faction: {} with {}".format(settlement, alg), "DEBUG")
                return False
            
        if self.exclude_allegiances:
            if not alg or alg.lower() in self.exclude_allegiances:
                EDRLOG.log("Alg matching an excluded state for the controlling faction: {} with {}".format(settlement, alg), "DEBUG")
                return False
        
        factionIDName = settlement.get("controllingFaction", { "id": -1, "name": ""})
        factionName = factionIDName.get("name", "")
        faction = self.edrsystems.faction_in_system(factionName, system_name)
        state = faction.get("state", "None").lower()
        if self.bgs_states:
            if not faction or state not in self.bgs_states:
                EDRLOG.log("BGS not matching any required state for the controlling faction: {} with {}".format(settlement, state), "DEBUG")
                return False
            
        if self.exclude_bgs_states:
            if not faction or state in self.exclude_bgs_states:
                EDRLOG.log("BGS matching an excluded state for the controlling faction: {} with {}".format(settlement, state), "DEBUG")
                return False
        
        return True
    
class EDRSettlementEcoCheck(EDRSystemSettlementCheck):

    def __init__(self, economy):
        super(EDRSettlementEcoCheck, self).__init__()
        self.economy = economy
        self.name = economy
        self.hint = None

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking SettlEco: {}".format(settlement['name']), "DEBUG")
        if not super(EDRSettlementEcoCheck, self).check_settlement(settlement):
            EDRLOG.log("Failed settlementcheck", "DEBUG")
            return False

        if not self.economy:
            EDRLOG.log("success: no condition on economy", "DEBUG")
            return True

        if not settlement.get('economy', None):
            EDRLOG.log("no economy", "DEBUG")
            return False
         
        EDRLOG.log("Eco: {}".format(settlement['economy']), "DEBUG")
        return self.economy == settlement['economy'].lower()

class EDROdySettlementEcoCheck(EDRSystemOdySettlementCheck):

    def __init__(self, economy):
        super(EDROdySettlementEcoCheck, self).__init__()
        self.economy = economy

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking OdySettlEco: {}".format(settlement['name']), "DEBUG")
        if not super(EDROdySettlementEcoCheck, self).check_settlement(settlement):
            EDRLOG.log("Failed settlementcheck", "DEBUG")
            return False

        if not self.economy:
            EDRLOG.log("success: no condition on economy", "DEBUG")
            return True

        if not settlement.get('economy', None):
            EDRLOG.log("no economy", "DEBUG")
            return False
         
        EDRLOG.log("Eco: {}".format(settlement['economy']), "DEBUG")
        return self.economy == settlement['economy'].lower()

class EDRAnarchyOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self, economy=None):
        super(EDRAnarchyOdySettlementCheck, self).__init__(economy)
        self.government = "anarchy"
        self.name = _("Anarchy settlement")
        self.hint = None

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking AnarcOdy: {}".format(settlement['name']), "DEBUG")
        if not super(EDRAnarchyOdySettlementCheck, self).check_settlement(settlement):
            EDRLOG.log("Failed OdySettlementCheck", "DEBUG")
            return False

        if not settlement.get('government', None):
            EDRLOG.log("No gvt", "DEBUG")
            return False
        
        EDRLOG.log("GVT: {}".format(settlement['government']), "DEBUG")
        return self.government == settlement['government'].lower()

class EDRAnarchyAgricultureOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("agriculture")
        self.name = _("Anarchy Agriculture settlement")

class EDRAnarchyExtractionOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("extraction")
        self.name = _("Anarchy Extraction settlement")

class EDRAnarchyHighTechOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("high tech")
        self.name = _("Anarchy High Tech settlement")

class EDRAnarchyIndustrialOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("industrial")
        self.name = _("Anarchy Industrial settlement")

class EDRAnarchyMilitaryOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("military")
        self.name = _("Anarchy Military settlement")

class EDRAnarchyTourismOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("tourism")
        self.name = _("Anarchy Tourism settlement")

class EDRAgricultureOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self):
        super().__init__("agriculture")
        self.name = _("Agriculture settlement")

class EDRExtractionOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self):
        super().__init__("extraction")
        self.name = _("Extraction settlement")

class EDRHighTechOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self):
        super().__init__("high tech")
        self.name = _("High Tech settlement")

class EDRIndustrialOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self):
        super().__init__("industrial")
        self.name = _("Industrial settlement")


class EDRMilitaryOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self):
        super().__init__("military")
        self.name = _("Military settlement")

class EDRTourismOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self):
        super().__init__("tourism")
        self.name = _("Tourism settlement")

class EDRSettlementCheckerFactory(object):
    GVT_LUT = {
        _("anarchy"): "anarchy",
        _("anar"): "anarchy",
        _("colony"): "colony",
        _("communism"): "communism",
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
        _("engineer"): "engineer",
        _("privateownership"): "privateownership",
    }

    ALG_LUT = {
        _("independent"): "independent",
        _("alliance"): "alliance",
        _("federal"): "federal",
        _("imperial"): "imperial",
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
        _("civilwar"): "civil war",
        _("coldwar"): "cold ward",
        _("colonisation"): "colonisation",
        _("drought"): "drought",
        _("elections"): "elections",
        _("expansion"): "expansion",
        _("famine"): "famine",
        _("historicevent"): "historic event",
        _("incursion"): "incursion",
        _("infested"): "infested",
        _("infrastructurefailure"): "infrastructure failure",
        _("investment"): "investment",
        _("lockdown"): "lockdown",
        _("natural disaster"): "natural disaster",
        _("outbreak"): "outbreak",
        _("pirateattack"): "pirate attack",
        _("publicholiday"): "public holiday",
        _("retreat"): "retreat",
        _("revolution"): "revolution",
        _("technologicalleap"): "technological leap",
        _("terroristattack"): "terrorist attack",
        _("tradewar"): "trade war",
        _("war"): "war",
    }

    ECO_LUT = {
        _("agriculture"): "agriculture",
        _("agri"): "agriculture",
        _("colony"): "colony",
        _("damaged"): "damaged",
        _("engineer"): "engineer",
        _("extraction"): "extraction",
        _("extr"): "extraction",
        _("hightech"): "hightech",
        _("high"): "hightech",
        _("industrial"): "industrial",
        _("indu"): "industrial",
        _("military"): "military",
        _("mili"): "military",
        _("prison"): "prison",
        _("privateenterprise"): "private enterprise",
        _("refinery"): "refinery",
        _("repair"): "repair",
        _("rescue"): "rescue",
        _("service"): "service",
        _("terraforming"): "terraforming",
        _("tourism"): "tourism",
        _("tour"): "tourism",
        _("underattack"): "under attack",
    }

    @staticmethod
    def recognized_settlement(settlement_conditions):
        cconditions = settlement_conditions.lower().strip().split(",")
        all_supported_conditions = {
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
        words_salad = words_salad.lower()

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