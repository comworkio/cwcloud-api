import os

from consume.handler import handle, pubsub_adapter
from utils.observability.otel import init_otel_metrics, init_otel_tracer
from utils.workers import wait_startup_time

wait_startup_time()
init_otel_tracer()
init_otel_metrics()

while True:
  pubsub_adapter().consume(os.environ['CONSUMER_GROUP'], os.environ['CONSUMER_CHANNEL'], handle)
