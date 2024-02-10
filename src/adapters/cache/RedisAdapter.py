from datetime import timedelta

from adapters.cache.CacheAdapter import CacheAdapter
from utils.logger import log_msg
from database.redis_db import redis_client as redis

class RedisAdapter(CacheAdapter):
    def get(self, key):
        data = redis.get(key)
        if not data:
            return None

        try:
            return data.decode('utf-8')
        except AttributeError as ae:
            log_msg("DEBUG", "[cache][RedisAdapter][get] cannot decode data, returning directly data = {}".format(data))
            return data

    def put(self, key, value, ttl):
        redis.set(key, value, ex = timedelta(hours = ttl))

    def delete(self, key):
        redis.delete(key)
