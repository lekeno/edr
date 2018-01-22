import edrlog
import edtime

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
        self.alignment_hints = None
        self.dex_profile = None
    
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
        self.karma = 0 #not supported by Inara
        self.alignment_hints = None #not supported by Inara

    def from_dict(self, json_cmdr):
        self.name = json_cmdr.get("name", "")
        self.squadron = json_cmdr.get("squadron", None)
        self.role = json_cmdr.get("role", None)
        self.karma = json_cmdr.get("karma", 0)
        self.alignment_hints = json_cmdr.get("alignment_hints", None)

    def complement(self, other_profile):
        if self.name.lower() != other_profile.name.lower():
            EDRLOG.log(u"[EDR]Can't complement profile since it doesn't match: {} vs. {}".format(other_profile.name, self.name), "DEBUG")
            return False

        if self.squadron is None or self.squadron == "":
            self.squadron = other_profile.squadron

        if self.role is None or self.role == "":
            self.role = other_profile.role

    def dex(self, dex_profile):
        if dex_profile is None:
            return False

        if self.name.lower() != dex_profile.get("name", "").lower():
            EDRLOG.log(u"[EDR]Can't augment with CmdrDex profile since it doesn't match: {} vs. {}".format(dex_profile.get("name", ""), self.name), "DEBUG")
            return False

        self.dex_profile = dex_profile
    
    def is_dangerous(self):
        if self.dex_profile:
            return self.dex_profile.get("alignment", None) == "outlaw"
        if self._karma <= -250:
            return True
        if self.alignment_hints and self.alignment_hints["outlaw"] > 0:
            total_hints = sum([hints for hints in self.alignment_hints.values()])
            return (self.alignment_hints["outlaw"] / total_hints > .2) 

    def karma_title(self):
        mapped_index = int(10*(self._karma + self.max_karma()) / (2.0*self.max_karma()))
        lut = ["Most wanted", "Wanted", "Outlaw", "Henchman", "Trouble maker", "Neutral", "Sentinel", "Space Ranger", "Avenger", "Savior", "Saint"]
        karma = lut[mapped_index]

        if self.dex_profile is None:
            return karma

        alignment = self.dex_profile.get("alignment", None)
        if alignment:
            return u"{} #{}".format(karma, alignment)

        return karma

    def alignment(self):
        if self.alignment_hints is None:
            return None

        total_hints = float(sum([hints for hints in self.alignment_hints.values()]))
        return u"[!{:.0%} ={:.0%}  +{:.0%}]".format(self.alignment_hints["outlaw"] / total_hints, self.alignment_hints["outlaw"] / total_hints, self.alignment_hints["outlaw"] / total_hints)


    def short_profile(self):
        result = u"{name}: {karma}{alignment}".format(name=self.name, karma=self.karma_title(), alignment=self.alignment())

        alignment = self.alignment()
        if not (alignment is None or alignment == ""):
            result += u" {}".format(alignment)

        if not (self.squadron is None or self.squadron == ""):
            result += u", {squadron}".format(squadron=self.squadron)

        if not (self.role is None or self.role == ""):
            result += u", {role}".format(role=self.role)

        if self.dex_profile:
            if self.dex_profile.get("friends", False):
                result += u" [friend]"

            tags = self.dex_profile.get("tags", None)
            if tags:
                result += u", #{}".format(" #".join(tags))
            
            memo = self.dex_profile.get("memo", None)
            if memo:
                result += u", {}".format(memo)
            
            updated_jse = self.dex_profile.get("updated", None)
            if updated_jse:
                updated_edt = edtime.EDTime()
                updated_edt.from_js_epoch(updated_jse)
                result += u" ({})".format(updated_edt.as_immersive_date())

        return result