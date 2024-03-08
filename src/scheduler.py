import os

from schedule.handler import handle, pubsub_adapter
from schedule.crontabs import init_triggered_functions
from utils.observability.otel import init_otel_metrics, init_otel_tracer
from utils.workers import wait_startup_time

wait_startup_time()
init_triggered_functions()
init_otel_tracer()
init_otel_metrics()

while True:
  pubsub_adapter().consume(os.environ['TRIGGERS_GROUP'], os.environ['TRIGGERS_CHANNEL'], handle)
