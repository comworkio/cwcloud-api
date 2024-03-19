from urllib.parse import parse_qs

from utils.logger import log_msg

def unmarshall_payload(payload):
    str = payload.decode("utf-8")
    log_msg("DEBUG", "[webhook_bytes][unmarshall_payload] decoded str = {}".format(str))
    return str

def unmarshall_formdata(payload):
    return parse_qs(unmarshall_payload(payload))
