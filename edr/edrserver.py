import json
import urllib
import calendar
import time

import edrcmdrprofile
import RESTFirebase
import edrconfig
import edrlog

import requests


EDRLOG = edrlog.EDRLog()

class EDRServer(object):

    def __init__(self):
        config = edrconfig.EDRConfig()
        self.REST_firebase = RESTFirebase.RESTFirebaseAuth()
        self.EDR_API_KEY = config.edr_api_key()
        self.EDR_SERVER = config.edr_server()

    def login(self, email, password):
        self.REST_firebase.api_key = self.EDR_API_KEY
        self.REST_firebase.email = email
        self.REST_firebase.password = password

        return self.REST_firebase.authenticate()

    def logout(self):
        self.REST_firebase.clear_authentication()

    def is_authenticated(self):
        return self.REST_firebase.is_valid_auth_token()

    def is_anonymous(self):
        return self.REST_firebase.anonymous

    def uid(self):
        return self.REST_firebase.uid()

    def auth_token(self):
        return self.REST_firebase.id_token()


    def server_version(self):
        endpoint = "{server}/version/.json".format(server=self.EDR_SERVER)
        resp = requests.get(endpoint)
        
        if resp.status_code != 200:
            EDRLOG.log(u"Failed to check for version update. code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            return None

        json_resp = json.loads(resp.content)
        return json_resp
    
    def notams(self, timespan_seconds):
        now_epoch_js = 1000 * calendar.timegm(time.gmtime())
        past_epoch_js = now_epoch_js - (1000 * timespan_seconds)
        future_epoch_js = 1830000000000L

        query_params = "orderBy=\"timestamp\"&startAt={past}&endAt={now}&auth={auth}".format(past=past_epoch_js, now=future_epoch_js, auth=self.auth_token())
        EDRLOG.log(u"query_params {}".format(query_params), "DEBUG")
        resp = requests.get("{server}/v1/notams.json?{query_params}".format(server=self.EDR_SERVER, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve notams.", "ERROR")
            return None
        
        return json.loads(resp.content)


    def sitreps(self, timespan_seconds):
        now_epoch_js = 1000 * calendar.timegm(time.gmtime())
        past_epoch_js = now_epoch_js - (1000 * timespan_seconds)

        query_params = "orderBy=\"timestamp\"&startAt={past}&endAt={now}&auth={auth}".format(past=past_epoch_js, now=now_epoch_js, auth=self.auth_token())
        resp = requests.get("{server}/v1/systems.json?{query_params}".format(server=self.EDR_SERVER, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve sitreps.", "ERROR")
            return None
        
        return json.loads(resp.content)

    def system_id(self, star_system, may_create):
        query_params = "orderBy=\"cname\"&equalTo={system}&limitToFirst=1&auth={auth}".format(system=json.dumps(star_system.lower()), auth=self.auth_token())
        resp = requests.get("{server}/v1/systems.json?{query_params}".format(
        server=self.EDR_SERVER, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve star system sid.", "ERROR")
            return None

        sid = None
        if resp.content == 'null':
            EDRLOG.log(u"System not recorded in EDR.", "DEBUG")
            if may_create:
                EDRLOG.log(u"Creating system in EDR.", "DEBUG")
                query_params = { "auth" : self.auth_token() }
                resp = requests.post("{server}/v1/systems.json?{query_params}".format(server=self.EDR_SERVER, query_params=urllib.urlencode(query_params)), json={"name": star_system, "uid" : self.uid()})
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
            server=self.EDR_SERVER, query_params=query_params)
        EDRLOG.log(u"Endpoint :" + endpoint, "DEBUG")
        resp = requests.get(endpoint)

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve cmdr id.", "ERROR")
            EDRLOG.log(u"{error}, {content}".format(error=resp.status_code, content=resp.content), "DEBUG")
            return None

        if resp.content == 'null':
            if autocreate:
                query_params = { "auth" : self.auth_token() }
                endpoint = "{server}/v1/cmdrs.json?{query_params}".format(server=self.EDR_SERVER, query_params=urllib.urlencode(query_params))
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

    def __post_json(self, endpoint, json_payload):
        query_params = { "auth" : self.auth_token()}
        endpoint = "{server}{endpoint}.json?{query_params}".format(server=self.EDR_SERVER, endpoint=endpoint, query_params=urllib.urlencode(query_params))
        EDRLOG.log(u"Post JSON to {}".format(endpoint), "DEBUG")
        resp = requests.post(endpoint, json=json_payload)
        EDRLOG.log(u" resp= {}; {}".format(resp.status_code, resp.content), "DEBUG")
        return resp.status_code == 200

    def blip(self, cmdr_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Blip for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info), "INFO")
        endpoint = "/v1/blips/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info)

    def traffic(self, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Traffic report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/traffic/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info)

    def scanned(self, cmdr_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Scan for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info), "INFO")
        endpoint = "/v1/scans/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info)

    # TODO connnect to load => client => ...
    def legal_record(self, cmdr_id):
        EDRLOG.log(u"Fetching legal record for cmdr {cid}".format(cid=cmdr_id), "INFO")
        endpoint = "/v1/legal/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__get_recent(endpoint, 60*60*24*7) #TODO proper parameter

    def crime(self,  system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Crime report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/crimes/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info)

    def __get_recent(self, endpoint, timespan_seconds):
        now_epoch_js = 1000 * calendar.timegm(time.gmtime())
        past_epoch_js = now_epoch_js - (1000 * timespan_seconds)

        query_params = "orderBy=\"timestamp\"&startAt={past}&endAt={now}&auth={auth}".format(past=past_epoch_js, now=now_epoch_js, auth=self.auth_token())
        resp = requests.get("{server}{endpoint}.json?{query_params}".format(server=self.EDR_SERVER, endpoint=endpoint, query_params=query_params))

        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve recent items.", "ERROR")
            return None
        
        results = json.loads(resp.content)
        # When using Firebase's REST API, the filtered results are returned in an undefined order since JSON interpreters don't enforce any ordering.
        # So, sorting has to be done on the client side
        sorted_results = sorted(results.values(), key=lambda t: t["timestamp"], reverse=True)
        return sorted_results

    def recent_crimes(self,  system_id, timespan_seconds):
        EDRLOG.log(u"Recent crimes for system {sid}".format(sid=system_id), "INFO")
        endpoint = "/v1/crimes/{sid}/".format(sid=system_id)
        return self.__get_recent(endpoint, timespan_seconds)

    def recent_traffic(self,  system_id, timespan_seconds):
        EDRLOG.log(u"Recent traffic for system {sid}".format(sid=system_id), "INFO")
        endpoint = "/v1/traffic/{sid}/".format(sid=system_id)
        return self.__get_recent(endpoint, timespan_seconds)

    def recent_outlaws(self, timespan_seconds):
        EDRLOG.log(u"Recently sighted outlaws", "INFO")
        endpoint = "/v1/outlaws/"
        return self.__get_recent(endpoint, timespan_seconds)
    
    def where(self, name):
        EDRLOG.log(u"Where query for outlaw named '{}'".format(name), "INFO")
        query_params = "orderBy=\"cname\"&equalTo={name}&limitToFirst=1&auth={auth}".format(name=json.dumps(name), auth=self.auth_token())
        endpoint = "{server}/v1/outlaws.json?{query_params}".format(server=self.EDR_SERVER, query_params=query_params)
        resp = requests.get(endpoint)
        if resp.status_code != 200:
            EDRLOG.log(u"Failed to retrieve location of outlaw.", "ERROR")
            return None
        
        sighting = json.loads(resp.content)
        if sighting:
            sid = sighting.keys()[0]
            return sighting[sid]
        return None

    def update_cmdrdex(self, cmdr_id, dex_entry):
        if self.is_anonymous():
            return False
        query_params = { "auth" : self.auth_token()}
        
        if dex_entry is None:
            EDRLOG.log(u"Removing CmdrDex entry for cmdr {cid}".format(cid=cmdr_id), "INFO")
            endpoint = "{server}/v1/cmdrsdex/{uid}/{cid}.json?{query_params}".format(server=self.EDR_SERVER, uid=self.uid(), cid=cmdr_id, query_params=urllib.urlencode(query_params))
            EDRLOG.log(u"Endpoint :" + endpoint, "DEBUG")
            resp = requests.delete(endpoint)
            EDRLOG.log(u"resp= {}; {}".format(resp.status_code, resp.content), "DEBUG")
            return resp.status_code == 200
        
        EDRLOG.log(u"CmdrDex entry for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=dex_entry), "INFO")
        endpoint = "{server}/v1/cmdrsdex/{uid}/{cid}/.json?{query_params}".format(server=self.EDR_SERVER, uid=self.uid(), cid=cmdr_id, query_params=urllib.urlencode(query_params))
        EDRLOG.log(u"Endpoint :" + endpoint, "DEBUG")
        resp = requests.put(endpoint, json=dex_entry)
        EDRLOG.log(u"resp= {}; {}".format(resp.status_code, resp.content), "DEBUG")

        return resp.status_code == 200

    def cmdrdex(self, cmdr_id):
        if self.is_anonymous():
            return None
        EDRLOG.log(u"CmdrDex request for {}".format(cmdr_id), "DEBUG")
        query_params = { "auth" : self.auth_token()}
        endpoint = "{server}/v1/cmdrsdex/{uid}/{cid}/.json?{query_params}".format(server=self.EDR_SERVER, uid=self.uid(), cid=cmdr_id, query_params=urllib.urlencode(query_params))
        EDRLOG.log(u"Endpoint :" + endpoint, "DEBUG")
        resp = requests.get(endpoint)
        EDRLOG.log(u"resp= {}; {}".format(resp.status_code, resp.content), "DEBUG")

        if resp.status_code == 200:
            return json.loads(resp.content)
        else:
            return None