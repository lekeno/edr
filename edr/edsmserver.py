
import json
import requests

from edrconfig import EDRConfig
from edrlog import EDR_LOG
from backoff import Backoff
from edtime import EDTime
from edrhttpcache import EDRHttpCache

class EDSMServer(object):

    SESSION = requests.Session()

    def __init__(self):
        config = EDRConfig()
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
            EDR_LOG.log(u"Empty systems within radius.", "INFO")
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
            EDR_LOG.log(u"No stations in system {}.".format(system_name), "INFO")
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
        if self.backoff.throttled():
            return None

        req = requests.Request('GET', endpoint, params=params)
        prepped = self.SESSION.prepare_request(req)
        cached = self.http_cache.get(prepped.url)
        if cached is not None:
            EDR_LOG.debug(u"Cache hit for {}".format(prepped.url))
            return cached

        while attempts:
            try:
                attempts -= 1
                resp = EDSMServer.SESSION.get(endpoint, params=params)
                if resp.status_code != requests.codes.ok:
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
                        
                    EDR_LOG.error(u"Failed to get {} from EDSM: {}.".format(params, resp.status_code))
                    return None
                
                self.backoff.reset()
                if "Cache-Control" in resp.headers:
                    cc = resp.headers["Cache-Control"]
                    if "max-age" in cc:
                        try:
                            max_age = int(cc.split("max-age=")[1].split(",")[0])
                            self.http_cache.set(prepped.url, json.loads(resp.content), max_age)
                            EDR_LOG.debug(u"Cached {} for {}s".format(prepped.url, max_age))
                        except:
                            pass

                return json.loads(resp.content)
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.log(u"ConnectionException {} for GET EDSM: attempts={}".format(e, attempts), u"WARNING")
        raise last_connection_exception 
