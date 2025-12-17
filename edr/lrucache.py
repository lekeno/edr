import os
import collections
import datetime
import pickle
from edrlog import EDR_LOG

class LRUCache(object):
    def __init__(self, max_size, default_max_age_seconds):
        self.capacity = max_size
        self.default_max_age = datetime.timedelta(seconds=default_max_age_seconds)
        self.cache = collections.OrderedDict()
        self.last_updated = None

    def __setstate__(self, state):
        # 1. Migrate the Global Attribute Name (max_age -> default_max_age)
        # This handles caches saved before you renamed the attribute.
        if 'max_age' in state:
            state['default_max_age'] = state['max_age']
            del state['max_age']
        
        # Determine the TTL to use for healing entries that are missing 'ttl'.
        # Prioritize 'default_max_age' (new name) then 'max_age' (old name).
        default_ttl_for_healing = state.get('default_max_age')
        
        if default_ttl_for_healing and 'cache' in state:
            for key, entry in state['cache'].items():
                if 'ttl' not in entry:
                    # Heal the old entry by adding the new attribute
                    entry['ttl'] = default_ttl_for_healing
        
        # 3. Apply the state to the instance (standard unpickling step)
        self.__dict__.update(state)
    
    def is_stale(self, key):
        if not self.has_key(key):
            return True
        
        entry = self.cache[key]
        entry_ttl = entry.get("ttl", self.default_max_age)

        return (datetime.datetime.now() - entry["datetime"]) > entry_ttl

    def is_older_than(self, key, age):
        if not self.has_key(key):
            return True
        
        entry = self.cache[key]
        age_delta = datetime.timedelta(seconds=age)
        
        return (datetime.datetime.now() - entry["datetime"]) > age_delta

    def values(self):
        return self.cache.values()

    def keys(self):
        return self.cache.keys()

    def has_key(self, key):
        return key in self.cache

    def refresh(self, key):
        if not self.has_key(key):
            return
        
        entry = self.cache[key]
        content = entry["content"]
        
        # Determine the TTL to use for the refresh:
        
        # 1. Try to get the entry's custom 'ttl' (a datetime.timedelta object).
        # 2. Fall back to the instance's self.default_max_age (also a timedelta).
        #    This covers old entries before the custom TTL change.
        ttl_timedelta = entry.get("ttl", self.default_max_age)
        
        # Convert the timedelta object back into seconds for the 'set' method.
        ttl_seconds = ttl_timedelta.total_seconds() 
        
        # Use the 'set' method to reset the timestamp to 'now' and update the LRU position,
        # using the most appropriate TTL (custom or default).
        self.set(key, content, ttl_seconds=ttl_seconds)

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
                entry_ttl = entry.get("ttl", self.default_max_age)
                EDR_LOG.debug(u"Stale entry for {key}: {now} - {dt} = {diff} > {mxa}, {content}".format(
                    key=key, 
                    now=datetime.datetime.now(), 
                    dt=entry["datetime"], 
                    diff=(datetime.datetime.now() - entry["datetime"]), 
                    mxa=entry_ttl,
                    content=entry["content"]
                ))
                self.cache.pop(key)
        except KeyError:
            pass
        
        return None

    def set(self, key, value, ttl_seconds=None):
        if self.capacity <= 0:
            return

        if ttl_seconds is not None:
            ttl = datetime.timedelta(seconds=ttl_seconds)
        else:
            ttl = self.default_max_age # Fallback to global default

        try:
            self.cache.pop(key)
        except KeyError:
            pass

        while len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        
        now = datetime.datetime.now()
        self.cache[key] = {
            "datetime": now,
            "content": value,
            "ttl": ttl
        }
        self.last_updated = now

    def __delitem__(self, key):
        del self.cache[key]

    def evict(self, key):
        try:
            self.cache.pop(key)
        except KeyError:
            pass

    def peek(self, key):
        if self.capacity <= 0:
            return None

        if not self.has_key(key):
            return None

        try:
            entry = self.cache[key]
            return entry["content"]
        except KeyError:
            pass
        
        return None

    def reset(self):
        self.cache = collections.OrderedDict()
        self.last_updated = None

    def save(self, file_path):
        """
        Persists the current cache instance to the specified file path.
        """
        try:
            with open(file_path, 'wb') as handle:
                pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            EDR_LOG.exception(f"Failed to save cache to {file_path}: {e}")
            pass

    @classmethod
    def load(cls, file_path, max_size, max_age_seconds):
        """
        Attempts to load a serialized LRUCache instance from the given file_path.
        Falls back to creating a new instance on failure.
        """
        try:
            with open(file_path, 'rb') as handle:
                # The pickle.load process automatically calls __setstate__ 
                # to handle attribute migration and entry healing.
                cache_instance = pickle.load(handle)
                
                # IMPORTANT: Ensure the loaded cache uses the current max_size/max_age 
                # configuration, as config can change between runs.
                cache_instance.capacity = max_size
                cache_instance.default_max_age = datetime.timedelta(seconds=max_age_seconds)

                return cache_instance
                
        except (FileNotFoundError, EOFError, pickle.UnpicklingError, Exception) as e:
            EDR_LOG.exception(f"Cache load failed for {file_path}: {e}")
            
            # Optionally: Clean up corrupt file
            if os.path.exists(file_path):
                EDR_LOG.warning(f"Deleting corrupt cache file: {file_path}")
                os.remove(file_path)
            
            # Fallback: Return a new, initialized instance
            return cls(max_size, max_age_seconds)