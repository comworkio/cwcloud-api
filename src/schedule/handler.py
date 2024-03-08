from adapters.AdapterConfig import get_adapter
from schedule.crontabs import init_triggered_functions
from utils.logger import log_msg
from utils.observability.otel import get_otel_tracer

pubsub_adapter = get_adapter("pubsub")

_span_prefix = "faas-scheduler"

async def handle(msg):
    with get_otel_tracer().start_as_current_span("{}-handle".format(_span_prefix)):
        payload = pubsub_adapter().decode(msg)
        if payload is None:
            log_msg("DEBUG", "[scheduler][handle] payload is none")
            return

        log_msg("INFO", "[scheduler][handle] there's a change on the crons: {}, reset everything from database".format(payload))
        
        init_triggered_functions()
