import json
import os

class EDEngineer(object):
    def __init__(self):
        self.name = None
        self.progress = None
        self.rank_progress = None
        self.rank = None
    
    def update(self, progress):
        if self.name is None or self.name == progress.get("Engineer", None):
            self.progress = progress.get("Progress", None)
            self.rank_progress = progress.get("RankProgress", 0)
            self.rank = progress.get("Rank", 0)
    
    def dibs(self, materials):
        return None

    def relevant(self, material_name):
        return False

    def interested_in(self, material_name):
        return False
    
class EDDominoGreen(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Domino Green"

class EDKitFowler(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Kit Fowler"

    def dibs(self, materials):
        needed = {}
        if self.progress is None:
            needed["push"] = 5
        if self.progress != "Unlocked":
            needed["opinionpolls"] = 5
        return needed

    def relevant(self, material_name):
        return material_name.lower() in ["opinionpolls", "push"]

    def interested_in(self, material_name):
        theset = ["opinionpolls"]
        if self.progress is None:
            theset.append("push")
        
        if self.progress != "Unlocked":
            return material_name.lower() in theset
        return False

class EDYardenBond(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Yarden Bond"

    def dibs(self, materials):
        needed = {}
        if self.progress is None:
            needed["surveillanceequipment"] = 5
        if self.progress != "Unlocked":
            needed["smearcampaignplans"] = 5
        return needed

    def relevant(self, material_name):
        return material_name.lower() in ["smearcampaignplans", "surveillanceequipment"]

    def interested_in(self, material_name):
        theset = ["smearcampaignplans"]
        if self.progress is None:
            theset.append("surveillanceequipment")
        
        if self.progress != "Unlocked":
            return material_name.lower() in theset
        return False

class EDJudeNavarro(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Jude Navarro"

class EDTerraVelasquez(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Terra Velasquez"

    def dibs(self, materials):
        needed = {}
        if self.progress is None:
            needed["geneticrepairmeds"] = 5
        return needed

    def relevant(self, material_name):
        return material_name.lower() == "geneticrepairmeds"

    def interested_in(self, material_name):
        theset = []
        if self.progress is None:
            theset.append("geneticrepairmeds")
        
        return material_name.lower() in theset

class EDOdenGeiger(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Oden Geiger"

    def dibs(self, materials):
        needed = {}
        if self.progress != "Unlocked":
            me = materials.get("geneticsample", 0)
            ce = materials.get("employeegeneticdata", 0)
            cm = materials.get("geneticresearch", 0)
            me = max(min(20, me), 7)
            ce = max(min(20-me, ce), 7)
            cm = 20-me-ce
            
        
            needed = {"geneticsample":me, "employeegeneticdata":ce, "geneticresearch": cm}
        
        if self.progress is None:
            needed["financialprojections"] = 15
        
        return needed

    def relevant(Self, material_name):
        return material_name.lower() in ["financialprojections", "geneticsample", "biologicalsample", "employeegeneticdata", "geneticresearch"]

    def interested_in(self, material_name):
        theset = ["geneticsample", "biologicalsample", "employeegeneticdata", "geneticresearch"]
        if self.progress is None:
            theset.append("financialprojections")
        
        if self.progress != "Unlocked":
            return material_name.lower() in theset
        return False

class EDHeroFerrari(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Hero Ferrari"

class EDWellingtonBeck(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Wellington Beck"

    def dibs(self, materials):
        needed = {}
        if self.progress != "Unlocked":
            me = materials.get("multimediaentertainment", 0)
            ce = materials.get("classicentertainment", 0)
            cm = materials.get("catmedia", 0)
            me = max(min(15, me), 5)
            ce = max(min(15-me, ce), 15-me-5)
            cm = 15-me-ce
            
            needed = {"multimedia entertainment":me, "classic entertainment":ce, "cat media": cm}
        
        if self.progress is None:
            needed["settlementdefenceplans"] = 5
        return needed

    def relevant(self, material_name):
        return material_name.lower() in ["settlementdefenceplans", "multimediaentertainment", "classicentertainment", "catmedia"]

    def interested_in(self, material_name):
        theset = ["multimediaentertainment", "classicentertainment", "catmedia"]
        if self.progress is None:
            theset.append("settlementdefenceplans")
        
        if self.progress != "Unlocked":
            return material_name.lower() in theset
        return False

class EDUmaLaszlo(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Uma Laszlo"

    
    def dibs(self, materials):
        needed = {}
        if self.progress is None:
            needed["insightentertainmentsuite"] = 5
        return needed

    def relevant(self, material_name):
        return material_name.lower() == "insightentertainmentsuite"

    def interested_in(self, material_name):
        if self.progress is None:
            return self.relevant(material_name)
        return False

class EDEleanorBresa(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Eleanor Bresa"

class EDBaltanos(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Baltanos"

class EDRosaDayette(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Rosa Dayette"

    def dibs(self, materials):
        needed = {}
        if self.progress != "Unlocked":
            cur = materials.get("culinaryrecipes", 0)
            cor = materials.get("cocktailrecipes", 0)
            cur = max(min(10, cur), 5)
            cor = max(min(10-cur, cor), 10-cur-5)
            
            needed = {"culinary recipes":cur, "cocktail recipes":cor}
        return needed

    def relevant(self, material_name):
        return material_name.lower() in ["culinaryrecipes", "cocktailrecipes"]

    def interested_in(self, material_name):
        theset = ["culinaryrecipes", "cocktailrecipes"]
        if self.progress != "Unlocked":
            return material_name.lower() in theset
        return False
        
class EDYiShen(EDEngineer):
    def __init__(self):
        super().__init__()
        self.name = "Yi Shen"

    def dibs(self, materials):
        needed = {}
        if self.progress is None:
            needed["factionassociates"] = 10
            needed["digitaldesigns"] = 10
            needed["manufacturinginstructions"] = 10
        return needed

    def relevant(self, material_name):
        return material_name.lower() in ["factionassociates", "digitaldesigns", "manufacturinginstructions"]

    def interested_in(self, material_name):
        theset = []
        if self.progress is None:
            theset = ["factionassociates", "digitaldesigns", "manufacturinginstructions"]
        
        if self.progress != "Unlocked":
            return material_name.lower() in theset
        return False

class EDEngineers(object):
    ODYSSEY_MATS = json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'odyssey_mats.json')).read())

    def __init__(self):
        self.engineers = {}
        engineers = ["domino green", "kit fowler", "yarden bond", "terra velasquez", "jude navarro", "hero ferrari", "wellington beck", "uma laszlo", "oden geiger", "baltanos", "rosa dayette", "eleanor bresa", "yi shen"]
        for e in engineers:
            self.engineers[e] = EDEngineerFactory.from_engineer_name(e)

    def update(self, engineer_progress_event):
        engineers = engineer_progress_event.get("Engineers", [])
        for e in engineers:
            if "Engineer" in e:
                self.engineers[e["Engineer"].lower()] = EDEngineerFactory.from_engineer_progress_dict(e)

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
            return False # better safe than sorry, and currently takes care of consumables.
        
        if EDEngineers.ODYSSEY_MATS[material_name].get("used", 0) > 0:
            return False
        
        return not self.is_contributing(material_name)

    def is_contributing(self, material_name):
        for name in self.engineers:
            if self.engineers[name].relevant(material_name):
                return True
        return False

    def is_necessary(self, material_name):
        for name in self.engineers:
            if self.engineers[name].relevant(material_name) and self.engineers[name].interested_in(material_name):
                return True
        return False

    def is_unnecessary(self, material_name):
        for name in self.engineers:
            if self.engineers[name].relevant(material_name) and not self.engineers[name].interested_in(material_name):
                return EDEngineers.ODYSSEY_MATS[material_name].get("used", 0) <= 0
        return False


class EDUnknownEngineer(EDEngineer):
    def __init__(self):
        super(EDUnknownEngineer, self).__init__()
        self.type = 'Unknown'

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
        "rosa dayette": EDRosaDayette,
        "baltanos": EDBaltanos,
        "eleanor bresa": EDEleanorBresa,
        "yi shen": EDYiShen,
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