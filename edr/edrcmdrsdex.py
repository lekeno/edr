
import time
import calendar
import json
import os
import edtime

#TODO make a proper EDRCmdrDexEntry class that can be json-ified or just use pickle and the edr website for exporting lists?

class EDRCmdrsDex(object):
    EDR_CMDRS_DEX_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'data/cmdrsdex.0.5.0.beta.3.json')

    def __init__(self):
        try:
            with open(self.EDR_CMDRS_DEX_PATH, 'r') as json_file:
                self.cmdrs = json.load(json_file)
        except:
            self.cmdrs = {}
    
    def get(self, cmdr_name):
        return self.cmdrs.get(cmdr_name.lower(), None)

    def __all_tags(self, cmdr_name):
        if not self.exists(cmdr_name):
            return None
        
        all_tags = []
        cname = cmdr_name.lower()
        if self.cmdrs[cname]["alignment"]:
            all_tags.append(self.cmdrs[cname]["alignment"])
        
        if self.cmdrs[cname]["tags"]:
            all_tags += self.cmdrs[cname]["tags"]
        return all_tags
    
    def short_profile(self, cmdr_name):
        if not self.exists(cmdr_name):
            return None

        cname = cmdr_name.lower()
        profile = u"{}".format(self.cmdrs[cname]["name"])
        
        if self.cmdrs[cname]["friend"]:
            profile += u" [friend]"


        all_tags = self.__all_tags(cmdr_name)
        if all_tags:
            profile += u" #{}".format(" #".join(all_tags))
        
        memo = self.cmdrs[cname]["memo"]
        if memo:
            profile += u" {}".format(memo)

        updated = self.cmdrs[cname]["updated"]
        if updated:
            ed_updated = edtime.EDTime()
            ed_updated.from_js_epoch(updated)
            profile += u" ({})".format(ed_updated.as_immersive_date())
        
        return profile

    def add(self, name):
        if self.exists(name):
            return False

        now = EDRCmdrsDex.__js_epoch_now()
        cmdr_entry = {
            u"name": name,
            u"alignment": None,
            u"tags": [],
            u"friend": False,
            u"memo": None,
            u"created": now,
            u"updated": now
        }
        self.cmdrs[name.lower()] = cmdr_entry
    
    def alignment(self, cmdr_name):
        if not self.exists(cmdr_name):
            return None
        return self.cmdrs[cmdr_name.lower()]["alignment"]

    @staticmethod 
    def alignments():
        return [u"outlaw", u"neutral", u"enforcer"]

    @staticmethod
    def __js_epoch_now():
        return 1000 * calendar.timegm(time.gmtime())
    
    def exists(self, name):
        return name.lower() in self.cmdrs

    def memo(self, name, memo):
        if not self.exists(name):
            self.add(name)

        cname = name.lower()
        self.cmdrs[cname]["memo"] = memo
        self.cmdrs[cname]["updated"] = EDRCmdrsDex.__js_epoch_now()
        #TODO EDRServer update
    
    def remove_memo(self, name):
        if not self.exists(name):
            self.add(name)

        cname = name.lower()
        self.cmdrs[cname]["memo"] = None
        self.cmdrs[cname]["updated"] = EDRCmdrsDex.__js_epoch_now()
        #TODO EDRServer update

    @staticmethod
    def __tagify(tag):
        tag = tag.lower()
        return tag.replace(u" ", u"")
    
    def tag(self, name, tag):
        updated = False
        if not self.exists(name):
            self.add(name)
            updated = True
        
        cname = name.lower()
        tag = EDRCmdrsDex.__tagify(tag)

        if tag == u"friend" and not self.cmdrs[cname]["friend"]:
            self.cmdrs[cname]["friend"] = True
            updated = True
        elif tag in EDRCmdrsDex.alignments() and self.cmdrs[cname]["alignment"] != tag:
            self.cmdrs[cname]["alignment"] = tag
            updated = True
        elif tag not in self.cmdrs[cname]["tags"]:
            self.cmdrs[cname]["tags"].append(tag)
            updated = True
        
        if updated:
            self.cmdrs[cname]["updated"] = EDRCmdrsDex.__js_epoch_now()

        return updated
        
    def untag(self, name, tag):
        updated = False
        if not self.exists(name):
            return False
        
        cname = name.lower()
        tag = EDRCmdrsDex.__tagify(tag)

        if tag == u"friend" and self.cmdrs[cname]["friend"]:
            self.cmdrs[cname]["friend"] = False
            updated = True
        elif tag == self.cmdrs[cname]["alignment"]:
            self.cmdrs[cname]["alignment"] = None
            updated = True
        elif tag in self.cmdrs[cname]["tags"]:
            self.cmdrs[cname]["tags"].remove(tag)
            updated = True

        if updated:
            self.cmdrs[cname]["updated"] = EDRCmdrsDex.__js_epoch_now()

        return updated
    
    def remove(self, name):
        try:
            del self.cmdrs[name.lower()]
            return True
        except KeyError:
            return False

    def persist(self):
        with open(self.EDR_CMDRS_DEX_PATH, 'w') as json_file:
            json.dump(self.cmdrs, json_file, sort_keys=True, indent=4)