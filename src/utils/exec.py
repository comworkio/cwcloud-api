import subprocess  # nosec B404
import shlex
from typing import List, Union

from utils.logger import log_msg

def exec_cmd(cmd: Union[str, List[str]]):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    
    log_msg("INFO", f"[exec_bash_cmd] running cmd = {' '.join(cmd)}")
    
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=False, shell=False) # nosec B603
        log_msg("INFO", f"[exec_bash_cmd] status = {p.returncode}, stdout = {p.stdout}, stderr = {p.stderr}")
        return p
    except Exception as e:
        log_msg("ERROR", f"[exec_bash_cmd] An unexpected error occurred: {str(e)}")
        raise
