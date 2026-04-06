import json
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.utils.edtime import EDTime
from edr.utils.clippy import copy
from edr.models.edsitu import EDPlanetaryLocation
from edr.controllers.edrserver import CommsJammedError

class EDRGuidanceManager:
    """
    Manages Navigation and Guidance capabilities,
    extracting logic for distance calculations, navigation, sitreps, and NOTAMs.
    """
    def __init__(self, edr_client):
        self.client = edr_client

    def notams(self):
        """
        Show active NOTAMs (Notice to Air Men).
        """
        summary = self.client.edrsystems.systems_with_active_notams()
        if summary:
            details = []
            safe_summary = [str(s) for s in summary if s is not None]
            
            # Translators: this shows a ist of systems {} with active NOtice To Air Men via the overlay
            details.append(_("Active NOTAMs for: {}").format("; ".join(safe_summary)))
            # Translators: this is the heading for the active NOTAMs overlay
            self.client._EDRClient__sitrep(_("NOTAMs"), details)
        else:
            self.client._EDRClient__sitrep(_("NOTAMs"), [_("No active NOTAMs.")])

    def notam(self, star_system):
        """
        Show active NOTAMs for a specific system.
        """
        summary = self.client.edrsystems.active_notams(star_system)
        if summary:
            EDR_LOG.debug("NOTAMs for {}: {}".format(star_system, summary))
            # Translators: this is the heading to show any active NOTAM for a given system {} 
            self.client._EDRClient__sitrep(_("NOTAM for {}").format(star_system), summary)
        else:
            self.client._EDRClient__sitrep(_("NOTAM for {}").format(star_system), [_("No active NOTAMs.")])

    def sitreps(self):
        """
        Show Situation Reports (SITREPs) for systems with recent activity.
        """
        try:
            details = []
            summary = self.client.edrsystems.systems_with_recent_activity()

            if not summary:
                return
            
            for section in summary:
                systems = summary.get(section)
                if systems:
                    safe_systems = [str(s) for s in systems if s is not None]
                    details.append("{}: {}".format(section, "; ".join(safe_systems)))
            
            if details:
                header = _("SITREPS") if self.client.player.in_open() else _("SITREPS (Open)")
                self.client._EDRClient__sitrep(header, details)
        except CommsJammedError:
            self.client._EDRClient__commsjammed()

    def distance(self, from_system, to_system):
        """
        Calculate and display distance between two systems.
        """
        details = []
        distance = None
        try:
            distance = self.client.edrsystems.distance(from_system, to_system)
        except ValueError:
            pass
            
        if distance:
            pretty_dist = _("{distance:.3g}").format(distance=distance) if distance < 50.0 else _("{distance}").format(distance=int(distance))
            details.append(_("{dist}ly from {from_sys} to {to_sys}").format(dist=pretty_dist, from_sys=from_system, to_sys=to_system))
            taxi_jump_range = 50
            jumping_time = self.client.edrsystems.jumping_time(from_system, to_system, taxi_jump_range)
            transfer_time = self.client.edrsystems.transfer_time(from_system, to_system)
            details.append(_("Taxi time ({}LY): {}").format(taxi_jump_range, EDTime.pretty_print_timespan(jumping_time)))
            details.append(_("Transfer time: {}").format(EDTime.pretty_print_timespan(transfer_time)))
            self.client.status = _("distance: {dist}ly").format(dist=pretty_dist)
        else:
            self.client.status = _("distance failed")
            details.append(_("Couldn't calculate a distance. Invalid or unknown system names?"))
        self.client._EDRClient__notify(_("Distance"), details, clear_before = True)

    def navigation(self, latitude, longitude, title="Navpoint"):
        """
        Set a navigation destination.
        """
        position = {"latitude": float(latitude), "longitude": float(longitude)}
        boi = {}
        poi = {}
        body = self.client.player.body or "unknown body"
        poi[body.lower()] = [{
            "title": title,
            "latitude": float(latitude),
            "longitude": float(longitude)
        }]
        boi[self.client.player.star_system.lower()] = poi
        copy(json.dumps(boi))
        loc = EDPlanetaryLocation(position)
        if loc.valid():
            self.client.player.planetary_destination = loc
            self.client._EDRClient__notify(_('Assisted Navigation'), [_("Destination set to {} | {}").format(latitude, longitude), _("Guidance will be shown when approaching a stellar body"), _("Destination added to the clipboard")], clear_before = True)
        else:
            self.client.player.planetary_destination = None
