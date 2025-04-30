from AnalysisResolver import AnalysisResolver
import pandas as pd
from datetime import timedelta

class Analyser():
    def __init__(self, userID):
        self.resolver = AnalysisResolver(userID)
        self.riskScore = None
        self.values = self.resolver.getTimestamp()
        self.now = pd.Timestamp.now()  

    def getEventsInPastDay(self):
        eventsInPastDay = self.values[self.values >= (self.now - timedelta(days=1))]
        return len(eventsInPastDay)


    def getEventsInPastWeek(self):
        lastWeek = self.now - timedelta(weeks=1)
        eventsLastWeek = self.values[self.values >= lastWeek]
        return len(eventsLastWeek)
    

    def getEventsAtNight(self):
        #events in the past week that happened overnight
        lastWeek = self.now - timedelta(weeks=1)
        overnight_mask = (
        (self.values >= lastWeek) &  # Within last week
        (
            (self.values.dt.hour >= 22) |  # 10PM-11:59PM
            (self.values.dt.hour <= 4)     # 12AM-4AM
        )
        )
        return overnight_mask.sum() 


    def calcRiskScore(self):
        a = self.getEventsInPastDay()
        b = self.getEventsInPastWeek()
        c = self.getEventsAtNight()    
        riskScore = a + b + (c * 2) #extra weighting for nighttime triggers, counts them again plus 1.5x
        print(f"""
        Risk Score Components:
        1. Triggers (last 24h): {a}
        2. Triggers (last week): {b}
        3. Nighttime triggers: {c}
        ---------------------------------
        Total Risk Score: {riskScore:.2f} / 25
        """)
        return riskScore

