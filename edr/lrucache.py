import collections
import datetime

import edrlog

EDRLOG = edrlog.EDRLog()

class LRUCache(object):
    def __init__(self, max_size, max_age_seconds):
        self.capacity = max_size
        self.max_age = datetime.timedelta(seconds=max_age_seconds)
        self.cache = collections.OrderedDict()
    
    def is_stale(self, key):
        if not self.has_key(key):
            return True
        entry = self.cache[key]
        return (datetime.datetime.now() - entry["datetime"]) > self.max_age

    def values(self):
        return self.cache.values()

    def keys(self):
        return self.cache.keys()

    def has_key(self, key):
        return key in self.cache

    def get(self, key):
        if self.capacity <= 0:
            return None

        try:
            self.cache[key] = self.cache.pop(key)
            entry = self.cache[key]
            if not self.is_stale(key):
                return entry["content"]
            else:
                EDRLOG.log(u"Stale entry: {now}-{dt}>{mxa}, {content}".format(now=datetime.datetime.now(), dt=entry["datetime"], mxa=self.max_age, content=entry["content"]), "DEBUG")
        except KeyError:
            pass
        
        return None

    def set(self, key, value):
        if self.capacity <= 0:
            return

        try:
            self.cache.pop(key)
        except KeyError:
            pass

        while len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        
        self.cache[key] = { "datetime": datetime.datetime.now(), "content": value}

    def __delitem__(self, key):
        del self.cache[key]

