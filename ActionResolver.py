from MongoDBConnection import *


class ActionResolver:
    def __init__(self):
        try:
            mongoDBConnection = MongoDBConnection()
            self.collection = mongoDBConnection.getDatabase()["Actions"]
            print("actions database opened")
        except Exception as e:
            print(e)
            
        
    def getAction(self,userID,signalType):
        action = self.collection.find_one({"signalType": signalType, "userID": userID})
        return action
    
    # def setValue(self,value):
    #     self.currentValue = value
        
    # def setBody(self,body):
    #     self.body = body
        
    # def setToEmail(self,toEmail):
    #     self.toEmail = toEmail    
        
    # def getBody(self,userID,signalType):
    #     body = self.collection.find({"signalType": signalType, "userID": userID})
    #     for document in body:
    #         print("1.) PRINTING DOCUMENTS FOR FLIC SIGNAL TYPE AND USERID",userID,":",document)
    #         body = document["body"]
    #         print("2.) PRINTING BODY VALUE: ",body)
    #     self.setBody(body)
    #     return self.body

    # def getToEmail(self,userID,signalType):
    #     queryResults = self.collection.find({"signalType": signalType, "userID": userID})
    #     for document in queryResults:
    #         print("1.) PRINTING DOCUMENTS FOR FLIC SIGNAL TYPE AND USERID",userID,":",document)
    #         toEmail = document["to"]
    #         print("2.) PRINTING to email VALUE: ",toEmail)
    #     self.setToEmail(toEmail)
    #     return self.toEmail
