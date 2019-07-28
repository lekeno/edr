import json
from os.path import join
from config import config
import edrlog
EDRLOG = edrlog.EDRLog()

class EDModulesInfoReader(object):
    def __init__(self):
        self.journal_location = config.get('journaldir') or config.default_journal_dir

    def process(self):
        # From EDMarketConnector while waiting for first party support
        try:
            with open(join(self.journal_location, 'ModulesInfo.json'), 'rb') as h:
                data = h.read().strip()
                if data:	# Can be empty if polling while the file is being re-written
                    entry = json.loads(data)
                    return entry.get("Modules", None)
        except:
            EDRLOG.log(u"Couldn't process modulesinfo", "WARNING")
