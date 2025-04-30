from EventDispatcher import *
import unittest


class test_EventDispatcher(unittest.TestCase):  
    
    @classmethod
    def setUpClass(self):
        self.newEventDispathcer = EventDispatcher("Body of message")
        self.newSMS = SMSEventDispatcher("Body of message", "+447700900000")
        self.newEmail = EmailEventDispatcher("Body of message", "abc@abc.com")
        self.newCall = CallEventDispatcher("Body of message", "+447700900000")
        self.newWhatsApp = WhatsAppEventDispatcher("Body of message", "+447700900000")
    
    def test_initializeBaseClass(self):
        self.assertEqual(self.newEventDispathcer.userMessage, "Body of message")

    def test_initializeSMS(self):
        self.assertEqual(self.newSMS.userMessage, "Body of message")
        self.assertEqual(self.newSMS.toPhoneNumber, "+447700900000")
    
    def test_initializeEmail(self):
        self.assertEqual(self.newEmail.userMessage, "Body of message")
        self.assertEqual(self.newEmail.toEmail, "abc@abc.com")
    
    def test_initializeCall(self):
        self.assertEqual(self.newCall.userMessage, "Body of message")
        self.assertEqual(self.newCall.toPhoneNumber, "+447700900000")

    def test_initializeWhatsApp(self):
        self.assertEqual(self.newWhatsApp.userMessage, "Body of message")
        self.assertEqual(self.newWhatsApp.toPhoneNumber, "+447700900000")

if __name__ == '__main__':
    unittest.main()