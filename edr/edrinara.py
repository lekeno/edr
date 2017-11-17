import urllib
import json
import datetime
import requests
import edrcmdrprofile
import edrconfig
import edrlog

EDRLOG = edrlog.EDRLog()

class EDRInara(object):

    def __init__(self):
        config = edrconfig.EDRConfig()
        self.version = config.edr_version()
        self.INARA_API_KEY = config.inara_api_key()
        self.INARA_ENDPOINT = config.inara_endpoint()
        self.cmdr_name = None

    def cmdr(self, cmdr_name):
        if self.version is None or self.cmdr_name is None:
            return

        payload = { "header": self.__api_header(), "events" : [self.__api_cmdrprofile(cmdr_name)] }

        resp = requests.post(self.INARA_ENDPOINT, json=payload)
        if resp.status_code != 200:
            EDRLOG.log(u"Failed to obtain cmdr profile from Inara. code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            return None
        
        EDRLOG.log(u"Obtained a response from the Inara API.", "INFO")
        try:
            json_resp = json.loads(resp.content)
            if json_resp["events"][0]["eventStatus"] == 204:
                EDRLOG.log(u"cmdr {} was not found via the Inara API.".format(cmdr_name), "INFO")
                return None
            elif json_resp["events"][0]["eventStatus"] != 200:
                EDRLOG.log(u"Error from Inara API. code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
                return None
        except:
            EDRLOG.log(u"Malformed cmdr profile response from Inara API? code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            return None


        try:
            json_resp = json.loads(resp.content)["events"][0]["eventData"]
            profile = edrcmdrprofile.EDRCmdrProfile()
            profile.from_inara_api(json_resp)
            EDRLOG.log(u"Obtained a cmdr profile from Inara API.", "INFO")
            return profile
        except:
            EDRLOG.log(u"Malformed cmdr profile response from Inara API? code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            return None        


    def __api_header(self):
        return {
            "appName": "Elidex",
            "appVersion": self.version,
            "isDeveloped": False,
            "APIkey": self.INARA_API_KEY,
            "commanderName": self.cmdr_name
        }

    def __api_cmdrprofile(self, cmdr_name):
        return {
            "eventName": "getCommanderProfile",
            "eventTimestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "eventData": {
                "searchName": cmdr_name
            }
        }
