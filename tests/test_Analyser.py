from Analyser import *
import unittest   
from unittest.mock import patch

class MockAnalyserScenario1:
    def __init__(self, userID):
        print("MockAnalyserScenario1: __init__ called")
        return
    def getEventsInPastDay(self):
        return 5
    def getEventsInPastWeek(self):
        return 10
    def getEventsAtNight(self):
        return 2


class MockAnalyserScenario2:
    def __init__(self, userID):
        print("MockAnalyserScenario1: __init__ called")
        return
    def getEventsInPastDay(self):
        return 2
    def getEventsInPastWeek(self):
        return 5
    def getEventsAtNight(self):
        return 4

class MockAnalyserScenario3:
    def __init__(self, userID):
        print("MockAnalyserScenario1: __init__ called")
        return
    def getEventsInPastDay(self):
        return 100
    def getEventsInPastWeek(self):
        return 200
    def getEventsAtNight(self):
        return 600


class AnalyserTest(unittest.TestCase):

    @patch.object(Analyser, '__init__', MockAnalyserScenario1.__init__)   
    @patch.object(Analyser, 'getEventsInPastDay', MockAnalyserScenario1.getEventsInPastDay)
    @patch.object(Analyser, 'getEventsInPastWeek', MockAnalyserScenario1.getEventsInPastWeek)
    @patch.object(Analyser, 'getEventsAtNight', MockAnalyserScenario1.getEventsAtNight)
    def test_scenario1(self):
        testAnalyser = Analyser("1234")
        result = testAnalyser.calcRiskScore()
        self.assertEqual(result, 19)


    @patch.object(Analyser, '__init__', MockAnalyserScenario2.__init__)   
    @patch.object(Analyser, 'getEventsInPastDay', MockAnalyserScenario2.getEventsInPastDay)
    @patch.object(Analyser, 'getEventsInPastWeek', MockAnalyserScenario2.getEventsInPastWeek)
    @patch.object(Analyser, 'getEventsAtNight', MockAnalyserScenario2.getEventsAtNight)
    def test_scenario2(self):
        testAnalyser = Analyser("1234")
        result = testAnalyser.calcRiskScore()
        self.assertEqual(result,15)

    @patch.object(Analyser, '__init__', MockAnalyserScenario3.__init__)   
    @patch.object(Analyser, 'getEventsInPastDay', MockAnalyserScenario3.getEventsInPastDay)
    @patch.object(Analyser, 'getEventsInPastWeek', MockAnalyserScenario3.getEventsInPastWeek)
    @patch.object(Analyser, 'getEventsAtNight', MockAnalyserScenario3.getEventsAtNight)
    def test_scenario3(self):
        testAnalyser = Analyser("1234")
        result = testAnalyser.calcRiskScore()
        self.assertEqual(result,1500)




if __name__ == '__main__':
    unittest.main()