import threading
import csv
import pickle
import requests
from urllib.parse import urlparse
import json
from os import path
from math import sqrt
import re

from edr.core.edri18n import _ # EDR_INTERNAL
from edr.utils.edtime import EDTime # EDR_INTERNAL
from edr.utils.edrpath import edr_cache_path # EDR_INTERNAL
from collections import deque
from edr.utils.edrutils import pretty_print_number, simplified_body_name # EDR_INTERNAL
from edr.core.edrconfig import EDR_CONFIG # EDR_INTERNAL

from edr.core.edrlog import EDR_LOG # EDR_INTERNAL


class BidiWaypointIterator:
    """
    A bidirectional iterator for a collection of waypoints.
    """

    def __init__(self, collection):
        """
        Initialize the bidirectional waypoint iterator.

        Args:
            collection (list): The list of waypoints to iterate over.
        """
        self.collection = collection
        self.current = collection[0] if collection else None
        self.index = 0

    def __next__(self):
        """
        Get the next waypoint in the collection.

        Returns:
            dict: The next waypoint, or None if at the end.
        """
        if self.collection is None:
            return None
        try:
            self.index += 1
            if self.index >= len(self.collection):
                raise StopIteration
            self.current = self.collection[self.index]
        except StopIteration:
            self.index = len(self.collection)
            self.current = None
        finally:
            return self.current

    def previous(self):
        """
        Get the previous waypoint in the collection.

        Returns:
            dict: The previous waypoint, or None if at the beginning.
        """
        if self.collection is None:
            return None
        try:
            self.index -= 1
            if self.index < 0:
                raise StopIteration
            self.current = self.collection[self.index]
        except StopIteration:
            self.index = -1
            self.current = None
        finally:
            return self.current

    def empty(self):
        """
        Check if the collection is empty.

        Returns:
            bool: True if empty, False otherwise.
        """
        return not self.collection

    def current_wp_sysname(self):
        """
        Get the system name of the current waypoint.

        Returns:
            str: The name of the star system.
        """
        return self.get_system_name(self.current)

    @staticmethod
    def get_system_name(waypoint):
        """
        Extract the system name from a waypoint dictionary.

        Args:
            waypoint (dict): The waypoint info.

        Returns:
            str: The star system name, or "???" if not found.
        """
        if not waypoint:
            return

        if "StarSystem" in waypoint:
            return waypoint["StarSystem"]

        if "system" in waypoint:
            return waypoint["system"]

        if "name" in waypoint:
            return waypoint["name"]

        return _("???")

    def includes(self, system_name):
        """
        Check if a system name is included in the waypoints.

        Args:
            system_name (str): The name of the system to check.

        Returns:
            bool: True if included, False otherwise.
        """
        if not self.collection:
            return False

        return any([self.get_system_name(waypoint) == system_name for waypoint in self.collection[self.index:]]) or any([self.get_system_name(waypoint) == system_name for waypoint in self.collection[:self.index]])

    def get(self, system_name):
        """
        Get a waypoint by its system name.

        Args:
            system_name (str): The name of the system to find.

        Returns:
            dict: The waypoint matching the system name, or None.
        """
        if not self.collection or not system_name:
            return

        result = None
        for wp in self.collection:
            name = self.get_system_name(wp)
            cname = name.lower() if name else None
            csystem_name = system_name.lower()
            if cname == csystem_name:
                result = wp
                break

        return result
        

class SpanshServer(threading.Thread):
    """
    Interface for interacting with the Spansh API to retrieve routes.
    """
    SPANSH_URL = "https://spansh.co.uk"
    SESSION = requests.Session()

    def __init__(self, url, callback):
        """
        Initialize the Spansh server interface.

        Args:
            url (str): The URL of the Spansh results page.
            callback (function): The callback to trigger when route retrieval is complete.
        """
        super().__init__()
        self.api_path = f"{self.SPANSH_URL}/api/results/"
        self.callback = callback
        self.url = url

    def run(self):
        """
        Execute the route retrieval thread.
        """
        result = self.__get_route()
        if self.callback:
            self.callback(result)

    @staticmethod
    def get_url(source, destination, jump_range, genre):
        """
        Construct a Spansh results URL.

        Args:
            source (str): The starting star system.
            destination (str): The destination star system.
            jump_range (float): The jump range of the ship.
            genre (str): The type of plotter to use (e.g., "plotter", "riches").

        Returns:
            str: The constructed URL.
        """
        genre = genre or "plotter"
        url = f"{SpanshServer.SPANSH_URL}/{genre}/results/auto?"
        if source:
            url += f"from={source.capitalize()}"

        if destination:
            url += f"&to={destination.capitalize()}"

        if jump_range:
            url += f"&range={jump_range}"

        return url

    @staticmethod
    def recognized_url(url):
        """
        Check if a URL is a recognized Spansh results URL.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if recognized, False otherwise.
        """
        spansh_regexp = r"^https:\/\/(?:www\.)?spansh\.co\.uk\/(plotter|riches|ammonia|earth|exact-plotter|exobiology|fleet-carrier|tourist)\/results\/.*$"
        return bool(re.match(spansh_regexp, url))

    def __get_route(self):
        """
        Internal method to retrieve and parse the route from Spansh.

        Returns:
            GenericRoute: An instance of a journey class, or None.
        """
        if not self.url or not self.recognized_url(self.url):
            return None

        parsed_url = urlparse(self.url)
        job_id, _ = path.splitext(path.basename(parsed_url.path))
        data = self.__get_job(job_id)
        if not data:
            return None
        if "plotter" in parsed_url.path:
            return SpanshPlotterJourneyJSON(data)
        elif any([x in parsed_url.path for x in ["riches", "ammonia", "earth"]]):
            return SpanshBodiesJourneyJSON(data)
        elif "exact-plotter" in parsed_url.path:
            return SpanshExactPlotterJourneyJSON(data)
        elif "exobiology" in parsed_url.path:
            return SpanshExobiologyJourneyJSON(data)
        elif "fleet-carrier" in parsed_url.path:
            # TODO fleet carrier failed
            return SpanshFleetCarrierJourneyJSON(data)
        elif "tourist" in parsed_url.path:
            return SpanshTouristJourneyJSON(data)
        # elif "trade" in parsed_url.path:
        #    return SpanshTradeJourneyJSON(data)
        return None

    def __get_job(self, job_id):
        """
        Retrieve job results from the Spansh API.

        Args:
            job_id (str): The job ID to retrieve.

        Returns:
            dict: The job result data, or None.
        """
        url = self.api_path + job_id
        response = SpanshServer.SESSION.get(url)
        if response.status_code != 200:
            EDR_LOG.debug(f"SpanshServer status not 200 OK: {response.status_code}")
            return None

        data = json.loads(response.content)
        if not data:
            EDR_LOG.debug("SpanshServer returned no data")
            return None
        return data.get("result", None)

    def close(self):
        """
        Close the Spansh server interface (no-op).

        Returns:
            None: Always returns None.
        """
        return None

