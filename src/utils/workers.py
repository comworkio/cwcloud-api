import os
import time

from utils.common import is_numeric
from utils.logger import log_msg

def wait_startup_time():
    wait_startup_time = os.getenv('FAAS_WAIT_STARTUP_TIME')
    if is_numeric(wait_startup_time):
        log_msg("DEBUG", "[wait_startup_time] Waiting for {} seconds".format(wait_startup_time))
        time.sleep(int(wait_startup_time))
