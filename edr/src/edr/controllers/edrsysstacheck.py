class EDRSystemStationCheck:
    """
    Checks if a system or station meets specific criteria (distance, etc.).
    """

    def __init__(self):
        """
        Initialize the check with default distance thresholds.
        """
        self.max_distance = 50
        self.max_sc_distance = 1500
        self.name = None
        self.hint = None
        self.systems_counter = 0
        self.stations_counter = 0
        self.dlc_name = None

    def set_dlc(self, name):
        """
        Set the DLC name for compatibility checks.

        Args:
            name (str): The name of the DLC (e.g., "Odyssey").
        """
        self.dlc_name = name

    def check_system(self, system):
        """
        Check if a system is within the maximum distance.

        Args:
            system (dict): System info, must include 'distance'.

        Returns:
            bool: True if valid and within range, False otherwise.
        """
        self.systems_counter += 1
        if not system:
            return False

        if system.get('distance', None) is None:
            return False

        return system['distance'] <= self.max_distance

    def check_station(self, station):
        """
        Check if a station is valid and within the supercruise distance.

        Args:
            station (dict): Station info.

        Returns:
            bool: True if valid and accessible, False otherwise.
        """
        self.stations_counter += 1
        if not station:
            return False

        if station.get('distanceToArrival', None) is None:
            return False

        if "odyssey" in station.get("type", "").lower() and self.dlc_name != "Odyssey":
            return False
        return station['distanceToArrival'] < self.max_sc_distance

    def is_service_availability_ambiguous(self, station):
        """
        Check if service availability is ambiguous for the station.

        Args:
            station (dict): The station dict.

        Returns:
            bool: Always False (default implementation).
        """
        return False


class EDRApexSystemStationCheck(EDRSystemStationCheck):
    """
    Specialized check for Apex Shuttle operations (stricter limits).
    """

    def __init__(self, max_sc_distance=1500):
        """
        Initialize with custom or default supercruise max distance.

        Args:
            max_sc_distance (int): Max supercruise distance.
        """
        super().__init__()
        self.max_distance = 100
        self.max_sc_distance = max_sc_distance

    def check_station(self, station):
        """
        Check if a station is valid for Apex logic (specific starports only).

        Args:
            station (dict): Station info.

        Returns:
            bool: True if allowed type, False otherwise.
        """
        if not super().check_station(station):
            return False

        if not station.get('type', None):
            return False

        allowed_types = {
            "asteroid base", "bernal starport", "coriolis starport",
            "ocellus starport", "orbis starport", "bernal",
            "bernal statioport", "planetary port", "outpost",
            "planetary outpost"
        }

        return station.get('type', "n/a").lower() in allowed_types
