
from unittest import TestCase, main
from edr.lrucache import LRUCache
import time

class TestLRUCache(TestCase):
    def test_basics(self):
        cache = LRUCache(5, 60)
        self.assertEqual(cache.capacity, 5)

        sample = {"test": True, "foo": "bar"}
        cache.set("a", sample)
        result = cache.get("a")
        self.assertEqual(result, sample)
        result = cache.get("a")
        self.assertDictEqual(result, sample)

        cache.evict("a")
        result = cache.get("a")
        self.assertEqual(result, None)

    def test_keys(self):
        cache = LRUCache(5, 60)
        samples = {
            "a": {"a": 123, "b": 456},
            "bc": {"z": 156}, 
            "foo": 223,
            "bar": "adada"}

        for key in samples:
            cache.set(key, samples[key])

        self.assertListEqual(sorted(list(cache.keys())), sorted(list(samples.keys()))) 
        
        for key in samples:
            self.assertTrue(cache.has_key(key))
            self.assertEqual(cache.get(key), samples[key])

    def test_values(self):
        cache = LRUCache(5, 60)
        
        # Test 1: Empty cache
        self.assertListEqual(list(cache.values()), [])
        
        # Test 2: Populated cache structure
        samples = {
            "key1": "data A",
            "key2": "data B"
        }
        
        # Set with a custom TTL to ensure 'ttl' key exists
        cache.set("key1", samples["key1"], ttl_seconds=120)
        cache.set("key2", samples["key2"], ttl_seconds=60)
        
        returned_values = list(cache.values())
        self.assertEqual(len(returned_values), 2)
        
        # Check the structure of the entries
        for entry in returned_values:
            self.assertIn("datetime", entry)
            self.assertIn("content", entry)
            self.assertIn("ttl", entry)
            
        # Check specific content values
        self.assertEqual(returned_values[0]["content"], "data A")
        self.assertEqual(returned_values[1]["content"], "data B")
        
    def test_stale(self):
        cache = LRUCache(5, 1)
        sample = {"test": True, "foo": "bar"}
        key = "a"
        cache.set(key, sample)
        self.assertFalse(cache.is_stale(key))
        time.sleep(1.2)
        self.assertTrue(cache.is_stale(key))
        self.assertEqual(cache.get("a"), None)

    def test_custom_ttl(self):
        # Set default TTL very long (30 seconds)
        cache = LRUCache(5, 30) 
        key_short = "short"
        key_long = "long"
        sample = {"data": 1}

        # Set entry with a short custom TTL (1 second)
        cache.set(key_short, sample, ttl_seconds=1) 
        
        # Set entry using the long default TTL (30 seconds)
        cache.set(key_long, sample)

        # 1. Verify custom TTL expires quickly
        self.assertFalse(cache.is_stale(key_short))
        time.sleep(1.2)
        self.assertTrue(cache.is_stale(key_short))
        self.assertEqual(cache.get(key_short), None)

        # 2. Verify the default TTL is still active
        self.assertFalse(cache.is_stale(key_long))
        self.assertDictEqual(cache.get(key_long), sample)

    def test_reset(self):
        cache = LRUCache(3,60)
        cache.set("a", 34)
        cache.reset()
        self.assertEqual(list(cache.keys()), [])
        self.assertEqual(list(cache.values()), [])
        self.assertEqual(cache.last_updated, None)

    def test_refresh(self):
        # Set default TTL to 1 second
        cache = LRUCache(5, 1) 
        key_default = "default"
        key_custom = "custom"
        sample = {"data": 1}

        # 1. Test refresh on default TTL
        cache.set(key_default, sample)
        time.sleep(0.5) # Almost stale
        self.assertFalse(cache.is_stale(key_default))
        
        cache.refresh(key_default) # Should reset the 1-second timer
        time.sleep(0.7) # Should still be fresh (0.5 passed, refreshed, now 0.7 passed)
        self.assertFalse(cache.is_stale(key_default))
        
        time.sleep(0.5) # Total time since refresh > 1 second
        self.assertTrue(cache.is_stale(key_default))
        
        # 2. Test refresh on custom TTL (2 seconds)
        cache.set(key_custom, sample, ttl_seconds=2)
        time.sleep(1.0)
        self.assertFalse(cache.is_stale(key_custom))
        
        cache.refresh(key_custom) # Should reset the 2-second timer
        time.sleep(1.5) # Should still be fresh (1.5 < 2)
        self.assertFalse(cache.is_stale(key_custom))

        time.sleep(1.0) # Total time since refresh > 2 seconds
        self.assertTrue(cache.is_stale(key_custom))


if __name__ == '__main__':
    main()