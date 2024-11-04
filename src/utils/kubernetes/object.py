import yaml

from pathlib import Path
from fastapi import UploadFile
from jinja2 import Environment, FileSystemLoader, select_autoescape

from schemas.Kubernetes import ObjectAddSchema

from utils.common import AUTOESCAPE_EXTENSIONS

_allowed_metadata_fields = ['name', 'namespace', 'labels', 'annotations', 'creation_timestamp', 'finalizers','resource_version', 'uid']
_allowed_metadata_create_fields = ['name', 'namespace', 'labels', 'annotations']

def clear_metadata(dict_obj: dict):
    keys = list(dict_obj['metadata'].keys())
    for key in keys:
        if key not in _allowed_metadata_fields:
            del dict_obj['metadata'][key]
      
def clear_metadata_for_create(dict_obj: dict):
    keys = list(dict_obj['metadata'].keys())
    for key in keys:
        if key not in _allowed_metadata_create_fields:
            del dict_obj['metadata'][key]

def generate_object(values_file: UploadFile, object: ObjectAddSchema):
    values_file.file.seek(0)
    yaml_data = yaml.safe_load(values_file.file.read())

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[2]) + '/templates/kubernetes/cluster_management')
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
    template = env.get_template(f'{object.kind.lower()}.j2')

    rendered_template = template.render(yaml_data)
    trimmed_yaml = yaml.dump(yaml.safe_load(rendered_template))
    return trimmed_yaml
