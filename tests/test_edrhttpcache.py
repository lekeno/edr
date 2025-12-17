
import sys
import os

import unittest
import datetime
import time
from edrhttpcache import EDRHttpCache # EDR_INTERNAL

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
        max_age = 1 # 1 second
        
        cache.set(url, content, max_age)
        cached = cache.get(url)
        self.assertEqual(cached, content)
        
        time.sleep(1.1)
        cached = cache.get(url)
        self.assertIsNone(cached)

    def test_eviction(self):
        cache = EDRHttpCache()
        cache.capacity = 2 # Small capacity
        cache.cache = cache.cache.__class__(2, 3600) # Re-init LRUCache with small cap

        cache.set("1", "v1", 60)
        cache.set("2", "v2", 60)
        cache.set("3", "v3", 60) # Should evict 1
        
        self.assertIsNone(cache.get("1"))
        self.assertEqual(cache.get("2"), "v2")
        self.assertEqual(cache.get("3"), "v3")

if __name__ == '__main__':
    unittest.main()
