import asyncio
import json

from adapters.pubsub.PubsubAdapter import PubsubAdapter
from utils.logger import log_msg
from database.redis_db import redis_client as redis

class RedisAdapter(PubsubAdapter):
    def publish(self, group, channel, payload):
        log_msg("DEBUG", "[Pubsub][RedisAdapter][send] channel = {}, group = {}, payload = {}".format(channel, group, payload))
        redis.publish(channel, json.dumps(payload))

    def consume(self, group, channel, handler):
        log_msg("DEBUG", "[Pubsub][RedisAdapter][consume] channel = {}, group = {}".format(channel, group))
        sub = redis.pubsub()
        sub.subscribe(channel)
        for payload in sub.listen():
            asyncio.run(handler(payload))

    def decode(self, msg):
        log_msg("DEBUG", "[Pubsub][RedisAdapter][decode] msg = {}".format(msg))
        if msg is None or not isinstance(msg, dict) or msg['type'] != 'message' or not 'data' in msg:
            return None

        return json.loads(msg['data'])

    async def reply(self, msg, payload):
        log_msg("DEBUG", "[Pubsub][RedisAdapter][reply] replying to msg = {} with payload = {}".format(msg, json.dumps(payload)))
