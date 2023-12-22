from edri18n import _, _c, _edr
import edrlog
import math

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
        if not settlement:
            return False

        if "settlement" not in settlement.get("type", "").lower():
            return False
        
        self.settlements_counter = self.settlements_counter + 1
        if settlement.get('distanceToArrival', None) is None:
            return False

        if "odyssey" in settlement.get("type", "").lower() and self.dlc_name != "Odyssey":
            return False
        return settlement['distanceToArrival'] < self.max_sc_distance
    

class EDRSystemOdySettlementCheck(EDRSystemSettlementCheck):

    def __init__(self):
        super(EDRSystemOdySettlementCheck, self).__init__()

    def check_settlement(self, settlement):
        backup = self.settlements_counter
        if not super(EDRSystemOdySettlementCheck, self).__init__():
            return False
        
        if settlement.get("type", "").lower() != "odyssey settlement":
            self.settlements_counter = backup
            return False
    
        return True
    
    
class EDRSettlementEcoCheck(EDRSystemSettlementCheck):

    def __init__(self, economy):
        super(EDRSettlementEcoCheck, self).__init__()
        self.economy = economy
        self.name = economy
        self.hint = None

    def check_settlement(self, settlement):
        if not super(EDRSettlementEcoCheck, self).check_settlement(settlement):
            return False

        if not self.economy:
            return True

        if not settlement.get('economy', None):
            return False
         
        return self.economy == settlement['economy'].lower()

class EDROdySettlementEcoCheck(EDRSystemOdySettlementCheck):

    def __init__(self, economy):
        super(EDROdySettlementEcoCheck, self).__init__()
        self.economy = economy

class EDRAnarchyOdySettlementCheck(EDROdySettlementEcoCheck):
    
    def __init__(self):
        super(EDRAnarchyOdySettlementCheck, self).__init__(None)
        self.government = "anarchy"
        self.name = _("Anarchy Odyssey settlement")
        self.hint = None

    def check_settlement(self, settlement):
        if not super(EDRAnarchyOdySettlementCheck, self).check_settlement(settlement):
            return False

        if not settlement.get('government', None):
            return False
        
        return self.government == settlement['government'].lower()

class EDRAnarchyAgricultureOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("agriculture")
        self.name = _("Anarchy Agriculture Odyssey settlement")

class EDRAnarchyExtractionOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("extraction")
        self.name = _("Anarchy Extraction Odyssey settlement")

class EDRAnarchyHighTechOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("high tech")
        self.name = _("Anarchy High Tech Odyssey settlement")

class EDRAnarchyIndustrialOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("industrial")
        self.name = _("Anarchy Industrial Odyssey settlement")

class EDRAnarchyMilitaryOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("military")
        self.name = _("Anarchy Military Odyssey settlement")

class EDRAnarchyTourismOdySettlementCheck(EDRAnarchyOdySettlementCheck):
    
    def __init__(self):
        super().__init__("tourism")
        self.name = _("Anarchy Tourism Odyssey settlement")

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
        return EDRSettlementCheckerFactory.SETTLEMENTS_LUT.get(csettlement, EDRAnarchyOdySettlementCheck)(edrsystems, edrfactions, override_sc)