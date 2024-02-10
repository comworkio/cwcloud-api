from sqlalchemy.ext.declarative import DeclarativeMeta
import json
from datetime import datetime

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                if field == "query":
                    continue;
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    continue;
            return fields

        return json.JSONEncoder.default(self, obj)
