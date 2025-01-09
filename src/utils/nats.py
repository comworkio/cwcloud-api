import os
import base64
import json
import nats

from utils.common import get_src_path, is_enabled
from utils.file import quiet_remove
from utils.logger import log_msg

_nats_url = os.getenv("NATS_URL", "nats://changeit.com:4222")
_creds_file = "{}/faas.creds".format(get_src_path())
_creds_base64 = os.getenv("NATS_CREDS_BASE64")

def get_nats_url():
    log_msg("DEBUG", "[NatsUtils][get_nats_url] connecting nats_url = {}".format(_nats_url))
    return _nats_url

def get_creds_file_if_exists():
    if is_enabled(_creds_base64):
        quiet_remove(_creds_file)
        creds_content = base64.b64decode(_creds_base64).decode()
        with open(_creds_file, "w") as creds_file:
            creds_file.write(creds_content)
            return _creds_file
    return None

async def close_nats(nc):
    await nc.drain()
    await nc.close()

async def reply(msg, payload):
    log_msg("DEBUG", "[NatsUtils][reply] replying to {}".format(msg))
    try:
        await msg.respond(json.dumps(payload).encode('UTF-8'))
    except nats.errors.Error as e:
        log_msg("DEBUG", "[NatsUtils][reply] cannot reply: e.type = {}, e.msg = {}".format(type(e), e))
    finally:
        await msg.ack()
