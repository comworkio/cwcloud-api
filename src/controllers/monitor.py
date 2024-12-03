import os
from datetime import datetime
from entities.Monitor import Monitor
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from utils.common import is_not_http_status_code
from utils.observability.cid import get_current_cid
from utils.dynamic_name import generate_hashed_name

def get_monitors(current_user, db):
    monitors = Monitor.getUserMonitors(current_user.id, db)
    return monitors

def get_monitor(current_user, monitor_id, db):
    monitor = Monitor.findUserMonitorById(current_user.id, monitor_id, db)
    if not monitor:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Monitor not found',
            'i18n_code': 'monitor_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    return monitor

def add_monitor(current_user, payload, db):
    try:
        max_monitors = int(os.getenv('MONITORS_MAX_NUMBER', 10))
        current_monitors = Monitor.getUserMonitors(current_user.id, db)
        if len(current_monitors) > max_monitors:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'User has reached the maximum number of monitors',
                'i18n_code': 'max_monitors_reached',
                'cid': get_current_cid()
            }, status_code = 403)
        
        if is_not_http_status_code(payload.expected_http_code):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid HTTP status code',
                'i18n_code': 'invalid_http_status_code',
                'cid': get_current_cid()
            }, status_code = 400)
        
        new_monitor = Monitor(**payload.dict())
        new_monitor.user_id = current_user.id
        _, hashed_monitor_name = generate_hashed_name(new_monitor.name)
        new_monitor.name = hashed_monitor_name
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        new_monitor.created_at = current_date
        new_monitor.updated_at = current_date
        new_monitor.save(db)

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'Monitor successfully created',
            'id': str(new_monitor.id),
            'i18n_code': 'monitor_created'
        }, status_code = 201)

    except HTTPException as e:
        return JSONResponse(content = {
            'status': 'ko',
            'message': e.detail,
            'cid': get_current_cid()
        }, status_code = e.status_code)
        
def update_monitor(current_user, monitor_id, payload, db):
    monitor = Monitor.findUserMonitorById(current_user.id, monitor_id, db)
    if not monitor:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Monitor not found',
            'i18n_code': 'monitor_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    if is_not_http_status_code(payload.expected_http_code):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid HTTP status code',
            'i18n_code': 'invalid_http_status_code',
            'cid': get_current_cid()
        }, status_code = 400)

    Monitor.updateInfo(payload, monitor_id, db)

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Monitor successfully updated',
        'id': monitor_id,
        'i18n_code': 'monitor_updated'
    })
    
def remove_monitor(current_user, monitor_id, db):
    monitor = Monitor.findUserMonitorById(current_user.id, monitor_id, db)
    if not monitor:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Monitor not found',
            'i18n_code': 'monitor_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    Monitor.deleteUserMonitor(current_user.id, monitor_id, db)
    
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Monitor successfully deleted',
        'id': monitor_id,
        'i18n_code': 'monitor_deleted'
    })