class GenericRoute:
    """
    A generic route base class for journeys.
    """

    def __init__(self):
        """
        Initialize the generic route.
        """
        self.journey_type = "generic"
        self.waypoints = None
        self.destination = None
        self.start = None
        self.total_jumps = None
        self.total_waypoints = None
        self.position = None
        self.distance = None

    def current(self):
        """
        Get the current waypoint.

        Returns:
            dict: The current waypoint, or None.
        """
        if self.waypoints:
            return self.waypoints.current
        return None

    def current_wp_sysname(self):
        """
        Get the system name of the current waypoint.

        Returns:
            str: The star system name.
        """
        if not self.waypoints:
            return None

        return self.waypoints.current_wp_sysname()

    def reached_wp(self):
        """
        Mark the current waypoint as reached.
        """
        if self.waypoints:
            self.position = self.waypoints.current

    def next(self):
        """
        Move to the next waypoint.

        Returns:
            dict: The next waypoint, or None.
        """
        if self.waypoints:
            return next(self.waypoints)
        return None

    def previous(self):
        """
        Move to the previous waypoint.

        Returns:
            dict: The previous waypoint, or None.
        """
        if self.waypoints:
            return self.waypoints.previous()
        return None

    def empty(self):
        """
        Check if the route is empty.

        Returns:
            bool: True if empty, False otherwise.
        """
        return self.waypoints is None

    def describe(self):
        """
        Provide a description of the route.

        Returns:
            list: A list of description fragments.
        """
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))

        if self.distance:
            details.append(_("Distance: {} LY").format(int(self.distance)))

        if self.total_waypoints:
            wp_progress = self.waypoints.index+1 if self.waypoints else 0
            details.append(_("{}/{} waypoints").format(wp_progress, self.total_waypoints))

        if self.total_jumps and self.total_jumps != self.total_waypoints:
            # TODO progress on jumps
            details.append(_("{} jumps").format(self.total_jumps))

        return details

    def is_waypoint(self, system_name):
        """
        Check if a star system is a waypoint in this route.

        Args:
            system_name (str): The name of the system to check.

        Returns:
            bool: True if it's a waypoint, False otherwise.
        """
        if not self.waypoints:
            return False

        return self.waypoints.includes(system_name)

    def describe_wp(self, source_coords=None):
        """
        Provide a description of the current waypoint.

        Args:
            source_coords (dict): Optional source coordinates (x, y, z).

        Returns:
            list: A list of description fragments.
        """
        current_wp = self.current()
        if not current_wp:
            return None

        details = []
        details.append(BidiWaypointIterator.get_system_name(current_wp))
        dest_coords = self._get_coords(current_wp)
        if source_coords and all([coord in dest_coords for coord in ["x", "y", "z"]]) and all([coord in source_coords for coord in ["x", "y", "z"]]):
            distance = sqrt((dest_coords["x"] - source_coords["x"])**2 + (dest_coords["y"] - source_coords["y"])**2 + (dest_coords["z"] - source_coords["z"])**2)
            details = []
            if distance:
                details.append(_("WP#{}/{}: {} @ {} LY").format(self.waypoints.index+1, self.total_waypoints or "?", BidiWaypointIterator.get_system_name(current_wp), int(distance)))
            else:
                details.append(_("WP#{}/{}: [here]").format(self.waypoints.index+1, self.total_waypoints or "?"))
        else:
            details.append(_("WP#{}/{}: {}").format(self.waypoints.index+1, self.total_waypoints or "?", BidiWaypointIterator.get_system_name(current_wp)))
        return details

    def describe_wp_bodies(self):
        """
        Provide a description of bodies at the current waypoint (no-op).

        Returns:
            None: Always returns None.
        """
        return None

    def wp_bodies_to_survey(self, star_system):
        """
        Get bodies to survey at the current star system (no-op).

        Args:
            star_system (str): The name of the star system.

        Returns:
            None: Always returns None.
        """
        return None

    def noteworthy_about_body(self, star_system, body_name):
        """
        Get noteworthy info about a body (no-op).

        Args:
            star_system (str): The name of the star system.
            body_name (str): The name of the body.

        Returns:
            None: Always returns None.
        """
        return None

    def leave_body(self, star_system, body_name):
        """
        Mark a body as left (no-op).

        Returns:
            bool: Always returns True.
        """
        return True

    def check_body(self, star_system, body_name):
        """
        Mark a body as checked (no-op).

        Returns:
            bool: Always returns True.
        """
        return True

    def surveyed_body(self, star_system, body_name):
        """
        Mark a body as surveyed (no-op).

        Returns:
            bool: Always returns True.
        """
        return True

    def mapped_body(self, star_system, body_name):
        """
        Mark a body as mapped (no-op).

        Returns:
            bool: Always returns True.
        """
        return True

    def current_wp_surveyed(self):
        """
        Check if the current waypoint is fully surveyed.

        Returns:
            bool: Always returns True.
        """
        return True

    def remaining_waypoints(self):
        """
        Calculate remaining waypoints in the journey.

        Returns:
            int: The number of remaining waypoints.
        """
        if not self.waypoints or not self.total_waypoints:
            return None

        return self.total_waypoints - self.waypoints.index+1

    @staticmethod
    def _get_coords(waypoint):
        """
        Extract coordinates from a waypoint.

        Args:
            waypoint (dict): The waypoint data.

        Returns:
            dict: Coordinates {x, y, z} or None.
        """
        if not waypoint:
            return

        if all([coord in waypoint for coord in ["x", "y", "z"]]):
            return {k: waypoint[k] for k in waypoint.keys() & {'x', 'y', 'z'}}

        return None

