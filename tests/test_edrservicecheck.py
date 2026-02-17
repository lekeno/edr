
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrservicecheck import (
    EDRStationServiceCheck, EDRStationFacilityCheck, EDRStagingCheck,
    EDRStationRRRCheck, EDRFleetCarrierRRRCheck, EDRRawTraderCheck,
    EDRManufacturedTraderCheck, EDREncodedTraderCheck, EDRHumanTechBrokerCheck,
    EDRGuardianTechBrokerCheck
)

class TestEDRServiceCheck(unittest.TestCase):
    def setUp(self):
        self.i18n_patch = patch('edr.controllers.edrservicecheck._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        self.edtime_patch = patch('edr.controllers.edrservicecheck.EDTime')
        self.mock_edtime = self.edtime_patch.start()
        
        # Mock sysstacheck super calls if needed, but since we test logic in subclasses, 
        # we might rely on the fact that they call super().check_station etc.
        # EDRSystemStationCheck is in another file, imported.
        # It's better to mock the parent if it does complex stuff, but here it seems simple?
        # Let's inspect imports. 
        # from .edrsysstacheck import EDRSystemStationCheck
        # I might need to mock this to avoid dependency issues or just let it run if simple.
        # Assuming simple for now.

    def tearDown(self):
        self.i18n_patch.stop()
        self.edtime_patch.stop()

    def test_station_service_check(self):
        checker = EDRStationServiceCheck('Interstellar Factors Contact')
        
        station = {'otherServices': ['Interstellar Factors Contact'], 'type': 'Ocellus Starport', 'distanceToArrival': 0}
        self.assertTrue(checker.check_station(station))
        
        station = {'otherServices': ['Market'], 'type': 'Ocellus Starport', 'distanceToArrival': 0}
        self.assertFalse(checker.check_station(station))

    def test_station_facility_check(self):
        checker = EDRStationFacilityCheck('Shipyard')
        
        station = {'haveShipyard': True, 'distanceToArrival': 0}
        self.assertTrue(checker.check_station(station))
        
        station = {'haveShipyard': False, 'distanceToArrival': 0}
        self.assertFalse(checker.check_station(station))

    def test_staging_check(self):
        checker = EDRStagingCheck(100)
        
        # Valid staging
        station = {
            'haveShipyard': True,
            'haveOutfitting': True,
            'otherServices': ['Restock', 'Refuel', 'Repair'],
            'type': 'Orbis Starport',
            'distanceToArrival': 0
        }
        self.assertTrue(checker.check_station(station))
        
        # Missing service
        station['otherServices'] = ['Restock', 'Refuel']
        self.assertFalse(checker.check_station(station))
        
        # Fleet Carrier (excluded)
        station['otherServices'] = ['Restock', 'Refuel', 'Repair']
        station['type'] = 'Fleet Carrier'
        self.assertFalse(checker.check_station(station))

    def test_station_rrr_check(self):
        checker = EDRStationRRRCheck(100, 1000)
        
        station = {
            'otherServices': ['Restock', 'Refuel', 'Repair'],
            'type': 'Outpost',
            'distanceToArrival': 0
        }
        self.assertTrue(checker.check_station(station))
        
        # Fleet Carrier excluded (there is a separate check for that)
        station['type'] = 'Fleet Carrier'
        self.assertFalse(checker.check_station(station))

    def test_fleet_carrier_rrr_check(self):
        checker = EDRFleetCarrierRRRCheck(100, 1000)
        
        station = {
            'otherServices': ['Restock', 'Refuel', 'Repair'],
            'type': 'Fleet Carrier',
            'distanceToArrival': 0
        }
        self.assertTrue(checker.check_station(station))
        
        station['type'] = 'Outpost'
        self.assertFalse(checker.check_station(station))

    def test_raw_trader_check(self):
        checker = EDRRawTraderCheck()
        
        # System check
        system = {
            'information': {
                'economy': 'Extraction', 
                'security': 'High', 
                'government': 'Democracy', 
                'population': 5000000
            }, 
            'distance': 0
        }
        self.assertTrue(checker.check_system(system))
        
        system = {
            'information': {
                'economy': 'High Tech',
                'security': 'High', 
                'government': 'Democracy', 
                'population': 5000000
            }, 
            'distance': 0
        }
        self.assertFalse(checker.check_system(system))

    def test_manufactured_trader_check(self):
        checker = EDRManufacturedTraderCheck()
        
        system = {
            'information': {
                'economy': 'Industrial',
                'security': 'High', 
                'government': 'Democracy', 
                'population': 5000000
            }, 
            'distance': 0
        }
        self.assertTrue(checker.check_system(system))

    def test_encoded_trader_check(self):
        checker = EDREncodedTraderCheck()
        
        system = {
            'information': {
                'economy': 'High Tech',
                'security': 'High', 
                'government': 'Democracy', 
                'population': 5000000
            }, 
            'distance': 0
        }
        self.assertTrue(checker.check_system(system))
        
        system = {
            'information': {
                'economy': 'Military',
                'security': 'High', 
                'government': 'Democracy', 
                'population': 5000000
            }, 
            'distance': 0
        }
        self.assertTrue(checker.check_system(system))

    def test_human_tech_broker_check(self):
        checker = EDRHumanTechBrokerCheck()
        
        system = {'information': {'economy': 'Industrial', 'population': 1000000}, 'distance': 0}
        self.assertTrue(checker.check_system(system))
        
        # Pop too low
        system = {'information': {'economy': 'Industrial', 'population': 500}, 'distance': 0}
        self.assertFalse(checker.check_system(system))

    def test_guardian_tech_broker_check(self):
        checker = EDRGuardianTechBrokerCheck()
        
        system = {'information': {'economy': 'High Tech', 'population': 1000000}, 'distance': 0}
        self.assertTrue(checker.check_system(system))

if __name__ == '__main__':
    unittest.main()
