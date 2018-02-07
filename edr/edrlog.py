import sys
import edrconfig

class EDRLog(object):

    LEVEL_MAPPING = {"DEBUG": 10,  "INFO": 20, "WARNING": 30, "ERROR": 40}

    def __init__(self):
        config = edrconfig.EDRConfig()
        self.importance_threshold = self.LEVEL_MAPPING.get(config.logging_level(), 0)

    def log(self, msg, level):
        if not self.is_important_enough(level):
            return

        print "[EDR]" + msg.encode(sys.getdefaultencoding(), 'replace')


    def is_important_enough(self, level):
        importance = self.LEVEL_MAPPING.get(level, None)
        if importance is None:
            return self.importance_threshold == 0

        return importance >= self.importance_threshold