class EDRNavRoute:
    """
    Interface for handling in-game NavRoutes.
    """

    def __init__(self, navroute):
        """
        Initialize the EDR NavRoute interface.

        Args:
            navroute (dict): The NavRoute journal event data.
        """
        self.jumps = BidiWaypointIterator(navroute.get("Route", None))
        self.total_jumps = len(navroute.get("Route", ["dummy"]))-1
        self.total_waypoints = self.total_jumps
        self.position = None
        if self.jumps:
            self.start = self.jumps.collection[0] if self.jumps.collection else None
            self.destination = self.jumps.collection[-1] if self.jumps.collection else None
            if (self.start and "StarPos" in self.start) and (self.destination and "StarPos" in self.destination):
                s_pos = self.start["StarPos"]
                e_pos = self.destination["StarPos"]
                self.distance = sqrt((s_pos[0] - e_pos[0])**2 + (s_pos[1] - e_pos[1])**2 + (s_pos[1] - e_pos[1])**2)

        self.jumps_threshold_min = EDR_CONFIG.navroute_jumps_threshold_to_show()
        self.jumps_threshold_max = EDR_CONFIG.navroute_jumps_threshold_to_give_up()
    
    def empty(self):
        """
        Check if the NavRoute is empty.

        Returns:
            bool: True if empty, False otherwise.
        """
        return self.jumps is None or self.total_jumps == 0

    
    def trivial(self):
        """
        Check if the NavRoute is too short/trivial to display.

        Returns:
            bool: True if trivial, False otherwise.
        """
        return self.empty() or self.total_jumps < self.jumps_threshold_min

    def too_complex(self):
        """
        Check if the NavRoute is too long/complex for EDR to track.

        Returns:
            bool: True if too complex, False otherwise.
        """
        return not self.empty() and self.total_jumps > self.jumps_threshold_max

    def next(self):
        """
        Move to the next jump in the route.

        Returns:
            dict: The next jump waypoint, or None.
        """
        if self.jumps:
            return next(self.jumps)
        return None

    def previous(self):
        """
        Move to the previous jump in the route.

        Returns:
            dict: The previous jump waypoint, or None.
        """
        if self.jumps:
            return self.jumps.previous()
        return None


    def update(self, current_system):
        """
        Update the NavRoute tracking with the current star system.

        Args:
            current_system (str): The name of the current star system.

        Returns:
            bool: True if updated to next waypoint, False otherwise.
        """
        if not self.jumps:
            return False

        if current_system == self.jumps.current_wp_sysname():
            self.position = self.jumps.current
            next_wp = next(self.jumps)
            return next_wp is not None
        return False


    def describe(self):
        """
        Provide a description of the NavRoute.

        Returns:
            list: A list of description fragments.
        """
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))
        if self.distance and self.total_jumps:
            details.append(_("Distance: {distance} LY; {jumps} jumps").format(distance=int(self.distance), jumps=self.total_jumps))

        return details

    def remaining_waypoints(self):
        """
        Calculate remaining jumps in the NavRoute.

        Returns:
            int: The number of remaining jumps.
        """
        if not self.jumps or not self.total_waypoints:
            return None

        return self.total_waypoints - self.jumps.index+1

class SpanshPlotterJourneyJSON(GenericRoute):
    """
    A journey based on Spansh Plotter JSON data.
    """

    def __init__(self, data):
        """
        Initialize the Spansh Plotter journey.

        Args:
            data (dict): The route data from Spansh.
        """
        super().__init__()
        self.journey_type = "plotter"
        self.waypoints = BidiWaypointIterator(data.get("system_jumps", None))
        self.destination_name = data.get("destination_system", None)
        self.destination = self.waypoints.collection[-1]
        self.via = data.get("via", None)
        self.start = data.get("source_system", None)
        self.efficiency = data.get("efficiency", None)
        self.range = data.get("range", None)
        self.distance = data.get("distance", None)
        self.total_jumps = data.get("total_jumps", None)
        self.total_waypoints = len(self.waypoints.collection) if self.waypoints.collection else 0

    def describe(self):
        """
        Provide a description of the Spansh Plotter journey.

        Returns:
            list: A list of description fragments.
        """
        details = []
        details.append(_("From {} to {}").format(self.start, self.destination_name))
        if self.via:
            details.append(_("From {} to {} (via {})").format(self.start, self.destination_name, ", ".join(self.via)))

        wp_progress = self.waypoints.index+1 if self.waypoints else 0
        if self.total_jumps and self.total_jumps != self.total_waypoints:
            details.append(_("Distance: {distance} LY; {wp_prog}/{wp_total} waypoints, {jumps} jumps").format(distance=int(self.distance), wp_prog=wp_progress, wp_total=self.total_waypoints, jumps=self.total_jumps))
        else:
            details.append(_("Distance: {distance} LY; {wp_prog}/{wp_total} waypoints").format(distance=int(self.distance), wp_prog=wp_progress, wp_total=self.total_waypoints))
        details.append(_("Range: {range} LY @ {eff}pct efficiency").format(range=self.range, eff=self.efficiency))
        return details

