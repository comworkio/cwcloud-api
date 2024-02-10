import os

from schedule.handler import handle, pubsub_adapter
from schedule.crontabs import reinit_crontabs
from utils.workers import wait_startup_time

wait_startup_time()
reinit_crontabs()

while True:
  pubsub_adapter().consume(os.environ['TRIGGERS_GROUP'], os.environ['TRIGGERS_CHANNEL'], handle)
