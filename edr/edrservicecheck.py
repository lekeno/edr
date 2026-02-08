
from edri18n import _, _c, _edr
from edrsysstacheck import EDRSystemStationCheck, EDRApexSystemStationCheck
from edtime import EDTime


class EDRStationServiceCheck(EDRSystemStationCheck):
    """
    Checks if a station has a specific service.
    """

    def __init__(self, service):
        """
        Initialize the check.

        Args:
            service (str): Service name to check for.
        """
        super().__init__()
        self.service = service
        self.name = service
        self.hint = None

    def check_station(self, station):
        """
        Check if station has the service.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if service is present.
        """
        if not super().check_station(station):
            return False

        if not station.get('otherServices', None):
            return False

        return self.service in station['otherServices']

    def is_service_availability_ambiguous(self, station):
        """
        Check if service availability might be ambiguous (e.g. Odyssey specifics).

        Args:
            station (dict): Station info.

        Returns:
            bool: True if ambiguous.
        """
        if "odyssey" in station.get("type", "").lower():
            # TODO possibly too strict? confirmed: IFactors
            return self.service not in ["Refuel", "Repair", "Contacts", "Missions"]
        if "planetary" in station.get("type", "").lower():
            # TODO not sure what's up but since Odyssey release, the planetary port/outpost don't seem to have I.Factors anymore :/
            return True
        return False


class EDRStationFacilityCheck(EDRSystemStationCheck):
    """
    Checks if a station has a specific facility (shipyard, market, outfitting).
    """
    def __init__(self, facility):
        """
        Initialize the check.

        Args:
            facility (str): Facility name ('shipyard', 'market', 'outfitting').
        """
        super().__init__()
        lut = {'shipyard': 'haveShipyard', 'market': 'haveMarket', 'outfitting': 'haveOutfitting'}
        self.has_facility = lut[facility.lower()] if facility.lower() in lut else None
        self.name = facility
        self.hint = None

    def check_station(self, station):
        """
        Check if station has the facility.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if facility is present.
        """
        if not super().check_station(station):
            return False

        if not self.has_facility:
            return True

        return station.get(self.has_facility, False)


class EDRStagingCheck(EDRSystemStationCheck):
    """
    Checks for a good staging station (Shipyard, Outfitting, RRR).
    """

    def __init__(self, max_distance):
        """
        Initialize the staging check.

        Args:
            max_distance (int): Max system distance.
        """
        super().__init__()
        self.max_distance = max_distance
        self.name = _("Staging station")
        self.hint = None

    def check_system(self, system):
        """
        Check if system is within range.

        Args:
            system (dict): System info.

        Returns:
            bool: True if inside range.
        """
        if not super().check_system(system):
            return False

        return system.get('distance', 1) >= 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        """
        Check if station meets staging criteria.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if it meets criteria.
        """
        if not super().check_station(station):
            return False

        if station.get("type", "") == "Fleet Carrier":
            return False

        if not station.get('otherServices', False):
            return False

        if not station.get('haveShipyard', False):
            return False

        if not station.get('haveOutfitting', False):
            return False

        if not (all(service in station['otherServices'] for service in ['Restock', 'Refuel', 'Repair'])):
            return False

        return True


class EDRStationRRRCheck(EDRSystemStationCheck):
    """
    Checks for stations with Repair/Rearm/Refuel services.
    """

    def __init__(self, max_distance, max_sc_distance):
        """
        Initialize the check.

        Args:
            max_distance (int): Max system distance.
            max_sc_distance (int): Max supercruise distance.
        """
        super().__init__()
        self.max_distance = max_distance
        self.max_sc_distance = max_sc_distance
        self.name = _("Station with Repair/Rearm/Refuel")
        self.hint = None
        self.threshold_seconds = 60*60*24*7

    def check_system(self, system):
        """
        Check if system is within range.

        Args:
            system (dict): System info.

        Returns:
            bool: True if inside range.
        """
        if not super().check_system(system):
            return False

        return system.get('distance', 1) >= 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        """
        Check if station has RRR services.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if RRR present.
        """
        if station.get("type", "") == "Fleet Carrier":
            return False

        if not super().check_station(station):
            return False

        if not (all(service in station['otherServices'] for service in ['Restock', 'Refuel', 'Repair'])):
            return False

        return True

    def is_service_availability_ambiguous(self, station):
        """
        Check if data is too old.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if data is ambiguous/old.
        """
        if not station.get('updateTime', None):
            return True

        if not station['updateTime'].get('information', None):
            return True

        updateTime = station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        return edt.older_than(self.threshold_seconds)


