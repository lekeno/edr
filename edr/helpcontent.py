import os
import json

class HelpContent(object):
    def __init__(self, help_file):
        self.content = json.loads(open(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), help_file)).read())

    def get(self, category):
        if category in self.content.keys():
            return self.content[category]
        return None