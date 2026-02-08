
import unittest
from unittest.mock import patch, MagicMock
import edri18n

class TestEDRI18n(unittest.TestCase):
    def setUp(self):
        self.translate_patcher = patch.object(edri18n, 'TRANSLATE', MagicMock())
        self.mock_translate = self.translate_patcher.start()
        self.mock_translate.gettext.side_effect = lambda x: x 

        self.language_patcher = patch.object(edri18n, 'LANGUAGE', None)
        self.language_patcher.start()

    def tearDown(self):
        self.translate_patcher.stop()
        self.language_patcher.stop()

    @patch('edri18n.l10n')
    def test_get_sys_lang_supported(self, mock_l10n):
        mock_l10n.Locale.preferred_languages.return_value = ["fr-CA", "en-US"]
        lang = edri18n._get_sys_lang()
        self.assertEqual(lang, "fr")

    @patch('edri18n.l10n')
    def test_get_sys_lang_unsupported(self, mock_l10n):
        mock_l10n.Locale.preferred_languages.return_value = ["es-ES"] # Spanish not in LANG_LIST
        lang = edri18n._get_sys_lang()
        self.assertIsNone(lang)

    @patch('edri18n.gettext.translation')
    def test_set_language_custom(self, mock_gh):
        edri18n.set_language("de")
        self.assertEqual(edri18n.LANGUAGE, "de")
        mock_gh.assert_called()

    def test_edrgettext_dict(self):
        edri18n.LANGUAGE = "fr"
        msgs = {
            "en": "Hello",
            "fr": "Bonjour",
            "de": "Hallo"
        }
        self.assertEqual(edri18n.edrgettext(msgs), "Bonjour")

    def test_edrgettext_fallback(self):
        edri18n.LANGUAGE = "it"
        msgs = {
            "en": "Hello",
            "fr": "Bonjour"
        }
        self.assertEqual(edri18n.edrgettext(msgs), "Hello") # Fallback to en

    def test_pgettext_context(self):
        # Setup mock behavior simulating translation missing
        edri18n.TRANSLATE.gettext.return_value = "Context|Message" 
        result = edri18n.pgettext("Context|Message")
        self.assertEqual(result, "Message")


if __name__ == '__main__':
    unittest.main()
