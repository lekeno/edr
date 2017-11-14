import requests
import urllib
import json
import datetime
import edrcmdrprofile

class EDRInara(object):

    EDR_INARA_API_KEY = ""
    INARA_ENDPOINT = "https://inara.cz/inapi/v1/"

    def __init__(self):
        self.version = None
        self.cmdr_name = None

    def cmdr(self, cmdr_name):
        if self.version is None or self.cmdr_name is None:
            return

        payload = { "header": self.__api_header(), "events" : [self.__api_cmdrprofile(cmdr_name)] }

        resp = requests.post(self.INARA_ENDPOINT, json=payload)
        if resp.status_code != 200:
            print "[EDR]Failed to obtain cmdr profile from Inara. code={code}, content={content}".format(code=resp.status_code, content=resp.content)
            return None
        
        print "[EDR]Obtained a response from the Inara API."
        try:
            json_resp = json.loads(resp.content)
            if json_resp["events"][0]["eventStatus"] == 204:
                print "[EDR]cmdr {} was not found via the Inara API.".format(cmdr_name)
                return None
            elif json_resp["events"][0]["eventStatus"] != 200:
                print "[EDR]Error from Inara API. code={code}, content={content}".format(code=resp.status_code, content=resp.content)
                return None
        except:
            print "[EDR]Malformed cmdr profile response from Inara API? code={code}, content={content}".format(code=resp.status_code, content=resp.content)
            return None


        try:
            json_resp = json.loads(resp.content)["events"][0]["eventData"]
            profile = edrcmdrprofile.EDRCmdrProfile()
            profile.from_inara_api(json_resp)
            print "[EDR]Obtained a cmdr profile from Inara API."
            return profile
        except:
            print "[EDR]Malformed cmdr profile response from Inara API? code={code}, content={content}".format(code=resp.status_code, content=resp.content)
            return None        


    def __api_header(self):
        return {
            "appName": "Elidex",
            "appVersion": self.version,
            "isDeveloped": False,
            "APIkey": self.EDR_INARA_API_KEY,
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
