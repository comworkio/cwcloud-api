from utils.common import is_not_empty

def convert_instance_state(switcher, server):
    if 'state' in server and is_not_empty(server['state']) and server['state'].lower() in switcher:
        return switcher.get(server['state'].lower())
    else:
        return "starting"
