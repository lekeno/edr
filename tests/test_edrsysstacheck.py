import unittest
from unittest.mock import patch
from edr.controllers.edrsysstacheck import EDRSystemStationCheck, EDRApexSystemStationCheck

class TestEDRSystemStationCheck(unittest.TestCase):
    def setUp(self):
        self.checker = EDRSystemStationCheck()

    def test_check_system(self):
        # Valid system within range
        self.assertTrue(self.checker.check_system({'distance': 10}))
        # Valid system at edge
        self.assertTrue(self.checker.check_system({'distance': 50}))
        # Invalid system out of range
        self.assertFalse(self.checker.check_system({'distance': 51}))
        # Malformed system
        self.assertFalse(self.checker.check_system({}))
        self.assertFalse(self.checker.check_system(None))

    def test_check_station(self):
        # Valid station within range
        self.assertTrue(self.checker.check_station({'distanceToArrival': 500}))
        # Invalid station out of range
        self.assertFalse(self.checker.check_station({'distanceToArrival': 1500})) # < strict
        
        # Odyssey compatibility
        odyssey_station = {'distanceToArrival': 100, 'type': 'On Foot Settlement (Odyssey)'}
        # Assuming default DLC is NOT Odyssey
        self.assertFalse(self.checker.check_station(odyssey_station))
        
        self.checker.set_dlc("Odyssey")
        self.checker.set_dlc("Odyssey")
        self.assertTrue(self.checker.check_station(odyssey_station))

    def test_is_service_availability_ambiguous(self):
        self.assertFalse(self.checker.is_service_availability_ambiguous({}))

class TestEDRApexSystemStationCheck(unittest.TestCase):
    def setUp(self):
        self.checker = EDRApexSystemStationCheck()

    def test_check_station_apex(self):
        # Valid station type
        valid_station = {'distanceToArrival': 100, 'type': 'Orbis Starport'}
        self.assertTrue(self.checker.check_station(valid_station))
        
        # Invalid station type (Outpost not allowed? actually wait, allowed_types includes outpost)
        # Let's check a Fleet Carrier which is NOT in allowed_types
        fc = {'distanceToArrival': 100, 'type': 'Fleet Carrier'}
        self.assertFalse(self.checker.check_station(fc))

        # Check distance override
        # EDRSystemStationCheck defaults max_distance=50, but Apex overrides to 100
        # Let's check system check logic inheritance
        self.assertTrue(self.checker.check_system({'distance': 90}))
        self.assertFalse(self.checker.check_system({'distance': 101}))

if __name__ == '__main__':
    unittest.main()