class SpanshBodiesJourneyJSON(GenericRoute):
    """
    A journey based on Spansh bodies (Riches, Ammonia, Earth) JSON data.
    """

    def __init__(self, data):
        """
        Initialize the Spansh bodies journey.

        Args:
            data (list): The list of waypoints and bodies from Spansh.
        """
        super().__init__()
        self.journey_type = "bodies"
        self.waypoints = BidiWaypointIterator(data)
        self.start = self.waypoints.collection[0]["name"] if self.waypoints.collection and "name" in self.waypoints.collection[0] else None
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.destination_name = self.waypoints.collection[-1]["name"] if self.waypoints.collection and "name" in self.waypoints.collection[-1] else None
        self.total_waypoints = len(self.waypoints.collection)
        # TODO total jumps by iterating on waypoints for "jumps"
        self.total_bodies = sum([len(waypoint.get("bodies", [])) for waypoint in self.waypoints.collection])

    def describe(self):
        """
        Provide a description of the Spansh bodies journey.

        Returns:
            list: A list of description fragments.
        """
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))

        if self.total_waypoints:
            wp_progress = self.waypoints.index+1 if self.waypoints else 0
            # TODO also do body progress?
            if self.total_bodies:
                details.append(_("{wp_prog}/{wp_total} waypoints; {bodies} bodies").format(wp_prog=wp_progress, wp_total=self.total_waypoints, bodies=self.total_bodies))
            else:
                details.append(_("{wp_prog}/{wp_total} waypoints").format(wp_prog=wp_progress, wp_total=self.total_waypoints))

        return details

    def describe_wp_baseline(self, source_coords=None):
        """
        Call the baseline waypoint description.

        Args:
            source_coords (dict): Optional source coordinates.

        Returns:
            list: Description fragments.
        """
        return super().describe_wp(source_coords)

    def describe_wp(self, source_coords=None):
        """
        Provide a description of the current waypoint, including bodies to check.

        Args:
            source_coords (dict): Optional source coordinates.

        Returns:
            list: A list of description fragments.
        """
        details = self.describe_wp_baseline(source_coords)
        current_wp = self.current()
        if not current_wp or "bodies" not in current_wp:
            return False

        activities = set()
        value = 0
        remaining_bodies = []
        for b in current_wp["bodies"]:
            if b.get("checked", False):
                continue

            remaining_bodies.append(b)

            if b.get("estimated_scan_value", None):
                activities.add(_("scan"))
                value += b["estimated_scan_value"]

            if b.get("estimated_mapping_value", None):
                activities.add(_("map"))
                value += b["estimated_mapping_value"]

            if b.get("landmark_value", None):
                activities.add(_("survey"))
                value += b["landmark_value"]

        if not remaining_bodies:
            return details

        if activities:
            if len(remaining_bodies) > 1:
                details.append(_("{nb} bodies to check; {act} for ~{val} cr").format(nb=len(remaining_bodies), act=" + ".join(activities), val=pretty_print_number(value)))
            else:
                details.append(_("1 body to check; {act} for ~{val} cr").format(act=" + ".join(activities), val=pretty_print_number(value)))
        else:
            if len(remaining_bodies) > 1:
                details.append(_("{nb} bodies to check").format(nb=len(current_wp["bodies"])))
            else:
                details.append(_("1 body to check").format(nb=len(current_wp["bodies"])))
            details.append(_("Send '!journey bodies' to see the list of bodies to check"))

        return details

    def update(self, current_system):
        """
        Update the journey tracking with the current star system.

        Args:
            current_system (str): The name of the current star system.

        Returns:
            bool: True if updated to next waypoint, False otherwise.
        """
        if not self.jumps:
            return False

        if current_system == self.jumps.current_wp_sysname():
            self.position = self.jumps.current
            if self.current_wp_surveyed():
                next_wp = next(self.jumps)
                return next_wp is not None
            else:
                return False
        return False

    def noteworthy_about_body(self, star_system, body_name):
        """
        Get noteworthy info about a body in the journey.

        Args:
            star_system (str): The name of the star system.
            body_name (str): The name of the body.

        Returns:
            list: Description fragments.
        """
        wp = self.current()
        if star_system:
            wp = self.waypoints.get(star_system)

        if not wp:
            return

        return self.__describe_wp_body(wp, body_name)

    def leave_body(self, star_system, body_name):
        """
        Mark a body as visited/left.

        Args:
            star_system (str): The name of the star system.
            body_name (str): The name of the body.

        Returns:
            bool: True if marking was successful.
        """
        wp = self.current()
        if star_system:
            wp = self.waypoints.get(star_system)

        if not wp or not body_name:
            return

        return self.__mark_body_as_checked(wp, body_name)

    def check_body(self, star_system, body_name):
        """
        Check if a body matches one in the journey and mark it as checked.

        Args:
            star_system (str): The name of the star system.
            body_name (str): The name of the body.

        Returns:
            bool: True if marking was successful.
        """
        wp = self.current()
        if star_system:
            wp = self.waypoints.get(star_system)

        if not wp or not body_name:
            return

        return self.__mark_body_as_checked(wp, star_system, body_name)

    def surveyed_body(self, star_system, body_name):
        """
        Mark a body as surveyed.

        Args:
            star_system (str): Star system name.
            body_name (str): Body name.

        Returns:
            bool: True if successful.
        """
        return self.check_body(star_system, body_name)

    def mapped_body(self, star_system, body_name):
        """
        Mark a body as mapped.

        Args:
            star_system (str): Star system name.
            body_name (str): Body name.

        Returns:
            bool: True if successful.
        """
        return self.check_body(star_system, body_name)

    def __mark_body_as_checked(self, wp, star_system, body_name):
        """
        Internal method to mark a body as checked in a waypoint.

        Args:
            wp (dict): The waypoint data.
            star_system (str): The star system name.
            body_name (str): The body name.

        Returns:
            bool: True if updated.
        """
        if not wp or "bodies" not in wp:
            return False

        updated = False
        for b in wp["bodies"]:
            full_body_name = b.get("name", "?")
            simple_body_name = simplified_body_name(star_system, full_body_name)
            if body_name.lower() not in [simple_body_name.lower(), full_body_name.lower()]:
                continue

            b["checked"] = True
            updated = True
            break

        return updated

    def current_wp_surveyed(self):
        """
        Check if all bodies at the current waypoint have been surveyed/checked.

        Returns:
            bool: True if all bodies are checked.
        """
        wp = self.current()

        if not wp:
            return False

        surveyed = True
        for b in wp["bodies"]:
            if b.get("checked", False) == False:
                surveyed = False
                break

        return surveyed

    def describe_wp_bodies(self):
        """
        Provide a list of bodies to check at the current waypoint.

        Returns:
            list: Description fragments for each body.
        """
        current_wp = self.current()
        if not current_wp or "bodies" not in current_wp:
            return

        details = []
        for b in current_wp["bodies"]:
            if b.get("checked", False):
                continue

            value = 0
            activities = set()
            if b.get("estimated_scan_value", None):
                activities.add(_("scan"))
                value += b["estimated_scan_value"]

            if b.get("estimated_mapping_value", None):
                activities.add(_("map"))
                value += b["estimated_mapping_value"]

            if b.get("landmark_value", None):
                activities.add(_("survey"))
                value += b["landmark_value"]

            if value and b.get("name", None):
                simple_body_name = simplified_body_name(self.current_wp_sysname(), b["name"])
                details.append(_("{body}: {val} cr ({act})").format(body=simple_body_name, val=pretty_print_number(value), act=" + ".join(activities)))

        return details

    def wp_bodies_to_survey(self, star_system):
        """
        Get a list of simplified body names to survey at a system.

        Args:
            star_system (str): The name of the star system.

        Returns:
            list: Simplified body names.
        """
        current_wp = self.current()
        if not current_wp or "bodies" not in current_wp:
            return None

        current_wp_sys_name = self.current_wp_sysname()
        if star_system and current_wp_sys_name and not (star_system.lower() == current_wp_sys_name.lower()):
            return None

        remaining_bodies = []
        for b in current_wp["bodies"]:
            if b.get("checked", False):
                continue

            if b.get("name", None):
                simple_body_name = simplified_body_name(self.current_wp_sysname(), b["name"])
                remaining_bodies.append(simple_body_name)

        return remaining_bodies

    def __describe_wp_body(self, wp, body_name):
        """
        Internal method to describe a specific body in a waypoint.

        Args:
            wp (dict): The waypoint data.
            body_name (str): The body name.

        Returns:
            list: Description fragments.
        """
        if not wp or "bodies" not in wp:
            return

        details = []
        value = 0
        activities = set()
        for b in wp["bodies"]:
            if b.get("name", None) != body_name:
                continue

            if b.get("estimated_scan_value", None):
                activities.add(_("scan"))
                value += b["estimated_scan_value"]

            if b.get("estimated_mapping_value", None):
                activities.add(_("map"))
                value += b["estimated_mapping_value"]

            if b.get("landmark_value", None):
                activities.add(_("survey"))
                value += b["landmark_value"]

            break

        distance = pretty_print_number(b["distance_to_arrival"]) if "distance_to_arrival" in b else None
        sys_name = BidiWaypointIterator.get_system_name(wp)
        simple_body_name = simplified_body_name(sys_name, b["name"])
        oneliner = f"{simple_body_name}: "
        if value:
            oneliner += _("{val} cr ({act}) ").format(val=pretty_print_number(value), act=" + ".join(activities))

        if distance:
            oneliner += _("@ {dist} LY").format(dist=distance)

        details.append(oneliner)

        return details

