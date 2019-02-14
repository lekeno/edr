import json
import urllib
import calendar
import time

import edrcmdrprofile
import RESTFirebase
import edrconfig
import edrlog

import requests
import urllib


EDRLOG = edrlog.EDRLog()

class EDRServer(object):
    @staticmethod
    def nodify(name):
        return name.lower().replace(" ", "_")

    def __init__(self):
        config = edrconfig.EDRConfig()
        self.REST_firebase = RESTFirebase.RESTFirebaseAuth()
        self.EDR_API_KEY = config.edr_api_key()
        self.EDR_SERVER = config.edr_server()
        self.player_name = None
        self.game_mode = None
        self.private_group = None
        self.version = edrconfig.EDRConfig().edr_version()
        self._throttle_until_timestamp = None

    def login(self, email, password):
        self.REST_firebase.api_key = self.EDR_API_KEY
        self.REST_firebase.email = email
        self.REST_firebase.password = password

        return self.REST_firebase.authenticate()

    def logout(self):
        self.REST_firebase.clear_authentication()

    def set_player_name(self, name):
        self.player_name = name

    def set_game_mode(self, mode, group = None):
        self.game_mode = mode
        self.private_group = group

    def is_authenticated(self):
        return self.REST_firebase.is_valid_auth_token()

    def is_anonymous(self):
        return self.REST_firebase.anonymous

    def uid(self):
        return self.REST_firebase.uid()

    def auth_token(self):
        return self.REST_firebase.id_token()

    def server_version(self):
        endpoint = "{}/version/.json".format(self.EDR_SERVER)
        resp = requests.get(endpoint)
        
        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to check for version update. code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            return None

        return  json.loads(resp.content)
    
    def notams(self, timespan_seconds):
        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))
        future_epoch_js = 1830000000000L

        params = {"orderBy": '"timestamp"', "startAt": past_epoch_js, "endAt": future_epoch_js, "auth": self.auth_token(), "limitToLast": 10}
        resp = requests.get("{}/v1/notams.json".format(self.EDR_SERVER), params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve notams.", "ERROR")
            return None
        
        return json.loads(resp.content)


    def sitreps(self, timespan_seconds):
        if not self.__preflight("sitreps", timespan_seconds):
            EDRLOG.log(u"Preflight failed for sitreps call.", "DEBUG")
            raise CommsJammedError("sitreps")
        
        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))

        params = {"orderBy": '"timestamp"', "startAt": past_epoch_js, "endAt": now_epoch_js, "auth": self.auth_token(), "limitToLast": 30}
        resp = requests.get("{}/v1/systems.json".format(self.EDR_SERVER), params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve sitreps.", "ERROR")
            return None
        
        return json.loads(resp.content)

    def system_id(self, star_system, may_create):
        if not self.__preflight("system_id", star_system):
            EDRLOG.log(u"Preflight failed for system_id call.", "DEBUG")
            raise CommsJammedError("system_id")

        # Firebase rest API needs double quoted params (fixes issues with queries for systems with a "+")
        params = {"orderBy": '"cname"', "equalTo": json.dumps(star_system.lower()), "limitToFirst": 1, "auth": self.auth_token()}
        endpoint = "{}/v1/systems.json".format(self.EDR_SERVER)
        EDRLOG.log(u"system_id endpoint: {}".format(endpoint), "DEBUG")
        resp = requests.get(endpoint, params= params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve star system sid.", "ERROR")
            return None

        sid = None
        if resp.content == 'null':
            EDRLOG.log(u"System {} is not recorded in EDR.".format(star_system), "DEBUG")
            if may_create:
                EDRLOG.log(u"Creating system in EDR.", "DEBUG")
                params = { "auth" : self.auth_token() }
                resp = requests.post("{}/v1/systems.json".format(self.EDR_SERVER), params=params, json={"name": star_system, "uid" : self.uid()})
                if resp.status_code != requests.codes.ok:
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

    def pledged_to(self, power, since):
        params = { "auth": self.auth_token() }
        if power is None:
            EDRLOG.log(u"Removing pledge info for uid {uid}".format(uid=self.uid), "INFO")
            endpoint = "{server}/v1/pledges/{uid}/.json".format(server=self.EDR_SERVER, uid=self.uid())
            EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
            resp = requests.delete(endpoint, params=params)
            EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
            return resp.status_code == requests.codes.ok
        
        EDRLOG.log(u"Pledge info for uid {uid} with power:{power}".format(uid=self.uid(), power=power), "INFO")
        endpoint = "{server}/v1/pledges/{uid}/.json".format(server=self.EDR_SERVER, uid=self.uid())
        json = { "cpower": self.nodify(power), "since": int(since*1000), "heartbeat": {".sv": "timestamp"} }
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = requests.put(endpoint, params=params, json=json)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return resp.status_code == requests.codes.ok            
    
    def cmdr(self, cmdr, autocreate=True):
        if not self.__preflight("cmdr", cmdr):
            EDRLOG.log(u"Preflight failed for cmdr call.", "DEBUG")
            raise CommsJammedError("cmdr")
        cmdr_profile = edrcmdrprofile.EDRCmdrProfile()

        params = { "orderBy": '"cname"', "equalTo": json.dumps(urllib.quote_plus(cmdr.lower().encode('utf-8'))), "limitToFirst": 1, "auth": self.auth_token()}
        endpoint = "{}/v1/cmdrs.json".format(self.EDR_SERVER)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve cmdr id.", "ERROR")
            EDRLOG.log(u"{error}, {content}".format(error=resp.status_code, content=resp.content), "DEBUG")
            return None

        if resp.content == 'null':
            if autocreate and not self.is_anonymous():
                params = { "auth" : self.auth_token() }
                endpoint = "{}/v1/cmdrs.json".format(self.EDR_SERVER)
                resp = requests.post(endpoint, params=params, json={"name": cmdr, "uid" : self.uid()})
                if resp.status_code != requests.codes.ok:
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
        params = { "auth" : self.auth_token()}
        endpoint = "{server}{endpoint}.json".format(server=self.EDR_SERVER, endpoint=endpoint)
        EDRLOG.log(u"Post JSON {} to {}".format(json_payload, endpoint), "DEBUG")
        resp = requests.post(endpoint, params=params, json=json_payload)
        EDRLOG.log(u" resp= {}; {}".format(resp.status_code, resp.content), "DEBUG")
        return resp.status_code == requests.codes.ok

    def blip(self, cmdr_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Blip for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info), "INFO")
        endpoint = "/v1/blips/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info)

    def traffic(self, system_id, info):
        if not self.__preflight("traffic", system_id):
            EDRLOG.log(u"Preflight failed for traffic call.", "DEBUG")
            raise CommsJammedError("traffic")

        info["uid"] = self.uid()
        EDRLOG.log(u"Traffic report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/traffic/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info)

    def scanned(self, cmdr_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Scan for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info), "INFO")
        endpoint = "/v1/scans/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info)

    def legal_records(self, cmdr_id, timespan_seconds):
        EDRLOG.log(u"Fetching legal record for cmdr {cid}".format(cid=cmdr_id), "INFO")
        endpoint = "/v1/legal/{cmdr_id}/".format(cmdr_id=cmdr_id)
        legal_records_perday = 24
        records_over_timespan = int(max(1, round(timespan_seconds / 86400.0 * legal_records_perday)))
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=records_over_timespan)

    def crime(self, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Crime report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/crimes/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info)

    def fight(self, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Fight report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/fights/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info)

    def call_central(self, service, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Central call from system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/central/{service}/{system_id}/".format(service=service, system_id=system_id)
        return self.__post_json(endpoint, info)


    def crew_report(self, crew_id, report):
        EDRLOG.log(u"Multicrew session report: {}".format(report), "INFO")
        endpoint = "/v1/crew_reports/{}/".format(crew_id)
        return self.__post_json(endpoint, report)

    def __get_recent(self, path, timespan_seconds, limitToLast=None):
        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))

        params = { "orderBy": '"timestamp"', "startAt": past_epoch_js, "endAt": now_epoch_js, "auth": self.auth_token()}
        if limitToLast:
            params["limitToLast"] = limitToLast
        endpoint = "{server}{path}.json".format(server=self.EDR_SERVER, path=path)
        EDRLOG.log(u"Get recent; endpoint: {}".format(endpoint), "DEBUG")
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve recent items. Error code: {}".format(resp.status_code), "ERROR")
            return []
        
        results = json.loads(resp.content)
        if not results:
            EDRLOG.log(u"Empty recent items.", "INFO")
            return []
        # When using Firebase's REST API, the filtered results are returned in an undefined order since JSON interpreters don't enforce any ordering.
        # So, sorting has to be done on the client side
        sorted_results = sorted(results.values(), key=lambda t: t["timestamp"], reverse=True)
        return sorted_results

    def recent_crimes(self, system_id, timespan_seconds):
        if not self.__preflight("recent_crimes", system_id):
            EDRLOG.log(u"Preflight failed for recent_crimes call.", "DEBUG")
            raise CommsJammedError("recent_crimes")

        EDRLOG.log(u"Recent crimes for system {sid}".format(sid=system_id), "INFO")
        endpoint = "/v1/crimes/{sid}/".format(sid=system_id)
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50)

    def recent_traffic(self, system_id, timespan_seconds):
        if not self.__preflight("recent_traffic", system_id):
            EDRLOG.log(u"Preflight failed for recent_traffic call.", "DEBUG")
            raise CommsJammedError("recent_traffic")

        EDRLOG.log(u"Recent traffic for system {sid}".format(sid=system_id), "INFO")
        endpoint = "/v1/traffic/{sid}/".format(sid=system_id)
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50)

    def recent_outlaws(self, timespan_seconds):
        if not self.__preflight("recent_outlaws", timespan_seconds):
            EDRLOG.log(u"Preflight failed for recent_outlaws call.", "DEBUG")
            raise CommsJammedError("recent_outlaws")

        EDRLOG.log(u"Recently sighted outlaws", "INFO")
        endpoint = "/v1/outlaws/"
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50)

    def recent_enemies(self, timespan_seconds, power):
        if not self.__preflight("recent_enemies", power):
            EDRLOG.log(u"Preflight failed for recent_enemies call.", "DEBUG")
            raise CommsJammedError("recent_enemies")

        EDRLOG.log(u"Recently sighted enemies", "INFO")                
        endpoint = "/v1/powerplay/{}/enemies/".format(self.nodify(power))
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=50)

    def heartbeat(self):
        EDRLOG.log(u"Sending heartbeat", "INFO")                
        endpoint = "https://us-central1-blistering-inferno-4028.cloudfunctions.net/heartbeat"
        params = {"uid": self.uid() }
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Heartbeat failed. Error code: {}".format(resp.status_code), "ERROR")
            return None
        EDRLOG.log(u"Heartbeat response: {}".format(resp.content), "INFO")
        return json.loads(resp.content)
    
    def where(self, name, power=None):
        if not self.__preflight("where", name):
            EDRLOG.log(u"Preflight failed for where call.", "DEBUG")
            raise CommsJammedError("where")

        EDRLOG.log(u"Where query for opponent named '{}'".format(name), "INFO")
        params = {"orderBy": '"cname"', "equalTo": json.dumps(name.lower()), "limitToFirst": 1, "auth": self.auth_token() }
        endpoint = "{}/v1/".format(self.EDR_SERVER)
        if power:
            endpoint += "powerplay/{}/enemies.json".format(self.nodify(power))
        else:
            endpoint += "outlaws.json"
        resp = requests.get(endpoint, params=params)

        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Failed to retrieve location of an oppponent.", "ERROR")
            return None
        
        sighting = json.loads(resp.content)
        if sighting:
            sid = sighting.keys()[0]
            return sighting[sid]
        return None

    def update_cmdrdex(self, cmdr_id, dex_entry):
        if self.is_anonymous():
            return False
        dex_path = "/v1/cmdrsdex/{}/".format(self.uid())
        if dex_entry is None:
            return self.__remove_dex(dex_path, cmdr_id)
        
        return self.__update_dex(dex_path, cmdr_id, dex_entry)    

    def cmdrdex(self, cmdr_id):
        if self.is_anonymous():
            return None
        dex_path = "/v1/cmdrsdex/{}/".format(self.uid())
        return self.__dex(dex_path, cmdr_id)

    def update_sqdrdex(self, sqdr_id, cmdr_id, dex_entry):
        if self.is_anonymous():
            return False
        dex_path = "/v1/sqdrsdex/{}/".format(sqdr_id)
        if dex_entry is None:
            return self.__remove_dex(dex_path, cmdr_id)
        
        return self.__update_dex(dex_path, cmdr_id, dex_entry)

    def sqdrdex(self, sqdr_id, cmdr_id):
        if self.is_anonymous():
            return None
        dex_path = "/v1/sqdrsdex/{}/".format(sqdr_id)
        return self.__dex(dex_path, cmdr_id)

    def __update_dex(self, dex_path, cmdr_id, dex_entry):
        params = { "auth" : self.auth_token()}
        EDRLOG.log(u"Dex entry for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=dex_entry), "INFO")
        endpoint = "{server}{dex}{cid}/.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {} with {}".format(endpoint, dex_entry), "DEBUG")
        resp = requests.put(endpoint, params=params, json=dex_entry)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return resp.status_code == requests.codes.ok

    def __remove_dex(self, dex_path, cmdr_id):
        params = { "auth" : self.auth_token()}
        EDRLOG.log(u"Removing Dex entry for cmdr {cid}".format(cid=cmdr_id), "INFO")
        endpoint = "{server}{dex}{cid}.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = requests.delete(endpoint, params=params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return resp.status_code == requests.codes.ok
    
    def __dex(self, dex_path, cmdr_id):
        EDRLOG.log(u"Dex request for {}".format(cmdr_id), "DEBUG")
        params = { "auth" : self.auth_token()}
        endpoint = "{server}{dex}{cid}/.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = requests.get(endpoint, params=params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")

        if resp.status_code == requests.codes.ok:
            return json.loads(resp.content)
        else:
            return None

    def preflight_realtime(self, kind):
        api_name = u"realtime_{}".format(kind.lower())
        if not self.__preflight(api_name, "n/a"):
            raise CommsJammedError(api_name)
        return True

    def __preflight(self, api_name, param):
        headers = {"Authorization": "Bearer {}".format(self.auth_token()), "EDR-Version": "v{}".format(self.version) }
        json = { "name": self.player_name, "timestamp": {".sv": "timestamp"}, "param": param, "api": api_name, "mode": self.game_mode, "group": self.private_group }
        EDRLOG.log(u"Preflight request for {} with {}".format(api_name, json), "DEBUG")
        endpoint = "https://us-central1-blistering-inferno-4028.cloudfunctions.net/edr/v1/preflight/{uid}".format(server=self.EDR_SERVER, uid=self.uid())
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = requests.put(endpoint, headers=headers, json=json)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return resp.status_code == requests.codes.ok

class CommsJammedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)