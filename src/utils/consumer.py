import os

from utils.common import get_env_int

CONSUMER_SLEEP_TIME = get_env_int('CONSUMER_SLEEP_TIME', 3600)
CONSUMER_GROUP = os.getenv('CONSUMER_GROUP', 'faas')
CONSUMER_CHANNEL = os.getenv('CONSUMER_CHANNEL', 'faas')

TRIGGERS_GROUP = os.getenv('TRIGGERS_GROUP', 'faastriggers')
TRIGGERS_CHANNEL = os.getenv('TRIGGERS_CHANNEL', 'faastriggers')
