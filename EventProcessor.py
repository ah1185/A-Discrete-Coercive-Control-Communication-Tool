from EventListener import *
from EventLogger import *
from ActionResolver import *
from EventDispatcher import *
class EventProcessor:
    def __init__(self, userID, signalType, ts):
        self.userID = userID
        self.signalType = signalType
        self.ts = ts
        self.action = None
        self.body = None
        self.toEmail = None
        self.toPhoneNumber = None
        
    def getAction(self):
        self.action =  self.newResolver.getActionFromDB(self.event.userID, self.event.signalType) #asks resolver to get the action
        print("ACTION ",self.action, "RECEIVED FROM RESOLVER")

        
        
    def getBody(self):
        self.body =  self.newResolver.getBody(self.event.userID, self.event.signalType)
        print("MESSAGE BODY ",self.body, "RECEIVED FROM RESOLVER")

    def getToEmail(self):
        self.toEmail =  self.newResolver.getToEmail(self.event.userID, self.event.signalType)
        print("To EMAIL ",self.toEmail, "RECEIVED FROM RESOLVER")    
        
    def process(self):
        actionResolver = ActionResolver()
        action = actionResolver.getAction(self.userID, self.signalType)
        if action == None:
            print("No action found for this signal type and userID")
            return
        else:
            print("ACTION ",action, "RECEIVED FROM RESOLVER")
            self.action = action["action"]
            self.body = action["body"]
            if self.action == 'email':
                self.toEmail = action["to"]
            elif self.action == 'message' or self.action == 'whatsapp' or self.action == 'call':
                self.toPhoneNumber = action["to"]
            self.log()
            self.dispatch()
    def processContactDetailsTest(self,action, body, to):
            self.action = action
            self.body = body
            if self.action == 'email':
                self.toEmail = to
            elif self.action == 'message' or self.action == 'whatsapp' or self.action == 'call':
                self.toPhoneNumber = to
            self.dispatch()

        
    def dispatch(self):
        eventDispatcher = None   
        if self.action == 'call':
            eventDispatcher = CallEventDispatcher(self.body, self.toPhoneNumber)
        elif self.action == 'message':
            eventDispatcher = SMSEventDispatcher(self.body, self.toPhoneNumber)
        elif self.action == 'email':
            eventDispatcher = EmailEventDispatcher(self.body, self.toEmail)
        elif self.action == 'whatsapp':    
            eventDispatcher = WhatsAppEventDispatcher(self.body, self.toPhoneNumber)
        elif self.action == 'log':
            print("Action was logged successfully")
        if eventDispatcher != None:
            eventDispatcher.dispatch()
        else:
            print("ERROR: No Dispatchers available for the action: ",self.action)
    
    
    def log(self):
        newLog = EventLogger(self.userID, self.ts, self.signalType, self.action, self.body)
        newLog.save()
        print("Log made: ",newLog)