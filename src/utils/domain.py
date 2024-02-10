import re

def is_subdomain_valid(instance_name):
    pattern = r'^[a-zA-Z0-9\-]+$'
    return re.match(pattern, instance_name) is not None

def is_not_subdomain_valid(instance_name):
    return not is_subdomain_valid(instance_name)
