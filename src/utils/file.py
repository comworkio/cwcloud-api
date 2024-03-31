import os

from utils.logger import log_msg

def quiet_remove (path):
    try:
      os.remove(path)
    except FileNotFoundError as e:
      log_msg("WARN", "[quiet_remove] file {} doesn't exists".format(path))
