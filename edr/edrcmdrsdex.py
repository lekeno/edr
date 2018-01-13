import datetime
import json
import os

class EDRCmdrsDex(object):
    EDR_CMDRS_DEX_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'data/cmdrsdex.json')

    def __init__(self):
        try:
            with open(self.EDR_CMDRS_DEX_PATH, 'r') as json_file:
                self.cmdrs = json.load(json_file)
        except:
            self.cmdrs = {}
    
    def get(self, cmdr_name):
        return self.cmdrs.get(cmdr_name.lower(), None)
    
    def short_profile(self, cmdr_name):
        cmdr_entry = self.get(cmdr_name)
        if cmdr_entry:
            return u"{}: {} #{} ({})".format(cmdr_entry["name"], cmdr_entry["memo"], " ".join(cmdr_entry["tags"]), cmdr_entry["date"])
        return None

    def add(self, name, memo, tag):
        tag = tag.lower()
        self.remove(name)
        cmdr_entry = {
            "name": name,
            "memo": memo,
            "tags": [tag],
            "date": datetime.datetime.today().strftime('%Y-%m-%d')
        }
        self.cmdrs[name.lower()] = cmdr_entry
    
    def set_memo(self, name, memo):
        cmdr_entry = self.get(name)
        if cmdr_entry:
            cmdr_entry["memo"] = memo
            self.cmdrs[name.lower()] = cmdr_entry
            #TODO EDRServer update
            return True
        return False

    def tag(self, name, tag):
        tag = tag.lower()
        cmdr_entry = self.get(name)
        if cmdr_entry is None:
            self.add(name, None, tag)
            return True

        if tag not in ["outlaw", "neutral", "enforcer"]:
            cmdr_entry["tags"].append(tag)
            self.cmdrs[name.lower()] = cmdr_entry
            return True

        if tag in cmdr_entry["tags"]:
            return True

        for karma_tag in ["outlaw", "neutral", "enforcer"]:
            try:
                cmdr_entry["tags"].remove(karma_tag)
            except:
                pass

        cmdr_entry["tags"].append(tag)
        self.cmdrs[name.lower()] = cmdr_entry
        return True

    def untag(self, name, tag):
        tag = tag.lower()
        cmdr_entry = self.get(name)
        if cmdr_entry is None:
            return False

        if tag not in cmdr_entry["tags"]:
            return True

        cmdr_entry["tags"].remove(tag)
        if cmdr_entry["tags"]:
            self.cmdrs[name.lower()] = cmdr_entry
        else:
            self.remove(name)
        return True

    
    def remove(self, name):
        try:
            del self.cmdrs[name.lower()]
        except KeyError:
            pass

    def persist(self):
        with open(self.EDR_CMDRS_DEX_PATH, 'w') as json_file:
            json.dump(self.cmdrs, json_file, sort_keys=True, indent=4)