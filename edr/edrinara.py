import urllib
import json
import datetime
import requests
import edrcmdrprofile
import edrconfig
import edrlog
import random
from edtime import EDTime

EDRLOG = edrlog.EDRLog()

class EDRInara(object):

    SESSION = requests.Session()

    def __init__(self):
        config = edrconfig.EDRConfig()
        self.version = config.edr_version()
        self.INARA_API_KEY = config.inara_api_key()
        self.INARA_ENDPOINT = config.inara_endpoint()
        self.requester = None
        self.backoff_until = 0 
        self.attempt = 0

    def squadron(self, cmdr_name):
        if self.requester is None:
            return None
        json_resp = self.__cmdr(cmdr_name)
        try:
            squadron = json_resp["commanderWing"]
            return { "id": squadron["wingID"], "name": squadron["wingName"], "rank": squadron["wingMemberRank"] }
        except:
            return None

    
    def cmdr(self, cmdr_name):
        if self.requester is None:
            return
        json_resp = self.__cmdr(cmdr_name)
        if json_resp:
            profile = edrcmdrprofile.EDRCmdrProfile()
            profile.from_inara_api(json_resp)
            EDRLOG.log(u"Obtained a cmdr profile from Inara API.", "INFO")
            return profile
        return None
        

    def __cmdr(self, cmdr_name):
        payload = { "header": self.__api_header(), "events" : [self.__api_cmdrprofile(cmdr_name)] }
        resp = None
        if self.__should_hold_back():
            EDRLOG.log(u"Backing off from calling Inara until {} (now={})".format(self.backoff_until, EDTime.py_epoch_now()), "DEBUG")
            return None

        try:
            resp = EDRInara.SESSION.post(self.INARA_ENDPOINT, json=payload)
            if resp.status_code != requests.codes.ok:
                EDRLOG.log(u"Failed to obtain cmdr profile from Inara. code={code}".format(code=resp.status_code), "ERROR")
                return None
        except:
            EDRLOG.log(u"Communication with Inara failed: code={code}".format(code=resp.status_code), "ERROR")
            return None
            
        EDRLOG.log(u"Obtained a response from the Inara API.", "INFO")
        try:
            json_resp = json.loads(resp.content)
            if json_resp["header"]["eventStatus"] == 400:
                EDRLOG.log(u"Too much requests for Inara.", "INFO")
                self.__backoff()
                return None
            if json_resp["events"][0]["eventStatus"] == 204:
                EDRLOG.log(u"cmdr {} was not found via the Inara API.".format(cmdr_name), "INFO")
                self.attempt = 0
                return None
            elif json_resp["events"][0]["eventStatus"] != requests.codes.ok:
                EDRLOG.log(u"Error from Inara API. code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
                self.__backoff()
                return None
        except:
            EDRLOG.log(u"Malformed response from Inara API? code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            self.__backoff()
            return None

        try:
            json_resp = json.loads(resp.content)["events"][0]["eventData"]
            self.attempt = 0
            return json_resp
        except:
            EDRLOG.log(u"Malformed cmdr profile response from Inara API? code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            self.__backoff()
            return None

    def __api_header(self):
        return {
            "appName": "EDRecon",
            "appVersion": self.version,
            "isDeveloped": False,
            "APIkey": self.INARA_API_KEY,
            "commanderName": self.requester
        }

    def __api_cmdrprofile(self, cmdr_name):
        return {
            "eventName": "getCommanderProfile",
            "eventTimestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "eventData": {
                "searchName": cmdr_name
            }
        }

    def __backoff(self):
        base = 10
        cap = 60 * 60 * 2
        self.attempt += 1
        self.backoff_until = EDTime.py_epoch_now() + min(cap, base * 2 ** self.attempt) + random.randint(0, 60)
        EDRLOG.log(u"Exponential backoff for Inara API calls: attempts={}, until={}".format(self.attempt, self.backoff_until), "DEBUG")

    def __should_hold_back(self):
        hold = EDTime.py_epoch_now() < self.backoff_until
        if not hold:
            self.attempt = 0
            self.backoff_until = 0
        return hold


