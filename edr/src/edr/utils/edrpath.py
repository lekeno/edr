import os

def plugin_root():
    """
    Returns the root directory of the EDR plugin.
    This is determined relative to this file's location.
    """
    # This file is located at <plugin_root>/src/edr/utils/edrpath.py
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def edr_resource_path(rel_path):
    """
    Returns the absolute path to a resource relative to the plugin root.
    """
    return os.path.join(plugin_root(), rel_path)

def edr_data_path(filename):
    """
    Returns the absolute path to a file in the data directory.
    """
    return edr_resource_path(os.path.join('data', filename))

def edr_cache_path(filename):
    """
    Returns the absolute path to a file in the cache directory.
    """
    return edr_resource_path(os.path.join('cache', filename))

def edr_config_path(filename):
    """
    Returns the absolute path to a file in the config directory.
    """
    return edr_resource_path(os.path.join('config', filename))

def edr_sound_path(filename):
    """
    Returns the absolute path to a file in the sounds directory.
    """
    return edr_resource_path(os.path.join('sounds', filename))
