class EDCodex(object):
    def __init__(self):
        self.entries = {}

    def process(self, scan_event):
        if scan_event["event"] == "ScanOrganic" and scan_event["ScanType"] == "Analyse":
            # mark species for that system/body as analyzed
            pass
        elif scan_event["event"] == "CodexEntry":
            # mark species as discovered
            pass
