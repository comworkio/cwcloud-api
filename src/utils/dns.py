import importlib

from utils.provider import get_driver


def import_driver(provider: str):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    driver = getattr(ProviderDriverModule, get_driver(provider))
    return driver
