from ActionResolver import *
from EventProcessor import *   
import unittest   
from unittest.mock import patch



class MockActionResolver:
    def __init__(self):
        print("MockActionResolver: __init__ called")
        return

    def getAction(self, userID, signalType):
        return {"action": "call", "body": "Test body", "to": "+447700900000"}

class MockEventProcessor:
    def log(self):
        print("MockEventProcessor: log called")
        return
    
    def dispatch(self):
        print("MockEventProcessor: dispatch called")
        return


class EventProcessorTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.testProcessor = EventProcessor("1234", "call", "11:53")

    def test_initialise(self):
        self.assertEqual("1234", self.testProcessor.userID)
        self.assertEqual("call", self.testProcessor.signalType)
        self.assertIsNotNone(self.testProcessor.ts)
        self.assertIsNone(self.testProcessor.action)
        self.assertIsNone(self.testProcessor.body)
        self.assertIsNone(self.testProcessor.toEmail)
        self.assertIsNone(self.testProcessor.toPhoneNumber)
        
    @patch.object(ActionResolver, '__init__', MockActionResolver.__init__)
    @patch.object(ActionResolver, 'getAction', MockActionResolver.getAction)
    @patch.object(EventProcessor, 'log', MockEventProcessor.log)
    @patch.object(EventProcessor, 'dispatch', MockEventProcessor.dispatch)
    def test_process(self):
        self.testProcessor.process()
        self.assertEqual(self.testProcessor.action, "call")
        self.assertEqual(self.testProcessor.body, "Test body")
        self.assertEqual(self.testProcessor.toPhoneNumber, "+447700900000")
        
if __name__ == '__main__':
    unittest.main()