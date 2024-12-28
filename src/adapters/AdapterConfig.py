import importlib
import os
import yaml

from utils.common import is_not_empty

_default_adapter = "log"

def get_adapter_type(key, default = _default_adapter):
    config_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'cloud_environments.yml'))
    with open(config_path, "r") as stream:
        loaded_data = yaml.safe_load(stream)
        return loaded_data['adapters'][key] if 'adapters' in loaded_data and key in loaded_data['adapters'] and is_not_empty(loaded_data['adapters'][key]) else default

def get_adapter_by_name(key, name):
    class_path = "{}Adapter".format(name.capitalize())
    module = importlib.import_module('adapters.{}.{}'.format(key, class_path))
    return getattr(module, class_path)

def get_default_adapter(key):
    return get_adapter_by_name(key, _default_adapter)

def get_adapter(key, default = _default_adapter):
    return get_adapter_by_name(key, get_adapter_type(key, default))
