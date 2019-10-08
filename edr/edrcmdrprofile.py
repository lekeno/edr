# coding= utf-8
import edrlog
import edtime
from edri18n import _, _c

EDRLOG = edrlog.EDRLog()

class EDRCmdrDexProfile(object):
    @staticmethod
    def alignments():
        return [u"outlaw", u"neutral", u"enforcer"]
    
    @staticmethod
    def iffs():
        return [u"enemy", u"ally"]
    
    def __init__(self, dex_dict=None):
        if dex_dict is None:
            dex_dict = {}
        self._alignment = dex_dict.get("alignment", None)
        self._iff = dex_dict.get("rel", None)
        self.iff_by = dex_dict.get("by", None)
        self.tags = set([self.__tagify(t) for t in dex_dict.get("tags", [])])
        self._friend = dex_dict.get("friend", False)
        self._memo = dex_dict.get("memo", None)

        now = edtime.EDTime.js_epoch_now()
        self.created = dex_dict.get("created", now)
        self.updated = dex_dict.get("updated", now)

    @property
    def alignment(self):
        lut = { u"outlaw": _(u"outlaw"), u"neutral": _(u"neutral"), u"enforcer": _(u"enforcer") }
        return lut.get(self._alignment, None)

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
    def iff(self):
        lut = { u"enemy": _(u"enemy"), u"ally": _(u"ally") }
        return lut.get(self._iff, None)

    @iff.setter
    def iff(self, new_iff):
        now = edtime.EDTime.js_epoch_now()
        if (new_iff is None):
            self._iff = None
            self.updated = now
            return

        if (new_iff not in EDRCmdrDexProfile.iffs()):
            return
        if (new_iff == self._iff):
            return
        self._iff = new_iff
        self.updated = now
    
    def is_ally(self):
        return self._iff == "ally"

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
        return (not self.friend) and (self.alignment is None) and (self.iff is None) and (self.memo is None) and (not self.tags)

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

        if self.iff:
            all_tags.append(self.iff)
        
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
        elif tag in EDRCmdrDexProfile.iffs() and self._iff != tag:
            self.iff = tag
            self.iff_by = None
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
        elif tag == self._iff:
            self.iff = None
            self.iff_by = None
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
        self.name = None
        self.squadron = None
        self.squadron_id = None
        self.squadron_rank = None
        self.role = None
        self._karma = 0
        self.dyn_karma = False
        self.alignment_hints = None
        self.patreon = None
        self.dex_profile = None
        self.sqdrdex_profile = None
        self.powerplay = None

        
    @property
    def karma(self):
        return self._karma

    @karma.setter
    def karma(self, new_karma):
        self._karma = min(max(EDRCmdrProfile.min_karma(), new_karma), EDRCmdrProfile.max_karma())

    def from_inara_api(self, json_cmdr):
        self.name = json_cmdr["commanderName"] if "commanderName" in json_cmdr else json_cmdr.get("userName", "")
        wing = json_cmdr.get("commanderWing", None)
        self.squadron = wing["wingName"] if wing else None
        self.squadron_id = wing["wingID"] if wing else None
        self.squadron_rank = wing["wingMemberRank"] if wing else None
        self.role = json_cmdr.get("preferredGameRole", None)
        self.powerplay = json_cmdr.get("preferredPowerName", None)
        self.karma = 0 #not supported by Inara
        self.dyn_karma = False
        self.alignment_hints = None #not supported by Inara
        self.patreon = None
        self.dex_profile = None
        self.sqdrdex_profile = None

    def from_dict(self, json_cmdr):
        self.name = json_cmdr.get("name", "")
        self.squadron = json_cmdr.get("squadron", None)
        self.squadron_id = json_cmdr.get("squadronID", None)
        self.squadron_rank = json_cmdr.get("squadronRank", None)
        self.role = json_cmdr.get("role", None)
        self.karma = json_cmdr.get("karma", 0)
        self.dyn_karma = False
        dkarma = json_cmdr.get("dkarma", 0)
        if self.karma == 0 or (self.karma < 0 and dkarma < self.karma):
            self.karma = dkarma
            self.dyn_karma = True
        self.alignment_hints = json_cmdr.get("alignmentHints", None)
        self.patreon = json_cmdr.get("patreon", None)
        self.dex_profile = None
        self.powerplay = None
        self.sqdrdex_profile = None
    
    def complement(self, other_profile):
        if self.name.lower() != other_profile.name.lower():
            EDRLOG.log(u"Can't complement profile since it doesn't match: {} vs. {}".format(other_profile.name, self.name), "DEBUG")
            return False

        self.squadron = self.squadron if self.squadron else other_profile.squadron
        self.squadron_id = self.squadron_id if self.squadron_id else other_profile.squadron_id
        self.squadron_rank = self.squadron_rank if self.squadron_rank else other_profile.squadron_rank

        if self.role is None or self.role == "":
            self.role = other_profile.role

        if self.powerplay is None or self.powerplay == "":
            self.powerplay = other_profile.powerplay

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
            u"alignment": self.dex_profile._alignment,
            u"tags": json_friendly_tags,
            u"friend": self.dex_profile.friend,
            u"memo": self.dex_profile.memo,
            u"created": self.dex_profile.created,
            u"updated": self.dex_profile.updated
        }

    def sqdrdex(self, dex_dict):
        if dex_dict is None:
            return False
        if self.name.lower() != dex_dict.get("name", "").lower():
            EDRLOG.log(u"Can't augment with CmdrDex profile since it doesn't match: {} vs. {}".format(dex_dict.get("name", ""), self.name), "DEBUG")
            return False

        self.sqdrdex_profile = EDRCmdrDexProfile(dex_dict)

    def sqdrdex_dict(self):
        if self.sqdrdex_profile is None:
            return None

        return {
            u"name": self.name,
            u"rel": self.sqdrdex_profile._iff,
            u"by": self.sqdrdex_profile.iff_by,
        }

    def tag(self, tag):
        if tag in EDRCmdrDexProfile.iffs():
            return self.__sqdrdex_tag(tag)
        return self.__cmdrdex_tag(tag)

    def __cmdrdex_tag(self, tag):
        if self.dex_profile is None:
            self.dex_profile = EDRCmdrDexProfile({})

        return self.dex_profile.tag(tag)

    def __sqdrdex_tag(self, tag):
        if self.sqdrdex_profile is None:
            self.sqdrdex_profile = EDRCmdrDexProfile({})

        return self.sqdrdex_profile.tag(tag)

    def untag(self, tag):
        if tag in EDRCmdrDexProfile.iffs():
            return self.__sqdrdex_untag(tag)
        return self.__cmdrdex_untag(tag)

    def __cmdrdex_untag(self, tag):
        if self.dex_profile is None:
            return False
        if tag is None:
            self.dex_profile = None
            return True
        return self.dex_profile.untag(tag)

    def __sqdrdex_untag(self, tag):
        if self.sqdrdex_profile is None:
            return False
        if tag is None:
            self.sqdrdex_profile = None
            return True
        return self.sqdrdex_profile.untag(tag)

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
    
    def is_friend(self):
        if self.dex_profile:
            return self.dex_profile.friend
        return False

    def is_ally(self):
        if self.sqdrdex_profile:
            return self.sqdrdex_profile.is_ally()
        return False

    def is_dangerous(self, powerplay=None):
        if self.sqdrdex_profile:
            return self.sqdrdex_profile._iff == "enemy"
        if self.dex_profile:
            return self.dex_profile._alignment == "outlaw"
        if self._karma < -200:
            return True
        if powerplay and self.powerplay:
            return powerplay.is_enemy(self.powerplay)
        if self.alignment_hints and self.alignment_hints["outlaw"] > 0:
            total_hints = sum([hints for hints in self.alignment_hints.values()])
            return (total_hints > 10 and self.alignment_hints["outlaw"] / total_hints > .5)

    def crowd_alignment(self):
        if self.alignment_hints is None:
            return None

        total_hints = float(sum([hints for hints in self.alignment_hints.values()]))
        if (total_hints < 10):
            return u"[!{} ?{} +{}]".format(self.alignment_hints["outlaw"], self.alignment_hints["neutral"], self.alignment_hints["enforcer"])
        return u"[!{:.0%} ?{:.0%} +{:.0%}]".format(self.alignment_hints["outlaw"] / total_hints, self.alignment_hints["neutral"] / total_hints, self.alignment_hints["enforcer"] / total_hints)

    def short_profile(self, powerplay=None):
        edr_parts = []
        mapped_index = int(10*(self._karma + self.max_karma()) / (2.0*self.max_karma()))
        lut = [_(u"Outlaw++++"), _(u"Outlaw+++"), _(u"Outlaw++"), _(u"Outlaw+"), _(u"Outlaw"), _(u"Ambiguous"), _(u"Lawful"), _(u"Lawful+"), _(u"Lawful++"), _(u"Lawful+++"), _(u"Lawful++++")]
        karma = ""
        if self.dyn_karma:
            karma += u"≈ "
        karma += lut[mapped_index]

        edr_parts.append(karma)
        
        alignment = self.crowd_alignment()
        if not (alignment is None or alignment == ""):
            edr_parts.append(alignment)
        
        if not (self.patreon is None or self.patreon == ""):
            edr_parts.append(u"${patreon}".format(patreon=self.patreon))

        inara_parts = []
        if not (self.squadron is None or self.squadron == ""):
            inara_parts.append(self.squadron)

        if not (self.role is None or self.role == ""):
            inara_parts.append(self.role)

        powerplay_parts = []
        if not (self.powerplay is None or self.powerplay == ""):
            inara_parts.append(self.powerplay)
            if powerplay and powerplay.is_enemy(self.powerplay):
                powerplay_parts.append(_(u"powerplay|enemy"))
        
        sqdex_parts = []
        iff = self.sqdrdex_profile.iff if self.sqdrdex_profile else None
        iff_by = self.sqdrdex_profile.iff_by if self.sqdrdex_profile else None
        if iff and iff_by:
            sqdex_parts.append(_(u"{iff} by {tagged_by}").format(iff=iff, tagged_by=iff_by))
        elif iff:
            sqdex_parts.append(iff)

        cdex_parts = []
        if self.dex_profile:
            alignment = self.dex_profile.alignment if self.dex_profile else None
            if alignment:
                cdex_parts.append(u"#{}".format(alignment))
            if self.dex_profile.friend:
                cdex_parts.append(_(u"#friend"))

            tags = self.dex_profile.tags
            if tags:
                cdex_parts.append(u"#{}".format(" #".join(tags)))
            
            memo = self.dex_profile.memo
            if memo:
                cdex_parts.append(memo)

        result = u"{}".format(self.name)
        if edr_parts:
            result += u" ✪EDR {}".format(", ".join(edr_parts))

        if inara_parts:
            result += u" ✪INR {}".format(", ".join(inara_parts))

        if sqdex_parts:
            result += u" ✪SQN {}".format(", ".join(sqdex_parts))
    
        if cdex_parts:
            result += u" ✪CMD {}".format(", ".join(cdex_parts))

        if powerplay_parts:
            result += u" ✪PP {}".format(", ".join(powerplay_parts))

        return result