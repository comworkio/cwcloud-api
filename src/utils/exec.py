import subprocess

from utils.logger import log_msg

def exec_cmd (cmd):
    log_msg("INFO", "[exec_bash_cmd] running cmd = {}".format(cmd))
    p = subprocess.run(cmd, capture_output = True)
    log_msg("INFO", "[exec_bash_cmd] status = {}, stdout = {}, stderr = {}".format(p.returncode, p.stdout.decode(), p.stderr.decode()))
