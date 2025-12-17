import sys
import os

# 1. Directory of this file: .../ProjectRoot/tests/
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Project Root (one level up): .../ProjectRoot/
# This allows 'from edr.edrlog import EDR_LOG' to work
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# 3. EDR Module Directory: .../ProjectRoot/edr/
# This allows internal flat imports like 'import edri18n' to work
edr_dir = os.path.join(root_dir, 'edr')

# 4. Inject into sys.path
# We use insert(0, ...) to ensure these versions are used even if 
# another version of EDR is installed in the Python environment.
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if edr_dir not in sys.path:
    sys.path.insert(0, edr_dir)