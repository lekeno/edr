import collections
import datetime

import edrlog

EDRLOG = edrlog.EDRLog()

class LRUCache(object):
    def __init__(self, max_size, max_age_seconds):
        self.capacity = max_size
        self.max_age = datetime.timedelta(seconds=max_age_seconds)
        self.cache = collections.OrderedDict()
        self.last_updated = None
    
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

        if not self.has_key(key):
            return None

        try:
            entry = self.cache[key]
            if not self.is_stale(key):
                self.cache[key] = self.cache.pop(key)
                return entry["content"]
            else:
                EDRLOG.log(u"Stale entry for {key}: {now} - {dt} = {diff} > {mxa}, {content}".format(key=key, now=datetime.datetime.now(), dt=entry["datetime"], diff=(datetime.datetime.now() - entry["datetime"]), mxa=self.max_age, content=entry["content"]), "DEBUG")
                self.cache.pop(key)
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
        
        now = datetime.datetime.now()
        self.cache[key] = { "datetime": now, "content": value}
        self.last_updated = now

    def __delitem__(self, key):
        del self.cache[key]

    def evict(self, key):
        try:
            self.cache.pop(key)
        except KeyError:
            pass

    def reset(self):
        self.cache = collections.OrderedDict()
        self.last_updated = None

