
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

from audiofeedback import EDRSoundEffects, SFXConfig, AudioFeedback

class TestAudioFeedback(unittest.TestCase):
    @patch('audiofeedback.os.path.exists')
    @patch('audiofeedback.cp.ConfigParser')
    def test_sfx_config_defaults(self, mock_cp, mock_exists):
        mock_exists.return_value = False # No user config
        sfx = SFXConfig("default.ini", "user.ini")
        # Should fallback
        self.assertEqual(sfx.config, sfx.fallback_config)

    @patch('audiofeedback.os.path.exists')
    @patch('audiofeedback.cp.ConfigParser')
    def test_sfx_config_user(self, mock_cp, mock_exists):
        mock_exists.return_value = True # Has user config
        sfx = SFXConfig("default.ini", "user.ini")
        sfx.config.read.assert_called()

    @patch('audiofeedback.SFXConfig')
    @patch('audiofeedback.AudioFeedback')
    def test_edr_sound_effects_init(self, MockAudio, MockConfig):
        MockConfig.return_value.snd.return_value = "sound.wav"
        
        effects = EDRSoundEffects()
        self.assertIn("startup", effects.sounds)
        MockAudio.assert_called_with("sound.wav")

    def test_play_wrapper(self):
        # Test the platform-specific AudioFeedback wrapper logic
        # We can't easily switch platforms at runtime, but we can verify the class structure
        
        # If on windows (test env)
        if sys.platform == 'win32':
            with patch('winsound.PlaySound') as mock_play:
                with patch('os.path.exists', return_value=True):
                    af = AudioFeedback("test.wav")
                    af.play()
                    mock_play.assert_called()

if __name__ == '__main__':
    unittest.main()
