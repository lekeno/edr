import config_tests
from unittest import TestCase, main
from edentities import EDFineOrBounty

class TestEDFineOrBounty(TestCase):
    def test_significant(self):
        bounty = EDFineOrBounty(12344)
        bounty.threshold = 12345
        self.assertFalse(bounty.is_significant())

        bounty = EDFineOrBounty(12345)
        bounty.threshold = 12345
        self.assertTrue(bounty.is_significant())

        bounty = EDFineOrBounty(12346)
        bounty.threshold = 12345
        self.assertTrue(bounty.is_significant())


    def test_pretty_print(self):
        bounty = EDFineOrBounty(999)
        self.assertEqual(bounty.pretty_print(), "999")

        bounty = EDFineOrBounty(1000)
        self.assertEqual(bounty.pretty_print(), "1.0 k")

        bounty = EDFineOrBounty(9999)
        self.assertEqual(bounty.pretty_print(), "10.0 k")

        bounty = EDFineOrBounty(12345)
        self.assertEqual(bounty.pretty_print(), "12 k")

        bounty = EDFineOrBounty(99999)
        self.assertEqual(bounty.pretty_print(), "99 k")

        bounty = EDFineOrBounty(100000)
        self.assertEqual(bounty.pretty_print(), "100 k")


if __name__ == '__main__':
    main()