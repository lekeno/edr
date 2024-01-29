# encoding: utf-8
import sys
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote # python 2.7.11
import urllib
import json
import calendar
import time

import edrcmdrprofile
import RESTFirebase
import edrconfig
import edrlog

import requests
import backoff


EDRLOG = edrlog.EDRLog()

class EDRServer(object):

    SESSION = requests.Session()

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
        self.dlc_name = None
        self.private_group = None
        self.version = edrconfig.EDRConfig().edr_version()
        self._throttle_until_timestamp = None
        self.anonymous_reports = None
        self.crimes_reporting = None
        self.fc_jump_psa = None
        self.backoff = {"EDR": backoff.Backoff(u"EDR"), "Inara": backoff.Backoff(u"Inara") }
        self.INARA_API_KEY = config.inara_api_key()

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

    def set_dlc(self, dlc):
        self.dlc_name = dlc

    def is_authenticated(self):
        return self.REST_firebase.is_valid_auth_token()

    def is_anonymous(self):
        return self.REST_firebase.anonymous

    def uid(self):
        return self.REST_firebase.uid()

    def auth_token(self):
        return self.REST_firebase.id_token()

    def refresh_auth(self):
        return self.REST_firebase.force_new_auth()

    def __check_response(self, response, service, call="Unknown"):
        if not response:
            return False
        
        EDRLOG.log(u"Checking response: service={}, call={}, status={}".format(service, call, response.status_code), "DEBUG")
        if response.status_code in [200, 404, 401, 403, 204]:
            self.backoff[service].reset()
        elif response.status_code in [429, 500]:
            self.backoff[service].throttle()
            
        return response.status_code == 200

    def __process_inara_response(self, resp):
        if not resp:
            return None

        json_resp = json.loads(resp)
        if not json_resp.get("body", None):
            return None
        
        body = json_resp["body"]
        
        try:
            if body["header"]["eventStatus"] == 400:
                EDRLOG.log(u"Too much requests for Inara.", "INFO")
                self.backoff["Inara"].throttle()
                return None
            if body["events"][0]["eventStatus"] == 204:
                EDRLOG.log(u"cmdr was not found via the Inara API: content={}.".format(resp), "INFO")
                self.backoff["Inara"].reset()
                return None
            if body["events"][0]["eventStatus"] != 200:
                EDRLOG.log(u"Error from Inara API. content={}".format(resp), "ERROR")
                self.backoff["Inara"].throttle()
                return None
        except:
            EDRLOG.log(u"Malformed response from Inara API? content={}".format(resp), "ERROR")
            self.backoff["Inara"].throttle()
            return None

        try:
            data = body["events"][0]["eventData"]
            self.backoff["Inara"].reset()
            return data
        except:
            EDRLOG.log(u"Malformed cmdr profile response from Inara API? content={}".format(resp), "ERROR")
            self.backoff["Inara"].throttle()
        return None

    def __get(self, endpoint, service, params=None, headers=None, attempts=3):
        if self.backoff[service].throttled():
            return None
        
        while attempts:
            try:
                attempts -= 1
                return EDRServer.SESSION.get(endpoint, params=params, headers=headers)
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDRLOG.log(u"ConnectionException {} for GET EDR: attempts={}".format(e, attempts), u"WARNING")
        raise last_connection_exception

    def __put(self, endpoint, service, json, params=None, headers=None, attempts=3):
        if self.backoff[service].throttled():
            return None

        while attempts:
            try:
                attempts -= 1
                return EDRServer.SESSION.put(endpoint, params=params, json=json, headers=headers)
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDRLOG.log(u"ConnectionException {} for PUT EDR: attempts={}".format(e, attempts), u"WARNING")
        raise last_connection_exception
    
    def __delete(self, endpoint, service, params=None, attempts=3):
        if self.backoff[service].throttled():
            return None

        while attempts:
            try:
                attempts -= 1
                return EDRServer.SESSION.delete(endpoint, params=params)
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDRLOG.log(u"ConnectionException {} for DELETE EDR: attempts={}".format(e, attempts), u"WARNING")
        raise last_connection_exception
        

    def __post(self, endpoint, service, json, params=None, attempts=3):
        if self.backoff[service].throttled():
            return None
        
        while attempts:
            try:
                attempts -= 1
                return EDRServer.SESSION.post(endpoint, params=params, json=json)
            except requests.exceptions.RequestException as e:
                last_connection_exception = e
                EDRLOG.log(u"ConnectionException {} for POST EDR: attempts={}".format(e, attempts), u"WARNING")
        raise last_connection_exception
        

    def server_version(self):
        resp = self.__get("{}/version/.json".format(self.EDR_SERVER), "EDR")
        
        if not self.__check_response(resp, "EDR", "Version"):
            EDRLOG.log(u"Failed to check for version update. code={code}, content={content}".format(code=resp.status_code, content=resp.text), "ERROR")
            return None

        return  json.loads(resp.content)
    
    
    def notams(self, timespan_seconds):
        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))
        future_epoch_js = 1830000000000

        params = {"orderBy": '"timestamp"', "startAt": past_epoch_js, "endAt": future_epoch_js, "auth": self.auth_token(), "limitToLast": 10}
        resp = self.__get("{}/v1/notams.json".format(self.EDR_SERVER), "EDR", params)

        if not self.__check_response(resp, "EDR", "notams"):
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
        resp = self.__get("{}/v1/systems.json".format(self.EDR_SERVER), "EDR", params)

        if not self.__check_response(resp, "EDR", "Sitreps"):
            EDRLOG.log(u"Failed to retrieve sitreps.", "ERROR")
            return None
        
        return json.loads(resp.content)

    def system(self, star_system, may_create, coords=None):
        if not self.__preflight("system_id", star_system):
            EDRLOG.log(u"Preflight failed for system call. Forcing a new authentication, just in case.", "DEBUG")
            self.refresh_auth()
            raise CommsJammedError("system")

        params = {"orderBy": '"cname"', "equalTo": json.dumps(star_system.lower()), "limitToFirst": 1, "auth": self.auth_token()}
        resp = self.__get("{}/v1/systems.json".format(self.EDR_SERVER), "EDR", params)

        if not self.__check_response(resp, "EDR", "system"):
            EDRLOG.log(u"Failed to retrieve star system.", "ERROR")
            return None

        the_system = None
        if resp.content == 'null' or resp.content == b'null':
            EDRLOG.log(u"System {} is not recorded in EDR.".format(star_system), "DEBUG")
            if may_create:
                EDRLOG.log(u"Creating system in EDR.", "DEBUG")
                params = { "auth" : self.auth_token() }
                payload = {"name": star_system, "uid" : self.uid()}
                if coords:
                    EDRLOG.log(u"With coords: {}".format(coords), "DEBUG")
                    payload["coords"] = {
                        "x": coords[0],
                        "y": coords[1],
                        "z": coords[2],
                        "uid": self.uid()
                    }
                resp = self.__post("{}/v1/systems.json".format(self.EDR_SERVER), "EDR", json=payload, params=params)
                if not self.__check_response(resp, "EDR", "Systems"):
                    EDRLOG.log(u"Failed to create new star system.", "ERROR")
                    return None
                the_system = json.loads(resp.content)
                EDRLOG.log(u"Created system {} in EDR.".format(star_system), "DEBUG")
            else:
                return None
        else:
            the_system = json.loads(resp.content)
            sid = list(the_system)[0] if the_system else None
            if sid is None:
                EDRLOG.log(u"System {} has no id={}.".format(star_system, sid), "DEBUG")
                return None
            EDRLOG.log(u"System {} is in EDR with id={}.".format(star_system, sid), "DEBUG")
            if may_create and coords and "coords" not in the_system[sid]:
                EDRLOG.log(u"Adding coords to system in EDR.", "DEBUG")
                params = { "auth" : self.auth_token() }
                payload = {
                    "x": coords[0],
                    "y": coords[1],
                    "z": coords[2],
                    "uid":  self.uid()
                }
                resp = self.__put("{}/v1/systems/{}/coords/.json".format(self.EDR_SERVER, sid), "EDR", json=payload, params=params)
                if not self.__check_response(resp, "EDR", "coords"):
                    EDRLOG.log(u"Failed to add coords to existing star system.", "ERROR")
                    return the_system
                EDRLOG.log(u"Added coords to system {} in EDR with id={} and coords={}.".format(star_system, sid, coords), "DEBUG")

        return the_system

    def fc(self, callsign, name, star_system, may_create):
        if not self.__preflight("fc_id", callsign):
            EDRLOG.log(u"Preflight failed for fc call. Forcing a new authentication, just in case.", "DEBUG")
            self.refresh_auth()
            raise CommsJammedError("fc")

        params = {"orderBy": '"ccallsign"', "equalTo": json.dumps(callsign.lower()), "limitToFirst": 1, "auth": self.auth_token()}
        resp = self.__get("{}/v1/fcs.json".format(self.EDR_SERVER), "EDR", params)

        if not self.__check_response(resp, "EDR", "system"):
            EDRLOG.log(u"Failed to retrieve FC.", "ERROR")
            return None

        the_fc = None
        if resp.content == 'null' or resp.content == b'null':
            EDRLOG.log(u"FC {} is not recorded in EDR.".format(callsign), "DEBUG")
            if may_create:
                EDRLOG.log(u"Creating FC in EDR.", "DEBUG")
                params = { "auth" : self.auth_token() }
                payload = {"callsign": callsign, "name": name, "starSystem": star_system, "uid" : self.uid()}
                resp = self.__post("{}/v1/fcs.json".format(self.EDR_SERVER), "EDR", json=payload, params=params)
                if not self.__check_response(resp, "EDR", "FCs"):
                    EDRLOG.log(u"Failed to create new FC.", "ERROR")
                    return None
                the_fc = json.loads(resp.content)
                EDRLOG.log(u"Created FC {} in EDR.".format(callsign), "DEBUG")
            else:
                return None
        else:
            the_fc = json.loads(resp.content)
            fcid = list(the_fc)[0] if the_fc else None
            if fcid is None:
                EDRLOG.log(u"FC {} has no id={}.".format(callsign, fcid), "DEBUG")
                return None
            EDRLOG.log(u"FC {} is in EDR with id={}.".format(callsign, fcid), "DEBUG")
            
        return the_fc

    def pledged_to(self, power, since):
        params = { "auth": self.auth_token() }
        if power is None:
            EDRLOG.log(u"Removing pledge info for uid {uid}".format(uid=self.uid), "INFO")
            endpoint = "{server}/v1/pledges/{uid}/.json".format(server=self.EDR_SERVER, uid=self.uid())
            EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
            resp = self.__delete(endpoint, "EDR", params=params)
            EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
            return self.__check_response(resp, "EDR", "Delete pledge")
        
        EDRLOG.log(u"Pledge info for uid {uid} with power:{power}".format(uid=self.uid(), power=power), "INFO")
        endpoint = "{server}/v1/pledges/{uid}/.json".format(server=self.EDR_SERVER, uid=self.uid())
        json = { "cpower": self.nodify(power), "since": int(since*1000), "heartbeat": {".sv": "timestamp"} }
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__put(endpoint, "EDR", params=params, json=json)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR", "Put pledge")            
    
    def cmdr(self, cmdr, autocreate=True):
        if not self.__preflight("cmdr", cmdr):
            EDRLOG.log(u"Preflight failed for cmdr call.", "DEBUG")
            raise CommsJammedError("cmdr")
        cmdr_profile = edrcmdrprofile.EDRCmdrProfile()

        params = {}
        if sys.version_info.major == 2:
            params = { "orderBy": '"cname"', "equalTo": json.dumps(cmdr.lower().encode('utf-8')), "limitToFirst": 1, "auth": self.auth_token()}
        else:
            params = { "orderBy": '"cname"', "equalTo": json.dumps(cmdr.lower()), "limitToFirst": 1, "auth": self.auth_token()}
        resp = self.__get("{}/v1/cmdrs.json".format(self.EDR_SERVER), "EDR", params)

        if not self.__check_response(resp, "EDR", "Cmdrs"):
            EDRLOG.log(u"Failed to retrieve cmdr id.", "ERROR")
            EDRLOG.log(u"{error}, {content}".format(error=resp.status_code, content=resp.text), "DEBUG")
            return None

        if resp.content == 'null' or resp.content == b'null':
            if autocreate and not self.is_anonymous():
                params = { "auth" : self.auth_token() }
                endpoint = "{}/v1/cmdrs.json".format(self.EDR_SERVER)
                resp = self.__post(endpoint, "EDR", params=params, json={"name": cmdr, "uid" : self.uid(), "requester" : self.player_name})
                if not self.__check_response(resp, "EDR", "Post cmdr"):
                    EDRLOG.log(u"Failed to retrieve cmdr key.", "ERROR")
                    return None
                json_cmdr = json.loads(resp.content)
                EDRLOG.log(u"New cmdr:{}".format(json_cmdr), "DEBUG")
                cmdr_profile.cid = list(json_cmdr.values())[0]
                cmdr_profile.name = cmdr
            else:
                return None
        else:
            json_cmdr = json.loads(resp.content)
            EDRLOG.log(u"Existing cmdr:{}".format(json_cmdr), "DEBUG")
            cmdr_profile.cid = list(json_cmdr)[0]
            cmdr_profile.from_dict(list(json_cmdr.values())[0])

        return cmdr_profile

    def inara_cmdr(self, cmdr):
        if self.player_name is None:
            return None
        
        if self.backoff["Inara"].throttled():
            EDRLOG.log(u"Backing off from Inara API calls", "DEBUG")
            return None

        EDRLOG.log(u"Requesting Inara profile for {}".format(cmdr), "INFO")             
        headers = {
            "Authorization": "ApiKey {}".format(self.INARA_API_KEY),
            "X-EDR-UID": self.uid()
        }
        requester = quote(self.player_name.encode('utf-8')) if self.player_name else u"-"
        endpoint = "https://us-central1-blistering-inferno-4028.cloudfunctions.net/edr/v1/inara/{}/{}".format(quote(cmdr.lower().encode('utf-8')), quote(requester))
        resp = self.__get(endpoint, "EDR", headers=headers)

        if not self.__check_response(resp, "Inara", "Inara"):
            EDRLOG.log(u"Inara profile failed. Error code: {}".format(resp.status_code), "ERROR")
            return None
            
        processed = self.__process_inara_response(resp.content)
        if not processed:
            return None

        cmdr_profile = edrcmdrprofile.EDRCmdrProfile()
        cmdr_profile.from_inara_api(processed)
        return cmdr_profile

    def __post_json(self, endpoint, json_payload, service):
        if self.backoff[service].throttled():
            return None
        
        params = { "auth" : self.auth_token()}
        if self.anonymous_reports != None:
            json_payload["anonymous"] = self.anonymous_reports
        if self.crimes_reporting != None:
            json_payload["creporting"] = self.crimes_reporting
        endpoint = "{server}{endpoint}.json".format(server=self.EDR_SERVER, endpoint=endpoint)
        EDRLOG.log(u"Post JSON {} to {}".format(json_payload, endpoint), "DEBUG")
        resp = self.__post(endpoint, "EDR", params=params, json=json_payload)
        EDRLOG.log(u" resp= {}; {}".format(resp.status_code, resp.text), "DEBUG")
        return self.__check_response(resp, "EDR", "Post json")

    def blip(self, cmdr_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Blip for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info), "INFO")
        endpoint = "/v1/blips/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info, "EDR")

    def traffic(self, system_id, info):
        if not self.__preflight("traffic", system_id):
            EDRLOG.log(u"Preflight failed for traffic call.", "DEBUG")
            raise CommsJammedError("traffic")

        info["uid"] = self.uid()
        EDRLOG.log(u"Traffic report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/traffic/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info, "EDR")

    def scanned(self, cmdr_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Scan for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=info), "INFO")
        endpoint = "/v1/scans/{cmdr_id}/".format(cmdr_id=cmdr_id)
        return self.__post_json(endpoint, info, "EDR")

    def legal_records(self, cmdr_id, timespan_seconds):
        EDRLOG.log(u"Fetching legal record for cmdr {cid}".format(cid=cmdr_id), "INFO")
        endpoint = "/v1/legal/{cmdr_id}/".format(cmdr_id=cmdr_id)
        legal_records_perday = 24
        records_over_timespan = int(max(1, round(timespan_seconds / 86400.0 * legal_records_perday)))
        return self.__get_recent(endpoint, timespan_seconds, limitToLast=records_over_timespan)

    def legal_stats(self, cmdr_id):
        if not self.__preflight("legal_stats", cmdr_id):
            EDRLOG.log(u"Preflight failed for legal_stats call.", "DEBUG")
            raise CommsJammedError("legal_stats")
        EDRLOG.log(u"Fetching legal stats for cmdr {cid}".format(cid=cmdr_id), "INFO")
        endpoint = "{server}/v1/stats/legal/{cmdr_id}/.json".format(server=self.EDR_SERVER,cmdr_id=cmdr_id)
        params = {"auth": self.auth_token()}
        resp = self.__get(endpoint, "EDR", params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")

        if self.__check_response(resp, "EDR", "Legal_Stats"):
            return json.loads(resp.content)
        else:
            return None

    def crime(self, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Crime report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/crimes/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info, "EDR")

    def fight(self, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Fight report for system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/fights/{system_id}/".format(system_id=system_id)
        return self.__post_json(endpoint, info, "EDR")

    def call_central(self, service, system_id, info):
        info["uid"] = self.uid()
        EDRLOG.log(u"Central call from system {sid} with json:{json}".format(sid=system_id, json=info), "INFO")
        endpoint = "/v1/central/{service}/{system_id}/".format(service=service, system_id=system_id)
        return self.__post_json(endpoint, info, "EDR")

    def fc_jump_scheduled(self, flight_plan):
        if self.fc_jump_psa is None:
            return False
        flight_plan["psa"] = self.fc_jump_psa
        EDRLOG.log(u"Fleet Carrier jump with json:{json}".format(json=flight_plan), "INFO")
        endpoint = "/v1/fcjumps/{uid}/".format(server=self.EDR_SERVER, uid=self.uid())
        return self.__post_json(endpoint, flight_plan, "EDR")

    def fc_jump_cancelled(self, status):
        if self.fc_jump_psa is None:
            return False
        EDRLOG.log(u"Cancelling Fleet Carrier jump", "INFO")
        status["psa"] = self.fc_jump_psa
        endpoint = "/v1/fcjumps/{uid}/".format(server=self.EDR_SERVER, uid=self.uid())
        return self.__post_json(endpoint, status, "EDR")

    def crew_report(self, crew_id, report):
        EDRLOG.log(u"Multicrew session report: {}".format(report), "INFO")
        endpoint = "/v1/crew_reports/{}/".format(crew_id)
        return self.__post_json(endpoint, report, "EDR")

    def report_fcs(self, system_id, report):
        if self.is_anonymous():
            return False
        EDRLOG.log(u"Reporting Fleet Carriers in system {}: {}".format(system_id, report), "INFO")
        report["uid"] = self.uid()
        params = { "auth": self.auth_token() }
        endpoint = "{server}/v1/fc_reports/{system_id}/{uid}/.json".format(server=self.EDR_SERVER, system_id=system_id, uid=self.uid())
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__put(endpoint, "EDR", params=params, json=report)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR", "Put fcs report")
    
    def fc_presence(self, star_system):
        if not self.__preflight("fc_presence", star_system):
            EDRLOG.log(u"Preflight failed for fc_presence call.", "DEBUG")
            raise CommsJammedError("fc_presence")

        EDRLOG.log(u"Querying Fleet Carriers in system {}".format(star_system), "INFO")
        params = {"orderBy": '"starSystem"', "equalTo": json.dumps(star_system), "limitToFirst": 1, "auth": self.auth_token()}
        resp = self.__get("{}/v1/fc_presence.json".format(self.EDR_SERVER), "EDR", params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        if self.__check_response(resp, "EDR", "FC_Presence"):
            result = json.loads(resp.content)
            sid = list(result)[0] if result else None
            return result[sid] if result else None
        else:
            return None

    def report_fc_materials(self, fc_id, report):
        if self.is_anonymous():
            return False
        EDRLOG.log(u"Reporting Materials on Fleet Carrier {}: {}".format(fc_id, report), "INFO")
        report["uid"] = self.uid()
        params = { "auth": self.auth_token() }
        endpoint = "{server}/v1/fc_materials_reports/{fc_id}/{uid}/.json".format(server=self.EDR_SERVER, fc_id=fc_id, uid=self.uid())
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__put(endpoint, "EDR", params=params, json=report)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR", "Put fcs materials report")

    def report_fc_market(self, fc_id, report):
        if self.is_anonymous():
            return False
        EDRLOG.log(u"Reporting Market info on Fleet Carrier {}: {}".format(fc_id, report), "INFO")
        report["uid"] = self.uid()
        params = { "auth": self.auth_token() }
        endpoint = "{server}/v1/fc_market_reports/{fc_id}/{uid}/.json".format(server=self.EDR_SERVER, fc_id=fc_id, uid=self.uid())
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__put(endpoint, "EDR", params=params, json=report)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR", "Put fcs market report")
    
    def __get_recent(self, path, timespan_seconds, limitToLast=None):
        now_epoch_js = int(1000 * calendar.timegm(time.gmtime()))
        past_epoch_js = int(now_epoch_js - (1000 * timespan_seconds))

        params = { "orderBy": '"timestamp"', "startAt": past_epoch_js, "endAt": now_epoch_js, "auth": self.auth_token()}
        if limitToLast:
            params["limitToLast"] = limitToLast
        endpoint = "{server}{path}.json".format(server=self.EDR_SERVER, path=path)
        EDRLOG.log(u"Get recent; endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__get(endpoint, "EDR", params)

        if not self.__check_response(resp, "EDR", "Get"):
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
        resp = self.__get(endpoint, "EDR", params)

        if not self.__check_response(resp, "EDR", "Heartbeat"):
            EDRLOG.log(u"Heartbeat failed. Error code: {}".format(resp.status_code), "ERROR")
            return None
        EDRLOG.log(u"Heartbeat response: {}".format(resp.text), "INFO")
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
        resp = self.__get(endpoint, "EDR", params)

        if not self.__check_response(resp, "EDR", "Where"):
            EDRLOG.log(u"Failed to retrieve location of an oppponent.", "ERROR")
            return None
        
        sighting = json.loads(resp.content)
        if sighting:
            sid = list(sighting)[0]
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
        resp = self.__put(endpoint, "EDR", json=dex_entry, params=params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR")

    def __remove_dex(self, dex_path, cmdr_id):
        params = { "auth" : self.auth_token()}
        EDRLOG.log(u"Removing Dex entry for cmdr {cid}".format(cid=cmdr_id), "INFO")
        endpoint = "{server}{dex}{cid}.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__delete(endpoint, "EDR", params=params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR")
    
    def __dex(self, dex_path, cmdr_id):
        EDRLOG.log(u"Dex request for {}".format(cmdr_id), "DEBUG")
        params = { "auth" : self.auth_token()}
        endpoint = "{server}{dex}{cid}/.json".format(server=self.EDR_SERVER, dex=dex_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__get(endpoint, "EDR", params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")

        if self.__check_response(resp, "EDR", "Dex"):
            return json.loads(resp.content)
        else:
            return None

    def contracts(self):
        if self.is_anonymous():
            return None
        contracts_path = "/v1/contracts/{}".format(self.uid())
        EDRLOG.log(u"Contracts request", "DEBUG")
        params = { "auth" : self.auth_token()}
        endpoint = "{server}{con}.json".format(server=self.EDR_SERVER, con=contracts_path)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__get(endpoint, "EDR", params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")

        if self.__check_response(resp, "EDR", "Contracts"):
            return json.loads(resp.content)
        else:
            return None
    
    def contract_for(self, cmdr_id):
        if self.is_anonymous():
            return None
        contracts_path = "/v1/contracts/{}/".format(self.uid())
        EDRLOG.log(u"Contract request for {}".format(cmdr_id), "DEBUG")
        params = { "auth" : self.auth_token()}
        endpoint = "{server}{con}{cid}/.json".format(server=self.EDR_SERVER, con=contracts_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__get(endpoint, "EDR", params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")

        if self.__check_response(resp, "EDR", "Contract_for"):
            return json.loads(resp.content)
        else:
            return None

    def place_contract(self, cmdr_id, contract_entry):
        if self.is_anonymous() or contract_entry is None:
            return False
        contract_path = "/v1/contracts/{}/".format(self.uid())
        
        return self.__update_contract(contract_path, cmdr_id, contract_entry)    
    
    def remove_contract(self, cmdr_id):
        if self.is_anonymous():
            return False
        contract_path = "/v1/contracts/{}/".format(self.uid())
        return self.__remove_contract(contract_path, cmdr_id)
        
    def __update_contract(self, contract_path, cmdr_id, contract_entry):
        params = { "auth" : self.auth_token()}
        EDRLOG.log(u"Contract entry for cmdr {cid} with json:{json}".format(cid=cmdr_id, json=contract_entry), "INFO")
        endpoint = "{server}{contract}{cid}/.json".format(server=self.EDR_SERVER, contract=contract_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {} with {}".format(endpoint, contract_entry), "DEBUG")
        resp = self.__put(endpoint, "EDR", json=contract_entry, params=params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR", "Update_contract")

    def __remove_contract(self, contract_path, cmdr_id):
        params = { "auth" : self.auth_token()}
        EDRLOG.log(u"Removing contract entry for cmdr {cid}".format(cid=cmdr_id), "INFO")
        endpoint = "{server}{contract}{cid}.json".format(server=self.EDR_SERVER, contract=contract_path, cid=cmdr_id)
        EDRLOG.log(u"Endpoint: {}".format(endpoint), "DEBUG")
        resp = self.__delete(endpoint, "EDR", params=params)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR", "Remove_contract")

    def preflight_realtime(self, kind):
        api_name = u"realtime_{}".format(kind.lower())
        if not self.__preflight(api_name, "n/a"):
            raise CommsJammedError(api_name)
        return True

    def __preflight(self, api_name, param):
        headers = {"Authorization": "Bearer {}".format(self.auth_token()), "EDR-Version": "v{}".format(self.version) }
        json = { "name": self.player_name, "timestamp": {".sv": "timestamp"}, "param": param, "api": api_name, "mode": self.game_mode, "dlc": self.dlc_name, "group": self.private_group }
        EDRLOG.log(u"Preflight request for {} with {}".format(api_name, json), "DEBUG")
        endpoint = "https://us-central1-blistering-inferno-4028.cloudfunctions.net/edr/v1/preflight/{uid}".format(server=self.EDR_SERVER, uid=self.uid())
        resp = self.__put(endpoint, "EDR", json=json, headers=headers)
        EDRLOG.log(u"resp= {}".format(resp.status_code), "DEBUG")
        return self.__check_response(resp, "EDR", "Preflight {}".format(api_name))

class CommsJammedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)