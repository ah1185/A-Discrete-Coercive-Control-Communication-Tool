from threading import Lock
from twilio.rest import Client
import os
class TwilioClientConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
                    cls._instance._auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
                    cls._instance._twilio_client = Client(cls._instance._account_sid, cls._instance._auth_token)
        return cls._instance

    def getTwilioClient(self):
        return self._twilio_client

