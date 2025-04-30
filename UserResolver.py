from MongoDBConnection import *
from bson.objectid import ObjectId
class UserResolver():
    def __init__(self):
        try:        
            mongoDBConnection = MongoDBConnection()
            self.collection = mongoDBConnection.getDatabase()["Users"]
            print("users database opened")
        except Exception as e:
            print(e)

        
    def getUserByEmail(self, email): #filters by userID
        try:
            user = self.collection.find_one({"email": email})
            if user is None:
                print("Not found", email)
                return None
            else:
                return user
        except Exception as e:
            print("Error retrieving user:", e)
            return None

    def saveUser(self, email, password, role): #save new action configuration to the database
        try:
            saveData = {"email": email, "password":password, "role":role}
            value = self.collection.update_one({'email': email},  {'$set': saveData}, upsert=True)
            if value.did_upsert: 
                return str(value.upserted_id)
            else:
                return "abc"
            #return self.collection.find_one({"email": email, "password":password})
        except Exception as e:
            print(e)
            
    def getSpotifyLinkedUsers(self):
        try:
            users = self.collection.find({"spotifyAccessToken":{'$exists': True, '$ne': None}})
            return users
        except Exception as e:
            print("Error retrieving linked users:", e)
            return None
        
    def saveSpotifyAccessToken(self,userID, accessToken):
        try:
            saveData = {"spotifyAccessToken":accessToken}
            value = self.collection.update_one({'_id': ObjectId(userID)},  {'$set': saveData})
            if value.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            
    def saveSpotifyTrackToggle(self, userID, trackToggle):
        try:
            saveData = {"spotifyTrackToggle":trackToggle}
            value = self.collection.update_one({'_id': ObjectId(userID)},  {'$set': saveData})
            if value.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(e)