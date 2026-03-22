import random
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.utils.edtime import EDTime
from edr.controllers.edrserver import CommsJammedError

class EDRIntelManager:
    """
    Manages Commander and System Intelligence gathering capabilities,
    extracting logic like !who, !where, sitreps, and NOTAMs.
    """
    def __init__(self, edr_client):
        self.client = edr_client

    def who(self, cmdr_name, autocreate=False):
        """
        Display intel about a commander.
        """
        try:
            profile = self.client.cmdr(cmdr_name, autocreate, check_inara_server=True)
            if profile:
                self.client.status = _("got info about {}").format(cmdr_name)
                EDR_LOG.info("Who {} : {}".format(cmdr_name, profile.short_profile(self.client.player.powerplay)))
                legal = self.client.edrlegal.summarize(profile.cid)
                details = [profile.short_profile(self.client.player.powerplay)]
                if legal:
                    details.append(legal["overview"])
                self.client._EDRClient__intel(_("Intel about {}").format(cmdr_name), details, clear_before=True, legal=legal)
            else:
                EDR_LOG.info("Who {} : no info".format(cmdr_name))
                self.client._EDRClient__intel(_("Intel about {}").format(cmdr_name), [_("No info").format(cmdr=cmdr_name)], clear_before=True)
        except CommsJammedError:
            self.client._EDRClient__commsjammed()

    def where(self, cmdr_name):
        """
        Locate a commander (last sighting).
        """
        report = {}
        try:
            for kind in self.client.edropponents:
                candidate_report = self.client.edropponents[kind].where(cmdr_name)
                if candidate_report and (not report or report["timestamp"] < candidate_report["timestamp"]):
                    report = candidate_report
            
            if report:
                self.client.status = _("got info about {}").format(cmdr_name)
                header = _("Intel about {}") if self.client.player.in_open() else _("Intel about {} (Open)")
                self.client._EDRClient__intel(header.format(cmdr_name), report["readable"], clear_before=True)
            else:
                EDR_LOG.info("Where {} : no info".format(cmdr_name))
                self.client.status = _("no info about {}").format(cmdr_name)
                self.client._EDRClient__intel(_("Intel about {}").format(cmdr_name), [_("No info").format(cmdr=cmdr_name)], clear_before=True)
        except CommsJammedError:
            self.client._EDRClient__commsjammed()
