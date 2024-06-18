from sqlalchemy import text

from utils.common import is_not_empty_key, is_true

ALL_FLAGS = [
    'billable',
    'without_vat',
    'auto_pay',
    'daasapi',
    'emailapi',
    'disable_emails',
    'cwaiapi',
    'faasapi',
    'k8sapi', 
    'iotapi'
]

def is_flag_enabled(vdict, key):
    return is_not_empty_key(vdict, key) and is_true(vdict[key])

def is_flag_disabled(vdict, key):
    return not is_flag_enabled(vdict, key)

def sql_filter_flag_enabled(flag):
    return text("enabled_features->>'{}' = 'true'".format(flag))
