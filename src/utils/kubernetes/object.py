import yaml

from pathlib import Path
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from jinja2 import Environment, FileSystemLoader

from schemas.Kubernetes import ObjectAddSchema
from utils.common import is_not_empty

ALLOWED_METADATA_FIELDS = ['name', 'namespace', 'labels', 'annotations', 'creation_timestamp', 'finalizers','resource_version', 'uid']
ALLOWED_METADATA_CREATE_FIELDS = ['name', 'namespace', 'labels', 'annotations']

def assert_presence(value: str, message: str):
    if is_not_empty(value):
        return JSONResponse(content = {"error": message, "i18n_code": "207"}, status_code = 400)

def clear_metadata(dict_obj: dict):
    keys = list(dict_obj['metadata'].keys())
    for key in keys:
        if key not in ALLOWED_METADATA_FIELDS:
            del dict_obj['metadata'][key]
      
def clear_metadata_for_create(dict_obj: dict):
    keys = list(dict_obj['metadata'].keys())
    for key in keys:
        if key not in ALLOWED_METADATA_CREATE_FIELDS:
            del dict_obj['metadata'][key]

def generate_object(values_file: UploadFile, object: ObjectAddSchema):
    values_file.file.seek(0)
    yaml_data = yaml.safe_load(values_file.file.read())

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[2]) + '/templates/kubernetes/cluster_management')
    env = Environment(loader=file_loader)
    template = env.get_template(f'{object.kind.lower()}.j2')

    rendered_template = template.render(yaml_data)
    trimmed_yaml = yaml.dump(yaml.safe_load(rendered_template))
    return trimmed_yaml
