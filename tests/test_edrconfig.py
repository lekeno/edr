

from unittest import TestCase, main
from unittest.mock import MagicMock, patch
from edr.edrconfig import EDR_CONFIG, EDRUserConfig

class TestEDRConfig(TestCase):
    def test_defaults_and_accessors(self):
        # Mock ConfigParser to control values
        with patch('configparser.ConfigParser') as mock_cp:
            mock_parser = MagicMock()
            mock_cp.return_value = mock_parser
            
            # Setup default return values for string gets
            mock_parser.get.side_effect = lambda section, key: f"{section}_{key}_value"
            
            # Setup return values for int gets
            mock_parser.getint.return_value = 100
            
            # Setup return values for boolean gets
            mock_parser.getboolean.return_value = True

            config = EDR_CONFIG
            
            self.assertEqual(config.edr_version(), "general_version_value")
            self.assertEqual(config.edr_api_key(), "edr_edr_api_key_value")
            self.assertEqual(config.edr_server(), "edr_edr_server_value")
            
            # Test int conversion wrappers
            # Since we mocked get(), we need to ensure the methods that cast to int() handle the mocked string return?
            # actually EDRConfig calls int(self.config.get(...))
            # so if get() returns a string "edr_edr_heartbeat_value", int() will fail.
            # I need to be more specific with side_effect or specific mocks.
            pass

    def test_mocked_values(self):
        with patch('configparser.ConfigParser') as mock_cp:
            mock_parser = MagicMock()
            mock_cp.return_value = mock_parser
            
            def get_side_effect(section, key):
                if key == 'edr_heartbeat': return '60'
                if key == 'legal_records_recent_threshold': return '72'
                return 'dummy'

            mock_parser.get.side_effect = get_side_effect
            
            config = EDR_CONFIG
            self.assertEqual(config.edr_heartbeat(), 60)
            self.assertEqual(config.legal_records_recent_threshold(), 72)

class TestEDRUserConfig(TestCase):
    def test_missing_config(self):
        # Test generic missing file behavior (should result in config being None)
        # However, EDRUserConfig catches exception on read.
        with patch('configparser.ConfigParser') as mock_cp:
            mock_parser = MagicMock()
            mock_cp.return_value = mock_parser
            mock_parser.read.side_effect = Exception("File not found")
            
            user_config = EDRUserConfig()
            self.assertIsNone(user_config.discord_webhook_for_comms("general"))
            self.assertIsNotNone(user_config.opsec_config())

if __name__ == '__main__':
    main()
