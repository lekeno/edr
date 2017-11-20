import datetime
import json
import requests

import edrlog

EDRLOG = edrlog.EDRLog()

class RESTFirebaseAuth(object):
    def __init__(self):
        self.email = ""
        self.password = ""
        self.auth = None
        self.timestamp = None
        self.api_key = ""

    def authenticate(self):
        if self.email == "" or self.password == "" or self.api_key == "":
            EDRLOG.log(u"can't authenticate: empty credentials and/or api key.", "ERROR")
            return False

        msg = {
            "email": self.email,
            "password": self.password,
            "returnSecureToken": True
        }

        requestTime = datetime.datetime.now()
        endpoint = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={}".format(self.api_key)
        resp = requests.post(endpoint,json=msg)
        if resp.status_code != 200:
            EDRLOG.log(u"Authentication failed", "ERROR")
            self.clear_authentication()
            return False
        
        self.timestamp= requestTime
        self.auth = json.loads(resp.content)

        refresh_token = self.auth['refreshToken']
        payload = { "grant_type": "refresh_token", "refresh_token": refresh_token}
        endpoint = "https://securetoken.googleapis.com/v1/token?key={}".format(self.api_key)
        resp = requests.post(endpoint,data=payload)
        if resp.status_code != 200:
            EDRLOG.log(u"Exchange of refresh token for ID token failed. Status code={code}, content={content}".format(code=resp.status_code, content=resp.content), "ERROR")
            self.clear_authentication()
            return False

        self.auth = json.loads(resp.content)

        return True

    def is_valid_auth_token(self):
        if self.auth is None or not 'expiresIn' in self.auth: 
            return True

        return 'idToken' in self.auth

    def is_auth_expiring(self):
        if not self.is_valid_auth_token():
            return True
        
        now = datetime.datetime.now()
        near_expiration = datetime.timedelta(seconds=int(self.auth['expires_in'])-30)
        return (now - self.timestamp) > near_expiration


    def renew_auth_if_needed(self):
        if self.email == "" or self.password == "":
            return False

        if self.is_auth_expiring():
            EDRLOG.log(u"Authentication token will expire soon. Clearing to renew.", "INFO")
            self.clear_authentication()
            return self.authenticate()

        return True


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
