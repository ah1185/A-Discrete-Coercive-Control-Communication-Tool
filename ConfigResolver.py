from bson.objectid import ObjectId
from MongoDBConnection import *


class ConfigResolver:
    def __init__(self):        
        mongoDBConnection = MongoDBConnection()
        self.collection = mongoDBConnection.getDatabase()["Actions"]
        print("Actions database opened")

        
    def save(self, userID, action, signalType,body,to): #save new action configuration to the database
        try:
            saveData = { "action": action, "body":body, "to": to }
            self.collection.update_one({'userID': userID, 'signalType' : signalType},  {'$set': saveData}, upsert=True)
        except Exception as e:
            print(e)
        
    def getmyActions(self, userID): #get all actions for a userID
        actions = []
        try:
            myActions = self.collection.find({"userID": userID})
            for document in myActions:
                actions.append(document)
                print(document)
            return actions
        except Exception as e:
            print(e)
        
    def deleteConfig(self, userID, objectID):
        deleteCount = 0
        for document in self.collection.find({"_id": ObjectId(objectID)}):
            if document["userID"] == userID:
                result = self.collection.delete_one({"_id": ObjectId(objectID)})
                deleteCount = result.deleted_count
        return deleteCount



