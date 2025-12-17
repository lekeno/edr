
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
        self.logger.debug(msg, *args, stacklevel=2, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, stacklevel=2, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, stacklevel=2, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, stacklevel=2, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, stacklevel=2, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, stacklevel=2, **kwargs)

_edr_logger_instance = None

def get_edr_log():
    global _edr_logger_instance
    if _edr_logger_instance is None:
        _edr_logger_instance = EDRLog()
    return _edr_logger_instance

EDR_LOG = get_edr_log()