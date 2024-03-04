import re

from datetime import datetime
from utils.common import is_empty
from utils.logger import log_msg

def parse_date(vdate):
    log_msg("DEBUG", "[parse_date] trying to parse {}".format(vdate))
    if is_empty(vdate):
        return {'status': False, 'value': ""}

    if isinstance(vdate, dict):
        return vdate if 'status' in vdate and 'value' in vdate else { 'status': False, 'value': vdate }

    if isinstance(vdate, datetime):
        return {'status': True, 'value': vdate}

    simple_date_regexp = r'^[0-9]{4,}\-[0-9]{1,}\-[0-9]{1,}$'
    fdate = vdate.replace('/', '-')
    if re.fullmatch(simple_date_regexp, fdate):
        return {'status': True, 'value': datetime.strptime(fdate, "%Y-%m-%d")}
    else:
        return {'status': False, 'value': fdate}

def is_iso_date_valid(date):
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\+\d{2}:\d{2})?$'
    return bool(re.match(pattern, date))
