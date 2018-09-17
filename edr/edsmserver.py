import json
import urllib

import edrconfig
import edrlog

import requests
import urllib


EDRLOG = edrlog.EDRLog()

class EDSMServer(object):

    def __init__(self):
        config = edrconfig.EDRConfig()
        self.EDSM_API_KEY = config.edsm_api_key()
        self.EDSM_SERVER = config.edsm_server()

    def system(self, system_name):
        params = {"systemName": system_name, "showCoordinates": 1, "showInformation":1, "showId": 1}
        endpoint = "{}/api-v1/systems".format(self.EDSM_SERVER)
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve system {} from EDSM: {}.".format(system_name, resp.status_code), "ERROR")
            return None
        
        return json.loads(resp.content)

    def systems_within_radius(self, system_name, radius):
        params = {"systemName": system_name, "showCoordinates": 1, "radius": radius, "showInformation": 1, "showId": 1, "showPermit": 1}
        endpoint = "{}/api-v1/sphere-systems".format(self.EDSM_SERVER)
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve system {} from EDSM: {}.".format(system_name, resp.status_code), "ERROR")
            return None

        results = json.loads(resp.content)
        if not results:
            EDRLOG.log(u"Empty systems within radius.", "INFO")
            return []
        sorted_results = sorted(results, key=lambda t: t["distance"])
        return sorted_results

    def stations_in_system(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/stations".format(self.EDSM_SERVER)
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve system {} from EDSM: {}.".format(system_name, resp.status_code), "ERROR")
            return None

        results = json.loads(resp.content)
        if not results or not results.get('stations', None):
            EDRLOG.log(u"No stations in system {}.".format(system_name), "INFO")
            return []
        sorted_results = sorted(results['stations'], key=lambda t: t["distanceToArrival"])
        return sorted_results

    def factions_in_system(self, system_name):
        params = {"systemName": system_name}
        endpoint = "{}/api-system-v1/factions".format(self.EDSM_SERVER)
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve state for system {} from EDSM: {}.".format(system_name, resp.status_code), "ERROR")
            return None

        return json.loads(resp.content)