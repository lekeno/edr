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

    def __init__(self, version):
        self.email = ""
        self.password = ""
        self.auth = None
        self.anonymous = True
        self.version = version
        try:
            with open(self.FIREBASE_ANON_AUTH_CACHE, 'rb') as handle:
                self.refresh_token = pickle.load(handle)
        except:
            self.refresh_token = None
        self.timestamp = None
        self.api_key = ""
        self.last_error = None

    @property
    def custom_user_agent(self):
        # Base version from your existing format
        base_agent = f"EDR-Plugin/v{self.version}" 
        
        # Append the specific auth state
        state = "(anon)" if self.anonymous else "(auth)"
        return f"{base_agent} {state}"

    def authenticate(self):
        if self.api_key == "":
            EDR_LOG.error("can't authenticate: empty api key.")
            return AuthState.API_KEY_ERROR

        login_status = self.__login()
        
        if login_status == AuthState.ANONYMOUS_ERROR and self.anonymous:
            EDR_LOG.info("Retrying authentication with a fresh guest profile.")
            self.refresh_token = None
            login_status = self.__login()

        if login_status != AuthState.SUCCESS:
            if login_status == AuthState.PENDING_APPROVAL:
                return AuthState.PENDING_APPROVAL

            self.__reset()
            return login_status

        if not self.__refresh_fb_token():
            # If we were anonymous and the refresh failed (bad token), 
            # wipe it and try ONE more time from scratch.
            if self.anonymous:
                EDR_LOG.info("Refresh failed for guest; trying one fresh signup.")
                self.__clear_cache_file()
                self.refresh_token = None
                if self.__login() == AuthState.SUCCESS:
                    if self.__refresh_fb_token():
                        return AuthState.SUCCESS
            
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

        if self.refresh_token and self.auth:
            EDR_LOG.info("We already have a token and a session.")
            return AuthState.SUCCESS

        if not self.refresh_token:
            headers = {
                "User-Agent": self.custom_user_agent,
                "Content-Type": "application/json"
            }
            requestTime = datetime.datetime.now()
            resp = requests.post(endpoint, json=payload, headers=headers)
            if resp.status_code != requests.codes.ok:
                try:
                    error_data = resp.json()
                    error_message = error_data.get("error", {}).get("message", "")
                    
                    if error_message == "USER_DISABLED":
                        EDR_LOG.warning("Login successful but account is pending approval.")
                        return AuthState.PENDING_APPROVAL
                    elif error_message == "INVALID_PASSWORD":
                        EDR_LOG.error("Authentication failed (invalid credentials).")
                        return AuthState.INVALID_CREDENTIALS
                    elif error_message in ["INVALID_REFRESH_TOKEN", "TOKEN_EXPIRED", "USER_NOT_FOUND"]:
                        EDR_LOG.warning(f"Cached token is invalid ({error_message}). Clearing cache.")
                        self.__clear_cache_file()
                        self.clear_authentication()
                        self.refresh_token = None
                        return AuthState.ANONYMOUS_ERROR
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
            
        return AuthState.SUCCESS if self.refresh_token else AuthState.UNKNOWN_ERROR

    def __refresh_fb_token(self):
        if not self.refresh_token:
            return False
        
        payload = { "grant_type": "refresh_token", "refresh_token": self.refresh_token}
        endpoint = "https://securetoken.googleapis.com/v1/token?key={}".format(self.api_key)
        headers = { "User-Agent": self.custom_user_agent }

        requestTime = datetime.datetime.now()
        resp = requests.post(endpoint, data=payload, headers=headers)

        if resp.status_code != requests.codes.ok:
            # If the refresh fails with a 400-range error, the token is likely purged/invalid
            if 400 <= resp.status_code < 500:
                EDR_LOG.error(f"Refresh failed ({resp.status_code}). Purging invalid token.")
                self.__clear_cache_file()
                self.clear_authentication()
                self.refresh_token = None
            else:
                EDR_LOG.error(f"Refresh of FB token failed. Status code={resp.status_code}")
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

    def __clear_cache_file(self):
        """Physically remove the poisoned token from disk."""
        try:
            if os.path.exists(self.FIREBASE_ANON_AUTH_CACHE):
                os.remove(self.FIREBASE_ANON_AUTH_CACHE)
                EDR_LOG.info("Deleted invalid anonymous auth cache file.")
        except Exception as e:
            EDR_LOG.error(f"Failed to delete auth cache: {e}")

    def __reset(self):
        """Wipe state and only reload if a file actually exists."""
        self.clear_authentication()
        if os.path.exists(self.FIREBASE_ANON_AUTH_CACHE):
            try:
                with open(self.FIREBASE_ANON_AUTH_CACHE, 'rb') as handle:
                    self.refresh_token = pickle.load(handle)
            except:
                self.refresh_token = None
        else:
            self.refresh_token = None
