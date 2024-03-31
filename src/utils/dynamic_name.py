import os

from utils.bytes_generator import generate_random_bytes
from utils.common import is_true, is_empty

_disable_dynamic_names = os.getenv('DISABLE_DYNAMIC_NAMES')

def generate_hashed_name(name):
   if is_disable_dynamic_names():
      return '', name
   hash = generate_random_bytes(6)
   return hash, "{}-{}".format(name, hash)

def is_disable_dynamic_names():
   return is_true(_disable_dynamic_names)

def rehash_dynamic_name(name, hash):
    return name if is_disable_dynamic_names() or is_empty(hash) else "{}-{}".format(name, hash)
