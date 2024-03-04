from adapters.AdapterConfig import get_adapter
from schedule.crontabs import init_triggered_functions
from utils.logger import log_msg

pubsub_adapter = get_adapter("pubsub")

async def handle(msg):   
    payload = pubsub_adapter().decode(msg)
    if payload is None:
        log_msg("DEBUG", "[scheduler][handle] payload is none")
        return

    log_msg("INFO", "[scheduler][handle] there's a change on the crons: {}, reset everything from database".format(payload))
    
    init_triggered_functions()

