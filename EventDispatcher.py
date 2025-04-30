
import smtplib
import email.message
import os
from TwilioClientConnection import *
class EventDispatcher:
    def __init__(self, body):
        self.userMessage = body
        

class SMSEventDispatcher(EventDispatcher):
    def __init__(self, body, toPhoneNumber):
        super().__init__(body)
        twilioConnection = TwilioClientConnection()
        self.client = twilioConnection.getTwilioClient()
        self.fromTwilio = os.environ.get("TWILIO_PHONE_NUMBER") 
        self.toPhoneNumber = toPhoneNumber
        
    def dispatch(self):    
        print("Sending Message...")
        message = self.client.messages.create(
        from_=self.fromTwilio,
        body=self.userMessage,
        to=self.toPhoneNumber
        )
        print(message.body)
        print(message.sid)
        print("SMS MESSAGE WAS SENT")
        return self.userMessage


class WhatsAppEventDispatcher(EventDispatcher):
    def __init__(self, body, toPhoneNumber):
        super().__init__(body)
        self.toPhoneNumber = toPhoneNumber
        self.fromTwilio = os.environ.get("TWILIO_WHATSAPP_NUMBER") 
        twilioConnection = TwilioClientConnection()
        self.client = twilioConnection.getTwilioClient()
    def dispatch(self):
        message = self.client.messages.create(
        from_=self.fromTwilio,
        body = self.userMessage,
        to='whatsapp:'+self.toPhoneNumber
        )
        print(message.body)
        print(message.sid)
        print("WHATSAPP MESSAGE WAS SENT")
        return self.userMessage



        
class EmailEventDispatcher(EventDispatcher):
    def __init__(self, message, toEmail):
        super().__init__(message)
        self.subject = ""
        self.smtpServer = os.environ.get("SMTP_SERVER")
        self.fromEmail = os.environ.get("SMTP_FROM_EMAIL")
        self.toEmail = toEmail
        self.emailPassword = os.environ.get("SMTP_PASSWORD")
        self.emailPort = os.environ.get("SMTP_PORT") 
        
    def dispatch(self):
        smtp = smtplib.SMTP(self.smtpServer, self.emailPort)   
        smtp.starttls()
        smtp.login(self.fromEmail,self.emailPassword ) 

        message = email.message.EmailMessage()
        message.set_content(self.userMessage)
        message['Subject'] = 'New Message'
        message['From'] = self.fromEmail 
        message['To'] = self.toEmail 

        try:
            e = smtp.send_message(message)
            if e:
                raise smtplib.SMTPException(f'Failures: {e}')
        finally:
            smtp.quit()
        
class CallEventDispatcher(EventDispatcher):
    def __init__(self, body, toPhoneNumber):
        super().__init__(body)
        twilioConnection = TwilioClientConnection()
        self.client = twilioConnection.getTwilioClient()
        self.fromTwilio = os.environ.get("TWILIO_PHONE_NUMBER") 
        self.toPhoneNumber = toPhoneNumber
        self.body = body
    def dispatch(self):
        call = self.client.calls.create(
        twiml="<Response><Say>"+self.body+"</Say></Response>",
        to=self.toPhoneNumber,
        from_=self.fromTwilio,
    )
        print(call.sid)
        