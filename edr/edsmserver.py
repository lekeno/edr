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
        params = {"systemName": system_name, "showCoordinates": 1}
        endpoint = "{}/api-v1/systems".format(self.EDSM_SERVER)
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve system {} from EDSM: {}.".format(system_name, resp.status_code), "ERROR")
            return None
        
        return json.loads(resp.content)
