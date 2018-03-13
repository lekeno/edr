import edrlog
import edtime

EDRLOG = edrlog.EDRLog()

class EDRCmdrDexProfile(object):
    @staticmethod 
    def alignments():
        return [u"outlaw", u"neutral", u"enforcer"]
    
    def __init__(self, dex_dict=None):
        if dex_dict is None:
            dex_dict = {}
        self._alignment = dex_dict.get("alignment", None)
        self.tags = set([self.__tagify(t) for t in dex_dict.get("tags", [])])
        self._friend = dex_dict.get("friend", False)
        self._memo = dex_dict.get("memo", None)

        now = edtime.EDTime.js_epoch_now()
        self.created = dex_dict.get("created", now)
        self.updated = dex_dict.get("updated", now)

    @property
    def alignment(self):
        return self._alignment

    @alignment.setter
    def alignment(self, new_alignment):
        now = edtime.EDTime.js_epoch_now()
        if (new_alignment is None):
            self._alignment = None
            self.updated = now
            return

        if (new_alignment not in EDRCmdrDexProfile.alignments()):
            return
        if (new_alignment == self._alignment):
            return
        self._alignment = new_alignment
        self.updated = now

    
    @property
    def friend(self):
        return self._friend

    @friend.setter
    def friend(self, is_friend):
        if is_friend == self._friend:
            return False
        self._friend = is_friend
        self.updated = edtime.EDTime.js_epoch_now()
        return True

    def is_useless(self):
        return (not self.friend) and (self.alignment is None) and (self.memo is None) and (not self.tags)

    @property
    def memo(self):
        return self._memo

    @memo.setter
    def memo(self, message):
        self._memo = message
        self.updated = edtime.EDTime.js_epoch_now()
        return True

    def __all_tags(self):
        all_tags = []
        if self.alignment:
            all_tags.append(self.alignment)
        
        if self.tags:
            all_tags += self.tags
        return all_tags


    @staticmethod
    def __tagify(tag):
        tag = tag.lower()
        return tag.replace(u" ", u"")

    def tag(self, tag):
        tag = EDRCmdrDexProfile.__tagify(tag)

        if tag == u"friend" and not self._friend:
            self.friend = True
            return True
        elif tag in EDRCmdrDexProfile.alignments() and self._alignment != tag:
            self.alignment = tag
            return True
        elif tag not in self.tags:
            self.tags.add(tag)
            self.updated = edtime.EDTime.js_epoch_now()
            return True

        return False

    def untag(self, tag):
        tag = EDRCmdrDexProfile.__tagify(tag)
        if tag == u"friend" and self._friend:
            self.friend = False
            return True
        elif tag == self._alignment:
            self.alignment = None
            return True
        elif tag in self.tags:
            self.tags.remove(tag)
            self.updated = edtime.EDTime.js_epoch_now()
            return True

        return False


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
        self.patreon = None
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
        self.patreon = None
        self.dex_profile = None

    def from_dict(self, json_cmdr):
        self.name = json_cmdr.get("name", "")
        self.squadron = json_cmdr.get("squadron", None)
        self.role = json_cmdr.get("role", None)
        self.karma = json_cmdr.get("karma", 0)
        self.alignment_hints = json_cmdr.get("alignmentHints", None)
        self.patreon = json_cmdr.get("patreon", None)
        self.dex_profile = None
    
    def complement(self, other_profile):
        if self.name.lower() != other_profile.name.lower():
            EDRLOG.log(u"Can't complement profile since it doesn't match: {} vs. {}".format(other_profile.name, self.name), "DEBUG")
            return False

        if self.squadron is None or self.squadron == "":
            self.squadron = other_profile.squadron

        if self.role is None or self.role == "":
            self.role = other_profile.role

    def dex(self, dex_dict):
        if dex_dict is None:
            return False

        if self.name.lower() != dex_dict.get("name", "").lower():
            EDRLOG.log(u"Can't augment with CmdrDex profile since it doesn't match: {} vs. {}".format(dex_dict.get("name", ""), self.name), "DEBUG")
            return False

        self.dex_profile = EDRCmdrDexProfile(dex_dict)

    def dex_dict(self):
        if self.dex_profile is None:
            return None

        json_friendly_tags = list(self.dex_profile.tags)
        return {
            u"name": self.name,
            u"alignment": self.dex_profile.alignment,
            u"tags": json_friendly_tags,
            u"friend": self.dex_profile.friend,
            u"memo": self.dex_profile.memo,
            u"created": self.dex_profile.created,
            u"updated": self.dex_profile.updated
        }

    def tag(self, tag):
        if self.dex_profile is None:
            self.dex_profile = EDRCmdrDexProfile({})

        return self.dex_profile.tag(tag)

    def untag(self, tag):
        if self.dex_profile is None:
            return False
        if tag is None:
            self.dex_profile = None
            return True
        return self.dex_profile.untag(tag)

    def memo(self, memo):
        if self.dex_profile is None:
            self.dex_profile = EDRCmdrDexProfile({})
            
        self.dex_profile.memo = memo
        return True

    def remove_memo(self):
        if self.dex_profile is None:
            return False
            
        self.dex_profile.memo = None
        if self.dex_profile.is_useless():
            self.dex_profile = None
        return True
    
    def is_dangerous(self):
        if self.dex_profile:
            return self.dex_profile.alignment == "outlaw"
        if self._karma <= -250:
            return True
        if self.alignment_hints and self.alignment_hints["outlaw"] > 0:
            total_hints = sum([hints for hints in self.alignment_hints.values()])
            return (total_hints > 10 and self.alignment_hints["outlaw"] / total_hints > .5)

    def karma_title(self):
        mapped_index = int(10*(self._karma + self.max_karma()) / (2.0*self.max_karma()))
        lut = ["Wanted ++++", "Wanted +++", "Wanted ++", "Wanted +", "Wanted", "Neutral", "Enforcer", "Enforcer +", "Enforcer ++", "Enforcer +++", "Enforcer ++++"]
        karma = lut[mapped_index]

        if self.dex_profile is None:
            return karma

        alignment = self.dex_profile.alignment
        if alignment:
            return u"{} #{}".format(karma, alignment)

        return karma

    def crowd_alignment(self):
        if self.alignment_hints is None:
            return None

        total_hints = float(sum([hints for hints in self.alignment_hints.values()]))
        #TODO increase threshold by an order of magnitude when there are more EDR users
        if (total_hints < 10):
            return u"[!{} ?{} +{}]".format(self.alignment_hints["outlaw"], self.alignment_hints["neutral"], self.alignment_hints["enforcer"])
        return u"[!{:.0%} ?{:.0%} +{:.0%}]".format(self.alignment_hints["outlaw"] / total_hints, self.alignment_hints["neutral"] / total_hints, self.alignment_hints["enforcer"] / total_hints)

    def short_profile(self):
        result = u"{name}: {karma}".format(name=self.name, karma=self.karma_title())

        alignment = self.crowd_alignment()
        if not (alignment is None or alignment == ""):
            result += u" {}".format(alignment)

        if not (self.squadron is None or self.squadron == ""):
            result += u", {squadron}".format(squadron=self.squadron)

        if not (self.role is None or self.role == ""):
            result += u", {role}".format(role=self.role)

        if not (self.patreon is None or self.patreon == ""):
            result += u", Patreon:{patreon}".format(patreon=self.patreon)

        if self.dex_profile:
            if self.dex_profile.friend:
                result += u" [friend]"

            tags = self.dex_profile.tags
            if tags:
                result += u", #{}".format(" #".join(tags))
            
            memo = self.dex_profile.memo
            if memo:
                result += u", {}".format(memo)
            
            updated_jse = self.dex_profile.updated
            if updated_jse:
                updated_edt = edtime.EDTime()
                updated_edt.from_js_epoch(updated_jse)
                result += u" ({})".format(updated_edt.as_immersive_date())

        return result