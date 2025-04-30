import unittest
from EventListener import *


class test_EventListener(unittest.TestCase):  
    
    @classmethod   
    def setUp(self):
        self.new = EventListener("1234")
        self.newflic = FlicEventListener("1234")
        self.newSpotify = SpotifyEventListener("1234")

    
    def test_initialise(self):
        self.assertEqual("1234", self.new.getuserID())
        self.assertIsNotNone(self.new.getTS())
        
        
    def test_flic(self):
        self.assertEqual("1234", self.newflic.getuserID())
        self.assertEqual("flic", self.newflic.getsignalType())
        self.assertIsNotNone(self.newflic.getTS())

    def test_spotify(self):
        self.assertEqual("1234", self.newflic.getuserID())
        self.assertEqual("spotify", self.newSpotify.getsignalType())
        self.assertIsNotNone(self.newSpotify.getTS())


if __name__ == '__main__':
    unittest.main()
