
import unittest
from edr.edrservicecheck import (
    EDRStationServiceCheck,
    EDRStationFacilityCheck,
    EDRStagingCheck,
    EDRRawTraderCheck,
    EDRBlackMarketCheck
)

class TestEDRServiceCheck(unittest.TestCase):
    def test_station_service_check(self):
        checker = EDRStationServiceCheck("Interstellar Factors Contact")
        # Station with the service
        station = {
            "otherServices": ["Refuel", "Interstellar Factors Contact"],
            "distanceToArrival": 100
        }
        self.assertTrue(checker.check_station(station))
        
        # Station without the service
        station_bad = {
            "otherServices": ["Refuel"],
            "distanceToArrival": 100
        }
        self.assertFalse(checker.check_station(station_bad))

    def test_station_facility_check(self):
        checker = EDRStationFacilityCheck("Shipyard")
        # Station with shipyard
        station = {
            "haveShipyard": True,
            "distanceToArrival": 100
        }
        self.assertTrue(checker.check_station(station))
        
        # Station without shipyard
        station_bad = {
            "haveShipyard": False,
            "distanceToArrival": 100
        }
        self.assertFalse(checker.check_station(station_bad))

    def test_staging_check(self):
        checker = EDRStagingCheck(max_distance=100)
        # Good staging system
        system = {"distance": 50}
        self.assertTrue(checker.check_system(system))
        
        # Too far
        system_bad = {"distance": 150}
        self.assertFalse(checker.check_system(system_bad))
        
        # Good station
        station = {
            "haveShipyard": True, 
            "haveOutfitting": True, 
            "otherServices": ["Restock", "Refuel", "Repair"],
            "distanceToArrival": 100
        }
        self.assertTrue(checker.check_station(station))

    def test_raw_trader_check(self):
        checker = EDRRawTraderCheck()
        # Good system
        system = {
            "information": {
                "security": "High",
                "government": "Democracy",
                "population": 10000000,
                "economy": "Extraction"
            },
            "distance": 10
        }
        self.assertTrue(checker.check_system(system))
        
        # Bad economy
        system_bad = {
            "information": {
                "security": "High",
                "government": "Democracy",
                "population": 10000000,
                "economy": "Tourism"
            },
            "distance": 10
        }
        self.assertFalse(checker.check_system(system_bad))

    def test_black_market_check(self):
        checker = EDRBlackMarketCheck()
        # Anarchy system (good for BM)
        system = {
            "information": {
                "security": "Anarchy",
                "government": "Anarchy"
            },
            "distance": 10
        }
        self.assertTrue(checker.check_system(system))
