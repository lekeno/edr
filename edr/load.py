"""
ED Recon Plugin for EDMC
"""

import os
import sys

# Ensure the src directory is in the path
try:
    from edr.utils.edrpath import plugin_root
    sys.path.insert(0, os.path.join(plugin_root(), 'src'))
except ImportError:
    pass

from edr.controllers.edrclient import EDRClient
from edr.controllers.edreventhandler import EDREventHandler
from edr.core.edrlog import EDR_LOG

try:
    import edmc_data
except ImportError:
    from edr.fakeenv import edmc_data

EDR_CLIENT = None
EVENT_HANDLER = None

def plugin_start3(plugin_dir):
    """
    Called by EDMC when the plugin is started (Python 3).
    """
    global EDR_CLIENT, EVENT_HANDLER
    EDR_LOG.info("Starting ED Recon.")
    EDR_CLIENT = EDRClient()
    EDR_CLIENT.apply_config()
    EDR_CLIENT.login()
    EVENT_HANDLER = EDREventHandler(EDR_CLIENT, edmc_data)
    return "ED Recon"

def plugin_stop():
    """
    Called by EDMC when the plugin is stopped.
    """
    EDR_LOG.info("Stopping ED Recon.")
    if EDR_CLIENT:
        EDR_CLIENT.shutdown(everything=True)

def prerequisites(edr_client, is_beta, from_genesis=False):
    """
    Check if EDR is ready to process events.
    """
    if edr_client is None:
        return False
    if edr_client.mandatory_update:
        return False
    if not edr_client.is_logged_in():
        return False
    return True

def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    Called by EDMC for every journal entry.
    """
    if prerequisites(EDR_CLIENT, is_beta):
        if EVENT_HANDLER:
            EVENT_HANDLER.process_journal_entry(entry, state)

def dashboard_entry(cmdr, is_beta, entry):
    """
    Called by EDMC for every dashboard entry (status.json).
    """
    if prerequisites(EDR_CLIENT, is_beta):
        if EVENT_HANDLER:
            EVENT_HANDLER.process_dashboard_entry(cmdr, entry)

def plugin_app(parent):
    """
    Called by EDMC to build the plugin UI.
    """
    if EDR_CLIENT:
        return EDR_CLIENT.app_ui(parent)
    return None

def plugin_prefs(parent, cmdr, is_beta):
    """
    Called by EDMC to build the preferences UI.
    """
    if EDR_CLIENT:
        return EDR_CLIENT.prefs_ui(parent)
    return None

def prefs_changed(cmdr, is_beta):
    """
    Called by EDMC when preferences are saved.
    """
    if EDR_CLIENT:
        EDR_CLIENT.prefs_changed()

# Backward compatibility for old EDMC versions
def plugin_start(plugin_dir):
    return plugin_start3(plugin_dir)