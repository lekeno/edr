import json
import utils2to3

class EDEngineer(object):
    def __init__(self):
        self.name = None
        self.progress = None
        self.rank_progress = None
        self.rank = None
    
    def update(self, progress):
        if self.name is None or self.name == progress.get("Engineer", None):
            self.progress = progress.get("EngineerProgress", None)
            self.rank_progress = progress.get("RankProgress", 0)
            self.rank = progress.get("Rank", 0)
    
    def dibs(self, materials):
        return None

    def interested_in(self, material_name):
        return False
    
class EDDominoGreen(EDEngineer):
    def __init__(self):
        self.name = "Domino Green"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            return {"push": 5}
        return None

    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() == "push"
        return False

class EDKitFowler(EDEngineer):
    def __init__(self):
        self.name = "Kit Fowler"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            return {"opinion polls": 20}
        return None

    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() == "opinion polls"
        return False

class EDYardenBond(EDEngineer):
    def __init__(self):
        self.name = "Yarden Bond"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            return {"smear campaign plans": 8}
        return None

    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() == "smear campaign plans"
        return False

class EDTerraVelasquez(EDEngineer):
    def __init__(self):
        self.name = "Terra Velasquez"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            return {"financial projections": 15}
        return None

    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() == "financial projections"
        return False

class EDJudeNavarro(EDEngineer):
    def __init__(self):
        self.name = "Jude Navarro"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            return {"genetic repair meds": 5}
        return None
    
    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() == "genetic repair meds"
        return False

class EDHeroFerrari(EDEngineer):
    def __init__(self):
        self.name = "Hero Ferrari"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            return {"settlement defence plans": 15}
        return None

    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() == "settlement defence plans"
        return False

class EDWellingtonBeck(EDEngineer):
    def __init__(self):
        self.name = "Wellington Beck"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            me = materials.get("multimedia entertainment", 0)
            ce = materials.get("classic entertainment", 0)
            cm = materials.get("cat media", 0)
            me = max(min(25, me), 8)
            ce = max(min(25-me, ce), 25-me-8)
            cm = 25-me-ce
            
            return {"multimedia entertainment":me, "classic entertainment":ce, "cat media": cm}
        return None

    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() in ["multimedia entertainment", "classic entertainment", "cat media"]
        return False

class EDUmaLaszlo(EDEngineer):
    def __init__(self):
        self.name = "Uma Laszlo"

class EDOdenGeiger(EDEngineer):
    def __init__(self):
        self.name = "Oden Geiger"

    def dibs(self, materials):
        if self.progress != "Unlocked":
            me = materials.get("biological sample", 0)
            ce = materials.get("employee genetic data", 0)
            cm = materials.get("genetic research", 0)
            me = max(min(20, me), 7)
            ce = max(min(20-me, ce), 7)
            cm = 20-me-ce
            
            return {"biological sample":me, "employee genetic data":ce, "genetic research": cm}
        return None

    def interested_in(self, material_name):
        if self.progress != "Unlocked":
            return material_name.lower() in ["biological sample", "employee genetic data", "genetic research"]
        return False

class EDEngineers(object):
    ODYSSEY_MATS = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'odyssey_mats.json')).read())

    def __init__(self):
        self.engineers = {}

    def update(self, engineer_progress_event):
        engineers = engineer_progress_event.get("Engineers", [])
        for e in engineers:
            self.engineers[e["Engineer"]] = EDEngineerFactory.from_engineer_progress_dict(e)

    def dibs(self, materials):
        dibs_list = []
        for name in self.engineers:
            dibs = self.engineers[name].dibs(materials)
            if dibs:
                dibs_list.append(dibs)
        for name in EDEngineers.ODYSSEY_MATS:
            quantity = materials.get(name, 0)
            if EDEngineers.ODYSSEY_MATS[name].get("used", 0) > 0 and quantity:
                dibs_list.append({name: quantity})
        return dibs_list

    def is_useless(self, material_name):
        if material_name not in EDEngineers.ODYSSEY_MATS:
            return False # better safe than sorry
        
        if EDEngineers.ODYSSEY_MATS[material_name].get("used", 0) > 0:
            return False
        
        for name in self.engineers:
            if self.engineers[name].interested_in(material_name):
                return False
        return True


class EDUnknownEngineer(EDEngineer):
    def __init__(self):
        super(EDUnknownEngineer, self).__init__()
        self.type = u'Unknown'

class EDEngineerFactory(object):
    __engineer_classes = {
        "domino green": EDDominoGreen,
        "kit fowler": EDKitFowler,
        "yarden bond": EDYardenBond,
        "terra velasquez": EDTerraVelasquez,
        "jude navarro": EDJudeNavarro,
        "hero ferrari": EDHeroFerrari,
        "wellington beck": EDWellingtonBeck,
        "uma laszlo": EDUmaLaszlo,
        "oden geiger": EDOdenGeiger,
        "unknown": EDUnknownEngineer
    }

    @staticmethod
    def from_engineer_progress_dict(progress):
        engineer = EDEngineerFactory.from_engineer_name(progress.get("Engineer", 'unknown'))
        engineer.update(progress)
        return engineer
        
    @staticmethod
    def from_engineer_name(name):
        return EDEngineerFactory.__engineer_classes.get(name.lower(), EDUnknownEngineer)()

    @staticmethod
    def unknown_engineer():
        return EDUnknownEngineer()