class SpanshExactPlotterJourneyJSON(GenericRoute):
    """
    A journey based on Spansh Exact Plotter JSON data.
    """

    def __init__(self, data):
        """
        Initialize the Spansh Exact Plotter journey.

        Args:
            data (dict): The route data from Spansh.
        """
        super().__init__()
        self.journey_type = "exact-plotter"
        self.destination_name = data.get("destination", None)
        self.start = data.get("source", None)
        self.algorithm = data.get("algorithm", None)
        self.tank_size = data.get("tank_size", 0)
        self.use_injections = data.get("use_injections", False)
        self.use_supercharge = data.get("use_supercharge", False)
        self.base_mass = data.get("base_mass", 0)
        self.cargo = data.get("cargo", 0)
        self.fuel_multiplier = data.get("fuel_multiplier", 0)
        self.fuel_power = data.get("fuel_power", 0)
        self.internal_tank_size = data.get("internal_tank_size", 0)
        self.is_supercharged = data.get("is_supercharged", 0)
        self.max_fuel_per_jump = data.get("max_fuel_per_jump", 0)
        self.max_time = data.get("max_time", 0)
        self.optimal_mass = data.get("optimal_mass", 0)
        self.range_boost = data.get("range_boost", 0)
        self.ship_build = data.get("ship_build", 0)
        self.waypoints = BidiWaypointIterator(data.get("jumps", None))
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.total_waypoints = len(self.waypoints.collection)
        
class SpanshExobiologyJourneyJSON(SpanshBodiesJourneyJSON):
    """
    A journey based on Spansh Exobiology JSON data.
    """

    def __init__(self, data):
        """
        Initialize the Spansh Exobiology journey.

        Args:
            data (dict): The route data from Spansh.
        """
        super().__init__(data)
        self.journey_type = "exobiology"

    def describe_wp(self, source_coords=None):
        """
        Provide a description of the current waypoint for exobiology.

        Args:
            source_coords (dict): Optional source coordinates.

        Returns:
            list: Description fragments.
        """
        details = super().describe_wp_baseline(source_coords)
        current_wp = self.current()
        if "bodies" in current_wp:
            body_names = []
            value = 0
            for b in current_wp["bodies"]:
                if b.get("landmark_value", False) and not b.get("checked", False):
                    value += b["landmark_value"]
                    simple_body_name = simplified_body_name(self.current_wp_sysname(), b.get("name", None))
                    if simple_body_name:
                        body_names.append(simple_body_name)

            if body_names:
                if value:
                    details.append(_("biomes to survey (~{val} cr): {bodies}").format(val=pretty_print_number(value), bodies="; ".join(body_names)))
                else:
                    details.append(_("biomes to survey: {bodies}").format(bodies=body_names))

        return details

    def mapped_body(self, star_system, body_name):
        """
        Mark a body as mapped (exobiology override).

        Returns:
            bool: Always returns True.
        """
        # overriding SpanshBodiesJourneyJSON's behavior since the point is to scan some biology.
        return True

class SpanshFleetCarrierJourneyJSON(GenericRoute):
    """
    A journey based on Spansh Fleet Carrier JSON data.
    """

    def __init__(self, data):
        """
        Initialize the Spansh Fleet Carrier journey.

        Args:
            data (dict): The route data from Spansh.
        """
        super().__init__()
        self.journey_type = "fleet-carrier"
        self.calc_starting_fuel = data.get("calculate_starting_fuel", False)
        self.capacity_used = data.get("capacity_used", 0)
        self.destinations = data.get("destinations", [])
        self.destination_name = self.destinations[-1] if self.destinations else None
        self.waypoints = BidiWaypointIterator(data.get("jumps", None))
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.fuel_loaded = data.get("fuel_loaded", 0)
        self.refuel_destinations = data.get("refuel_destinations", [])
        self.start = data.get("source", None)
        self.tritium_stored = data.get("tritium_stored", 0)
        self.total_waypoints = len(self.waypoints.collection)
        self.total_tritium_necessary = sum([waypoint.get("fuel_used", 0) for waypoint in self.waypoints.collection])

    def describe(self):
        """
        Provide a description of the Fleet Carrier journey.

        Returns:
            list: A list of description fragments.
        """
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))

        if len(self.destinations) > 1:
            details.append(_("via: {via}").format(via=", ".join(self.destinations[:-1])))

        if self.total_waypoints:
            wp_progress = self.waypoints.index+1 if self.waypoints else 0
            details.append(_("{wp_prog}/{wp_total} waypoints; {tritium} tritium ({restocks} restocks)").format(wp_prog=wp_progress, wp_total=self.total_waypoints, tritium=self.total_tritium_necessary, restocks=len(self.refuel_destinations)))

        return details

    def describe_wp(self, source_coords=None):
        """
        Provide a description of the current waypoint, including fuel and restock info.

        Args:
            source_coords (dict): Optional source coordinates.

        Returns:
            list: A list of description fragments.
        """
        details = super().describe_wp(source_coords)
        current_wp = self.current()

        prefix = ""
        if current_wp.get("is_desired_destination", False):
            prefix = _("[Stopover]") + " "

        if current_wp.get("distance", None) and current_wp.get("distance_to_destination", None):
            total_distance = current_wp["distance"] + current_wp["distance_to_destination"]
            trip_percentage = round((current_wp["distance"] / total_distance) * 100, 1)
            details.append(_("{pref}Trip: {dist}/{total} LY ({perc}%)").format(pref=prefix, dist=current_wp["distance"], total=total_distance, perc=trip_percentage))

        if current_wp.get("must_restock", False):
            details.append(_("Restock {amt} tritium").format(amt=current_wp.get("restock_amount", 0)))

        if current_wp.get("has_icy_ring", False):
            pristine = current_wp.get("is_system_pristine", False)
            if pristine:
                details.append(_("[Pristine icy ring]"))
            else:
                details.append(_("[Icy ring]"))

        return details

