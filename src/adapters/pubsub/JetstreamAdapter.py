import json

from adapters.pubsub.PubsubAdapter import PubsubAdapter
from database.jetstream_client import JetstreamClient
from utils.logger import log_msg
from utils.nats import reply

_jc = JetstreamClient()

class JetstreamAdapter(PubsubAdapter):
    def publish(self, group, channel, payload):
        log_msg("DEBUG", "[Pubsub][JetstreamAdapter][send] payload = {}".format(payload))
        _jc.publish(group, channel, payload)

    def consume(self, group, channel, handler):
        log_msg("DEBUG", "[Pubsub][JetstreamAdapter][consume] channel = {}, group = {}".format(channel, group))
        _jc.consume(group, channel, handler)

    def decode(self, msg):
        return json.loads(msg.data.decode())

    async def reply(self, msg, payload):
        await reply(msg, payload)
