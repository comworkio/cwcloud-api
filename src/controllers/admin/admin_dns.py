from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from schemas.Dns import DnsDeleteSchema, DnsRecordSchema
from schemas.User import UserSchema
from utils.dns import import_driver
from utils.observability.cid import get_current_cid
from utils.provider import exist_provider, get_provider_dns_zones


def admin_list_dns_zones(current_user: UserSchema, provider: str, db: Session):
    try:
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'provider does not exist',
                'i18n_code': 'provider_not_exist',
                'cid': get_current_cid()
            }, status_code = 404)
        return {
            'status': 'ok',
            'dns_zones': get_provider_dns_zones(provider)
        } 
    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "{}".format(e),
            'cid': get_current_cid()
        }, status_code = 500)

def admin_list_dns_records(current_user: UserSchema, provider: str, db: Session):
    try:
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'provider does not exist', 
                'i18n_code': 'provider_not_exist',
                'cid': get_current_cid()
            }, status_code = 404)
        
        driver = import_driver(provider)
        result =  driver().list_dns_records()
        if result is None:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Not Implemented',
                'i18n_code': 'not_implemented',
                'cid': get_current_cid()
            }, status_code = 405)
        return result
    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "{}".format(e),
            'cid': get_current_cid()
        }, status_code = 500)
        
def admin_create_dns_record(current_user: UserSchema, provider: str, payload: DnsRecordSchema, db: Session):
    try:
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'provider does not exist',
                'i18n_code': 'provider_not_exist',
                'cid': get_current_cid()
            }, status_code = 404)
        driver = import_driver(provider)
        result =  driver().create_custom_dns_record(payload.record_name, payload.dns_zone, payload.type, payload.ttl, payload.data)
        if result is None:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Not Implemented',
                'i18n_code': 'not_implemented',
                'cid': get_current_cid()
            }, status_code = 405)
        return result
    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "{}".format(e),
            'cid': get_current_cid()
        }, status_code = 500)
        
        
def admin_delete_dns_record(current_user: UserSchema, provider: str, dns_delete_schema: DnsDeleteSchema, db: Session):
    try:
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'provider does not exist',
                'i18n_code': 'provider_not_exist',
                'cid': get_current_cid()
            }, status_code = 404)
        driver = import_driver(provider)
        result =  driver().delete_dns_records(dns_delete_schema.id, dns_delete_schema.record_name, dns_delete_schema.dns_zone)
        if result is None:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Not Implemented',
                'i18n_code': 'not_implemented',
                'cid': get_current_cid()
            }, status_code = 405)
        return result
    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "{}".format(e),
            'cid': get_current_cid()
        }, status_code = 500)
