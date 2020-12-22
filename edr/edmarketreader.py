from __future__ import absolute_import

import json
from os.path import join
from config import config
from edrlog import EDRLog

EDRLOG = EDRLog()

class EDMarketReader(object):
    def __init__(self):
        self.journal_location = config.get('journaldir') or config.default_journal_dir

    def process(self):
        try:
            with open(join(self.journal_location, 'Market.json'), 'rb') as h:
                data = h.read().strip()
                if data:	# Can be empty if polling while the file is being re-written
                    entry = json.loads(data)
                    return entry
        except:
            EDRLOG.log(u"Couldn't process market", u"WARNING")
