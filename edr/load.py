"""
Plugin for "EDR"
"""
import sys
import os

# Ensure the src directory is in the path
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(PLUGIN_DIR, 'src'))

try:
    import edmc_data
except ImportError:
    from edr.fakeenv import plug as edmc_data

from edr.controllers.edrclient import EDRClient
from edr.controllers.edreventdispatcher import EDREventDispatcher

from edr.core.edrlog import EDR_LOG
from edr.core.edrconfig import EDR_CONFIG
from edr.core import edrautoupdater

VERSION = EDR_CONFIG.edr_version()

EDR_CLIENT = EDRClient()
EDR_EVENT_DISPATCHER = EDREventDispatcher(EDR_CLIENT)

def plugin_start3(plugin_dir):
    return plugin_start()


def plugin_start():
    """
    Start up EDR, try to login.
    """
    edrautoupdater.EDRAutoUpdater.clean_up_obsolete_files()
    EDR_CLIENT.apply_config()

    if not EDR_CLIENT.email:
        EDR_CLIENT.email = ""

    if not EDR_CLIENT.password:
        EDR_CLIENT.password = ""

    EDR_CLIENT.login()


def plugin_stop():
    """
    Stop the EDR plugin and perform cleanup.
    """
    EDR_LOG.info("Stopping the plugin...")
    EDR_CLIENT.shutdown(everything=True)
    if EDR_CLIENT.autoupdate_pending:
        plugin_update()
    EDR_LOG.info("Plugin stopped")


def plugin_update():
    """
    Perform automatic update of the plugin.
    """
    EDR_LOG.info("Please wait: auto updating EDR")
    auto_updater = edrautoupdater.EDRAutoUpdater()
    downloaded = auto_updater.download_latest()
    if downloaded:
        EDR_LOG.info("Download successful, creating a backup.")
        auto_updater.make_backup()
        EDR_LOG.info("Cleaning old backups.")
        auto_updater.clean_old_backups()
        EDR_LOG.info("Extracting latest version.")
        auto_updater.extract_latest()


def plugin_app(parent):
    return EDR_CLIENT.app_ui(parent)


def plugin_prefs(parent, cmdr, is_beta):
    return EDR_CLIENT.prefs_ui(parent)


def prefs_changed(cmdr, is_beta):
    EDR_CLIENT.prefs_changed()
            
def journal_entry(cmdr, is_beta, system, station, entry, state):
    EDR_EVENT_DISPATCHER.journal_entry(cmdr, is_beta, system, station, entry, state)

def dashboard_entry(cmdr, is_beta, entry):
    EDR_EVENT_DISPATCHER.dashboard_entry(cmdr, is_beta, entry)