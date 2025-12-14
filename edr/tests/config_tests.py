import sys
import os

# 1. Get the directory of the current file (edr/tests/)
current_dir = os.path.dirname(__file__)

# 2. Get the parent directory (edr/)
edr_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# 3. Get the grandparent directory (EDRecon/ - project root)
root_dir = os.path.abspath(os.path.join(edr_dir, os.pardir))

# 4. Add both to sys.path
# Add edr_dir so we can import modules like 'lrucache' directly if needed (though usually best to use package imports)
# Add root_dir so we can import 'config' and other top-level modules
sys.path.insert(0, root_dir)
sys.path.insert(0, edr_dir)
