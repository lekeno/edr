from edri18n import _, _c, _edr
import edrlog

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

    def check_settlement(self, settlement):
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
    

class EDRSystemOdySettlementCheck(EDRSystemSettlementCheck):

    def __init__(self):
        super(EDRSystemOdySettlementCheck, self).__init__()

    def check_settlement(self, settlement):
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
    
    
class EDRSettlementEcoCheck(EDRSystemSettlementCheck):

    def __init__(self, economy):
        super(EDRSettlementEcoCheck, self).__init__()
        self.economy = economy
        self.name = economy
        self.hint = None

    def check_settlement(self, settlement):
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

    def check_settlement(self, settlement):
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

    def check_settlement(self, settlement):
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

    @staticmethod
    def recognized_settlement(settlement):
        csettlement = settlement.lower()
        return csettlement in EDRSettlementCheckerFactory.SETTLEMENTS_LUT

    @staticmethod
    def recognized_candidates(settlement):
        csettlement = settlement.lower()
        keys = EDRSettlementCheckerFactory.SETTLEMENTS_LUT.keys()
        matches = [k for k in keys if csettlement in k or k.startswith(csettlement)]
        return matches


    @staticmethod
    def get_checker(settlement, edrsystems, edrfactions, override_sc):
        csettlement = settlement.lower()
        # return EDRSettlementCheckerFactory.SETTLEMENTS_LUT.get(csettlement, EDRAnarchyOdySettlementCheck)(edrsystems, edrfactions, override_sc)
        return EDRSettlementCheckerFactory.SETTLEMENTS_LUT.get(csettlement, EDRAnarchyOdySettlementCheck)()