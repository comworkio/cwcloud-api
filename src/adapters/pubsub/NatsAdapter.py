import json

from adapters.pubsub.PubsubAdapter import PubsubAdapter
from database.nats_client import NatsClient
from utils.logger import log_msg
from utils.nats import reply

_nc = NatsClient()

class NatsAdapter(PubsubAdapter):
    def publish(self, group, channel, payload):
        log_msg("DEBUG", "[Pubsub][NatsAdapter][send] payload = {}, channel = {}, group = {}".format(payload, channel, group))
        _nc.publish(channel, payload)

    def consume(self, group, channel, handler):
        log_msg("DEBUG", "[Pubsub][NatsAdapter][consume] channel = {}, group = {}".format(channel, group))
        _nc.consume(channel, handler)

    def decode(self, msg):
        return json.loads(msg.data.decode())

    async def reply(self, msg, payload):
        await reply(msg, payload)
