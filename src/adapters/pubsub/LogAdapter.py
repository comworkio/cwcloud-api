import json

from adapters.pubsub.PubsubAdapter import PubsubAdapter
from utils.logger import log_msg

class LogAdapter(PubsubAdapter):    
    def publish(self, group, channel, payload):
        log_msg("INFO", "[Pubsub][LogAdapter][publish] payload = {}, channel = {}, group = {}".format(payload, channel, group))

    def consume(self, group, channel, handler):
        log_msg("INFO", "[Pubsub][LogAdapter][consume] consuming channel = {}, group = {}".format(channel, group))

    def decode(self, msg):
        return msg

    async def reply(self, msg, payload):
        log_msg("DEBUG", "[Pubsub][LogAdapter][consume] replying to msg = {} with payload = {}".format(msg, json.dumps(payload)))
