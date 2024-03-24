import importlib

from time import sleep

from entities.Registry import Registry

from utils.logger import log_msg
from utils.provider import get_driver
from utils.constants import MAX_RETRY, WAIT_TIME

def register_registry(hash, provider, region, userid, name, type, db):
    from entities.Registry import Registry
    new_registry = Registry()
    new_registry.hash = hash
    new_registry.user_id = userid
    new_registry.provider = provider
    new_registry.region = region
    new_registry.name = name
    new_registry.type = type
    new_registry.save(db)
    return new_registry

def update_credentials(provider, registry, db):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    result = ProviderDriver().update_registry_credentials(registry)
    if 'secret_key' in result:
        Registry.updateCredentials(registry.id, result['access_key'], result['secret_key'], db)
    else:
        Registry.updateAccessKey(registry.id, result['access_key'], db)

def delete_registry(provider, registry, user_email, retry = 0):
    try:
        if retry >= MAX_RETRY:
            log_msg("WARN", "[delete_registry] max retries has been reached : provider = {}, registry = {}, user_email = {}".format(provider, registry, user_email))
            return

        if retry > 0:
            waiting_time = WAIT_TIME * retry
            log_msg("DEBUG", "[delete_registry] waiting: provider = {}, registry = {}, user_email = {}, wait = {}".format(provider, registry, user_email, waiting_time))
            sleep(waiting_time)

        ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
        ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
        ProviderDriver().delete_registry(registry, user_email)
    except Exception as e:
        log_msg("WARN", "[delete_registry] trying again because of this error: provider = {}, registry = {}, user_email = {}, error = {}".format(provider, registry, user_email, e))
        delete_registry(provider, registry, user_email, retry + 1)

def create_registry(provider, user_email, registry_id, hashed_name, region, type, db):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    result = ProviderDriver().create_registry(user_email, registry_id, hashed_name, region, type)
    log_msg("DEBUG", "[create_registry] driver result = {}".format(result))
    if not "secret_key" in result:
        Registry.updateSingleCred(registry_id, result['endpoint'], result['access_key'], result['status'], db)
    else:
        Registry.update(registry_id, result['endpoint'], result['access_key'], result['secret_key'], result['status'], db)

def refresh_registry(user_email, provider, registry_id, hashed_registry_name, db):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    result = ProviderDriver().refresh_registry(user_email, registry_id, hashed_registry_name)
    if "type" in result:
        Registry.updateType(registry_id, result['type'], db)
