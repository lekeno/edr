import os
import sys
import os

def abspathmaker(currentfile, *paths):
    base = os.path.abspath(os.path.dirname(currentfile))
    if sys.version_info.major == 2:
        return os.path.join(base.decode(sys.getfilesystemencoding()), *paths)
    else:
        return os.path.join(base, *paths)

def pathmaker(currentfile, *paths):
    base = os.path.dirname(currentfile)
    if sys.version_info.major == 2:
        return os.path.join(base.decode(sys.getfilesystemencoding()), *paths)
    else:
        return os.path.join(base, *paths)