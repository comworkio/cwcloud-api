import os
import random

from utils.common import is_true

_disable_dynamic_names = os.getenv('DISABLE_DYNAMIC_NAMES')

def generate_random_bytes(length):
    possible_characters = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_character_list = [random.choice(possible_characters) for i in range(length)]
    random_bytes = "".join(random_character_list)
    return random_bytes

def is_disable_dynamic_names():
   return is_true(_disable_dynamic_names)

def generate_hashed_name(name):
   if is_disable_dynamic_names():
      return '', name
   hash = generate_random_bytes(6)
   return hash, "{}-{}".format(name, hash)
