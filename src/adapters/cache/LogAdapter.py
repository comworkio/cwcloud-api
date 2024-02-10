from adapters.cache.CacheAdapter import CacheAdapter
from utils.logger import log_msg

class LogAdapter(CacheAdapter):
    def get(self, key):
        log_msg("INFO", "[cache][LogAdapater][get] key = {}".format(key))
        return None

    def put(self, key, value, ttl):
        log_msg("INFO", "[cache][LogAdapater][put] key = {}, value = {}, ttl = {}".format(key, value, ttl))
    
    def delete(self, key):
        log_msg("INFO", "[cache][LogAdapater][delete] key = {}".format(key))
