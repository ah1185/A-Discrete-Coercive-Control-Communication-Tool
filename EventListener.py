from EventProcessor import EventProcessor
import pandas as pd
class EventListener:
    def __init__(self, userID):
        self.userID = userID
        self.ts = pd.Timestamp.now()
        self.signalType = None
        
    
    def showData(self): #for testing purposes
        print("SIGNAL TYPE:",self.signalType,"userID:",self.userID, "TIMESTAMP:",self.ts)

        
    def sendData(self):
        newProcessor = EventProcessor(self.userID, self.signalType, self.ts)
        print("NEW PROCESSOR MADE")
        newProcessor.process()
        print("Done")
        
    def getsignalType(self):
        return self.signalType
    
    def getuserID(self):
        return self.userID
    
    def getTS(self):
        return self.ts
    
class FlicEventListener(EventListener):
    def __init__(self, userID):
        super().__init__(userID)
        self.signalType = 'flic'

    
    
class SpotifyEventListener(EventListener):
    def __init__(self, userID):
        super().__init__(userID)
        self.signalType = 'spotify'

    

        

        
