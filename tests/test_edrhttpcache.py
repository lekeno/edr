
import sys
import os
import unittest
import datetime
import time

# Add 'edr' directory path to allow imports


from edr.utils.edrhttpcache import EDRHttpCache
from edr.utils.lrucache import LRUCache

class TestEDRHttpCache(unittest.TestCase):
    def test_set_get(self):
        cache = EDRHttpCache()
        url = "http://example.com/api"
        content = {"data": "test"}
        max_age = 60
        
        cache.set(url, content, max_age)
        cached = cache.get(url)
        self.assertEqual(cached, content)

    def test_expiration(self):
        cache = EDRHttpCache()
        url = "http://example.com/api"
        content = {"data": "test"}
        max_age = 60
        
        # Start at T=1000
        initial_time = datetime.datetime(2023, 1, 1, 12, 0, 0)
        with unittest.mock.patch('edr.utils.edrhttpcache.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = initial_time
            mock_datetime.timedelta = datetime.timedelta # Passthrough
            
            cache.set(url, content, max_age)
            
            # Check immediately (T=1000) -> Not expired
            cached = cache.get(url)
            self.assertEqual(cached, content)
            
            # Advance to T=1061 (Expired)
            mock_datetime.now.return_value = initial_time + datetime.timedelta(seconds=61)
            cached = cache.get(url)
            self.assertIsNone(cached)

    def test_eviction(self):
        cache = EDRHttpCache()
        cache.capacity = 2 # Small capacity
        cache.cache = LRUCache(2, 3600) # Re-init LRUCache with small cap

        cache.set("1", "v1", 60)
        cache.set("2", "v2", 60)
        cache.set("3", "v3", 60) # Should evict 1
        
        self.assertIsNone(cache.get("1"))
        self.assertEqual(cache.get("2"), "v2")
        self.assertEqual(cache.get("3"), "v3")

    def test_get_etag(self):
        cache = EDRHttpCache()
        cache.set("url", "data", 60, etag="1234")
        self.assertEqual(cache.get_etag("url"), "1234")
        self.assertIsNone(cache.get_etag("missing"))

    def test_refresh(self):
        cache = EDRHttpCache()
        cache.set("url", "data", 60) # Expires in 60s
        self.assertTrue(cache.refresh("url", 120)) # Refresh to 120s
        # We can't easily check internal expiration without mocking datetime, but we know it returned True
        self.assertFalse(cache.refresh("missing"))

    def test_evict_prefix(self):
        cache = EDRHttpCache()
        cache.set("api/v1/user", "u", 60)
        cache.set("api/v1/profile", "p", 60)
        cache.set("api/v2/other", "o", 60)
        
        cache.evict_prefix("api/v1")
        self.assertIsNone(cache.get("api/v1/user"))
        self.assertIsNone(cache.get("api/v1/profile"))
        self.assertEqual(cache.get("api/v2/other"), "o")

if __name__ == '__main__':
    unittest.main()
