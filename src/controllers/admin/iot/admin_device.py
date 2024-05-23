from entities.iot.Device import Device
from fastapi.responses import JSONResponse
from utils.observability.cid import get_current_cid

def get_devices(db):
    devices = Device.getAllDevices(db)
    return devices

def delete_device(device_id, db):
    device = Device.getDeviceById(device_id, db)
    if not device:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Device not found',
            'i18n_code': 'device_not_found',    
            'cid': get_current_cid()
        }, status_code = 404)
    
    Device.deleteDeviceById(device_id, db)

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Device successfully deleted',
        'i18n_code': 'device_deleted'
    }, status_code = 200)
