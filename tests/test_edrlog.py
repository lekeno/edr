
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

    @patch('edr.core.edrconfig.EDR_CONFIG')
    def test_init_level(self, mock_config):
        mock_config.logging_level.return_value = "DEBUG"
        
        # We need to force re-instantiation or handle the fact that logging.getLogger returns the same logger
        # For testing __init__ logic, we can construct EDRLog again.
        log = EDRLog()
        self.assertEqual(log.logger.level, logging.DEBUG)
        
        mock_config.logging_level.return_value = "INFO"
        log = EDRLog()
        self.assertEqual(log.logger.level, logging.INFO)

    def test_singleton_accessor(self):
        from edr.core.edrlog import get_edr_log
        log1 = get_edr_log()
        log2 = get_edr_log()
        self.assertIs(log1, log2)

    def test_logging_methods(self):
        # We can't easily mock the internal logger creation without patching __init__, 
        # but we can patch the logger attribute after creation.
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

if __name__ == '__main__':
    unittest.main()
