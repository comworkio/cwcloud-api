import shlex
from subprocess import check_output, PIPE, CalledProcessError # nosec B404
from utils.logger import log_msg

def get_script_output(cmd):
    log_msg("DEBUG", f"[get_script_output] cmd = {cmd}")
    try:
        cmd_args = shlex.split(cmd)
        return check_output(cmd_args, stderr=PIPE, universal_newlines=True) # nosec B603
    except CalledProcessError as e:
        log_msg("ERROR", f"Command failed with error: {e.stderr}")
        return e.stderr
