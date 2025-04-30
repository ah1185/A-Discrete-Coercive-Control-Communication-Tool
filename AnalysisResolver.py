import pandas as pd
from MongoDBConnection import *

class AnalysisResolver():
    def __init__(self, userID):
        #self.timestamp = None
        self.userID = userID
        #self.value = None
        #self.collection = None
        try:
            mongoDBConnection = MongoDBConnection()
            self.collection = mongoDBConnection.getDatabase()["Log"]
            print("Log database opened")
        except Exception as e:
            print("Error opening connection to MongoDB: ", e)



    def getTimestamp(self): 
        values = pd.Series()  # create an empty Series to hold the timestamps
        try:
            selectionCriteria = {}
            if self.userID != None:
                selectionCriteria["userID"] = self.userID
                
            logs = self.collection.find(selectionCriteria) 
            for document in logs:
                #print("1.) PRINTING ALL DOCUMENTS FOR USERID",self.userID,":",document)
                new_value = document["timestamp"]
                #print("2.) PRINTING TIMESTAMP VALUE: ",new_value)
                values = pd.concat([values, pd.Series([new_value])], ignore_index=True)
        finally:
            if len(values) == 0:
                print("No timestamps found for userID", self.userID," Adding dummy timestamps")
                new_values = ["2025-02-02T14:56:23.380+00:00","2025-03-02T17:54:23.380+00:00","2025-02-01T15:13:23.380+00:00"]
                values = pd.concat([values, pd.Series([new_values])], ignore_index=True)
            return values

    # def getNumLogs(self):
    #     numlogs = 0
    #     logs = self.collection.find({"userID": self.userID})
    #     try:
    #         for i in logs:
    #             numlogs = numlogs + 1
    #     finally:
    #         return numlogs
