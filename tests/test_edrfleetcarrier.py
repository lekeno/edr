import config_tests
from unittest import TestCase, main
from edrfleetcarrier import EDRFleetCarrier
import edtime

class TestEDRFleetCarrier(TestCase):
    def test_constructor(self):
        fc = EDRFleetCarrier()
        self.assertIsNone(fc.id)
        self.assertEqual(fc.type, "FleetCarrier")

    def test_bought(self):
        fc = EDRFleetCarrier()
        buy_event = {
            "CarrierID": 123,
            "Callsign": "K2V-1L",
            "Location": "Sol"
        }
        fc.bought(buy_event)
        self.assertEqual(fc.id, 123)
        self.assertEqual(fc.callsign, "K2V-1L")
        self.assertEqual(fc.position, "Sol")

    def test_update_from_location_or_docking(self):
        fc = EDRFleetCarrier()
        entry = {
            "event": "Docked",
            "StationType": "FleetCarrier",
            "MarketID": 123,
            "StationName": "K2V-1L",
            "Name": "My Carrier",
            "StarSystem": "Sol",
            "Body": "Earth"
        }
        self.assertTrue(fc.update_from_location_or_docking(entry))
        self.assertEqual(fc.id, 123)
        self.assertEqual(fc.callsign, "K2V-1L")
        self.assertEqual(fc.name, "My Carrier")
        self.assertEqual(fc.position, "Sol")
        self.assertEqual(fc._position["body"], "earth")

    def test_update_from_stats(self):
        fc = EDRFleetCarrier()
        stats_event = {
            "CarrierID": 123,
            "Callsign": "K2V-1L",
            "Name": "My Carrier",
            "DockingAccess": "all",
            "AllowNotorious": True,
            "FuelLevel": 100,
            "JumpRangeCurr": 500,
            "JumpRangeMax": 500,
            "PendingDecommission": False,
            "SpaceUsage": {"Total": 1000},
            "Finance": {"Balance": 10000},
            "Crew": [{"CrewRole": "Refuel", "Activated": True, "Enabled": True, "CrewName": "John Doe"}],
            "ShipPacks": {},
            "ModulePacks": {}
        }
        fc.update_from_stats(stats_event)
        self.assertEqual(fc.id, 123)
        self.assertEqual(fc.callsign, "K2V-1L")
        self.assertEqual(fc.name, "My Carrier")
        self.assertEqual(fc.access, "all")
        self.assertTrue(fc.allow_notorious)
        self.assertEqual(fc.fuel_level, 100)
        self.assertEqual(fc.jump_range_current, 500)
        self.assertEqual(fc.jump_range_max, 500)
        self.assertFalse(fc.decommission)
        self.assertEqual(fc.space_usage, {"Total": 1000})
        self.assertEqual(fc.finance, {"Balance": 10000})
        self.assertIn("refuel", fc.services)
        self.assertTrue(fc.services["refuel"]["active"])

    def test_jump_requested(self):
        fc = EDRFleetCarrier()
        fc.id = 123
        now = edtime.EDTime()
        jump_request_event = {
            "CarrierID": 123,
            "SystemName": "Alpha Centauri",
            "Body": "Proxima Centauri",
            "timestamp": now.as_journal_timestamp()
        }
        fc.jump_requested(jump_request_event)
        self.assertEqual(fc.departure["destination"], "Alpha Centauri")
        self.assertEqual(fc.departure["body"], "proxima centauri")
        self.assertAlmostEqual(fc.departure["time"], now.as_py_epoch() + 15 * 60, delta=1)

    def test_jump_cancelled(self):
        fc = EDRFleetCarrier()
        fc.id = 123
        now = edtime.EDTime()
        jump_request_event = {
            "CarrierID": 123,
            "SystemName": "Alpha Centauri",
            "Body": "Proxima Centauri",
            "timestamp": now.as_journal_timestamp()
        }
        fc.jump_requested(jump_request_event)
        self.assertIsNotNone(fc.departure["destination"])

        jump_cancel_event = {
            "CarrierID": 123
        }
        fc.jump_cancelled(jump_cancel_event)
        self.assertIsNone(fc.departure["destination"])

    def test_update_docking_permissions(self):
        fc = EDRFleetCarrier()
        fc.id = 123
        event = {
            "CarrierID": 123,
            "DockingAccess": "squadron",
            "AllowNotorious": False
        }
        fc.update_docking_permissions(event)
        self.assertEqual(fc.access, "squadron")
        self.assertFalse(fc.allow_notorious)

    def test_update_from_jump_if_relevant(self):
        fc = EDRFleetCarrier()
        fc.id = 123
        event = {
            "MarketID": 123,
            "StarSystem": "Sol",
            "Body": "Earth"
        }
        fc.update_from_jump_if_relevant(event)
        self.assertEqual(fc.position, "Sol")
        self.assertEqual(fc._position["body"], "earth")

    def test_update_star_system_if_relevant(self):
        fc = EDRFleetCarrier()
        self.assertTrue(fc.update_star_system_if_relevant("Sol", 123, "K2V-1L"))
        self.assertEqual(fc.id, 123)
        self.assertEqual(fc.callsign, "K2V-1L")
        self.assertEqual(fc.position, "Sol")

    def test_decommission(self):
        fc = EDRFleetCarrier()
        fc.id = 123
        scrap_time = edtime.EDTime()
        scrap_time.advance(1000)
        event = {
            "CarrierID": 123,
            "ScrapTime": scrap_time.as_py_epoch()
        }
        fc.decommission_requested(event)
        self.assertEqual(fc.decommission_time, scrap_time.as_py_epoch())
        fc.cancel_decommission({"CarrierID": 123})
        self.assertEqual(fc.decommission_time, scrap_time.as_py_epoch())


    def test_is_parked(self):
        fc = EDRFleetCarrier()
        self.assertTrue(fc.is_parked())
        fc.id = 123
        now = edtime.EDTime()
        jump_request_event = {
            "CarrierID": 123,
            "SystemName": "Alpha Centauri",
            "Body": "Proxima Centauri",
            "timestamp": now.as_journal_timestamp()
        }
        fc.jump_requested(jump_request_event)
        self.assertFalse(fc.is_parked())

    def test_is_open_to_all(self):
        fc = EDRFleetCarrier()
        self.assertFalse(fc.is_open_to_all())
        fc.access = "all"
        self.assertTrue(fc.is_open_to_all())
        fc.allow_notorious = True
        self.assertTrue(fc.is_open_to_all(include_notorious=True))

    def test_json_jump_schedule(self):
        fc = EDRFleetCarrier()
        self.assertIsNone(fc.json_jump_schedule())
        fc.id = 123
        now = edtime.EDTime()
        jump_request_event = {
            "CarrierID": 123,
            "SystemName": "Alpha Centauri",
            "Body": "Proxima Centauri",
            "timestamp": now.as_journal_timestamp()
        }
        fc.jump_requested(jump_request_event)
        json_schedule = fc.json_jump_schedule()
        self.assertIsNotNone(json_schedule)
        self.assertEqual(json_schedule["to"], "Alpha Centauri")

    def test_json_status(self):
        fc = EDRFleetCarrier()
        self.assertIsNone(fc.json_status())
        fc.id = 123
        fc.name = "My Carrier"
        fc.callsign = "K2V-1L"
        json_status = fc.json_status()
        self.assertIsNotNone(json_status)
        self.assertEqual(json_status["name"], "My Carrier")

if __name__ == '__main__':
    main()
