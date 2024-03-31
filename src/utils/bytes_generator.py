import os
import random

from utils.common import is_true

def generate_random_bytes(length):
    possible_characters = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_character_list = [random.choice(possible_characters) for i in range(length)]
    random_bytes = "".join(random_character_list)
    return random_bytes

