from datetime import datetime, timezone
import re

from edr.controllers.edrjournalhandler import EDRJournalHandler
from edr.controllers.edrdashboardhandler import EDRDashboardHandler
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _

class EDREventDispatcher:
    def __init__(self, edr_client):
        self.edr_client = edr_client
        self.in_legacy_mode = None
        self.journal_handler = EDRJournalHandler(edr_client)
        self.dashboard_handler = EDRDashboardHandler(edr_client)

    def is_legacy(self, gameVersionRawString):
        # The Legacy / Live split only happens after Update 14 which is scheduled to go live by November 29th 15:00 UTC
        # Servers go down by 7:00
        if datetime.now(timezone.utc) <= datetime.fromisoformat("2022-11-29T07:00:00+00:00"):
            return False
        gameversion = "0.0.0.0"
        m = re.match(r"^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*$", gameVersionRawString)
        if m:
            gameversion = m.group(1)
        client_parts = list(map(int, gameversion.split('.')))
        live_baseline_parts = list(map(int, "4.0.0.0".split('.')))
        return client_parts < live_baseline_parts

    def prerequisites(self, is_beta):
        if self.edr_client.mandatory_update:
            EDR_LOG.error("Out-of-date client, aborting.")
            return False

        if not self.edr_client.is_logged_in():
            EDR_LOG.error("Not logged in, aborting.")
            return False

        if is_beta:
            EDR_LOG.info("Player is in beta: skip!")
            return False

        if self.in_legacy_mode is None:
            EDR_LOG.error("Legacy mode not set, aborting.")
            return False

        if self.in_legacy_mode:
            self.edr_client.status = _("Legacy mode is not supported.")
            EDR_LOG.info("Player is in Legacy mode: skip!")
            return False
        return True

    def dashboard_entry(self, cmdr, is_beta, entry):
        if not self.prerequisites(is_beta):
            return
            
        self.dashboard_handler.dashboard_entry(cmdr, is_beta, entry)    

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        self.edr_client.player_name(cmdr)
        ed_player = self.edr_client.player
        ed_player.friends = state["Friends"]

        if self.in_legacy_mode is None:
            self.in_legacy_mode = self.is_legacy(state["GameVersion"])

        if not self.prerequisites(is_beta):
            return
        
        self.journal_handler.journal_entry(entry, state)
