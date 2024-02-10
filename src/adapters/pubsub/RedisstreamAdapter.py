import asyncio
import json

from uuid import uuid4

from adapters.pubsub.PubsubAdapter import PubsubAdapter
from utils.logger import log_msg

from redis.exceptions import ResponseError
from database.redis_db import redis_client as redis

_consumer_name = "consumer_{}".format(uuid4())

class RedisstreamAdapter(PubsubAdapter):
    def publish(self, group, channel, payload):
        log_msg("DEBUG", "[Pubsub][RedisstreamAdapter][send] channel = {}, group = {}, payload = {}".format(channel, group, payload))
        redis.xadd(channel, { 'data': json.dumps(payload) })

    def consume(self, group, channel, handler):
        log_msg("DEBUG", "[Pubsub][RedisstreamAdapter][consume] channel = {}, group = {}".format(channel, group))

        try:
            redis.xgroup_create(channel, group, mkstream=True)
        except ResponseError as re:
            log_msg("DEBUG", "[Pubsub][RedisstreamAdapter][consume] group {} already exists: {}".format(group, re))

        while True:
            messages = redis.xreadgroup(group, _consumer_name, { channel: '>' }, count=1, block=1000)
            for message in messages:
                if not isinstance(message, list):
                    continue
                stream, message_data = message
                log_msg("DEBUG", "[Pubsub][RedisstreamAdapter][consume] stream = {}, message_data = {}".format(stream, message_data))
                for msg_id, data in message_data:
                    log_msg("DEBUG", "[Pubsub][RedisstreamAdapter][consume] msg_id = {}, data = {}".format(msg_id, data))
                    asyncio.run(handler(data))

    def decode(self, msg):
        log_msg("DEBUG", "[Pubsub][RedisstreamAdapter][decode] msg = {}".format(msg))
        if msg is None or not isinstance(msg, dict) or not 'data' in msg:
            return None

        return json.loads(msg['data'])

    async def reply(self, msg, payload):
        log_msg("DEBUG", "[Pubsub][RedisAdapter][reply] replying to msg = {} with payload = {}".format(msg, json.dumps(payload)))
