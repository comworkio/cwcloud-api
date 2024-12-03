from fastapi_utils.guid_type import GUID

class CachedGUID(GUID):
    cache_ok = True
