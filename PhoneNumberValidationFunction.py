import re

def isValidUKMobileNumber(number):
    rule = re.compile(r"^\+44[0-9]{10}$")
    if not rule.match(number):
        return False
    else:
        return True

