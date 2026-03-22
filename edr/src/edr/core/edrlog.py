
import logging
import sys
import os
import threading
from config import appname  # EDR_INTERNAL

if sys.version_info.major == 3:
    sys.stdout.reconfigure(encoding="utf-8")


class EDRLogFilter(logging.Filter):
    """
    Filter to ensure 'osthreadid' is present in LogRecords.
    EDMC's logging formatter expects this field.
    """
    def filter(self, record):
        if not hasattr(record, 'osthreadid'):
            if hasattr(threading, 'get_native_id'):
                record.osthreadid = threading.get_native_id()
            else:
                record.osthreadid = threading.current_thread().ident
        return True


class EDRLog:
    """
    Singleton-ish logger wrapper for EDR.
    """
    PLUGIN_NAME = "edr"

    def __init__(self):
        """
        Initialize the EDR Logger.

        Sets up logging level and stream handler if not present.
        """
        from .edrconfig import EDR_CONFIG
        config = EDR_CONFIG
        self.logger = logging.getLogger(f'{appname}.{self.PLUGIN_NAME}')
        level_name = config.logging_level()
        level = logging.getLevelName(level_name.upper())
        self.logger.setLevel(level)

        self.logger.addFilter(EDRLogFilter())

        if not self.logger.hasHandlers():
            logger_channel = logging.StreamHandler()
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s'
            logger_formatter = logging.Formatter(log_format)

            logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
            logger_formatter.default_msec_format = '%s.%03d'

            logger_channel.setFormatter(logger_formatter)
            self.logger.addHandler(logger_channel)

    def debug(self, msg, *args, **kwargs):
        """
        Logs a debug message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the message format string.
            **kwargs: Keyword arguments for the logger.
        """
        if sys.version_info >= (3, 8):
            kwargs.setdefault('stacklevel', 2)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Logs an info message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the message format string.
            **kwargs: Keyword arguments for the logger.
        """
        if sys.version_info >= (3, 8):
            kwargs.setdefault('stacklevel', 2)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Logs a warning message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the message format string.
            **kwargs: Keyword arguments for the logger.
        """
        if sys.version_info >= (3, 8):
            kwargs.setdefault('stacklevel', 2)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Logs an error message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the message format string.
            **kwargs: Keyword arguments for the logger.
        """
        if sys.version_info >= (3, 8):
            kwargs.setdefault('stacklevel', 2)
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """
        Logs an exception message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the message format string.
            **kwargs: Keyword arguments for the logger.
        """
        if sys.version_info >= (3, 8):
            kwargs.setdefault('stacklevel', 2)
        self.logger.exception(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Logs a critical message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the message format string.
            **kwargs: Keyword arguments for the logger.
        """
        if sys.version_info >= (3, 8):
            kwargs.setdefault('stacklevel', 2)
        self.logger.critical(msg, *args, **kwargs)


_edr_logger_instance = None


def get_edr_log():
    """
    Get the global EDRLog instance.

    Returns:
        EDRLog: The logger instance.
    """
    global _edr_logger_instance
    if _edr_logger_instance is None:
        _edr_logger_instance = EDRLog()
    return _edr_logger_instance


EDR_LOG = get_edr_log()