class SpanshTouristJourneyJSON(GenericRoute):
    """
    A journey based on Spansh Tourist JSON data.
    """

    def __init__(self, data):
        """
        Initialize the Spansh Tourist journey.

        Args:
            data (dict): The route data from Spansh.
        """
        super().__init__()
        self.journey_type = "tourist"
        self.destinations = data.get("destination_systems", [])
        self.range = data.get("range", None)
        self.start = data.get("source_system", None)
        self.waypoints = BidiWaypointIterator(data.get("system_jumps", None))
        self.destination_name = self.waypoints.collection[-1].get("system", None) if self.waypoints.collection else None
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.total_waypoints = len(self.waypoints.collection)
        self.total_jumps = sum([waypoint.get("jumps", 0) for waypoint in self.waypoints.collection])

    def describe(self):
        """
        Provide a description of the Tourist journey.

        Returns:
            list: A list of description fragments.
        """
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))

        if len(self.destinations) > 1:
            details.append(_("via: {via}").format(via=", ".join(self.destinations[:-1])))

        wp_progress = self.waypoints.index+1 if self.waypoints else 0
        if self.total_jumps and self.total_jumps != self.total_waypoints:
            details.append(_("{wp_prog}/{wp_total} waypoints; {jumps} jumps").format(wp_prog=wp_progress, wp_total=self.total_waypoints, jumps=self.total_jumps))
        else:
            details.append(_("{wp_prog}/{wp_total} waypoints").format(wp_prog=wp_progress, wp_total=self.total_waypoints))

        return details

    def describe_wp(self, source_coords=None):
        """
        Provide a description of the current waypoint, including stopover and next jump info.

        Args:
            source_coords (dict): Optional source coordinates.

        Returns:
            list: A list of description fragments.
        """
        details = super().describe_wp(source_coords)
        current_wp = self.current()

        if current_wp.get("name", "") in self.destinations:
            details.append(_("[Stopover]"))

        if self.waypoints.index < self.total_waypoints-1:
            next_wp = self.waypoints.collection[self.waypoints.index + 1]
            if next_wp and next_wp.get("jumps", 0):
                details.append(_("{nb} jumps to next waypoint").format(nb=next_wp["jumps"]))

        return details
    
class CSVJourney(GenericRoute):
    """
    A journey based on a custom CSV file.
    """

    def __init__(self, csvfile):
        """
        Initialize the custom CSV journey.

        Args:
            csvfile (str): Path to the CSV file.
        """
        self.journey_type = "custom"
        try:
            with open(csvfile, newline='', encoding='utf-8') as csvdata:
                self.waypoints = BidiWaypointIterator(list(csv.DictReader(csvdata, delimiter=",", quotechar='"')))
        except Exception:
            self.waypoints = BidiWaypointIterator([])

        if not self.waypoints.empty():
            next(self.waypoints)
            self.start = self.waypoints.collection[0].get("system", None) if self.waypoints.collection else None
            self.destination_name = self.waypoints.collection[-1].get("system", None) if self.waypoints.collection else None
            self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
            self.total_waypoints = len(self.waypoints.collection)
            self.total_jumps = sum([int(waypoint.get("jumps", 0)) for waypoint in self.waypoints.collection]) or None
        else:
            self.start = None
            self.destination_name = None
            self.destination = None
            self.total_waypoints = 0
            self.total_jumps = None

    def describe(self):
        """
        Provide a description of the custom CSV journey.

        Returns:
            list: A list of description fragments.
        """
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))

        wp_progress = self.waypoints.index+1 if self.waypoints else 0
        if self.total_jumps and self.total_jumps != self.total_waypoints:
            details.append(_("{wp_prog}/{wp_total} waypoints; {jumps} jumps").format(wp_prog=wp_progress, wp_total=self.total_waypoints, jumps=self.total_jumps))
        else:
            details.append(_("{wp_prog}/{wp_total} waypoints").format(wp_prog=wp_progress, wp_total=self.total_waypoints))

        return details

    def describe_wp(self, source_coords=None):
        """
        Provide a description of the current waypoint, including next jump info.

        Args:
            source_coords (dict): Optional source coordinates.

        Returns:
            list: A list of description fragments.
        """
        details = super().describe_wp(source_coords)
        if self.waypoints is None:
            return details

        if self.waypoints.index < self.total_waypoints-1:
            next_wp = self.waypoints.collection[self.waypoints.index + 1]
            if next_wp and next_wp.get("jumps", 0):
                details.append(_("{nb} jumps to next waypoint").format(nb=next_wp["jumps"]))

        return details

