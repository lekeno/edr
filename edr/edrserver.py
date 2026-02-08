import sys
from urllib.parse import quote
import json
import calendar
import time
import requests
import re

from edrcmdrprofile import EDRCmdrProfile  # EDR_INTERNAL
from RESTFirebase import RESTFirebaseAuth, AuthState  # EDR_INTERNAL
from edrconfig import EDR_CONFIG  # EDR_INTERNAL
from edrlog import EDR_LOG  # EDR_INTERNAL
from edtime import EDTime  # EDR_INTERNAL
from backoff import Backoff  # EDR_INTERNAL
from edrhttpcache import EDRHttpCache  # EDR_INTERNAL


class EDRServer:
    """
    Handles communication with the EDR server and other APIs (Inara, EDSM, etc.).
    """

    SESSION = requests.Session()

    @staticmethod
    def nodify(name):
        """
        Normalize a name for use as a node key.
        """
        return name.lower().replace(" ", "_")

    def __init__(self):
        """
        Initialize the EDR Server interface.
        """
        self.version = EDR_CONFIG.edr_version()
        self.REST_firebase = RESTFirebaseAuth(self.version)
        self.EDR_API_KEY = EDR_CONFIG.edr_api_key()
        self.EDR_SERVER = EDR_CONFIG.edr_server()
        self.EDR_SERVER_FUNCTIONS = EDR_CONFIG.edr_server_functions()
        self.player_name = None
        self.game_mode = None
        self.dlc_name = None
        self.private_group = None
        self._throttle_until_timestamp = None
        self.anonymous_reports = None
        self.crimes_reporting = None
        self.fc_jump_psa = None
        self.backoff = {"EDR": Backoff("EDR"), "Inara": Backoff("Inara")}
        self.http_cache = EDRHttpCache()
        self.INARA_API_KEY = EDR_CONFIG.inara_api_key()

    def login(self, email="", password=""):
        """
        Log in to the EDR backend.

        Args:
            email (str): User email.
            password (str): User password.

        Returns:
            dict: Authentication response.
        """
        self.REST_firebase.api_key = self.EDR_API_KEY
        self.REST_firebase.email = email
        self.REST_firebase.password = password

        return self.REST_firebase.authenticate()

    def logout(self):
        """
        Log out from the EDR backend.
        """
        self.REST_firebase.clear_authentication()

    def set_player_name(self, name):
        """
        Set the current player's name.

        Args:
            name (str): Commander name.
        """
        self.player_name = name

    def set_game_mode(self, mode, group=None):
        """
        Set the current game mode.

        Args:
            mode (str): Game mode (Open, Solo, Private).
            group (str, optional): Private group name.
        """
        self.game_mode = mode
        self.private_group = group

    def set_dlc(self, dlc):
        """
        Set the current DLC.

        Args:
            dlc (str): DLC name (e.g. Horizons, Odyssey).
        """
        self.dlc_name = dlc

    def is_authenticated(self):
        """
        Check if the user is authenticated.

        Returns:
            bool: True if authenticated.
        """
        return self.REST_firebase.is_valid_auth_token()

    def is_anonymous(self):
        """
        Check if the user is anonymous (guest).

        Returns:
            bool: True if anonymous.
        """
        return self.REST_firebase.anonymous

    def uid(self):
        """
        Get the user's UID.

        Returns:
            str: User ID.
        """
        return self.REST_firebase.uid()

    def auth_token(self):
        """
        Get the current authentication token.

        Returns:
            str: Auth token.
        """
        return self.REST_firebase.id_token()

    def refresh_auth(self):
        """
        Force a refresh of the authentication token.
        """
        return self.REST_firebase.force_new_auth()

    def __check_response(self, response, service, call="Unknown"):
        if response is None:
            EDR_LOG.warning("No response: service={}, call={}, resp={}".format(service, call, response))
            return False

        EDR_LOG.debug("Checking response: service={}, call={}, status={}".format(service, call, response.status_code))
        if response.status_code in [200, 204, 304, 404]:
            EDR_LOG.debug("Acceptable response => resetting backoff: service={}, call={}, resp={}".format(service, call, response))
            self.backoff[service].reset()
            return True

        if response.status_code in [401, 403, 429] or response.status_code >= 500:
            EDR_LOG.debug("Bad response => throttling: service={}, call={}, resp={}".format(service, call, response))
            retry_after = response.headers.get("Retry-After")
            epoch = None
            if retry_after:
                try:
                    dt = EDTime()
                    dt.from_http_header(retry_after)
                    epoch = dt.as_py_epoch()
                except:
                    pass

            if epoch:
                self.backoff[service].until(epoch)
            else:
                self.backoff[service].throttle()

        return False

    def __process_inara_response(self, json_resp):
        if json_resp is None:
            EDR_LOG.warning("No Inara response: resp={}".format(json_resp))
            return None

        EDR_LOG.debug("Processing Inara response: resp={}".format(json_resp))

        body = None

        if not json_resp.get("body", None):
            EDR_LOG.warning("No Inara body: json_resp={}".format(json_resp))
            return None

        body = json_resp["body"]

        if not isinstance(body, dict):
            EDR_LOG.warning("Inara body is not a dictionary (likely an error code): body={}".format(body))
            if body == 401 or body == 403:
                self.backoff["Inara"].throttle()
            return None

        EDR_LOG.debug("Inara body={}".format(body))
        try:
            header = body.get("header", {})
            if header.get("eventStatus") == 400:
                EDR_LOG.info(f"Too many requests for Inara.")
                self.backoff["Inara"].throttle()
                return None

            events = body.get("events", [])
            if not events:
                EDR_LOG.warning("No Inara events: body={}".format(body))
                return None

            event_status = events[0].get("eventStatus")
            if event_status == 204:
                EDR_LOG.info(f"cmdr was not found via the Inara API: content={body}")
                self.backoff["Inara"].reset()
                return None
            if event_status != 200:
                EDR_LOG.error(f"Error from Inara API. Status: {event_status}; content={body}")
                self.backoff["Inara"].throttle()
                return None

            data = events[0].get("eventData")
            self.backoff["Inara"].reset()
            return data
        except Exception as e:
            EDR_LOG.exception(f"Unexpected error parsing Inara response: {e}")
            self.backoff["Inara"].throttle()
        return None

    def __get(self, endpoint, service, params=None, headers=None, attempts=3, call="Unknown"):
        headers = headers if headers is not None else {}
        headers.update({"EDR-Version": f"v{self.version}"})

        req = requests.Request('GET', endpoint, params=params, headers=headers)
        prepped = self.SESSION.prepare_request(req)
        cache_key = prepped.url

        cached_data = self.http_cache.get(cache_key)
        if cached_data is not None:
            EDR_LOG.debug("Cache hit for {}".format(cache_key))
            return cached_data

        etag = self.http_cache.get_etag(cache_key)
        if etag:
            prepped.headers.update({"If-None-Match": etag})
            EDR_LOG.debug("Conditional GET for {} with ETag {}".format(cache_key, etag))

        last_connection_exception = None
        while attempts > 0:
            attempts -= 1

            if self.backoff[service].throttled():
                EDR_LOG.debug("Exponential backoff active for {} API calls: attempts={}, until={}".format(service, self.backoff[service].attempts, EDTime.t_plus_py(self.backoff[service].backoff_until)))
                return None

            try:
                resp = EDRServer.SESSION.send(prepped)
                if self.__check_response(resp, service, call):

                    if resp.status_code == 304:
                        EDR_LOG.debug("ETag Match (304) for {}".format(cache_key))
                        self.http_cache.refresh(cache_key)
                        return self.http_cache.get(cache_key)

                    data = {}
                    if resp.status_code == 200:
                        data = resp.json() if resp.text else {}

                        if data is None:
                            data = {}

                    cache_control = resp.headers.get("Cache-Control", "")
                    max_age_match = re.search(r"max-age=(\d+)", cache_control)
                    maxAge = int(max_age_match.group(1)) if max_age_match else 0
                    etag = resp.headers.get("ETag", None)

                    self.http_cache.set(cache_key, data, max_age_seconds=maxAge, etag=etag)
                    return data

                EDR_LOG.warning(f"Bad response for {call}. Retries left: {attempts}")
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.warning("ConnectionException {} for GET EDR {}: attempts={}".format(e, service, attempts))
                time.sleep(1)

        if last_connection_exception:
            raise last_connection_exception
        return None

    def __put(self, endpoint, service, json, params=None, headers=None, attempts=3, call="Unknown"):
        headers = headers if headers is not None else {}
        headers.update({"EDR-Version": f"v{self.version}"})

        req = requests.Request('PUT', endpoint, params=params, json=json, headers=headers)
        prepped = self.SESSION.prepare_request(req)

        last_connection_exception = None
        while attempts > 0:
            attempts -= 1

            if self.backoff[service].throttled():
                EDR_LOG.debug("Exponential backoff active for {} API calls: attempts={}, until={}".format(service, self.backoff[service].attempts, EDTime.t_plus_py(self.backoff[service].backoff_until)))
                return None

            try:
                resp = EDRServer.SESSION.send(prepped)

                if self.__check_response(resp, service, call):
                    self.http_cache.evict(prepped.url)
                    try:
                        return resp.json() if resp.text else {}
                    except ValueError:
                        return {}

                EDR_LOG.warning(f"Bad response for PUT {call}. Retries left: {attempts}")
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.warning("ConnectionException {} for PUT EDR {}: attempts={}".format(e, service, attempts))
                time.sleep(1)

        if last_connection_exception:
            raise last_connection_exception
        return None 
    
    def __delete(self, endpoint, service, params=None, headers=None, attempts=3, call="Unknown"):
        headers = headers if headers is not None else {}
        headers.update({"EDR-Version": f"v{self.version}"})

        req = requests.Request('DELETE', endpoint, params=params, headers=headers)
        prepped = self.SESSION.prepare_request(req)

        last_connection_exception = None
        while attempts > 0:
            attempts -= 1

            if self.backoff[service].throttled():
                EDR_LOG.debug("Exponential backoff active for {} API calls: attempts={}, until={}".format(service, self.backoff[service].attempts, EDTime.t_plus_py(self.backoff[service].backoff_until)))
                return None

            try:
                resp = EDRServer.SESSION.send(prepped)

                if self.__check_response(resp, service, call):
                    self.http_cache.evict(prepped.url)
                    return True

                EDR_LOG.warning(f"Bad response for DELETE {call}. Retries left: {attempts}")
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.warning("ConnectionException {} for DELETE EDR {}: attempts={}".format(e, service, attempts))
                time.sleep(1)

        if last_connection_exception:
            raise last_connection_exception
        return False

    def __post(self, endpoint, service, json, params=None, headers=None, attempts=3, call="Unknown"):
        headers = headers if headers is not None else {}
        headers.update({"EDR-Version": f"v{self.version}"})

        req = requests.Request('POST', endpoint, params=params, json=json, headers=headers)
        prepped = self.SESSION.prepare_request(req)

        last_connection_exception = None
        while attempts > 0:
            attempts -= 1

            if self.backoff[service].throttled():
                EDR_LOG.debug("Exponential backoff active for {} API calls: attempts={}, until={}".format(service, self.backoff[service].attempts, EDTime.t_plus_py(self.backoff[service].backoff_until)))
                return None

            try:
                resp = EDRServer.SESSION.send(prepped)

                if self.__check_response(resp, service, call):
                    self.http_cache.evict(prepped.url)
                    try:
                        return resp.json() if resp.text else {}
                    except ValueError:
                        return {}

                EDR_LOG.warning(f"Bad response for POST {call}. Retries left: {attempts}")
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.warning("ConnectionException {} for POST EDR {}: attempts={}".format(e, service, attempts))

        if last_connection_exception:
            raise last_connection_exception
        return None

    def server_version(self):
        """
        Check for server version.

        Returns:
            dict: Server version info or None.
        """
        data = self.__get("{}/version/.json".format(self.EDR_SERVER), "EDR", call="Version")

        if data is None:
            EDR_LOG.error("Failed to check for version update.")
            return None

        if not data:
            EDR_LOG.error("Version information is missing on the server.")
            return None

        return data

    def notams(self, timespan_seconds):
        """
        Retrieve NOTAMs (Notices to Airmen).

        Args:
            timespan_seconds (int): Timespan to check for.

        Returns:
            dict: NOTAMs data or None.
        """
        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))
        future_epoch_js = 1830000000000

        params = {"orderBy": '"timestamp"', "startAt": past_epoch_js, "endAt": future_epoch_js, "auth": self.auth_token(), "limitToLast": 10}
        data = self.__get("{}/v1/notams.json".format(self.EDR_SERVER), "EDR", call="notams", params=params)

        if data is None:
            EDR_LOG.error("Failed to retrieve notams.")
            return None

        return data

    def sitreps(self, timespan_seconds):
        """
        Retrieve SITREPs (Situation Reports).

        Args:
            timespan_seconds (int): Timespan to check.

        Returns:
            dict: SITREPs data or None.
        """
        if not self.__preflight("sitreps", timespan_seconds):
            EDR_LOG.debug("Preflight failed for sitreps call.")
            raise CommsJammedError("sitreps")

        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))

        params = {
            "orderBy": '"timestamp"',
            "startAt": past_epoch_js,
            "endAt": now_epoch_js,
            "auth": self.auth_token(),
            "limitToLast": 30
        }

        sitreps_data = self.__get("{}/v1/systems.json".format(self.EDR_SERVER), "EDR", params, call="Sitreps")

        if sitreps_data is None:
            EDR_LOG.error("Failed to retrieve sitreps.")
            return None

        return sitreps_data

    def system(self, star_system, may_create, coords=None):
        """
        Get or create a star system in EDR backend.

        Args:
            star_system (str): System name.
            may_create (bool): Whether to create if missing.
            coords (list): [x, y, z] coordinates.

        Returns:
            dict: System data or None.
        """
        if not self.__preflight("system_id", star_system):
            EDR_LOG.debug("Preflight failed for system call. Forcing a new authentication, just in case.")
            self.refresh_auth()
            raise CommsJammedError("system")

        params = {"orderBy": '"cname"', "equalTo": json.dumps(star_system.lower()), "limitToFirst": 1, "auth": self.auth_token()}
        the_system = self.__get("{}/v1/systems.json".format(self.EDR_SERVER), "EDR", params, call="System")

        if the_system is None:
            EDR_LOG.error(f"Network error checking for system {star_system}.")
            return None

        if not the_system:
            if not may_create:
                EDR_LOG.error(f"Failed to retrieve star system {star_system}.")
                return None

            EDR_LOG.debug(f"Creating system {star_system} in EDR.")
            params = {"auth": self.auth_token()}
            payload = {"name": star_system, "uid": self.uid()}
            if coords:
                EDR_LOG.debug(f"With coords: {coords}")
                payload["coords"] = {
                    "x": coords[0],
                    "y": coords[1],
                    "z": coords[2],
                    "uid": self.uid()
                }

            post_resp = self.__post("{}/v1/systems.json".format(self.EDR_SERVER), "EDR", json=payload, params=params, call="Create_system")
            if post_resp and "name" in post_resp:
                new_id = post_resp["name"]
                EDR_LOG.debug(f"Created system {star_system} in EDR with new ID: {new_id}.")
                return {new_id: payload}

            EDR_LOG.error("Unexpected response format after system creation.")
            return None

        sid = list(the_system)[0]
        if sid is None:
            EDR_LOG.debug(f"System {star_system} has no id={sid}.")
            return None

        EDR_LOG.debug(f"System {star_system} is in EDR with id={sid}.")
        if may_create and not self.is_anonymous() and coords and "coords" not in the_system[sid]:
            EDR_LOG.debug(f"Adding coords to system {star_system} in EDR.")
            params = {"auth": self.auth_token()}
            coord_payload = {
                "x": coords[0],
                "y": coords[1],
                "z": coords[2],
                "uid": self.uid()
            }
            put_resp = self.__put("{}/v1/systems/{}/coords/.json".format(self.EDR_SERVER, sid), "EDR", json=coord_payload, params=params, call="Add Coords")
            if put_resp:
                EDR_LOG.debug(f"Added coords to system {star_system} in EDR with id={sid} and coords={coords}.")
                the_system[sid]["coords"] = coord_payload
                return the_system
            EDR_LOG.error("Failed to add coords to existing star system.")

        return the_system

    def fc(self, callsign, name, star_system, may_create):
        """
        Get or create a Fleet Carrier in EDR backend.

        Args:
            callsign (str): Carrier callsign.
            name (str): Carrier name.
            star_system (str): Current system.
            may_create (bool): Whether to create if missing.

        Returns:
            dict: Carrier data or None.
        """
        if not self.__preflight("fc_id", callsign):
            EDR_LOG.debug("Preflight failed for fc call. Forcing a new authentication, just in case.")
            self.refresh_auth()
            raise CommsJammedError("fc")

        params = {
            "orderBy": '"ccallsign"',
            "equalTo": json.dumps(callsign.lower()),
            "limitToFirst": 1,
            "auth": self.auth_token()
        }
        the_fc = self.__get("{}/v1/fcs.json".format(self.EDR_SERVER), "EDR", params, call="FC")

        if the_fc is None:
            EDR_LOG.error(f"Network error checking for FC {callsign}.")
            return None

        if not the_fc:
            if not may_create:
                EDR_LOG.error(f"Failed to retrieve FC {callsign}.")
                return None

            EDR_LOG.debug(f"FC {callsign} is not recorded in EDR. Creating it.")
            params = {"auth": self.auth_token()}
            payload = {
                "callsign": callsign,
                "name": name,
                "starSystem": star_system,
                "uid": self.uid()
            }
            post_resp = self.__post("{}/v1/fcs.json".format(self.EDR_SERVER), "EDR", json=payload, params=params, call="Create FC")
            if post_resp and "name" in post_resp:
                new_id = post_resp["name"]
                EDR_LOG.debug(f"Created FC {callsign} in EDR with new ID: {new_id}.")
                return {new_id: payload}
            EDR_LOG.error("Failed to create new FC.")
            return None

        fcid = list(the_fc)[0]
        EDR_LOG.debug("FC {} is in EDR with id={}.".format(callsign, fcid))

        return the_fc

    def pledged_to(self, power, since):
        """
        Update pledge information.

        Args:
            power (str): Power name (e.g. "Aisling Duval").
            since (int): Timestamp.

        Returns:
            bool: Success status.
        """
        params = {"auth": self.auth_token()}
        endpoint = "{server}/v1/pledges/{uid}/.json".format(server=self.EDR_SERVER, uid=self.uid())

        if power is None:
            EDR_LOG.info("Removing pledge info for uid {uid}".format(uid=self.uid))
            return self.__delete(endpoint, "EDR", params=params, call="Delete_pledge")

        EDR_LOG.info("Pledge info for uid {uid} with power:{power}".format(uid=self.uid(), power=power))
        payload = {
            "cpower": self.nodify(power),
            "since": int(since * 1000),
            "heartbeat": {".sv": "timestamp"}
        }

        result = self.__put(endpoint, "EDR", params=params, json=payload, call="Put_pledge")

        if result is None:
            EDR_LOG.error(f"Failed to update pledge info for {power} due to network error.")
            return False

        return True

    def cmdr(self, cmdr, autocreate=True):
        """
        Get or create a commander profile.

        Args:
            cmdr (str): Commander name.
            autocreate (bool): Create if missing.

        Returns:
            EDRCmdrProfile: Commander profile or None.
        """
        if not self.__preflight("cmdr", cmdr):
            EDR_LOG.debug("Preflight failed for cmdr call.")
            raise CommsJammedError("cmdr")
        cmdr_profile = EDRCmdrProfile()

        endpoint = "{}/v1/cmdrs.json".format(self.EDR_SERVER)
        params = {
            "orderBy": '"cname"',
            "equalTo": json.dumps(cmdr.lower()),
            "limitToFirst": 1,
            "auth": self.auth_token()
        }

        json_cmdr = self.__get(endpoint, "EDR", params=params, call="Get_cmdr")

        if json_cmdr is None:
            # This was a network error or a throttle. Don't autocreate!
            EDR_LOG.error("Could not check for existing cmdr due to network error.")
            return None

        if not json_cmdr:
            if autocreate and not self.is_anonymous():
                EDR_LOG.debug(f"Cmdr {cmdr} not found. Autocreating.")
                params = {"auth": self.auth_token()}
                payload = {"name": cmdr, "uid": self.uid(), "requester": self.player_name}
                post_resp = self.__post(endpoint, "EDR", json=payload, params=params, call="Create_cmdr")

                if post_resp and "name" in post_resp:
                    # In POST, the 'name' key holds the new ID
                    cmdr_profile.cid = post_resp["name"]
                    cmdr_profile.name = cmdr
                    return cmdr_profile

                EDR_LOG.error("Cmdr did not exist and autocreation failed.")
                return None

            EDR_LOG.debug("Cmdr {} not found in EDR database.".format(cmdr))
            return None

        try:
            cid = next(iter(json_cmdr))
            cmdr_data = json_cmdr[cid]

            cmdr_profile.cid = cid
            cmdr_profile.from_dict(cmdr_data)

            EDR_LOG.debug("Existing cmdr found: {}".format(cid))
            return cmdr_profile
        except (StopIteration, KeyError, IndexError) as e:
            EDR_LOG.exception("Error parsing existing cmdr result: {}".format(e))
            return None

    def inara_cmdr(self, cmdr):
        """
        Fetch commander profile from Inara (via EDR proxy).

        Args:
            cmdr (str): Commander name.

        Returns:
            EDRCmdrProfile: Profile from Inara or False/None.
        """
        if self.player_name is None:
            return False

        if self.backoff["Inara"].throttled():
            EDR_LOG.debug("Exponential backoff active for Inara API calls: attempts={}, until={}".format(self.backoff["Inara"].attempts, EDTime.t_plus_py(self.backoff["Inara"].backoff_until)))
            return False

        EDR_LOG.info("Requesting Inara profile for {}".format(cmdr))
        headers = {
            "Authorization": "ApiKey {}".format(self.INARA_API_KEY),
            "X-EDR-UID": self.uid()
        }
        requester = quote(self.player_name.encode('utf-8'))
        endpoint = "{}/edr/v1/inara/{}/{}".format(
            self.EDR_SERVER_FUNCTIONS,
            quote(cmdr.lower().encode('utf-8')),
            requester)

        json_resp = self.__get(endpoint, "Inara", headers=headers, call="Inara_cmdr_via_EDR")
        EDR_LOG.debug(f"Inara response: endpoint={endpoint}, resp={json_resp}")

        if json_resp is None:
            EDR_LOG.error("Inara profile failed (network error or throttled).")
            return False

        processed_data = self.__process_inara_response(json_resp)
        if not processed_data:
            EDR_LOG.debug(f"No profile found in Inara response. Resp: {json_resp}")
            return False

        cmdr_profile = EDRCmdrProfile()
        cmdr_profile.from_inara_api(processed_data)
        return cmdr_profile

    def __post_json(self, endpoint, json_payload, service, call="Unknown"):
        params = {"auth": self.auth_token()}

        if self.anonymous_reports is not None:
            json_payload["anonymous"] = self.anonymous_reports
        if self.crimes_reporting is not None:
            json_payload["creporting"] = self.crimes_reporting

        full_url = "{server}{endpoint}.json".format(server=self.EDR_SERVER, endpoint=endpoint)
        EDR_LOG.debug("Post JSON {} to {}".format(json_payload, full_url))

        return self.__post(full_url, service, params=params, json=json_payload, call=call)

    def blip(self, cmdr_id, info):
        """
        Report a blip (sighting) of a commander.

        Args:
            cmdr_id (str): Commander ID.
            info (dict): Sighting info.
        """
        info["uid"] = self.uid()
        EDR_LOG.info("Blip for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info))
        endpoint = "/v1/blips/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info, "EDR", call="Blip")

    def traffic(self, system_id, info):
        """
        Report traffic in a system.

        Args:
            system_id (str): System ID.
            info (dict): Traffic info.
        """
        if not self.__preflight("traffic", system_id):
            EDR_LOG.debug("Preflight failed for traffic call.")
            raise CommsJammedError("traffic")

        info["uid"] = self.uid()
        EDR_LOG.info("Traffic report for system {sid} with json:{json}".format(sid=system_id, json=info))
        endpoint = "/v1/traffic/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info, "EDR", call="Traffic")

    def scanned(self, cmdr_id, info):
        """
        Report a scan of a commander.

        Args:
            cmdr_id (str): Commander ID.
            info (dict): Scan info.
        """
        info["uid"] = self.uid()
        EDR_LOG.info("Scan for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info))
        endpoint = "/v1/scans/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info, "EDR", call="Scanned")

    def legal_records(self, cmdr_id, timespan_seconds):
        """
        Fetch legal records for a commander.

        Args:
            cmdr_id (str): Commander ID.
            timespan_seconds (int): Timespan.

        Returns:
            list: List of legal records.
        """
        EDR_LOG.info("Fetching legal record for cmdr {cid}".format(cid=cmdr_id))
        endpoint = "/v1/legal/{cmdr_id}/".format(cmdr_id=cmdr_id)
        legal_records_perday = 24
        records_over_timespan = int(max(1, round(timespan_seconds / 86400.0 * legal_records_perday)))
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=records_over_timespan, call="Recent_legal_records")

    def legal_stats(self, cmdr_id):
        """
        Fetch legal stats for a commander.

        Args:
            cmdr_id (str): Commander ID.

        Returns:
            dict: Legal stats or None.
        """
        if not self.__preflight("legal_stats", cmdr_id):
            EDR_LOG.debug("Preflight failed for legal_stats call.")
            raise CommsJammedError("legal_stats")
        EDR_LOG.info("Fetching legal stats for cmdr {cid}".format(cid=cmdr_id))
        endpoint = "{server}/v1/stats/legal/{cmdr_id}/.json".format(server=self.EDR_SERVER, cmdr_id=cmdr_id)
        params = {"auth": self.auth_token()}
        data = self.__get(endpoint, "EDR", params, call="Legal_Stats")
        EDR_LOG.debug("data= {}".format("None" if data is None else data))

        return data

    def crime(self, system_id, info):
        """
        Report a crime in a system.

        Args:
            system_id (str): System ID.
            info (dict): Crime info.
        """
        info["uid"] = self.uid()
        EDR_LOG.info("Crime report for system {sid} with json:{json}".format(sid=system_id, json=info))
        endpoint = "/v1/crimes/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info, "EDR", call="Crime")

    def fight(self, system_id, info):
        """
        Report a fight in a system.

        Args:
            system_id (str): System ID.
            info (dict): Fight info.
        """
        info["uid"] = self.uid()
        EDR_LOG.info("Fight report for system {sid} with json:{json}".format(sid=system_id, json=info))
        endpoint = "/v1/fights/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info, "EDR", call="Fight")

    def call_central(self, service, system_id, info):
        """
        Make a call to EDR Central.

        Args:
            service (str): The service to call.
            system_id (str): The ID of the system.
            info (dict): Additional information for the call.
        """
        info["uid"] = self.uid()
        EDR_LOG.info("Central call from system {sid} with json:{json}".format(sid=system_id, json=info))
        endpoint = "/v1/central/{service}/{system_id}/".format(service=service, system_id=system_id)
        return self.__post_json(endpoint, info, "EDR", call="Call_Central")

    def fc_jump_scheduled(self, flight_plan):
        """
        Report a scheduled Fleet Carrier jump.

        Args:
            flight_plan (dict): The flight plan details.

        Returns:
            bool: True if the report was successful, False otherwise.
        """
        if self.fc_jump_psa is None:
            return False
        flight_plan["psa"] = self.fc_jump_psa
        EDR_LOG.info("Fleet Carrier jump with json:{json}".format(json=flight_plan))
        endpoint = "/v1/fcjumps/{uid}/".format(uid=self.uid())
        return self.__post_json(endpoint, flight_plan, "EDR", call="FC_Jump_Scheduled")

    def fc_jump_cancelled(self, status):
        """
        Report a cancelled Fleet Carrier jump.

        Args:
            status (dict): The status of the cancellation.

        Returns:
            bool: True if the report was successful, False otherwise.
        """
        if self.fc_jump_psa is None:
            return False
        EDR_LOG.info("Cancelling Fleet Carrier jump")
        status["psa"] = self.fc_jump_psa
        endpoint = "/v1/fcjumps/{uid}/".format(uid=self.uid())
        return self.__post_json(endpoint, status, "EDR", call="FC_Jump_Cancelled")

    def crew_report(self, crew_id, report):
        """
        Report a multicrew session.

        Args:
            crew_id (str): The ID of the crew.
            report (dict): The multicrew session report.

        Returns:
            dict: The response from the server.
        """
        EDR_LOG.info("Multicrew session report: {}".format(report))
        endpoint = "/v1/crew_reports/{}/".format(crew_id)
        return self.__post_json(endpoint, report, "EDR", call="Crew_Report")

    def report_fcs(self, system_id, report):
        """
        Report Fleet Carriers in a system.

        Args:
            system_id (str): The ID of the system.
            report (dict): The report containing Fleet Carrier information.

        Returns:
            bool: True if the report was successful, False otherwise.
        """
        if self.is_anonymous():
            return False

        EDR_LOG.info("Reporting Fleet Carriers in system {}: {}".format(system_id, report))
        report["uid"] = self.uid()
        params = {"auth": self.auth_token()}
        endpoint = "{server}/v1/fc_reports/{system_id}/{uid}/.json".format(server=self.EDR_SERVER, system_id=system_id, uid=self.uid())

        result = self.__put(endpoint, "EDR", params=params, json=report, call="Report_fcs")
        return result is not None

    def fc_presence(self, star_system):
        """
        Check for Fleet Carrier presence in a system.

        Args:
            star_system (str): The name of the star system.

        Returns:
            dict: Fleet Carrier presence data or None.
        """
        if not self.__preflight("fc_presence", star_system):
            EDR_LOG.debug("Preflight failed for fc_presence call.")
            raise CommsJammedError("fc_presence")

        EDR_LOG.info("Querying Fleet Carriers in system {}".format(star_system))
        params = {"orderBy": '"starSystem"', "equalTo": json.dumps(star_system), "limitToFirst": 1, "auth": self.auth_token()}
        result = self.__get("{}/v1/fc_presence.json".format(self.EDR_SERVER), "EDR", params, call="FC_Presence")
        EDR_LOG.debug(f"result= {result}")

        if result:
            sid = list(result)[0]
            return result[sid]

        return None

    def report_fc_materials(self, fc_id, report):
        """
        Report materials on a Fleet Carrier.

        Args:
            fc_id (str): The ID of the Fleet Carrier.
            report (dict): The report containing material information.

        Returns:
            bool: True if the report was successful, False otherwise.
        """
        if self.is_anonymous():
            return False

        EDR_LOG.info("Reporting Materials on Fleet Carrier {}: {}".format(fc_id, report))
        report["uid"] = self.uid()
        params = {"auth": self.auth_token()}
        endpoint = "{server}/v1/fc_materials_reports/{fc_id}/{uid}/.json".format(server=self.EDR_SERVER, fc_id=fc_id, uid=self.uid())

        result = self.__put(endpoint, "EDR", params=params, json=report, call="Report_fc_materials")
        return result is not None

    def report_fc_market(self, fc_id, report):
        """
        Report market info on a Fleet Carrier.

        Args:
            fc_id (str): The ID of the Fleet Carrier.
            report (dict): The report containing market information.

        Returns:
            bool: True if the report was successful, False otherwise.
        """
        if self.is_anonymous():
            return False

        EDR_LOG.info("Reporting Market info on Fleet Carrier {}: {}".format(fc_id, report))
        report["uid"] = self.uid()
        params = {"auth": self.auth_token()}
        endpoint = "{server}/v1/fc_market_reports/{fc_id}/{uid}/.json".format(server=self.EDR_SERVER, fc_id=fc_id, uid=self.uid())

        result = self.__put(endpoint, "EDR", params=params, json=report, call="Report_fc_market")
        return result is not None

    def __get_recent(self, path, timespan_seconds, limitToLast=None, call="Get_recent"):
        """
        Helper method to fetch recent items from a given path.

        Args:
            path (str): The API path.
            timespan_seconds (int): The timespan in seconds to look back.
            limitToLast (int, optional): Limit the number of results. Defaults to None.
            call (str, optional): Identifier for the API call. Defaults to "Get_recent".

        Returns:
            list: A sorted list of recent items.
        """
        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))

        params = {
            "orderBy": '"timestamp"',
            "startAt": past_epoch_js,
            "endAt": now_epoch_js,
            "auth": self.auth_token()
        }

        if limitToLast:
            params["limitToLast"] = limitToLast

        endpoint = "{server}{path}.json".format(server=self.EDR_SERVER, path=path)
        EDR_LOG.debug("Get recent; endpoint: {}".format(endpoint))
        results = self.__get(endpoint, "EDR", params, call=call)

        if results is None:
            EDR_LOG.error("Failed to retrieve recent items due to network error.")
            return []

        if not results:
            EDR_LOG.info(f"No recent items found for {call}.")
            return []

        # When using Firebase's REST API, the filtered results are returned in an undefined order since JSON interpreters don't enforce any ordering.
        # So, sorting has to be done on the client side
        sorted_results = sorted(results.values(), key=lambda t: t["timestamp"], reverse=True)
        return sorted_results

    def recent_crimes(self, system_id, timespan_seconds):
        """
        Fetch recent crimes in a system.

        Args:
            system_id (str): The ID of the system.
            timespan_seconds (int): The timespan in seconds to look back.

        Returns:
            list: A list of recent crime reports.
        """
        if not self.__preflight("recent_crimes", system_id):
            EDR_LOG.debug("Preflight failed for recent_crimes call.")
            raise CommsJammedError("recent_crimes")

        EDR_LOG.info("Recent crimes for system {sid}".format(sid=system_id))
        endpoint = "/v1/crimes/{sid}/".format(sid=system_id)
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50, call="Recent_crimes")

    def recent_traffic(self, system_id, timespan_seconds):
        """
        Fetch recent traffic in a system.

        Args:
            system_id (str): The ID of the system.
            timespan_seconds (int): The timespan in seconds to look back.

        Returns:
            list: A list of recent traffic reports.
        """
        if not self.__preflight("recent_traffic", system_id):
            EDR_LOG.debug("Preflight failed for recent_traffic call.")
            raise CommsJammedError("recent_traffic")

        EDR_LOG.info("Recent traffic for system {sid}".format(sid=system_id))
        endpoint = "/v1/traffic/{sid}/".format(sid=system_id)
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50, call="Recent_traffic")

    def recent_outlaws(self, timespan_seconds):
        """
        Fetch recent outlaws sighted.

        Args:
            timespan_seconds (int): The timespan in seconds to look back.

        Returns:
            list: A list of recently sighted outlaws.
        """
        if not self.__preflight("recent_outlaws", timespan_seconds):
            EDR_LOG.debug("Preflight failed for recent_outlaws call.")
            raise CommsJammedError("recent_outlaws")

        EDR_LOG.info("Recently sighted outlaws")
        endpoint = "/v1/outlaws/"
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50, call="Recent_outlaws")

    def recent_enemies(self, timespan_seconds, power):
        """
        Fetch recent enemies for a power.

        Args:
            timespan_seconds (int): The timespan in seconds to look back.
            power (str): The power name.

        Returns:
            list: A list of recently sighted enemies.
        """
        if not self.__preflight("recent_enemies", power):
            EDR_LOG.debug("Preflight failed for recent_enemies call.")
            raise CommsJammedError("recent_enemies")

        EDR_LOG.info("Recently sighted enemies")
        endpoint = "/v1/powerplay/{}/enemies/".format(self.nodify(power))
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50, call="Recent_enemies")

    def heartbeat(self):
        """
        Send a heartbeat to the server.

        Returns:
            dict: The heartbeat response data or None.
        """
        EDR_LOG.info("Sending heartbeat")
        endpoint = "{}/heartbeat".format(self.EDR_SERVER_FUNCTIONS)
        params = {"uid": self.uid()}
        data = self.__get(endpoint, "EDR", params, call="Heartbeat")

        if data is None:
            EDR_LOG.error("Heartbeat failed.")
            return None

        EDR_LOG.info("Heartbeat response: {}".format(data))
        return data

    def where(self, name, power=None):
        """
        Locate an opponent.

        Args:
            name (str): The name of the opponent.
            power (str, optional): The power the opponent is associated with. Defaults to None.

        Returns:
            dict: Sighting information or None.
        """
        if not self.__preflight("where", name):
            EDR_LOG.debug("Preflight failed for where call.")
            raise CommsJammedError("where")

        EDR_LOG.info("Where query for opponent named '{}'".format(name))
        endpoint = "{}/v1/".format(self.EDR_SERVER)
        if power:
            endpoint += "powerplay/{}/enemies.json".format(self.nodify(power))
        else:
            endpoint += "outlaws.json"
        params = {
            "orderBy": '"cname"',
            "equalTo": json.dumps(name.lower()),
            "limitToFirst": 1,
            "auth": self.auth_token()
        }

        sighting = self.__get(endpoint, "EDR", params, call="Where")

        if sighting is None:
            EDR_LOG.error(f"Network error or throttled during 'where' query for {name}.")
            return None

        if sighting:
            sid = list(sighting)[0]
            return sighting[sid]

        return None

    def update_cmdrdex(self, cmdr_id, dex_entry):
        """
        Update a commander's DEX entry.

        Args:
            cmdr_id (str): The ID of the commander.
            dex_entry (dict): The DEX entry to update or None to remove.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if self.is_anonymous():
            return False
        dex_path = "/v1/cmdrsdex/{}/".format(self.uid())
        if dex_entry is None:
            return self.__remove_dex(dex_path, cmdr_id)

        return self.__update_dex(dex_path, cmdr_id, dex_entry)

    def cmdrdex(self, cmdr_id):
        """
        Get a commander's DEX entry.

        Args:
            cmdr_id (str): The ID of the commander.

        Returns:
            dict: The DEX entry for the commander or None.
        """
        if self.is_anonymous():
            return None
        dex_path = "/v1/cmdrsdex/{}/".format(self.uid())
        return self.__dex(dex_path, cmdr_id)

    def update_sqdrdex(self, sqdr_id, cmdr_id, dex_entry):
        """
        Update a squadron DEX entry.

        Args:
            sqdr_id (str): The ID of the squadron.
            cmdr_id (str): The ID of the commander within the squadron.
            dex_entry (dict): The DEX entry to update or None to remove.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if self.is_anonymous():
            return False
        dex_path = "/v1/sqdrsdex/{}/".format(sqdr_id)
        if dex_entry is None:
            return self.__remove_dex(dex_path, cmdr_id)

        return self.__update_dex(dex_path, cmdr_id, dex_entry)

    def sqdrdex(self, sqdr_id, cmdr_id):
        """
        Get a squadron DEX entry.

        Args:
            sqdr_id (str): The ID of the squadron.
            cmdr_id (str): The ID of the commander within the squadron.

        Returns:
            dict: The DEX entry for the commander in the squadron or None.
        """
        if self.is_anonymous():
            return None
        dex_path = "/v1/sqdrsdex/{}/".format(sqdr_id)
        return self.__dex(dex_path, cmdr_id)

    def __update_dex(self, dex_path, cmdr_id, dex_entry):
        """
        Helper method to update a DEX entry.

        Args:
            dex_path (str): The base path for the DEX.
            cmdr_id (str): The ID of the commander.
            dex_entry (dict): The DEX entry data.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        params = {"auth": self.auth_token()}
        EDR_LOG.info("Dex entry for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=dex_entry))
        endpoint = "{server}{dex}{cid}/.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)

        result = self.__put(endpoint, "EDR", json=dex_entry, params=params, call="Update_dex")
        return result is not None

    def __remove_dex(self, dex_path, cmdr_id):
        """
        Helper method to remove a DEX entry.

        Args:
            dex_path (str): The base path for the DEX.
            cmdr_id (str): The ID of the commander.

        Returns:
            bool: True if the removal was successful, False otherwise.
        """
        EDR_LOG.info("Removing Dex entry for cmdr {cid}".format(cid=cmdr_id))

        endpoint = "{server}{dex}{cid}.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)
        params = {"auth": self.auth_token()}

        return self.__delete(endpoint, "EDR", params=params, call="Remove_dex")

    def __dex(self, dex_path, cmdr_id):
        """
        Helper method to get a DEX entry.

        Args:
            dex_path (str): The base path for the DEX.
            cmdr_id (str): The ID of the commander.

        Returns:
            dict: The DEX entry data or None.
        """
        EDR_LOG.debug("Dex request for {}".format(cmdr_id))
        params = {"auth": self.auth_token()}
        endpoint = "{server}{dex}{cid}/.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)
        EDR_LOG.debug("Endpoint: {}".format(endpoint))

        data = self.__get(endpoint, "EDR", params, call="Dex")
        EDR_LOG.debug("data= {}".format("None" if data is None else data))

        return data

    def contracts(self):
        """
        Get active contracts.

        Returns:
            dict: A dictionary of active contracts or None.
        """
        if self.is_anonymous():
            return None
        contracts_path = "/v1/contracts/{}".format(self.uid())
        EDR_LOG.debug("Contracts request")
        params = {"auth": self.auth_token()}
        endpoint = "{server}{con}.json".format(server=self.EDR_SERVER, con=contracts_path)
        EDR_LOG.debug("Endpoint: {}".format(endpoint))
        data = self.__get(endpoint, "EDR", params, call="Contracts")
        EDR_LOG.debug("data= {}".format("None" if data is None else data))

        return data

    def contract_for(self, cmdr_id):
        """
        Get contract for a specific commander.

        Args:
            cmdr_id (str): The ID of the commander.

        Returns:
            dict: The contract details for the commander or None.
        """
        if self.is_anonymous():
            return None
        contracts_path = "/v1/contracts/{}/".format(self.uid())
        EDR_LOG.debug("Contract request for {}".format(cmdr_id))
        params = {"auth": self.auth_token()}
        endpoint = "{server}{con}{cid}/.json".format(server=self.EDR_SERVER, con=contracts_path, cid=cmdr_id)
        EDR_LOG.debug("Endpoint: {}".format(endpoint))
        data = self.__get(endpoint, "EDR", params, call="Contract_for")
        EDR_LOG.debug("data= {}".format("None" if data is None else data))

        return data

    def place_contract(self, cmdr_id, contract_entry):
        """
        Place a new contract.

        Args:
            cmdr_id (str): The ID of the commander for whom the contract is placed.
            contract_entry (dict): The contract details.

        Returns:
            bool: True if the contract was placed successfully, False otherwise.
        """
        if self.is_anonymous() or contract_entry is None:
            return False
        contract_path = "/v1/contracts/{}/".format(self.uid())

        return self.__update_contract(contract_path, cmdr_id, contract_entry)

    def remove_contract(self, cmdr_id):
        """
        Remove a contract.

        Args:
            cmdr_id (str): The ID of the commander whose contract is to be removed.

        Returns:
            bool: True if the contract was removed successfully, False otherwise.
        """
        if self.is_anonymous():
            return False
        contract_path = "/v1/contracts/{}/".format(self.uid())
        return self.__remove_contract(contract_path, cmdr_id)

    def __update_contract(self, contract_path, cmdr_id, contract_entry):
        """
        Helper method to update a contract.

        Args:
            contract_path (str): The base path for contracts.
            cmdr_id (str): The ID of the commander.
            contract_entry (dict): The contract details.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        params = {"auth": self.auth_token()}
        EDR_LOG.info("Contract entry for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=contract_entry))
        endpoint = "{server}{contract}{cid}/.json".format(server=self.EDR_SERVER, contract=contract_path, cid=cmdr_id)

        result = self.__put(endpoint, "EDR", json=contract_entry, params=params, call="Update_contract")
        return result is not None

    def __remove_contract(self, contract_path, cmdr_id):
        """
        Helper method to remove a contract.

        Args:
            contract_path (str): The base path for contracts.
            cmdr_id (str): The ID of the commander.

        Returns:
            bool: True if the removal was successful, False otherwise.
        """
        EDR_LOG.info("Removing contract entry for cmdr {cid}".format(cid=cmdr_id))

        endpoint = "{server}{contract}{cid}.json".format(server=self.EDR_SERVER, contract=contract_path, cid=cmdr_id)
        params = {"auth": self.auth_token()}

        return self.__delete(endpoint, "EDR", params=params, call="Remove_contract")

    def preflight_realtime(self, kind):
        """
        Check if realtime updates are allowed.

        Args:
            kind (str): The type of realtime update.

        Returns:
            bool: True if preflight check passes, False otherwise.

        Raises:
            CommsJammedError: If the preflight check fails.
        """
        api_name = "realtime_{}".format(kind.lower())
        if not self.__preflight(api_name, "n/a"):
            raise CommsJammedError(api_name)
        return True

    def __preflight(self, api_name, param):
        """
        Perform a preflight check for an API call.

        Args:
            api_name (str): The name of the API call.
            param (str): A parameter related to the API call.

        Returns:
            bool: True if the preflight check is successful, False otherwise.
        """
        headers = {
            "Authorization": "Bearer {}".format(self.auth_token()),
        }

        payload = {
            "name": self.player_name,
            "timestamp": {".sv": "timestamp"},
            "param": param,
            "api": api_name,
            "mode": self.game_mode,
            "dlc": self.dlc_name,
            "group": self.private_group
        }

        EDR_LOG.debug("Preflight request for {} with {}".format(api_name, payload))
        endpoint = "{server_functions}/edr/v1/preflight/{uid}".format(server_functions=self.EDR_SERVER_FUNCTIONS, uid=self.uid())

        result = self.__put(endpoint, "EDR", json=payload, headers=headers, call=f"Preflight_{api_name}")
        return result is not None

class CommsJammedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)