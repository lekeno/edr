import edrlog

EDRLOG = edrlog.EDRLog()

class EDRCmdrProfile(object):
    @staticmethod
    def max_karma():
        return 1000

    @staticmethod
    def min_karma():
        return -1000
    
    def __init__(self):
        self.cid = None
        self._name = None
        self.squadron = None
        self.role = None
        self._karma = 0
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if new_name is None:
            self._name = None
            return
        
        self._name = new_name
        
    @property
    def karma(self):
        return self._karma

    @karma.setter
    def karma(self, new_karma):
        self._karma = min(max(EDRCmdrProfile.min_karma(), new_karma), EDRCmdrProfile.max_karma())

    def from_inara_api(self, json_cmdr):
        self.name = json_cmdr.get("userName", "")
        wing = json_cmdr.get("commanderWing", None)
        self.squadron = None if wing is None else wing["wingName"] 
        self.role = json_cmdr.get("preferredGameRole", None)
        self.karma = 0 #not supported by Inara API

    def from_dict(self, json_cmdr):
        self.name = json_cmdr.get("name", "")
        self.squadron = json_cmdr.get("squadron", None)
        self.role = json_cmdr.get("role", None)
        self.karma = json_cmdr.get("karma", 0)

    def complement(self, other_profile):
        if self.name.lower() != other_profile.name.lower():
            EDRLOG.log(u"[EDR]Can't complement profile since it doesn't match: {} vs. {}".format(other_profile.name, self.name), "DEBUG")
            return False

        if self.squadron is None or self.squadron == "":
            self.squadron = other_profile.squadron

        if self.role is None or self.role == "":
            self.role = other_profile.role
    
    def is_dangerous(self):
        return self._karma <= -250

    def karma_title(self):
        mapped_index = int(10*(self._karma + self.max_karma()) / (2.0*self.max_karma()))
        lut = ["Most wanted", "Wanted", "Outlaw", "Henchman", "Trouble maker", "Neutral", "Sentinel", "Space Ranger", "Avenger", "Savior", "Saint"]
        return lut[mapped_index]

    def short_profile(self):
        result = u"{name}: {karma}".format(name=self.name, karma=self.karma_title())
       
        if not (self.squadron is None or self.squadron == ""):
            result += ", {squadron}".format(squadron=self.squadron)

        if not (self.role is None or self.role == ""):
            result += ", {role}".format(role=self.role)    
        return result