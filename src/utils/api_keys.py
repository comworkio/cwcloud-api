import string
import random
import uuid

def generate_apikey_access_key():
    length = 17
    prefix = "CWC"
    letters = string.ascii_uppercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return prefix+result_str

def generate_apikey_secret_key():
    return str(uuid.uuid4())
