import yaml

from urllib.error import HTTPError

def read_uploaded_yaml_file(input:bytes):
    try:
        yaml_data = yaml.safe_load(input)
        return yaml_data
    except yaml.YAMLError as e:
        raise HTTPError("invalid_yaml_value", 400, "Invalid yaml value", hdrs = {"i18n_code": "invalid_yaml_value"}, fp = None)

