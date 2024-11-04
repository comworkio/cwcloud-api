import re
import secrets 
import math
from datetime import datetime, timedelta
from utils.jwt import jwt_encode
from utils.common import is_empty

def check_password(password):
    if len(password) < 8:
        return {
            'status': False,
            'i18n_code': 'password_too_short'
        }

    if re.search(r"\d", password) is None:
        return {
            'status': False,
            'i18n_code': 'password_no_number'
        }

    if re.search(r"[A-Z]", password) is None:
        return {
            'status': False,
            'i18n_code': 'password_no_upper'
        }

    if re.search(r"[a-z]", password) is None:
        return {
            'status': False,
            'i18n_code': 'password_no_lower'
        }

    if re.search(r"[ !#$%&'()*+, -./[\\\]^_`{|}~"+r'"]', password) is None:
        return {
            'status': False,
            'i18n_code': 'password_no_symbol'
        }

    return {
        'status': True
    }

def random_password(length):
    lower_chars = "abcdefghijklmnopqrstuvwxyz"
    upper_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "1234567890"
    specials = "$!%+-, "
    
    random_first_part = ''.join(secrets.choice(lower_chars) for _ in range(math.ceil(length/3)))
    random_second_part = ''.join(secrets.choice(upper_chars) for _ in range(math.ceil(length/3)))
    random_third_part = ''.join(secrets.choice(numbers) for _ in range(math.ceil(length/3)))
    random_fourth_part = secrets.choice(specials)
    
    password = f"{random_first_part}{random_second_part}{random_third_part}{random_fourth_part}"
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)

    return ''.join(password_list)

def is_email_valid(email):
    if is_empty(email):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_not_email_valid(email):
    return not is_email_valid(email)

def is_ref_invoice_valid(ref):
    if is_empty(ref):
        return False

    pattern = r"^\d{5,}$"
    return re.match(pattern, ref) is not None

def is_not_ref_invoice_valid(ref):
    return not is_ref_invoice_valid(ref)

def is_forbidden (var):
    forbidden_chars = ["'" , "\"", "&", ";", "|", "\\", "$"]
    return any(char in var for char in forbidden_chars)

def generate_token(user):
    token = jwt_encode({
        'exp': (datetime.now() + timedelta(minutes = 5)).timestamp(),
        'id': user.id,
        'email': user.email,
        'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    })

    return token
