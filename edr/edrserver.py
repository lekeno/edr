import json
import requests
import urllib

import edrcmdrprofile
import RESTFirebase
import edrconfig
import edrlog
import calendar
import datetime

EDRLOG = edrlog.EDRLog()

class EDRServer(object):

    def __init__(self):
        config = edrconfig.EDRConfig()
        self.REST_firebase = RESTFirebase.RESTFirebaseAuth()
        self.EDR_API_KEY = config.edr_api_key()
        self.EDR_ENDPOINT = config.edr_endpoint()


    def login(self, email, password):
        self.REST_firebase.api_key = self.EDR_API_KEY
        self.REST_firebase.email = email
        self.REST_firebase.password = password

        return self.REST_firebase.authenticate()

    def logout(self):
        self.REST_firebase.clear_authentication()

    def is_authenticated(self):
        return self.REST_firebase.is_valid_auth_token()

    def uid(self):
        return self.REST_firebase.uid()

    def auth_token(self):
        return self.REST_firebase.id_token()


    def server_version(self):
        endpoint = "{server}/version/.json".format(server=self.EDR_ENDPOINT)
        resp = requests.get(endpoint)
        
        if resp.status_code != 200:
            EDRLOG.log(u"Failed to check for version update. code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            return None

        json_resp = json.loads(resp.content)
        return json_resp
    
    def notams(self, timespan_seconds):
        now_epoch_js = 1000 * calendar.timegm(datetime.datetime.now().timetuple())
        past_epoch_js = now_epoch_js - (1000 * timespan_seconds)
        future_epoch_js = 1830000000000L

        query_params = "orderBy=\"timestamp\"&startAt={past}&endAt={now}&auth={auth}".format(past=past_epoch_js, now=future_epoch_js, auth=self.auth_token())
        resp = requests.get("{server}/v1/notams.json?{query_params}".format(server=self.EDR_ENDPOINT, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve notams.", "ERROR")
            return None
        
        return json.loads(resp.content)


    def sitreps(self, timespan_seconds):
        now_epoch_js = 1000 * calendar.timegm(datetime.datetime.now().timetuple())
        past_epoch_js = now_epoch_js - (1000 * timespan_seconds)

        query_params = "orderBy=\"timestamp\"&startAt={past}&endAt={now}&auth={auth}".format(past=past_epoch_js, now=now_epoch_js, auth=self.auth_token())
        resp = requests.get("{server}/v1/systems.json?{query_params}".format(server=self.EDR_ENDPOINT, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve sitreps.", "ERROR")
            return None
        
        return json.loads(resp.content)

    def system_id(self, star_system, may_create):
        query_params = "orderBy=\"cname\"&equalTo={system}&limitToFirst=1&auth={auth}".format(system=json.dumps(star_system.lower()), auth=self.auth_token())
        resp = requests.get("{server}/v1/systems.json?{query_params}".format(
        server=self.EDR_ENDPOINT, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve star system sid.", "ERROR")
            return None

        if resp.content == 'null':
            EDRLOG.log(u"System not recorded in EDR.", "DEBUG")
            if may_create:
                EDRLOG.log(u"Creating system in EDR.", "DEBUG")
                query_params = { "auth" : self.auth_token() }
                resp = requests.post("{server}/v1/systems.json?{query_params}".format(server=self.EDR_ENDPOINT, query_params=urllib.urlencode(query_params)), json={"name": star_system, "uid" : self.uid()})
                if resp.status_code != 200:
                    EDRLOG.log(u"Failed to create new star system.", "ERROR")
                    return None
                sid = json.loads(resp.content).values()[0]
                EDRLOG.log(u"Created system {} in EDR with id={}.".format(star_system, sid), "DEBUG")
            else:
                return None
        else:
            sid = json.loads(resp.content).keys()[0]
            EDRLOG.log(u"System {} is in EDR with id={}.".format(star_system, sid), "DEBUG")

        return sid


    def cmdr(self, cmdr, autocreate=True):
        cmdr_profile = edrcmdrprofile.EDRCmdrProfile()
        query_params = "orderBy=\"cname\"&equalTo={cmdr}&limitToFirst=1&auth={auth}".format(cmdr=json.dumps(cmdr.lower()), auth=self.auth_token())
        endpoint = "{server}/v1/cmdrs.json?{query_params}".format(
            server=self.EDR_ENDPOINT, query_params=query_params)
        EDRLOG.log(u"Endpoint :" + endpoint, "DEBUG")
        resp = requests.get(endpoint)

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve cmdr id.", "ERROR")
            EDRLOG.log(u"{error}, {content}".format(error=resp.status_code, content=resp.content), "DEBUG")
            return None

        if resp.content == 'null':
            if autocreate:
                query_params = { "auth" : self.auth_token() }
                endpoint = "{server}/v1/cmdrs.json?{query_params}".format(server=self.EDR_ENDPOINT, query_params=urllib.urlencode(query_params))
                resp = requests.post(endpoint, json={"name": cmdr, "uid" : self.uid()})
                if resp.status_code != 200:
                    EDRLOG.log(u"Failed to retrieve cmdr key.", "ERROR")
                    return None
                json_cmdr = json.loads(resp.content)
                EDRLOG.log(u"New cmdr:{}".format(json_cmdr), "DEBUG")
                cmdr_profile.cid = json_cmdr.values()[0]
                cmdr_profile.name = cmdr
            else:
                return None
        else:
            json_cmdr = json.loads(resp.content)
            EDRLOG.log(u"Existing cmdr:{}".format(json_cmdr), "DEBUG")
            cmdr_profile.cid = json_cmdr.keys()[0]
            cmdr_profile.from_dict(json_cmdr.values()[0])

        return cmdr_profile


    def blip(self, cmdr_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Blip for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info), "INFO")
        query_params = { "auth" : self.auth_token()}
        endpoint = "{server}/v1/blips/{cmdr_id}/.json?{query_params}".format(server=self.EDR_ENDPOINT, cmdr_id=cmdr_id, query_params=urllib.urlencode(query_params))
        EDRLOG.log(u"Endpoint :" + endpoint, "DEBUG")
        resp = requests.post(endpoint, json=info)

        return resp.status_code == 200


    def traffic(self, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Traffic report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        query_params = { "auth" : self.auth_token()}
        endpoint = "{server}/v1/traffic/{system_id}/.json?{query_params}".format(server=self.EDR_ENDPOINT, system_id=system_id, query_params=urllib.urlencode(query_params))
        EDRLOG.log(u"Endpoint :" + endpoint, "DEBUG")
        resp = requests.post(endpoint, json=info)

        return resp.status_code == 200


    def crime(self,  system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Crime report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        query_params = { "auth" : self.auth_token()}
        endpoint = "{server}/v1/crimes/{system_id}/.json?{query_params}".format(server=self.EDR_ENDPOINT, system_id=system_id, query_params=urllib.urlencode(query_params))
        resp = requests.post(endpoint, json=info)

        return resp.status_code == 200

    def recent_crimes(self,  system_id, timespan_seconds):
        EDRLOG.log(u"Recent crimes for system {sid}".format(sid=system_id), "INFO")
        now_epoch_js = 1000 * calendar.timegm(datetime.datetime.now().timetuple())
        past_epoch_js = now_epoch_js - (1000 * timespan_seconds)

        query_params = "orderBy=\"timestamp\"&startAt={past}&endAt={now}&auth={auth}".format(past=past_epoch_js, now=now_epoch_js, auth=self.auth_token())
        resp = requests.get("{server}/v1/crimes/{sid}/.json?{query_params}".format(server=self.EDR_ENDPOINT, sid=system_id, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve recent crimes.", "ERROR")
            return None
        
        return json.loads(resp.content)

    def recent_traffic(self,  system_id, timespan_seconds):
        EDRLOG.log(u"Recent traffic for system {sid}".format(sid=system_id), "INFO")
        now_epoch_js = 1000 * calendar.timegm(datetime.datetime.now().timetuple())
        past_epoch_js = now_epoch_js - (1000 * timespan_seconds)

        query_params = "orderBy=\"timestamp\"&startAt={past}&endAt={now}&auth={auth}".format(past=past_epoch_js, now=now_epoch_js, auth=self.auth_token())
        resp = requests.get("{server}/v1/traffic/{sid}/.json?{query_params}".format(server=self.EDR_ENDPOINT, sid=system_id, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve recent traffic.", "ERROR")
            return None
        
        return json.loads(resp.content)