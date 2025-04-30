from pymongo import MongoClient
from threading import Lock
import os
class MongoDBConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.connection_string = os.environ.get("MONGO_CONNECTION_STRING")
                    cls._instance._client = MongoClient(cls._instance.connection_string)
                    cls._instance._db = cls._instance._client["Cluster0"]
        return cls._instance

    def getDatabase(self):
        return self._db
    