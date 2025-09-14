import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.modules['myNotebook'] = MagicMock()
sys.modules['ttkHyperlinkLabel'] = MagicMock()

sys.modules['edr.edrclientui'] = MagicMock()
sys.modules['edr.ingamemsg'] = MagicMock()


with patch('tkinter.StringVar', MagicMock()), \
     patch('tkinter.IntVar', MagicMock()):
    from edr.edrclient import EDRClient
    client = EDRClient()
    print(f"Blips max age from config: {client.blips_cache.max_age}")
    print(f"Scans max age from config: {client.scans_cache.max_age}")
    print(f"Cognitive scans cache max age: {client.cognitive_scans_cache.max_age}")

    assert client.cognitive_scans_cache.max_age == 200
    print("Assertion passed! The fix is working correctly.")
