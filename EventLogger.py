#from pymongo.mongo_client import MongoClient
#from pymongo.server_api import ServerApi
from MongoDBConnection import *



class EventLogger:
    def __init__(self, userID, ts, signalType, action, body):
        try:
            mongoDBConnection = MongoDBConnection()
            self.collection = mongoDBConnection.getDatabase()["Log"]
            print("Log database opened")
        except Exception as e:
            print(e)
        self.userID = userID
        self.ts = ts
        self.signalType = signalType
        self.action = action
        self.body = body
        

    def save(self):
        """
        saves log data (id, timestamp, signalType, action, message body) to a collection and prints the inserted ID.
        """
        logData = { "userID":self.userID, "timestamp": self.ts,"signalType":self.signalType, "action":self.action, "body":self.body}
        x = self.collection.insert_one(logData)
        print(x.inserted_id)
        
