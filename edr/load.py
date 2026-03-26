"""
Plugin for "EDR"
"""
import sys
import os

# Ensure the src directory is in the path
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(PLUGIN_DIR, 'src'))

import re
import random
import codecs
from datetime import datetime, timedelta, timezone

try:
    import edmc_data
except ImportError:
    from edr.fakeenv import plug as edmc_data

from edr.models.edspacesuits import EDSpaceSuit  # EDR_INTERNAL
from edr.controllers.edrclient import EDRClient
from edr.models.edentities import EDPlayer  # EDR_INTERNAL
from edr.models.edsitu import EDPlanetaryLocation  # EDR_INTERNAL
from edr.models.edvehicles import EDVehicleFactory  # EDR_INTERNAL
from edr.models.edrrawdepletables import EDRRawDepletables
from edr.utils.edtime import EDTime  # EDR_INTERNAL
from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL
from edr.core import edrautoupdater  # EDR_INTERNAL
from edr.core.edri18n import _, _c  # EDR_INTERNAL
from edr.core.edrconfig import EDR_CONFIG # EDR_INTERNAL

VERSION = EDR_CONFIG.edr_version()

EDR_CLIENT = EDRClient()

LAST_KNOWN_SHIP_NAME = ""
OVERLAY_DUMMY_COUNTER = 0
IN_LEGACY_MODE = False


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



from edr.controllers.edrevents import EDREventHandler
EDR_EVENTS = EDREventHandler(EDR_CLIENT)

def dashboard_entry(cmdr, is_beta, entry):
    return EDR_EVENTS.dashboard_entry(cmdr, is_beta, entry)

def journal_entry(cmdr, is_beta, system, station, entry, state):
    return EDR_EVENTS.journal_entry(cmdr, is_beta, system, station, entry, state)
