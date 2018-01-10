import datetime
import json
import os
import io

class EDRCmdrsDex(object):
    EDR_CMDRS_DEX_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'data/cmdrsdex.json')

    def __init__(self):
        try:
            with open(self.EDR_CMDRS_DEX_PATH, 'r') as fp:
                self.cmdrs = json.load(fp)
        except:
            self.cmdrs = {}
    
    def is_outlaw(self, name):
        if not name.lower() in self.cmdrs:
            return False
        return self.cmdrs[name.lower()]["tag"] == "outlaw"

    def cmdr_profile(self, name):
        if not name.lower() in self.cmdrs:
            return None
        cmdr_entry = self.cmdrs[name.lower()]
        return u"{}: {} #{} ({:%Y-%m-%d})".format(cmdr_entry["name"], cmdr_entry["memo"], cmdr_entry["tag"], cmdr_entry["date"])

    def add_outlaw(self, name, memo=""):
        self.add(name, memo, "outlaw")

    def add_neutral(self, name, memo=""):
        self.add(name, memo, "neutral")

    def add_friend(self, name, memo=""):
        self.add(name, memo, "friend")

    def add(self, name, memo, tag):
        self.remove(name)
        cmdr_entry = {
            "name": name,
            "memo": memo,
            "tag": tag,
            "date": datetime.datetime.today().strftime('%Y-%m-%d')
        }
        self.cmdrs[name.lower()] = cmdr_entry
    
    def remove(self, name):
        try:
            del self.cmdrs[name.lower()]
        except KeyError:
            pass

    def persist(self):
        with open(self.EDR_CMDRS_DEX_PATH, 'w') as fp:
            json.dump(self.cmdrs, fp, sort_keys=True, indent=4)


