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
        self.governments = set()
        self.bgs_states = set()
        self.allegiances = set()
        self.edrsystems = edrsystems

    def check_settlement(self, settlement, system_name=None):
        EDRLOG.log("Checking OdySettlEco: {}".format(settlement['name']), "DEBUG")
        if not super().check_settlement(settlement):
            EDRLOG.log("Failed settlementcheck", "DEBUG")
            return False

        if self.economies:
            eco = settlement.get('economy', None)
            EDRLOG.log("Eco: {}".format(eco), "DEBUG")
            if not eco or eco.lower() not in self.economies:
                EDRLOG.log("Eco not matching any required state for the controlling faction: {} with {}".format(settlement, eco), "DEBUG")
                return False
    
        if self.governments:
            gvt = settlement.get('government', None)
            EDRLOG.log("GVT: {}".format(gvt), "DEBUG")
            if not gvt or gvt.lower() not in self.governments:
                EDRLOG.log("Gvt not matching any required state for the controlling faction: {} with {}".format(settlement, gvt), "DEBUG")
                return False
                
        
        if self.allegiances:
            alg = settlement.get('allegiance', None)
            EDRLOG.log("ALG: {}".format(alg), "DEBUG")
            if not alg or alg.lower() not in self.allegiances:
                EDRLOG.log("Alg not matching any required state for the controlling faction: {} with {}".format(settlement, alg), "DEBUG")
                return False
        
        factionIDName = settlement.get("controllingFaction", { "id": -1, "name": ""})
        factionName = factionIDName.get("name", "")
        faction = self.edrsystems.faction_in_system(factionName, system_name)
        if self.bgs_states:
            if not faction or faction.get("state", "None").lower() not in self.bgs_states:
                EDRLOG.log("BGS not matching any required state for the controlling faction: {} with {}".format(settlement, faction), "DEBUG")
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
    SETTLEMENTS_LUT = {
        "anarchy": EDRAnarchyOdySettlementCheck,
        "anarchy a": EDRAnarchyAgricultureOdySettlementCheck,
        "anarchy agri": EDRAnarchyAgricultureOdySettlementCheck,
        "anarchy agriculture": EDRAnarchyAgricultureOdySettlementCheck,
        "anarchy e": EDRAnarchyExtractionOdySettlementCheck,
        "anarchy extr": EDRAnarchyExtractionOdySettlementCheck,
        "anarchy extraction": EDRAnarchyExtractionOdySettlementCheck,
        "anarchy i": EDRAnarchyIndustrialOdySettlementCheck,
        "anarchy indu": EDRAnarchyIndustrialOdySettlementCheck,
        "anarchy industrial": EDRAnarchyIndustrialOdySettlementCheck,
        "anarchy m": EDRAnarchyMilitaryOdySettlementCheck,
        "anarchy mili": EDRAnarchyMilitaryOdySettlementCheck,
        "anarchy military": EDRAnarchyMilitaryOdySettlementCheck,
        "anarchy t": EDRAnarchyTourismOdySettlementCheck,
        "anarchy tour": EDRAnarchyTourismOdySettlementCheck,
        "anarchy tourism": EDRAnarchyTourismOdySettlementCheck,
        "anarchy h": EDRAnarchyHighTechOdySettlementCheck,
        "anarchy h t": EDRAnarchyHighTechOdySettlementCheck,
        "anarchy high": EDRAnarchyHighTechOdySettlementCheck,
        "anarchy high tech": EDRAnarchyHighTechOdySettlementCheck,
        "anarchy tech": EDRAnarchyHighTechOdySettlementCheck,
        "anarchy": EDRAnarchyOdySettlementCheck,
        "agriculture": EDRAgricultureOdySettlementCheck,
        "extraction": EDRExtractionOdySettlementCheck,
        "industrial": EDRIndustrialOdySettlementCheck,
        "military": EDRMilitaryOdySettlementCheck,
        "tourism": EDRTourismOdySettlementCheck,
        "high tech": EDRHighTechOdySettlementCheck,
    }

    GVT_LUT = {
        _("anarchy"): "anarchy",
        _("anar"): "anarchy",
        _("democracy"): "democracy",
        _("demo"): "democracy",
        # TODO is that it?
    }

    ALG_LUT = {
        _("alliance"): "alliance",
        _("federal"): "federal",
        _("indenpendent"): "independent",
        _("imperial"): "imperial",
        _("thargoid"): "thargoid",
        # TODO is that it?
    }

    BGS_LUT = {
        _("bust"): "bust",
        _("boom"): "boom",
    }

    ECO_LUT = {
        _("agriculture"): "agriculture",
        _("agri"): "agriculture",
        _("extraction"): "extraction",
        _("extr"): "extraction",
        _("industrial"): "industrial",
        _("indu"): "industrial",
        _("military"): "military",
        _("mili"): "military",
        _("tourism"): "tourism",
        _("tour"): "tourism",
        _("hightech"): "hightech",
        _("high"): "hightech",
    }

    @staticmethod
    def recognized_settlement(settlement):
        csettlement = settlement.lower()
        return csettlement in EDRSettlementCheckerFactory.SETTLEMENTS_LUT
    
    @staticmethod
    def recognized_settlement_ex(settlement_conditions):
        cconditions = settlement_conditions.lower()
        all_supported_conditions = {
            **EDRSettlementCheckerFactory.GVT_LUT,
            **EDRSettlementCheckerFactory.ALG_LUT,
            **EDRSettlementCheckerFactory.ECO_LUT,
            **EDRSettlementCheckerFactory.BGS_LUT
        }
        for condition in cconditions:
            if condition in all_supported_conditions:
                return True
        return False

    @staticmethod
    def recognized_candidates(settlement):
        csettlement = settlement.lower()
        keys = EDRSettlementCheckerFactory.SETTLEMENTS_LUT.keys()
        matches = [k for k in keys if csettlement in k or k.startswith(csettlement)]
        return matches


    @staticmethod
    def get_checker(settlement, override_sc_distance):
        csettlement = settlement.lower()
        checker = EDRSettlementCheckerFactory.SETTLEMENTS_LUT.get(csettlement, EDRAnarchyOdySettlementCheck)()
        checker.max_sc_distance = override_sc_distance
        return checker
    

    @staticmethod
    def get_checker_ex(words_salad, override_sc_distance):
        words_salad = words_salad.lower()
        words = words_salad.split(" ")
        
        checker = EDROdySettlementCheck()
        checker.max_sc_distance = override_sc_distance

        irrelevant_salad = True
        for word in words:
            if word in EDRSettlementCheckerFactory.GVT_LUT:
                checker.governments.add(EDRSettlementCheckerFactory.GVT_LUT(word))
                irrelevant_salad = False
                continue
            
            if word in EDRSettlementCheckerFactory.ALG_LUT:
                checker.allegiances.add(EDRSettlementCheckerFactory.ALG_LUT(word))
                irrelevant_salad = False
                continue

            if word in EDRSettlementCheckerFactory.BGS_LUT:
                checker.bgs_states.add(EDRSettlementCheckerFactory.BGS_LUT(word))
                irrelevant_salad = False
                continue

            if word in EDRSettlementCheckerFactory.ECO_LUT:
                checker.economies.add(EDRSettlementCheckerFactory.ECO_LUT(word))
                irrelevant_salad = False
                continue

            EDRLOG("unknown qualifier: {}".format(word))

        if irrelevant_salad:
            return None
        return checker