class EDRFleetCarrierRRRCheck(EDRSystemStationCheck):
    """
    Checks for fleet carriers with Repair/Rearm/Refuel services.
    """

    def __init__(self, max_distance, max_sc_distance):
        """
        Initialize the check.

        Args:
            max_distance (int): Max system distance.
            max_sc_distance (int): Max supercruise distance.
        """
        super().__init__()
        self.max_distance = max_distance
        self.max_sc_distance = max_sc_distance
        self.name = _("Fleet Carrier with Repair/Rearm/Refuel")
        self.hint = None
        self.threshold_seconds = 60*60*24*2

    def check_system(self, system):
        """
        Check if system is within range.

        Args:
            system (dict): System info.

        Returns:
            bool: True if inside range.
        """
        if not super().check_system(system):
            return False

        return system.get('distance', 1) >= 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        """
        Check if fleet carrier has RRR services.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if RRR present.
        """
        if station.get("type", "") != "Fleet Carrier":
            return False

        if not super().check_station(station):
            return False

        if not (all(service in station['otherServices'] for service in ['Restock', 'Refuel', 'Repair'])):
            return False

        return True

    def is_service_availability_ambiguous(self, station):
        """
        Check if data is too old.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if data is ambiguous/old.
        """
        if not station.get('updateTime', None):
            return True

        if not station['updateTime'].get('information', None):
            return True

        updateTime = station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        return edt.older_than(self.threshold_seconds)


class EDRMaterialTraderBasicCheck(EDRStationServiceCheck):
    """
    Base class for material trader checks.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__('Material Trader')

    def check_system(self, system):
        """
        Check if system meets criteria for a material trader (security, economy, population).

        Args:
            system (dict): System info.

        Returns:
            bool: True if criteria met.
        """
        if not super().check_system(system):
            return False

        if not system or not system.get('information', None):
            return False

        info = system['information']
        info['security'] = info.get('security', 'N/A')
        info['government'] = info.get('government', 'N/A')
        info['population'] = info.get('population', 0)

        if info['government'] == 'Anarchy' or info['security'].lower() not in ['high', 'medium']:
            return False

        if info['population'] < 1000000 or info['population'] > 22000000:
            return False

        if info['economy'].lower() not in ['extraction', 'refinery', 'industrial', 'high tech', 'military']:
            return False

        return True


class EDRRawTraderCheck(EDRMaterialTraderBasicCheck):
    """
    Checks for Raw Material Trader.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Raw material trader'
        self.hint = _("Found in systems with medium-high security, an 'extraction' or 'refinery' economy, a rather large population (>= 1 million)")

    def check_system(self, system):
        """
        Check if system has Extraction/Refinery economy.

        Args:
            system (dict): System info.

        Returns:
            bool: True if economy matches.
        """
        if system.get('name', '') in ['Kojeara']:
            return True

        if not super().check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')

        return info['economy'].lower() in ['extraction', 'refinery']


    def check_station(self, station):
        """
        Check station override.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if acceptable.
        """
        if station.get('name', '') in ["TolaGarf's Junkyard"]:
            return True
        return super().check_station(station)

    def is_service_availability_ambiguous(self, station):
        """
        Check ambiguity based on second economy.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if ambiguous.
        """
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['industrial', 'high tech', 'military']


class EDRManufacturedTraderCheck(EDRMaterialTraderBasicCheck):
    """
    Checks for Manufactured Material Trader.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Manufactured material trader'
        self.hint = _("Found in systems with medium-high security, an 'industrial' economy, and a rather large population (>= 1 million)")

    def check_system(self, system):
        """
        Check if system has Industrial economy.

        Args:
            system (dict): System info.

        Returns:
            bool: True if economy matches.
        """
        if system.get('name', '') in ['Coeus']:
            return True

        if not super().check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')

        return info['economy'].lower() == 'industrial'

    def check_station(self, station):
        """
        Check station override.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if acceptable.
        """
        if station.get('name', '') in ["Foster Terminal"]:
            return True
        return super().check_station(station)

    def is_service_availability_ambiguous(self, station):
        """
        Check ambiguity based on second economy.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if ambiguous.
        """
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['extraction', 'refinery', 'high tech', 'military']


class EDREncodedTraderCheck(EDRMaterialTraderBasicCheck):
    """
    Checks for Encoded Data Trader.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Encoded data trader'
        self.hint = _("Found in systems with medium-high security, a 'high tech' or 'military' economy, and a rather large population (>= 1 million)")

    def check_system(self, system):
        """
        Check if system has High Tech or Military economy.

        Args:
            system (dict): System info.

        Returns:
            bool: True if economy matches.
        """
        if system.get('name', '') in ['Ratraii']:
            return True

        if not super().check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')

        return info['economy'].lower() in ['high tech', 'military']

    def check_station(self, station):
        """
        Check station override.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if acceptable.
        """
        if station.get('name', '') in ["Colonia Dream"]:
            return True
        return super().check_station(station)

    def is_service_availability_ambiguous(self, station):
        """
        Check ambiguity based on second economy.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if ambiguous.
        """
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['extraction', 'refinery', 'industrial']


