import os
import requests

from PIL import Image
from utils.common import get_env_int, is_empty, is_empty_key, is_response_ok
from utils.logger import log_msg

TRACKER_IMAGE_PATH = os.getenv('TRACKER_IMAGE_PATH', "tracker_image.png")
TRACKER_LOCATION_TIMEOUT = get_env_int('TRACKER_LOCATION_TIMEOUT', 60)
DEFAULT_VALUE = "unknown"

def init_tracker_img():
    if not os.path.exists(TRACKER_IMAGE_PATH):
        img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
        img.save(TRACKER_IMAGE_PATH)

def override_if_is_empty(payload, pkey, data, dkey = None):
    if is_empty(dkey):
        dkey = pkey

    return data.get(dkey, DEFAULT_VALUE) if is_empty_key(payload, pkey) or payload[pkey] == DEFAULT_VALUE else payload[pkey]

def get_infos_from_ip(ip: str):
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json", timeout=TRACKER_LOCATION_TIMEOUT)
        status_code = response.status_code
        if is_response_ok(status_code):
            data = response.json()
            payload = {
                "status": "ok",
                "status_code": status_code,
                "city": data.get("city", DEFAULT_VALUE),
                "region": data.get("region", DEFAULT_VALUE),
                "country": data.get("country_name", DEFAULT_VALUE),
                "region_code": data.get("region_code", DEFAULT_VALUE),
                "country_iso": data.get("country_code", DEFAULT_VALUE),
                "timezone": data.get("timezone", DEFAULT_VALUE),
                "utc_offset": data.get("country_code", DEFAULT_VALUE),
                "currency": data.get("currency", DEFAULT_VALUE),
                "asn": data.get("asn", DEFAULT_VALUE),
                "org": data.get("org", DEFAULT_VALUE),
                "ip": data.get("ip", ip),
                "network": data.get("network", DEFAULT_VALUE),
                "version": data.get("version", DEFAULT_VALUE)
            }
        else:
            try:
                data = response.json()
                reason = data.get("reason", DEFAULT_VALUE)
            except Exception as pe:
                log_msg("WARN", "[get_infos_from_ip] unexpected error with ipapi.co: ip = {}, pe.type = {}, pe.msg = {}".format(ip, type(pe), pe))
                reason = str(pe)

            payload = {
                "status": "ko",
                "status_code": status_code,
                "ip": ip,
                "reason": reason
            }
    except Exception as e:
        log_msg("WARN", "[get_infos_from_ip] unexpected error with ipapi.co: ip = {}, e.type = {}, e.msg = {}".format(ip, type(e), e))
        payload = {
            "status": "ko",
            "ip": ip,
            "reason": str(e)
        }

    response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=TRACKER_LOCATION_TIMEOUT)
    status_code = response.status_code
    try:
        if is_response_ok(status_code):
            data = response.json()
            payload['status'] = "ok"
            payload['status_code'] = status_code
            payload['hostname'] = data.get("hostname", DEFAULT_VALUE)
            payload['loc'] = data.get("loc", DEFAULT_VALUE)
            payload['city'] = override_if_is_empty(payload, 'city', data)
            payload['region'] = override_if_is_empty(payload, 'region', data)
            payload['region_code'] = override_if_is_empty(payload, 'region_code', data, 'region')
            payload['country'] = override_if_is_empty(payload, 'country', data)
            payload['country_iso'] = override_if_is_empty(payload, 'country_iso', data, 'country')
            payload['timezone'] = override_if_is_empty(payload, 'timezone', data)
            payload['ip'] = override_if_is_empty(payload, 'ip', data)
    except Exception as e:
        log_msg("WARN", "[get_infos_from_ip] unexpected error with ipinfo.io: ip = {}, e.type = {}, e.msg = {}".format(ip, type(e), e))

    return payload
