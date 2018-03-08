import config_tests
from unittest import TestCase, main
from edentities import EDLocation

class TestEDLocation(TestCase):
    def test_is_anarchy_or_lawless(self):
        location = EDLocation()
        self.assertFalse(location.is_anarchy_or_lawless())

        location = EDLocation()
        location.security = ""
        self.assertFalse(location.is_anarchy_or_lawless())

        location = EDLocation()
        location.security = "dummy"
        self.assertFalse(location.is_anarchy_or_lawless())

        location = EDLocation()
        location.security = "$SYSTEM_SECURITY_high;"
        self.assertFalse(location.is_anarchy_or_lawless())

        location = EDLocation()
        location.security = "$SYSTEM_SECURITY_medium;"
        self.assertFalse(location.is_anarchy_or_lawless())

        location = EDLocation()
        location.security = "$GAlAXY_MAP_INFO_state_anarchy;"
        self.assertTrue(location.is_anarchy_or_lawless())

        location = EDLocation()
        location.security = "$GALAXY_MAP_INFO_state_lawless;"
        self.assertTrue(location.is_anarchy_or_lawless())


if __name__ == '__main__':
    main()