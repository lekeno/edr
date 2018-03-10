import config_tests
from unittest import TestCase, main
from lrucache import LRUCache
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

        self.assertListEqual(cache.keys(), samples.keys())
        
        for key in samples:
            self.assertTrue(cache.has_key(key))
            self.assertEqual(cache.get(key), samples[key])
        
    def test_stale(self):
        cache = LRUCache(5, 1)
        sample = {"test": True, "foo": "bar"}
        key = "a"
        cache.set(key, sample)
        self.assertFalse(cache.is_stale(key))
        time.sleep(1.2)
        self.assertTrue(cache.is_stale(key))
        self.assertEqual(cache.get("a"), None)

if __name__ == '__main__':
    main()