class EDRRouteStatistics:
    """
    Statistics and tracking for a route.
    """

    DEFAULT_SEC_PER_JUMP = 90

    def __init__(self, route, ship_jump_range=None):
        """
        Initialize the route statistics.

        Args:
            route (GenericRoute): The route to track.
            ship_jump_range (float): Optional override for ship jump range.
        """
        self.departure = route.start
        self.destination = route.destination
        self.distance = route.distance
        self.position = None
        self.coords = None
        self.total_jumps = route.total_jumps
        self.remaining_waypoints = route.total_waypoints
        self.jumps_nb = 0
        self.distances = deque([], 25)
        self.intervals = deque([], 25)
        now = EDTime.py_epoch_now()
        self.start = now
        self.previous_timestamp = now
        self.current = now
        self.travelled_ly = 0
        self.ship_jump_range = ship_jump_range

    def meaningful(self):
        """
        Check if we have enough data for meaningful statistics.

        Returns:
            bool: True if intervals are recorded.
        """
        return len(self.intervals) > 0

    def update(self, system, coords, waypoints_to_go):
        """
        Update statistics with current location.

        Args:
            system (str): Current system name.
            coords (dict): Current coordinates.
            waypoints_to_go (int): Number of waypoints remaining.
        """
        now = EDTime.py_epoch_now()
        self.current = now
        self.remaining_waypoints = waypoints_to_go
        self.jumps_nb += 1
        if self.coords and coords:
            distance = sqrt((self.coords["x"] - coords["x"])**2 + (self.coords["y"] - coords["y"])**2 + (self.coords["z"] - coords["z"])**2)
            self.distances.append(distance)
            self.travelled_ly += distance
        elif "StarPos" in self.departure and coords:
            s_pos = self.departure["StarPos"]
            distance = sqrt((s_pos[0] - coords["x"])**2 + (s_pos[1] - coords["y"])**2 + (s_pos[2] - coords["z"])**2)
            self.distances.append(distance)
            self.travelled_ly += distance

        jump_duration = now - self.previous_timestamp
        self.intervals.append(jump_duration)
        self.previous_timestamp = now
        self.position = system
        self.coords = coords

    def elapsed_time(self):
        """
        Get the elapsed time since start.

        Returns:
            float: Elapsed seconds.
        """
        return EDTime.py_epoch_now() - self.start

    def remaining_time(self, waypoints_based=False):
        """
        Calculate remaining time.

        Args:
            waypoints_based (bool): If True, calculate based on jump count.

        Returns:
            int: Remaining seconds, or None.
        """
        if waypoints_based:
            jumps = self.remaining_waypoints
            duration = self.s_jmp()
            if duration:
                return int(jumps * duration)
            else:
                return None
        else:
            remaining_distance = self.remaining_ly()
            ly_hr_stat = self.ly_hr()
            if not remaining_distance or not ly_hr_stat:
                return None
            return int(remaining_distance / ly_hr_stat * 60 * 60)

    def remaining_ly(self):
        """
        Calculate remaining distance in light years.

        Returns:
            int: Remaining LY, or None.
        """
        if self.coords and all([coord in self.coords for coord in ["x", "y", "z"]]):
            if "StarPos" in self.destination:
                d_pos = self.destination["StarPos"]
                return round(sqrt((d_pos[0] - self.coords["x"])**2 + (d_pos[1] - self.coords["y"])**2 + (d_pos[2] - self.coords["z"])**2))
            else:
                return round(sqrt((self.destination["x"] - self.coords["x"])**2 + (self.destination["y"] - self.coords["y"])**2 + (self.destination["z"] - self.coords["z"])**2))
        else:
            return round(self.distance) if self.distance is not None else None

    def ly_hr(self):
        """
        Calculate light years per hour.

        Returns:
            int: LY/HR.
        """
        jmp_range = self.ly_jmp()
        if jmp_range:
            return round(jmp_range * self.jmp_hr())
        return 0

    def jmp_hr(self):
        """
        Calculate jumps per hour.

        Returns:
            int: Jumps/HR.
        """
        if self.s_jmp():
            return round(3600 / self.s_jmp())
        return 0

    def s_jmp(self):
        """
        Calculate seconds per jump.

        Returns:
            int: Seconds/Jump.
        """
        if len(self.intervals):
            total_duration = sum(self.intervals)
            return min(999, int(total_duration / len(self.intervals)))
        return self.DEFAULT_SEC_PER_JUMP

    def ly_jmp(self):
        """
        Calculate light years per jump.

        Returns:
            float: LY/Jump, or None.
        """
        range_val = self.inferred_range() or self.ship_jump_range
        if range_val:
            return round(range_val, 1)
        return None

    def remaining_jumps(self):
        """
        Calculate estimated remaining jumps.

        Returns:
            int: Remaining jumps, or None.
        """
        remaining_distance = self.remaining_ly()
        ly_jmp_stat = self.ly_jmp()
        if remaining_distance is None or not ly_jmp_stat:
            return None

        if remaining_distance == 0:
            return 0

        return int(remaining_distance / ly_jmp_stat)

    def inferred_range(self):
        """
        Infer ship's jump range from travel history.

        Returns:
            float: Average jump distance, or None.
        """
        total_distance = sum(self.distances)
        if len(self.distances):
            return total_distance / len(self.distances)
        return None
    
