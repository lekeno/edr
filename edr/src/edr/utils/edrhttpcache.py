import datetime
from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL
from .lrucache import LRUCache  # EDR_INTERNAL


class EDRHttpCache:
    """
    A caching layer for HTTP responses with ETag and expiration support.
    """

    def __init__(self):
        """
        Initialize the cache with default capacity and long max-age.
        """
        self.capacity = 50
        # Initialize LRUCache with a very long max_age because we handle expiration ourselves
        # per item. We mostly use LRUCache for the capacity management.
        self.max_age = datetime.timedelta(days=365)
        self.cache = LRUCache(self.capacity, self.max_age.total_seconds())

    def get(self, key):
        """
        Retrieve a value from the cache if it hasn't expired.

        Args:
            key (str): The cache key (usually the URL).

        Returns:
            object: The cached content, or None if missing/expired.
        """
        # LRUCache.get return the content, treating it as not stale if within self.max_age
        # It also updates the usage order (LRU).
        wrapped_content = self.cache.get(key)
        if not wrapped_content:
            return None

        # Wrapped content is expected to be { "data": actual_data, "expires": timestamp }
        if datetime.datetime.now() > wrapped_content["expires"]:
            EDR_LOG.debug(f"Expired entry for {key}: {wrapped_content['expires']}")
            self.cache.evict(key)
            return None

        return wrapped_content["data"]

    def get_etag(self, key):
        """
        Peek at the cache to get the ETag without evicting if stale.

        Args:
            key (str): The cache key.

        Returns:
            str: The ETag string or None.
        """
        wrapped_content = self.cache.peek(key)
        return wrapped_content.get("etag") if wrapped_content else None

    def set(self, key, content, max_age_seconds, etag=None):
        """
        Set a value in the cache with a specific expiration time.

        Args:
            key (str): The cache key.
            content (object): The data to cache.
            max_age_seconds (int): Time to live in seconds.
            etag (str): Optional ETag for the content.
        """
        if max_age_seconds is None:
            max_age_seconds = 0

        expires = datetime.datetime.now() + datetime.timedelta(seconds=max_age_seconds)
        wrapped_content = {"data": content, "expires": expires, "etag": etag}

        self.cache.set(key, wrapped_content, ttl_seconds=max_age_seconds)

    def refresh(self, key, max_age_seconds=None):
        """
        Updates the expiration and LRU position for a 304 response.

        Args:
            key (str): The cache key.
            max_age_seconds (int): New TTL in seconds (optional).

        Returns:
            bool: True if refreshed, False if key not found.
        """
        wrapped_content = self.cache.peek(key)
        if wrapped_content:
            if max_age_seconds is None:
                max_age_seconds = wrapped_content.get('ttl_seconds', 300)

            new_expires = datetime.datetime.now() + datetime.timedelta(seconds=max_age_seconds)
            wrapped_content["expires"] = new_expires

            self.cache.set(key, wrapped_content, ttl_seconds=max_age_seconds)
            return True
        return False

    def evict(self, key):
        """
        Removes an entry from the cache immediately.

        Args:
            key (str): The item to remove.
        """
        EDR_LOG.debug(f"Evicting {key} from HTTP cache")
        self.cache.evict(key)

    def evict_prefix(self, prefix):
        """
        Removes all entries that start with a specific prefix.
        Useful for clearing all variants of an endpoint (e.g., different auth tokens).

        Args:
            prefix (str): The prefix string to match.
        """
        # This assumes the underlying LRUCache.cache is a dict or similar iterable
        keys_to_remove = [k for k in self.cache.cache.keys() if k.startswith(prefix)]
        for k in keys_to_remove:
            EDR_LOG.debug(f"Prefix-evicting {k} from HTTP cache")
            self.cache.evict(k)
