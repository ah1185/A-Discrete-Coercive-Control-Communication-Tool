import unittest  
import os
os.environ['SPOTIFY_URL'] = 'testing'
os.environ['SPOTIFY_TRIGGER_TRACK'] = 'testing'
os.environ['SPOTIFY_POLL_INTERVAL'] = "200"
os.environ['SECRET_KEY'] = "temp_test_secret"
from app import app
from unittest.mock import patch
from Analyser import Analyser

class MockAnalyser:
    def __init__(self, userID):
        self.userID = userID
    def calcRiskScore(self):
        return 7




class test_App_WebPages_NotLoggedIn(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.client = app.test_client()  

    #public Pages, no login required
    def test_homePage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
    

    #secure Pages, login required. expect redirect http 302
    def test_addActions(self):
        response = self.client.get("/addActions")
        self.assertEqual(response.status_code, 302)

    def test_help(self):
        response = self.client.get("/helplines")
        self.assertEqual(response.status_code, 302)


@patch.object(Analyser, '__init__', MockAnalyser.__init__)
@patch.object(Analyser, 'calcRiskScore', MockAnalyser.calcRiskScore)
class test_App_WebPages_LoggedIn(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.client = app.test_client()  
        with self.client.session_transaction() as session:
            session['userid'] = '1234'
        
    def test_addActions(self):
        #add action should return redirect if not logged in
        response = self.client.get("/addActions")
        self.assertEqual(response.status_code, 200)

    def test_help(self):
        response = self.client.get("/helplines")
        self.assertEqual(response.status_code, 200)


class test_App_APIs(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = app.test_client()

        
    if __name__ == '__main__':
        unittest.main()
        