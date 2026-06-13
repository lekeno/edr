import os
import collections
import datetime
import pickle
from edr.core.edrlog import EDR_LOG
from .edrpickle import edr_load_pickle


class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with Time-To-Live (TTL) support.
    """

    def __init__(self, max_size, default_max_age_seconds):
        """
        Initializes the LRU Cache.

        Args:
            max_size (int): Maximum number of items in the cache.
            default_max_age_seconds (int): Default TTL for items in seconds.
        """
        self.capacity = max_size
        self.default_max_age = datetime.timedelta(seconds=default_max_age_seconds)
        self.cache = collections.OrderedDict()
        self.last_updated = None

    def __setstate__(self, state):
        """
        Restores state from pickle, creating default_max_age if missing and healing entries with missing TTLs.

        Args:
            state (dict): The state dictionary to restore.
        """
        # 1. Migrate the Global Attribute Name (max_age -> default_max_age)
        if 'max_age' in state:
            state['default_max_age'] = state['max_age']
            del state['max_age']

        # 2. Determine the TTL to use for healing entries that are missing 'ttl'.
        default_ttl_for_healing = state.get('default_max_age')

        if default_ttl_for_healing and 'cache' in state:
            for key, entry in state['cache'].items():
                if 'ttl' not in entry:
                    # Heal the old entry by adding the new attribute
                    entry['ttl'] = default_ttl_for_healing

        # 3. Apply the state to the instance
        self.__dict__.update(state)

    def is_stale(self, key):
        """
        Checks if an item has expired based on its TTL.

        Args:
            key (object): The key to check.

        Returns:
            bool: True if expired or not found, False otherwise.
        """
        if key not in self.cache:
            return True

        entry = self.cache[key]
        # We can trust that 'ttl' exists because of set() and __setstate__
        return (datetime.datetime.now() - entry["datetime"]) > entry["ttl"]

    def is_older_than(self, key, age):
        """
        Checks if an item is older than a specific age in seconds.

        Args:
            key (object): The key to check.
            age (int): Age threshold in seconds.

        Returns:
            bool: True if older or not found, False otherwise.
        """
        if not self.has_key(key):
            return True

        entry = self.cache[key]
        age_delta = datetime.timedelta(seconds=age)

        return (datetime.datetime.now() - entry["datetime"]) > age_delta

    def values(self):
        """
        Returns a list of all values in the cache.

        Returns:
            list: List of values.
        """
        return list(self.cache.values())

    def keys(self):
        """
        Returns a list of all keys in the cache.

        Returns:
            list: List of keys.
        """
        return list(self.cache.keys())

    def has_key(self, key):
        """
        Checks if a key exists in the cache (ignores expiration).

        Args:
            key (object): The key to check.

        Returns:
            bool: True if found, False otherwise.
        """
        return key in self.cache

    def refresh(self, key):
        """
        Refreshes the TTL and LRU position of an item.

        Args:
            key (object): The key of the item to refresh.
        """
        if not self.has_key(key):
            return

        entry = self.cache[key]
        content = entry["content"]

        # Determine the TTL to use for the refresh:
        # 1. Try to get the entry's custom 'ttl'.
        # 2. Fall back to the instance's self.default_max_age.
        ttl_timedelta = entry.get("ttl", self.default_max_age)

        # Convert the timedelta object back into seconds for the 'set' method.
        ttl_seconds = ttl_timedelta.total_seconds()

        # Use the 'set' method to reset the timestamp to 'now' and update the LRU position
        self.set(key, content, ttl_seconds=ttl_seconds)

    def get(self, key):
        """
        Retrieves an item from the cache.

        Args:
            key (object): The key to retrieve.

        Returns:
            object: The content if found and not stale, else None.
        """
        if self.capacity <= 0:
            return None

        entry = self.cache.get(key)
        if not entry:
            return None

        if self.is_stale(key):
            EDR_LOG.debug(f"Stale entry for {key}")
            self.cache.pop(key)
            return None

        # Move to end (most recently used)
        self.cache[key] = self.cache.pop(key)
        return entry["content"]

    def set(self, key, value, ttl_seconds=None):
        """
        Adds or updates an item in the cache.

        Args:
            key (object): The key to store.
            value (object): The content to store.
            ttl_seconds (int, optional): Optional custom TTL in seconds. Defaults to None.
        """
        if self.capacity <= 0:
            return

        if ttl_seconds is not None:
            ttl = datetime.timedelta(seconds=ttl_seconds)
        else:
            ttl = self.default_max_age  # Fallback to global default

        try:
            self.cache.pop(key, None)
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
        """
        Removes a specific item from the cache.

        Args:
            key (object): The key to remove.
        """
        try:
            self.cache.pop(key, None)
        except KeyError:
            pass

    def peek(self, key):
        """
        Retrieves content without updating usage statistics or checking expiration.

        Args:
            key (object): The key to peek.

        Returns:
            object: The content if present, else None.
        """
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
        """Clears the cache."""
        self.cache = collections.OrderedDict()
        self.last_updated = None

    def save(self, file_path):
        """
        Persists the current cache instance to the specified file path.

        Args:
            file_path (str): Path to save the cache to.
        """
        try:
            cache_dir = os.path.dirname(file_path)
            if cache_dir and not os.path.exists(cache_dir):
                EDR_LOG.debug(f"Creating missing cache directory: {cache_dir}")
                os.makedirs(cache_dir)

            with open(file_path, 'wb') as handle:
                pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            EDR_LOG.exception(f"Failed to save cache to {file_path}: {e}")

    @classmethod
    def load(cls, file_path, max_size, max_age_seconds):
        """
        Attempts to load a serialized LRUCache instance from the given file_path.

        Falls back to creating a new instance on failure.

        Args:
            file_path (str): Path to load the cache from.
            max_size (int): Max size for the cache (applied if loaded).
            max_age_seconds (int): Max age for the cache items (applied if loaded).

        Returns:
            LRUCache: The loaded or new cache instance.
        """
        if not os.path.exists(file_path):
            EDR_LOG.debug(f"No cache file found at {file_path}. Starting fresh.")
            return cls(max_size, max_age_seconds)

        try:
            with open(file_path, 'rb') as handle:
                # The pickle.load process automatically calls __setstate__ 
                # to handle attribute migration and entry healing.
                cache_instance = edr_load_pickle(handle)

                # IMPORTANT: Ensure the loaded cache uses the current max_size/max_age 
                # configuration, as config can change between runs.
                cache_instance.capacity = max_size
                cache_instance.default_max_age = datetime.timedelta(seconds=max_age_seconds)

                return cache_instance

        except FileNotFoundError:
            EDR_LOG.debug(f"Cache file {file_path} was empty or missing. Starting fresh.")
            return cls(max_size, max_age_seconds)
        except (pickle.UnpicklingError, EOFError, Exception) as e:
            EDR_LOG.error(f"Cache load failed for {file_path}: {e}. Starting fresh.")

            if os.path.exists(file_path):
                try:
                    EDR_LOG.warning("Deleting corrupt cache file: {}".format(file_path))
                    os.remove(file_path)
                except Exception as del_e:
                    EDR_LOG.error("Failed to delete corrupt file {}: {}".format(file_path, del_e))

            return cls(max_size, max_age_seconds)
