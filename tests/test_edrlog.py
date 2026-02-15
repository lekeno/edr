
import unittest
from unittest.mock import MagicMock, patch
import logging
from edr.core.edrlog import EDRLog

class TestEDRLog(unittest.TestCase):
    def test_singleton(self):
        log1 = EDRLog()
        log2 = EDRLog()
        # EDRLog isn't a strict singleton class, but the module level get_edr_log ensures one instance.
        # Here we just verify the class can be instantiated and has a logger.
        self.assertIsInstance(log1.logger, logging.Logger)
        self.assertIsInstance(log2.logger, logging.Logger)

    def test_logging_methods(self):
        log = EDRLog()
        log.logger = MagicMock()
        
        log.debug("test")
        log.logger.debug.assert_called_with("test", stacklevel=2)
        
        log.info("test")
        log.logger.info.assert_called_with("test", stacklevel=2)
        
        log.warning("test")
        log.logger.warning.assert_called_with("test", stacklevel=2)

        log.error("test")
        log.logger.error.assert_called_with("test", stacklevel=2)

        log.critical("test")
        log.logger.critical.assert_called_with("test", stacklevel=2)

        log.exception("test")
        log.logger.exception.assert_called_with("test", stacklevel=2)
