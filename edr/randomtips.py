import os
import json
import random

class RandomTips(object):
    def __init__(self, tips_file):
        self.tips = json.loads(open(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), tips_file)).read())

    def tip(self):
        category = random.choice(self.tips.keys())
        return random.choice(self.tips[category])