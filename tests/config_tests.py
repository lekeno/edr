import sys
import os

# 1. Get the path to the 'edr' subfolder
current_dir = os.path.dirname(os.path.abspath(__file__))
edr_dir = os.path.abspath(os.path.join(current_dir, '..', 'edr'))

# 2. Add the 'edr' folder itself to sys.path
# This makes 'from lrucache import ...' work because Python now looks INSIDE /edr/
if edr_dir not in sys.path:
    sys.path.insert(0, edr_dir)