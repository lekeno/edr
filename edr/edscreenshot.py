from os.path import join

import edrconfig

class EDScreenshot(object):
    def __init__(self, entry):
        config = edrconfig.EDRUserConfig()
        self.directory = config.screenshots_directory()
        self.filename = entry.get("Filename", "")
        useless_prefix = "ED_screenshots\\"
        if self.filename.startswith(useless_prefix):
            self.filename = self.filename[len(useless_prefix):]
        self.w = entry.get("Width", 0)
        self.h = entry.get("Height", 0)
        self.system = entry.get("System", "Unknown")
        self.body = entry.get("Body", "")
        self.lat = entry.get("Latitude", None)
        self.lon = entry.get("Longitude", None)
        self.heading = entry.get("Heading", None)
        self.altitude = entry.get("Altitude", None)

    def getFilePath(self):
        if not self.directory:
            return None
        return join(self.directory, self.filename)

    def jpg(self):
        filepath = self.getfilepath()
        if not filepath:
            return None
        # TODO need some image processing library....

    def save_as_jpg(self):
        #TODO

    def resize(self, w, h):
        #TODO