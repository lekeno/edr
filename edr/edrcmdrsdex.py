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
        return self.cmdrs.get(cmdr_name.lower, None)
    
    def short_profile(self, cmdr_name):
        cmdr_entry = self.get(cmdr_name)
        if cmdr_entry:
            return u"{}: {} #{} ({})".format(cmdr_entry["name"], cmdr_entry["memo"], cmdr_entry["tag"], cmdr_entry["date"])
        return None

    def add(self, name, memo, tag):
        #TODO tag array
        self.remove(name)
        cmdr_entry = {
            "name": name,
            "memo": memo,
            "tag": tag,
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

    #TODO add tag method

    def untag_cmdr(self, name, tag):
        if tag is None:
            return self.remove(name)
        #TODO remove tag if present, return result

    
    def remove(self, name):
        try:
            del self.cmdrs[name.lower()]
        except KeyError:
            pass

    def persist(self):
        with open(self.EDR_CMDRS_DEX_PATH, 'w') as json_file:
            json.dump(self.cmdrs, json_file, sort_keys=True, indent=4)