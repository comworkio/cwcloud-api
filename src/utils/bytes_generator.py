import secrets
import string

def generate_random_bytes(length):
    possible_characters = string.ascii_lowercase + string.digits
    random_character_list = [secrets.choice(possible_characters) for _ in range(length)]
    random_bytes = "".join(random_character_list)
    return random_bytes
