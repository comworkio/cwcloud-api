import os

from utils.common import is_empty

def get_payment_currency():
    return get_payment_currency_from_unit(os.getenv('PRICE_UNIT'))

def get_payment_currency_from_unit(price_unit):
    if is_empty(price_unit):
        return "eur"

    usd = ["usd", "dollars", "$"]
    tnd = ["tnd", "dt", "dinars"]

    if any(c == "{}".format(price_unit).lower() for c in usd):
        return usd[0]
    elif any(c == "{}".format(price_unit).lower() for c in tnd):
        return tnd[0]
    else:
        return "eur"
