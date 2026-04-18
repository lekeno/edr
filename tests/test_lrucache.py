
from unittest import TestCase, main
from edr.utils.lrucache import LRUCache
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


    def test_peek(self):
        cache = LRUCache(5, 60)
        cache.set("a", 1)
        
        # Peek should return value but not change order? 
        # Actually LRUCache.peek implementation does NOT change order.
        # Let's verify that.
        cache.set("b", 2)
        cache.set("c", 3)
        # Order: a, b, c (most recent)
        
        val = cache.peek("a")
        self.assertEqual(val, 1)
        
        # If peek updated LRU, 'a' would be most recent.
        # If it didn't, 'c' is still most recent.
        # Let's add 3 more items to force eviction of least recent.
        cache.set("d", 4)
        cache.set("e", 5)
        cache.set("f", 6)
        
        # Now we have 5 items. capacity is 5.
        # If 'a' was not updated, it should have been evicted first (as it was inserted first).
        # Order before d,e,f: a, b, c.
        # After d: b, c, d. (a evicted)
        # After e: c, d, e. (b evicted)
        # After f: d, e, f. (c evicted)
        # Wait, capacity is 5.
        # Insert a, b, c. Size 3.
        # Peek a.
        # Insert d (4), e (5). Size 5. [a, b, c, d, e]
        # Insert f (6). Size 6 -> Evict LRU.
        
        # If peek updated a, order would be b, c, a, d, e. LRU is b.
        # If peek did NOT update a, order is a, b, c, d, e. LRU is a.
        
        # So if we insert 'f', and 'a' is gone, then peek did not update.
        self.assertFalse(cache.has_key("a"))
        
    def test_is_older_than(self):
        cache = LRUCache(5, 60)
        cache.set("a", 1)
        time.sleep(0.1)
        # Should be older than 0 seconds
        self.assertTrue(cache.is_older_than("a", 0))
        # Should NOT be older than 2 seconds
        self.assertFalse(cache.is_older_than("a", 2))
        
    def test_magic_methods(self):
        cache = LRUCache(5, 60)
        cache.set("a", 1)
        self.assertTrue(cache.has_key("a"))
        del cache["a"]
        self.assertFalse(cache.has_key("a"))

    def test_persistence(self):
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
            
        try:
            # 1. Save
            cache = LRUCache(5, 60)
            cache.set("a", {"data": 123})
            cache.save(tmp_path)
            
            # 2. Load
            loaded_cache = LRUCache.load(tmp_path, 5, 60)
            self.assertTrue(loaded_cache.has_key("a"))
            self.assertEqual(loaded_cache.get("a"), {"data": 123})
            
            # 3. Load with different config
            loaded_cache_resized = LRUCache.load(tmp_path, 10, 120)
            self.assertEqual(loaded_cache_resized.capacity, 10)
            self.assertEqual(loaded_cache_resized.default_max_age.total_seconds(), 120)
            
            # 4. Load non-existent (should start fresh)
            fresh_cache = LRUCache.load(tmp_path + ".missing", 5, 60)
            self.assertEqual(len(fresh_cache.keys()), 0)
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == '__main__':
    main()