import sys
import os

# Get the directory where your .py files are
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the root_dir to the path so 'import edrlog' works
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# THE TRICK: Map the current directory to the 'edr' module name
# This allows 'from edr.clippy' to work even if there is no edr/ folder
try:
    import edr
except ImportError:
    import types
    # Create a fake module named 'edr'
    edr_module = types.ModuleType('edr')
    # Point that module's path to your root directory
    edr_module.__path__ = [root_dir]
    sys.modules['edr'] = edr_module