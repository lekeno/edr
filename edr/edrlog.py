
import logging
import sys
import os
from config import appname
from edrconfig import EDRConfig

if sys.version_info.major == 3:
    sys.stdout.reconfigure(encoding="utf-8")

class EDRLog(object):

    PLUGIN_NAME = os.path.basename(os.path.dirname(__file__))

    def __init__(self):
        config = EDRConfig()
        self.logger = logging.getLogger(f'{appname}.{self.PLUGIN_NAME}')
        level_name = config.logging_level()
        level = logging.getLevelName(level_name.upper())
        self.logger.setLevel(level)
        
        if not self.logger.hasHandlers():
            logger_channel = logging.StreamHandler()
            log_format = f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s'
            logger_formatter = logging.Formatter(log_format)

            logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
            logger_formatter.default_msec_format = '%s.%03d'
            
            logger_channel.setFormatter(logger_formatter)
            self.logger.addHandler(logger_channel)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)


EDR_LOG = EDRLog()