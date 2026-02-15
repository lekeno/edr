import sys
import pytest
from unittest.mock import MagicMock

# Mock external dependencies globally for the test session
# This must be done at module level because some tests import modules that import these dependencies
if 'config' not in sys.modules:
    m = MagicMock()
    m.config = MagicMock()
    m.config.get_str.return_value = "en"
    m.config.get_int.return_value = 0
    sys.modules['config'] = m

if 'l10n' not in sys.modules:
    mock_l10n = MagicMock()
    # Mock Locale.preferred_languages() which returns an iterable
    mock_l10n.Locale.preferred_languages.return_value = ["en"]
    sys.modules['l10n'] = mock_l10n

@pytest.fixture
def mock_dependencies():
    # Kept for compatibility if needed, but the work is done above
    pass