class EDRNavigator:
    """
    Manages navigation, routes, and journeys for EDR.
    """
    EDR_JOURNEY_CACHE = edr_cache_path('navigator.v1.p')

    def __init__(self):
        """
        Initialize the EDR Navigator.
        """
        self.route = None
        self.route_stats = None
        self.journey = None
        self.journey_stats = None
        self.position = None
        try:
            with open(self.EDR_JOURNEY_CACHE, 'rb') as handle:
                self.journey = pickle.load(handle)
                if self.journey:
                    self.journey_stats = EDRRouteStatistics(self.journey)
        except Exception:
            self.journey = None

    def persist(self):
        """
        Persist the current journey to cache.
        """
        with open(self.EDR_JOURNEY_CACHE, 'wb') as handle:
            pickle.dump(self.journey, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def update(self, current_sys, coords):
        """
        Update navigator with current system and coordinates.

        Args:
            current_sys (str): Current system name.
            coords (dict): Current coordinates.

        Returns:
            dict: Status of updates {'journey_updated': bool, 'route_updated': bool}.
        """
        self.position = {"system": current_sys, "coords": coords}
        journey_updated = self.__update_journey(current_sys)
        route_updated = self.__update_route(current_sys)

        if self.route_stats and (journey_updated or route_updated):
            self.route_stats.update(current_sys, coords, self.route.remaining_waypoints())

        if self.journey_stats and (journey_updated or route_updated):
            self.journey_stats.update(current_sys, coords, self.journey.remaining_waypoints())

        return {
            "journey_updated": journey_updated,
            "route_updated": route_updated
        }

    def __update_journey(self, current_sys):
        """
        Internal method to update journey status.

        Args:
            current_sys (str): Current system name.

        Returns:
            bool: True if journey updated.
        """
        if self.no_journey():
            return False

        current_wp_sysname = self.journey.current_wp_sysname()
        if not current_wp_sysname:
            return False

        if current_sys == current_wp_sysname:
            if self.journey.current_wp_surveyed():
                next_wp = self.journey.next()
                return next_wp is not None
            else:
                return True
        return False

    def __update_route(self, current_sys):
        """
        Internal method to update route status.

        Args:
            current_sys (str): Current system name.

        Returns:
            bool: True if route updated.
        """
        if self.no_route():
            return False

        return self.route.update(current_sys)

    def fsd_range(self, range_val):
        """
        Set or update FSD range.

        Args:
            range_val (float): The FSD jump range.
        """
        if self.route_stats:
            self.route_stats.ship_jump_range = range_val

    def set_journey(self, route):
        """
        Set the current journey.

        Args:
            route (GenericRoute): The journey route object.
        """
        self.journey = route
        self.journey_stats = EDRRouteStatistics(self.journey)

    def set_route(self, navroute):
        """
        Set the current NavRoute.

        Args:
            navroute (dict): The NavRoute data.
        """
        self.route = EDRNavRoute(navroute)
        self.route_stats = EDRRouteStatistics(self.route)
        # get past the starting poinnt which should be the current system
        self.route.next()

    def clear_journey(self):
        """
        Clear the current journey.
        """
        self.journey = None

    def clear_route(self):
        """
        Clear the current NavRoute.
        """
        self.route = None
        self.route_stats = None

    def no_journey(self):
        """
        Check if there is no active journey.

        Returns:
            bool: True if no journey.
        """
        return self.journey is None or self.journey.empty()

    def no_route(self):
        """
        Check if there is no active NavRoute.

        Returns:
            bool: True if no route.
        """
        return self.route is None or self.route.empty()

    def journey_next(self):
        """
        Move to next waypoint in journey.

        Returns:
            dict: The next waypoint, or False.
        """
        if self.journey:
            return self.journey.next()
        return False

    def journey_previous(self):
        """
        Move to previous waypoint in journey.

        Returns:
            dict: The previous waypoint, or False.
        """
        if self.journey:
            return self.journey.previous()
        return False

    def current(self):
        """
        Get current journey waypoint.

        Returns:
            dict: Current waypoint, or False.
        """
        if self.journey:
            return self.journey.current()
        return False

    def current_wp_sysname(self):
        """
        Get current journey waypoint system name.

        Returns:
            str: System name, or False.
        """
        if self.journey:
            return self.journey.current_wp_sysname()
        return False

    def describe(self):
        """
        Describe the current journey and its statistics.

        Returns:
            list: Description fragments.
        """
        if not self.journey:
            return None

        details = self.journey.describe()
        stats_summary = self.journey_stats_summary()
        if details and stats_summary:
            details.extend(stats_summary)
        return details

    def is_waypoint(self, system_name):
        """
        Check if system is a waypoint in the journey.

        Args:
            system_name (str): System name.

        Returns:
            bool: True if waypoint.
        """
        if not self.journey:
            return None

        return self.journey.is_waypoint(system_name)

    def describe_wp(self, current_coords=None):
        """
        Describe current journey waypoint.

        Args:
            current_coords (dict): Current coordinates.

        Returns:
            list: Description fragments.
        """
        if not self.journey:
            return None

        return self.journey.describe_wp(current_coords)

    def route_stats_summary(self):
        """
        Get summary of route statistics.

        Returns:
            list: Statistics summary.
        """
        if not self.route_stats:
            return None

        return self.__stats_summary(self.route_stats)

    def journey_stats_summary(self):
        """
        Get summary of journey statistics.

        Returns:
            list: Statistics summary.
        """
        if not self.journey_stats:
            return None

        return self.__stats_summary(self.journey_stats)

    def __stats_summary(self, stats):
        """
        Internal method to generate stats summary.

        Args:
            stats (EDRRouteStatistics): Stats object.

        Returns:
            list: Summary strings.
        """
        if not stats.meaningful():
            return None
        summary = []
        remaining_time = stats.remaining_time()
        remaining_ly = stats.remaining_ly()
        remaining_jumps = stats.remaining_jumps()

        ly_hr = stats.ly_hr()
        jmp_hr = stats.jmp_hr()
        ly_jmp = stats.ly_jmp()
        s_jmp = stats.s_jmp()

        elements = []
        if remaining_time:
            elements.append(_("ETA: {eta}").format(eta=EDTime.pretty_print_timespan(remaining_time)))

        if remaining_ly:
            elements.append(_("Distance: {dist}").format(dist=int(remaining_ly)))

        if remaining_jumps:
            elements.append(_("Jumps: {jumps}").format(jumps=int(remaining_jumps)))

        if elements:
            summary.append("; ".join(elements))

        elements = []
        if ly_hr:
            elements.append(_("LY/HR: {ly_hr}").format(ly_hr=int(ly_hr)))

        if jmp_hr:
            elements.append(_("JMP/HR: {jmp_hr}").format(jmp_hr=int(jmp_hr)))

        if ly_jmp:
            elements.append(_("LY/JMP: {ly_jmp}").format(ly_jmp=int(ly_jmp)))

        if s_jmp:
            elements.append(_("T/JMP: {s_jmp}").format(s_jmp=EDTime.pretty_print_timespan(s_jmp)))

        if elements:
            summary.append("; ".join(elements))

        return summary

    def noteworthy_about_body(self, star_system, body_name):
        """
        Check if body is noteworthy in journey.

        Args:
            star_system (str): System name.
            body_name (str): Body name.

        Returns:
            list: Details if noteworthy.
        """
        if self.no_journey():
            return False

        return self.journey.noteworthy_about_body(star_system, body_name)

    def leave_body(self, star_system, body_name):
        """
        Handle leaving a body in journey.

        Args:
            star_system (str): System name.
            body_name (str): Body name.

        Returns:
            bool: True if processed.
        """
        if self.no_journey():
            return False

        return self.journey.leave_body(star_system, body_name)

    def check_bodies(self, star_system, bodies_names):
        """
        Check multiple bodies in journey.

        Args:
            star_system (str): System name.
            bodies_names (list): List of body names.

        Returns:
            bool: True if updated.
        """
        if self.no_journey():
            return False

        checked = False
        for body_name in bodies_names:
            checked |= self.journey.check_body(star_system, body_name)

        return checked

    def surveyed_body(self, star_system, body_name):
        """
        Handle surveyed body in journey.

        Args:
            star_system (str): System name.
            body_name (str): Body name.

        Returns:
            bool: True if processed.
        """
        if self.no_journey():
            return False

        return self.journey.surveyed_body(star_system, body_name)

    def mapped_body(self, star_system, body_name):
        """
        Handle mapped body in journey.

        Args:
            star_system (str): System name.
            body_name (str): Body name.

        Returns:
            bool: True if processed.
        """
        if self.no_journey():
            return False

        return self.journey.mapped_body(star_system, body_name)

    def describe_wp_bodies(self):
        """
        Describe bodies at current journey waypoint.

        Returns:
            list: Description fragments.
        """
        if self.no_journey():
            return False

        return self.journey.describe_wp_bodies()

    def wp_bodies_to_survey(self, star_system):
        """
        Get bodies to survey at system for journey.

        Args:
            star_system (str): System name.

        Returns:
            list: Body names.
        """
        if self.no_journey():
            return None

        return self.journey.wp_bodies_to_survey(star_system)
        