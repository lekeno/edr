import config_tests
from unittest import TestCase, main
from edentities import EDBounty

class TestEDBounty(TestCase):
    def test_significant(self):
        bounty = EDBounty(12344)
        bounty.threshold = 12345
        self.assertFalse(bounty.is_significant())

        bounty = EDBounty(12345)
        bounty.threshold = 12345
        self.assertTrue(bounty.is_significant())

        bounty = EDBounty(12346)
        bounty.threshold = 12345
        self.assertTrue(bounty.is_significant())


    def test_pretty_print(self):
        bounty = EDBounty(999)
        self.assertEqual(bounty.pretty_print(), "999")

        bounty = EDBounty(1000)
        self.assertEqual(bounty.pretty_print(), "1.0 k")

        bounty = EDBounty(9999)
        self.assertEqual(bounty.pretty_print(), "10.0 k")

        bounty = EDBounty(12345)
        self.assertEqual(bounty.pretty_print(), "12 k")

        bounty = EDBounty(99999)
        self.assertEqual(bounty.pretty_print(), "99 k")

        bounty = EDBounty(100000)
        self.assertEqual(bounty.pretty_print(), "100 k")


if __name__ == '__main__':
    main()