import os
import uvicorn

from utils.common import get_env_int

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=os.genenv('LISTEN_ADDR', '0.0.0.0'), 
        port=get_env_int('LISTEN_PORT', 5000), 
        workers=get_env_int('UVICORN_WORKERS', 10),
        timeout_keep_alive=get_env_int('UVICORN_TIMEOUT_KEEP_ALIVE', 30),
        timeout_graceful_shutdown=get_env_int('UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN', 10),
    )