class EDRBlackMarketCheck(EDRStationServiceCheck):
    """
    Checks for Black Market service.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__('Black Market')

    def check_system(self, system):
        """
        Check if system likely has a Black Market (Anarchy or Low Security).

        Args:
            system (dict): System info.

        Returns:
            bool: True if criteria met.
        """
        if not super().check_system(system):
            return False

        if not system or not system.get('information', None):
            return False

        if not system.get('information', None):
            return False

        info = system['information']
        info['security'] = info.get('security', 'N/A')
        info['government'] = info.get('government', 'N/A')

        if info['government'] == 'Anarchy':
            return True

        if info['security'].lower() == 'low':
            return True

        return False


class EDRHumanTechBrokerCheck(EDRStationServiceCheck):
    """
    Checks for Human Technology Broker.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__('Technology Broker')
        self.name = _('Human Technology Broker')
        self.hint = _("Found in systems with an 'Industrial' economy', and a rather large population (>= 1 million)")

    def check_system(self, system):
        """
        Check if system meets criteria for Human Tech Broker.

        Args:
            system (dict): System info.

        Returns:
            bool: True if criteria met.
        """
        if system.get('name', '') in ['Tir']:
            return True

        if not super().check_system(system):
            return False

        if not system.get('information', None):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        info['population'] = info.get('population', 0)

        if info['population'] < 1000000:
            return False

        return info['economy'].lower() == 'industrial'

    def check_station(self, station):
        """
        Check station override.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if acceptable.
        """
        if station.get('name', '') in ["Bolden's Enterprise"]:
            return True
        return super().check_station(station)

    def is_service_availability_ambiguous(self, station):
        """
        Check ambiguity based on second economy.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if ambiguous.
        """
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['high tech']


class EDRGuardianTechBrokerCheck(EDRStationServiceCheck):
    """
    Checks for Guardian Technology Broker.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__('Technology Broker')
        self.name = _('Guardian Technology Broker')
        self.hint = _("Found in systems with a 'high tech' economy', and a rather large population (>= 1 million)")

    def check_system(self, system):
        """
        Check if system meets criteria for Guardian Tech Broker.

        Args:
            system (dict): System info.

        Returns:
            bool: True if criteria met.
        """
        if system.get('name', '') in ['Colonia']:
            return True

        if not super().check_system(system):
            return False

        if not system.get('information', None):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        info['population'] = info.get('population', 0)

        if info['population'] < 1000000:
            return False

        return info['economy'].lower() == 'high tech'

    def check_station(self, station):
        """
        Check station override.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if acceptable.
        """
        if station.get('name', '') in ["Jaques Station"]:
            return True
        return super().check_station(station)

    def is_service_availability_ambiguous(self, station):
        """
        Check ambiguity based on second economy.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if ambiguous.
        """
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['industrial']


class EDROffBeatStationCheck(EDRApexSystemStationCheck):
    """
    Checks for offbeat stations (low traffic, not visited recently).
    """

    def __init__(self, max_distance_sc=100000):
        """
        Initialize the check.

        Args:
            max_distance_sc (int): Max supercruise distance.
        """
        super().__init__(max_distance_sc or 100000)
        self.name = _("Offbeat station")
        self.hint = _("Look for low traffic systems with stations that haven't been visited in a while.")
        self.threshold_seconds = 60*60*24*14

    def check_system(self, system):
        """
        Check if system is within range.

        Args:
            system (dict): System info.

        Returns:
            bool: True if inside range.
        """
        if not super().check_system(system):
            return False

        return system.get('distance', 0) > 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        """
        Check if station data is old enough.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if station matches criteria.
        """
        if not super().check_station(station):
            return False

        if not station.get('updateTime', None):
            return True

        if not station['updateTime'].get('information', None):
            return True

        updateTime = station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        return edt.older_than(self.threshold_seconds)

    def is_service_availability_ambiguous(self, station):
        """
        Check for close calls on staleness.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if ambiguous/close call.
        """
        if not station.get('updateTime', None):
            return False

        if not station['updateTime'].get('information', None):
            return False

        updateTime = station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        if not edt.older_than(self.threshold_seconds):
            return True
        close_call = not edt.older_than(self.threshold_seconds*1.25)
        return close_call
