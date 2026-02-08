class EDCodex:
    """Tracks Codex discoveries and organic scans."""

    def __init__(self):
        """Initialize the EDCodex with empty entries."""
        self.entries = {}

    def process(self, scan_event):
        """Process a scan event to update codex entries.

        Args:
            scan_event (dict): The event dictionary from the journal.
        """
        if scan_event.get("event") == "ScanOrganic" and scan_event.get("ScanType") == "Analyse":
            # TODO: mark species for that system/body as analyzed
            pass
        elif scan_event.get("event") == "CodexEntry":
            # TODO: mark species as discovered
            pass
