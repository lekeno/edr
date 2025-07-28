
import json

from edrconfig import EDRConfig
from edrlog import EDR_LOG

import requests




class EDSMServer(object):

    SESSION = requests.Session()

    def __init__(self):
        config = EDRConfig()
        self.EDSM_API_KEY = config.edsm_api_key()
        self.EDSM_SERVER = config.edsm_server()


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
        while attempts:
            try:
                attempts -= 1
                resp = EDSMServer.SESSION.get(endpoint, params=params)
                if resp.status_code != requests.codes.ok:
                    EDR_LOG.log(u"Failed to get {} from EDSM: {}.".format(params, resp.status_code), "ERROR")
                    return None
                
                return json.loads(resp.content)
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDR_LOG.log(u"ConnectionException {} for GET EDSM: attempts={}".format(e, attempts), u"WARNING")
        raise last_connection_exception 
