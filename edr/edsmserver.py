
import requests
import re
import time

from edrconfig import EDR_CONFIG # EDR_INTERNAL
from edrlog import EDR_LOG # EDR_INTERNAL
from backoff import Backoff
from edtime import EDTime # EDR_INTERNAL
from edrhttpcache import EDRHttpCache # EDR_INTERNAL

class EDSMServer(object):

    SESSION = requests.Session()

    def __init__(self):
        config = EDR_CONFIG
        self.EDSM_API_KEY = config.edsm_api_key()
        self.EDSM_SERVER = config.edsm_server()
        self.backoff = Backoff("EDSM")
        self.http_cache = EDRHttpCache()


    def system(self, system_name):
        params = {"systemName": system_name, "showCoordinates": 1, "showInformation":1, "showId": 1, "showPermit": 1, "showPrimaryStar": 1}
        endpoint = "{}/api-v1/systems".format(self.EDSM_SERVER)
        return self.__get(endpoint, params)
        

    def bodies(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/bodies".format(self.EDSM_SERVER)
        system_and_bodies = self.__get(endpoint, params)
        
        if not system_and_bodies:
            return None
        return system_and_bodies.get("bodies", None)
        

    def systems_within_radius(self, system_name, radius):
        params = {"systemName": system_name, "showCoordinates": 1, "radius": radius, "showInformation": 1, "showId": 1, "showPermit": 1}
        endpoint = "{}/api-v1/sphere-systems".format(self.EDSM_SERVER)
        results = self.__get(endpoint, params) 
        
        if not isinstance(results, list):
            EDR_LOG.warning(u"Systems within radius is not a list, EDSM API may be having issues. Response: {}".format(results))
            return None

        if not results:
            EDR_LOG.info(u"Empty systems within radius.")
            return []
        sorted_results = sorted(results, key=lambda t: t["distance"])
        return sorted_results

    def system_value(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/estimated-value".format(self.EDSM_SERVER)
        system_value = self.__get(endpoint, params)
        
        if not system_value:
            return None
        return system_value
        

    def stations_in_system(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/stations".format(self.EDSM_SERVER)
        results = self.__get(endpoint, params)

        if not results or not results.get('stations', None):
            EDR_LOG.info(u"No stations in system {}.".format(system_name))
            return []
        sorted_results = sorted(results['stations'], key=lambda t: t["distanceToArrival"])
        return sorted_results


    def factions_in_system(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/factions".format(self.EDSM_SERVER)
        return self.__get(endpoint, params)


    def market(self, marketId):
        params = {"marketId": marketId}
        endpoint = "{}/api-system-v1/stations/market".format(self.EDSM_SERVER)
        return self.__get(endpoint, params)


    def shipyard(self, marketId):
        params = {"marketId": marketId}
        endpoint = "{}/api-system-v1/stations/shipyard".format(self.EDSM_SERVER)
        return self.__get(endpoint, params)


    def outfitting(self, marketId):
        params = {"marketId": marketId}
        endpoint = "{}/api-system-v1/stations/outfitting".format(self.EDSM_SERVER)
        return self.__get(endpoint, params)


    def deaths(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/deaths".format(self.EDSM_SERVER)
        return self.__get(endpoint, params)


    def traffic(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/traffic".format(self.EDSM_SERVER)
        return self.__get(endpoint, params)


    def __get(self, endpoint, params, attempts=3):
        req = requests.Request('GET', endpoint, params=params)
        prepped = self.SESSION.prepare_request(req)
        cache_key = prepped.url
        
        cached = self.http_cache.get(cache_key)
        if cached is not None:
            EDR_LOG.debug(u"Cache hit for {}".format(cache_key))
            return cached

        last_connection_exception = None
        while attempts > 0:
            attempts -= 1

            if self.backoff.throttled():
                EDR_LOG.debug(u"EDSM backoff active. Aborting.")
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
                        EDR_LOG.debug(u"Cached {} for {}s".format(cache_key, max_age))
                    
                    return data

                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    retry_after = resp.headers.get("Retry-After")
                    epoch = None
                    if retry_after:
                        try:
                            dt = EDTime()
                            dt.from_http_header(retry_after)
                            epoch = dt.as_py_epoch()
                        except:
                            pass
                    
                    if epoch:
                        self.backoff.until(epoch)
                    else:
                        self.backoff.throttle()
                
                EDR_LOG.error(u"Failed to get from EDSM: status={}. Attempts left: {}".format(resp.status_code, attempts))
                
                if resp.status_code == 404:
                    return None

            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.warning(u"ConnectionException {} for GET EDSM: attempts={}".format(e, attempts))
                time.sleep(1) # Grace period before retry

        if last_connection_exception:
            raise last_connection_exception
        
        return None