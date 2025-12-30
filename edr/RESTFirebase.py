import datetime
import json
import requests
import pickle
import os
from enum import Enum

from edrlog import EDR_LOG # EDR_INTERNAL

class AuthState(Enum):
    SUCCESS = (1, "Authenticated.")
    PENDING_APPROVAL = (2, "Pending approval.")
    INVALID_CREDENTIALS = (3, "Invalid credentials.")
    EMAIL_NOT_FOUND = (4, "Email not found.")
    ANONYMOUS_ERROR = (5, "Technical error with guest mode.")
    NETWORK_ERROR = (6, "Network error.")
    API_KEY_ERROR = (7, "API key is missing or invalid.")
    UNKNOWN_ERROR = (8, "Unexpected error.")
    
    def __init__(self, id, message):
        self.id = id
        self.description = message

class RESTFirebaseAuth(object):
    FIREBASE_ANON_AUTH_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'private', 'fbaa.v2.p')

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
        self.last_error = None

    def authenticate(self):
        if self.api_key == "":
            EDR_LOG.error("can't authenticate: empty api key.")
            return AuthState.API_KEY_ERROR

        login_status = self.__login()
        if login_status != AuthState.SUCCESS:
            if login_status == AuthState.PENDING_APPROVAL:
                return AuthState.PENDING_APPROVAL

            self.__reset()
            return login_status

        if not self.__refresh_fb_token():
            self.__reset()
            return AuthState.NETWORK_ERROR
        
        return AuthState.SUCCESS

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
            try:
                error_data = resp.json()
                error_message = error_data.get("error", {}).get("message", "")
                
                if error_message == "USER_DISABLED":
                    EDR_LOG.warning("Login successful but account is pending approval.")
                    return AuthState.PENDING_APPROVAL
                elif error_message == "INVALID_PASSWORD":
                    EDR_LOG.error("Authentication failed (invalid password).")
                    return AuthState.INVALID_CREDENTIALS
                elif error_message == "EMAIL_NOT_FOUND":
                    EDR_LOG.error("Authentication failed (email not found).")
                    return AuthState.EMAIL_NOT_FOUND
                else:
                    EDR_LOG.error(f"Authentication failed: {error_message}")
                    return AuthState.UNKNOWN_ERROR
            except Exception as e:
                EDR_LOG.exception(f"Authentication failed: {e}")
                return AuthState.UNKNOWN_ERROR
        
        self.timestamp = requestTime
        auth = json.loads(resp.content)
        self.refresh_token = auth['refreshToken']
        if self.anonymous:
            try:
                with open(self.FIREBASE_ANON_AUTH_CACHE, 'wb') as handle:
                    pickle.dump(self.refresh_token, handle, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                EDR_LOG.exception(f"Failed to save anonymous auth cache: {e}")
                return AuthState.ANONYMOUS_ERROR
        
        return AuthState.SUCCESS

    def __refresh_fb_token(self):
        payload = { "grant_type": "refresh_token", "refresh_token": self.refresh_token}
        endpoint = "https://securetoken.googleapis.com/v1/token?key={}".format(self.api_key)
        requestTime = datetime.datetime.now()
        resp = requests.post(endpoint,data=payload)
        if resp.status_code != requests.codes.ok:
            EDR_LOG.error("Refresh of FB token failed. Status code={code}, content={content}".format(code=resp.status_code, content=resp.content))
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
            EDR_LOG.info("Renewing authentication since the token will expire soon.")
            self.clear_authentication()
            return self.authenticate()
        return True

    def force_new_auth(self):
        if self.api_key == "":
            return False

        EDR_LOG.info("Forcing a new authentication.")
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
