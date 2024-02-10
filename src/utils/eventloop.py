import asyncio

def get_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as re:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop
