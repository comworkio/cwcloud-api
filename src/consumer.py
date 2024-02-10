import os

from consume.handler import handle, pubsub_adapter
from utils.workers import wait_startup_time

wait_startup_time()

while True:
  pubsub_adapter().consume(os.environ['CONSUMER_GROUP'], os.environ['CONSUMER_CHANNEL'], handle)
