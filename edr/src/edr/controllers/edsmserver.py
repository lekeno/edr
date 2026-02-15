
import re
import time
import requests

from edr.core.edrconfig import EDR_CONFIG # EDR_INTERNAL
from edr.core.edrlog import EDR_LOG # EDR_INTERNAL
from edr.utils.backoff import Backoff
from edr.utils.edtime import EDTime # EDR_INTERNAL
from edr.utils.edrhttpcache import EDRHttpCache # EDR_INTERNAL


class EDSMServer:
    """
    Client for the EDSM API.
    """
    SESSION = requests.Session()

    def __init__(self):
        self.edsm_api_key = EDR_CONFIG.edsm_api_key()
        self.edsm_server_url = EDR_CONFIG.edsm_server()
        self.backoff = Backoff("EDSM")
        self.http_cache = EDRHttpCache()

    def system(self, system_name):
        """
        Get information about a system.
        """
        params = {
            "systemName": system_name,
            "showCoordinates": 1,
            "showInformation": 1,
            "showId": 1,
            "showPermit": 1,
            "showPrimaryStar": 1
        }
        endpoint = f"{self.edsm_server_url}/api-v1/systems"
        return self._get(endpoint, params)

    def bodies(self, system_name):
        """
        Get bodies in a system.
        """
        params = {"systemName": system_name}
        endpoint = f"{self.edsm_server_url}/api-system-v1/bodies"
        system_and_bodies = self._get(endpoint, params)

        if not system_and_bodies:
            return None
        return system_and_bodies.get("bodies", None)

    def systems_within_radius(self, system_name, radius):
        """
        Get unique systems within a radius of a system.
        """
        params = {
            "systemName": system_name,
            "showCoordinates": 1,
            "radius": radius,
            "showInformation": 1,
            "showId": 1,
            "showPermit": 1
        }
        endpoint = f"{self.edsm_server_url}/api-v1/sphere-systems"
        results = self._get(endpoint, params)

        if not isinstance(results, list):
            EDR_LOG.warning(f"Systems within radius is not a list, EDSM API may be having issues. Response: {results}")
            return None

        if not results:
            EDR_LOG.info("Empty systems within radius.")
            return []
        
        return sorted(results, key=lambda t: t["distance"])

    def system_value(self, system_name):
        """
        Get estimated value of a system.
        """
        params = {"systemName": system_name}
        endpoint = f"{self.edsm_server_url}/api-system-v1/estimated-value"
        return self._get(endpoint, params)

    def stations_in_system(self, system_name):
        """
        Get stations in a system.
        """
        params = {"systemName": system_name}
        endpoint = f"{self.edsm_server_url}/api-system-v1/stations"
        results = self._get(endpoint, params)

        if not results or not results.get('stations', None):
            EDR_LOG.info(f"No stations in system {system_name}.")
            return []
        
        return sorted(results['stations'], key=lambda t: t["distanceToArrival"])

    def factions_in_system(self, system_name):
        """
        Get factions in a system.
        """
        params = {"systemName": system_name}
        endpoint = f"{self.edsm_server_url}/api-system-v1/factions"
        return self._get(endpoint, params)

    def market(self, market_id):
        """
        Get market information for a station.
        """
        params = {"marketId": market_id}
        endpoint = f"{self.edsm_server_url}/api-system-v1/stations/market"
        return self._get(endpoint, params)

    def shipyard(self, market_id):
        """
        Get shipyard information for a station.
        """
        params = {"marketId": market_id}
        endpoint = f"{self.edsm_server_url}/api-system-v1/stations/shipyard"
        return self._get(endpoint, params)

    def outfitting(self, market_id):
        """
        Get outfitting information for a station.
        """
        params = {"marketId": market_id}
        endpoint = f"{self.edsm_server_url}/api-system-v1/stations/outfitting"
        return self._get(endpoint, params)

    def deaths(self, system_name):
        """
        Get death statistics for a system.
        """
        params = {"systemName": system_name}
        endpoint = f"{self.edsm_server_url}/api-system-v1/deaths"
        return self._get(endpoint, params)

    def traffic(self, system_name):
        """
        Get traffic statistics for a system.
        """
        params = {"systemName": system_name}
        endpoint = f"{self.edsm_server_url}/api-system-v1/traffic"
        return self._get(endpoint, params)

    def _get(self, endpoint, params, attempts=3):
        req = requests.Request('GET', endpoint, params=params)
        prepped = self.SESSION.prepare_request(req)
        cache_key = prepped.url

        cached = self.http_cache.get(cache_key)
        if cached is not None:
            EDR_LOG.debug(f"Cache hit for {cache_key}")
            return cached

        last_connection_exception = None
        while attempts > 0:
            attempts -= 1

            if self.backoff.throttled():
                EDR_LOG.debug("EDSM backoff active. Aborting.")
                return None

            try:
                resp = EDSMServer.SESSION.get(endpoint, params=params, timeout=5)

                if resp.status_code == requests.codes.ok:
                    self.backoff.reset()
                    data = resp.json()

                    cache_control = resp.headers.get("Cache-Control", "")
                    max_age_match = re.search(r"max-age=(\d+)", cache_control)
                    if max_age_match:
                        max_age = int(max_age_match.group(1))
                        self.http_cache.set(cache_key, data, max_age)
                        EDR_LOG.debug(f"Cached {cache_key} for {max_age}s")

                    return data

                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    retry_after = resp.headers.get("Retry-After")
                    epoch = None
                    if retry_after:
                        try:
                            dt = EDTime()
                            dt.from_http_header(retry_after)
                            epoch = dt.as_py_epoch()
                        except Exception:
                            pass

                    if epoch:
                        self.backoff.until(epoch)
                    else:
                        self.backoff.throttle()

                EDR_LOG.error(f"Failed to get from EDSM: status={resp.status_code}. Attempts left: {attempts}")

                if resp.status_code == 404:
                    return None

            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.warning(f"ConnectionException {e} for GET EDSM: attempts={attempts}")
                time.sleep(1)  # Grace period before retry

        if last_connection_exception:
            raise last_connection_exception

        return None
