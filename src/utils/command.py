from subprocess import check_output

from utils.logger import log_msg

def get_script_output (cmd):
    log_msg("DEBUG", "[get_script_output] cmd = {}".format(cmd))
    try:
        return check_output(cmd, shell=True, text=True)
    except Exception as e:
        return check_output(cmd, shell=True, universal_newlines=True)
