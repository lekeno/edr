import datetime
import json
import requests
import pickle
import os

import edrlog
import utils2to3

EDRLOG = edrlog.EDRLog()

class RESTFirebaseAuth(object):
    FIREBASE_ANON_AUTH_CACHE = utils2to3.abspathmaker(__file__, 'private', 'fbaa.v2.p')

    def __init__(self):
        self.email = ""
        self.password = ""
        self.auth = None
        self.anonymous = True
        try:
            with open(self.FIREBASE_ANON_AUTH_CACHE, 'rb') as handle:
                self.refresh_token = pickle.load(handle)
        except:
            self.refresh_token = None
        self.timestamp = None
        self.api_key = ""

    def authenticate(self):
        if self.api_key == "":
            EDRLOG.log(u"can't authenticate: empty api key.", "ERROR")
            return False

        if not self.__login():
            EDRLOG.log(u"Authentication failed (login)", "ERROR")
            self.__reset()
            return False

        if not self.__refresh_fb_token():
            EDRLOG.log(u"Authentication failed (FB token)", "ERROR")
            self.__reset()
            return False
        return True

    def __login(self):
        payload = {
            "returnSecureToken": True
        }

        endpoint = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={}".format(self.api_key)
        self.anonymous = True

        if self.email != "" and self.password != "":
            payload["email"] = self.email
            payload["password"] = self.password
            self.anonymous = False
            self.refresh_token = None
            endpoint = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={}".format(self.api_key)

        if self.refresh_token:
            return True

        requestTime = datetime.datetime.now()
        resp = requests.post(endpoint,json=payload)
        if resp.status_code != requests.codes.ok:
            return False
        
        self.timestamp = requestTime
        auth = json.loads(resp.content)
        self.refresh_token = auth['refreshToken']
        if self.anonymous:
            try:
                with open(self.FIREBASE_ANON_AUTH_CACHE, 'wb') as handle:
                    pickle.dump(self.refresh_token, handle, protocol=pickle.HIGHEST_PROTOCOL)
            except:
                return False
        return True

    def __refresh_fb_token(self):
        payload = { "grant_type": "refresh_token", "refresh_token": self.refresh_token}
        endpoint = "https://securetoken.googleapis.com/v1/token?key={}".format(self.api_key)
        requestTime = datetime.datetime.now()
        resp = requests.post(endpoint,data=payload)
        if resp.status_code != requests.codes.ok:
            EDRLOG.log(u"Refresh of FB token failed. Status code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            return False

        self.auth = json.loads(resp.content)
        self.timestamp = requestTime
        self.refresh_token = self.auth["refresh_token"]

        return True

    def is_valid_auth_token(self):
        return (self.auth and 'expires_in' in self.auth and 'id_token' in self.auth)

    def is_auth_expiring(self):
        if not self.is_valid_auth_token():
            return True
        
        now = datetime.datetime.now()
        near_expiration = datetime.timedelta(seconds=int(self.auth['expires_in'])-30)
        return (now - self.timestamp) > near_expiration


    def renew_auth_if_needed(self):
        if self.api_key == "":
            return False

        if self.is_auth_expiring():
            EDRLOG.log(u"Renewing authentication since the token will expire soon.", "INFO")
            self.clear_authentication()
            return self.authenticate()
        return True

    def force_new_auth(self):
        if self.api_key == "":
            return False

        EDRLOG.log(u"Forcing a new authentication.", "INFO")
        self.clear_authentication()
        return self.authenticate()

    def id_token(self):
        if not self.renew_auth_if_needed():
            return None

        if not self.is_valid_auth_token():
            return None
        
        return self.auth['id_token']

    def uid(self):
        if not self.renew_auth_if_needed():
            return None

        if not self.is_valid_auth_token():
            return None
        
        return self.auth['user_id']
        
    def clear_authentication(self):
        self.auth = None
        self.timestamp = None

    def __reset(self):
        self.clear_authentication()
        try:
            with open(self.FIREBASE_ANON_AUTH_CACHE, 'rb') as handle:
                self.refresh_token = pickle.load(handle)
        except:
            self.refresh_token = None
