
import logging
import sys
import os
from config import appname
from edrconfig import EDRConfig

if sys.version_info.major == 3:
    sys.stdout.reconfigure(encoding="utf-8")

class EDRLog(object):

    LEVEL_MAPPING = {"DEBUG": logging.DEBUG,  "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
    PLUGIN_NAME = os.path.basename(os.path.dirname(__file__))

    def __init__(self):
        config = EDRConfig()
        self.logger = logging.getLogger(f'{appname}.{self.PLUGIN_NAME}')
        level = self.LEVEL_MAPPING.get(config.logging_level(), logging.NOTSET)
        self.logger.setLevel(level)
        if not self.logger.hasHandlers():
            logger_channel = logging.StreamHandler()
            logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
            logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
            logger_formatter.default_msec_format = '%s.%03d'
            logger_channel.setFormatter(logger_formatter)
            self.logger.addHandler(logger_channel)

    def log(self, msg, level):
        level = self.LEVEL_MAPPING.get(level, logging.NOTSET)
        self.logger.log(level, msg)


EDR_LOG = EDRLog()