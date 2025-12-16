import datetime
from edrlog import EDR_LOG
from lrucache import LRUCache

class EDRHttpCache(object):
    def __init__(self):
        self.capacity = 50
        # Initialize LRUCache with a very long max_age because we handle expiration ourselves
        # per item. We mostly use LRUCache for the capacity management.
        self.max_age = datetime.timedelta(days=365)
        self.cache = LRUCache(self.capacity, self.max_age.total_seconds())

    def get(self, key):
        # LRUCache.get return the content, treating it as not stale if within self.max_age
        # It also updates the usage order (LRU).
        wrapped_content = self.cache.get(key)
        if not wrapped_content:
            return None
        
        # Wrapped content is expected to be { "data": actual_data, "expires": timestamp }
        if datetime.datetime.now() > wrapped_content["expires"]:
            EDR_LOG.debug(u"Expired entry for {}: {}".format(key, wrapped_content["expires"]))
            self.cache.evict(key)
            return None
        
        return wrapped_content["data"]

    def set(self, key, content, max_age_seconds):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=max_age_seconds)
        wrapped_content = { "data": content, "expires": expires }
        self.cache.set(key, wrapped_content)
