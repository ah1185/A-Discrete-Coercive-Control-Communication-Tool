import unittest  
from PhoneNumberValidationFunction import *

class test_PhoneNumberValidationFunction(unittest.TestCase):
    
    def test_isValidUKMobileNumber(self):
        testNumber = "+447700900000"
        result = isValidUKMobileNumber(testNumber)
        self.assertEqual(result,True)
        
    def test_isInvalidUKMobileNumberNoCountryCode(self):
        testNumber = "+7843600000"
        result = isValidUKMobileNumber(testNumber)
        self.assertEqual(result,False)
        
    def test_isInvalidUKMobileNumberNoPlus(self):
        testNumber = "447843600000"
        result = isValidUKMobileNumber(testNumber)
        self.assertEqual(result,False)

    def test_isInvalidUKMobileNumberTooShort(self):
        testNumber = "+44784360000"
        result = isValidUKMobileNumber(testNumber)
        self.assertEqual(result,False)

    def test_isInvalidUKMobileNumberTooLong(self):
        testNumber = "+4478436000000"
        result = isValidUKMobileNumber(testNumber)
        self.assertEqual(result,False)
        
if __name__ == '__main__':
    unittest.main()