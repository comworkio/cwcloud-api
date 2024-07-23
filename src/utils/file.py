import os
import time

from utils.logger import log_msg

def create_dir_if_not_exists (path):
   if not os.path.exists(path):
        log_msg("DEBUG", "[create_dir_if_not_exists] path {} doesn't exists, creating...".format(path))
        os.makedirs(path)

def quiet_remove (path):
    try:
      os.remove(path)
    except FileNotFoundError as e:
      log_msg("WARN", "[quiet_remove] file {} doesn't exists".format(path))

def create_cert_locally (file_name, file_content):
    with open(f"{file_name}.pem" , "w") as file:
        file.write(file_content)

    time.sleep(1)

def delete_cert_locally (file_name):
    quiet_remove(f"{file_name}.pem")
