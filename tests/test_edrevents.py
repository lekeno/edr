import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mocking EDR modules
sys.modules['edr.core.edri18n'] = MagicMock()
sys.modules['edr.core.edrlog'] = MagicMock()
sys.modules['edr.utils.edtime'] = MagicMock()
sys.modules['edr.models.edentities'] = MagicMock()
sys.modules['edr.models.edsitu'] = MagicMock()
sys.modules['edr.models.edvehicles'] = MagicMock()
sys.modules['edr.models.edrrawdepletables'] = MagicMock()
sys.modules['edmc_data'] = MagicMock()

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edr', 'src')))

from edr.controllers.edrevents import EDREventHandler

class TestEDREventHandler(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.handler = EDREventHandler(self.mock_client)

    def test_prerequisites_success(self):
        self.mock_client.mandatory_update = False
        self.mock_client.is_logged_in.return_value = True
        self.assertTrue(self.handler.prerequisites(self.mock_client, False, False))

    def test_prerequisites_fail_mandatory_update(self):
        self.mock_client.mandatory_update = True
        self.assertFalse(self.handler.prerequisites(self.mock_client, False, False))

    def test_prerequisites_fail_not_logged_in(self):
        self.mock_client.mandatory_update = False
        self.mock_client.is_logged_in.return_value = False
        self.assertFalse(self.handler.prerequisites(self.mock_client, False, False))

    def test_plain_cmdr_name(self):
        self.assertEqual(self.handler.plain_cmdr_name("Joe"), "Joe")
        self.assertEqual(self.handler.plain_cmdr_name("$cmdr_decorate:#name=Joe;"), "Joe")

if __name__ == '__main__':
    unittest.main()
