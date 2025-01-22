from fastapi.responses import JSONResponse
from fastapi import HTTPException

from entities.iot.Device import Device
from entities.User import User
from schemas.User import UserRegisterSchema

from utils.common import generate_hash_password, get_admin_status, is_empty, is_false, is_not_empty, is_true
from utils.env_vars import DOMAIN
from utils.gitlab import create_gitlab_user
from utils.logger import log_msg
from utils.mail import send_device_confirmation_email, send_user_and_device_confirmation_email, send_user_confirmation_email_without_activation_link
from utils.observability.cid import get_current_cid
from utils.security import generate_token, is_not_email_valid, random_password
from utils.jwt import jwt_decode

def add_device(current_user, payload, db):
    try:
        is_admin = get_admin_status(current_user)
        email = payload.username
        if is_not_email_valid(email):
            return JSONResponse(content = {
                'status': 'ko',
                'message': 'Invalid email',
                'i18n_code': 'invalid_email',
                'cid': get_current_cid()
            }, status_code = 400)

        existing_user = User.getUserByEmail(email, db)
        if existing_user:
            if is_false(is_admin):
                log_msg("INFO", f"[add_device] device confirmation email sent to {existing_user.email}")
                token = generate_token(existing_user)
                device_activation_link = '{}/device-confirmation/{}'.format(DOMAIN, token)
                send_device_confirmation_email(email, device_activation_link, "Device confirmation")
        else:
            password = random_password(8)
            register_payload = UserRegisterSchema(
                email = email,
                password = password
            )

            register_payload.password = generate_hash_password(password)
            new_user = User(**register_payload.dict())
            new_user.save(db)
            create_gitlab_user(email)
            log_msg("INFO", f"[add_device] user account created with {email}")

            created_user = User.getUserByEmail(email, db)
            if is_true(is_admin):
                User.updateConfirmation(created_user.id, True, db)
                log_msg("INFO", f"[add_device] user confirmation email without activation link sent to {created_user.email}")
                send_user_confirmation_email_without_activation_link(created_user.email, password, "User confirmation")
            else:
                log_msg("INFO", f"[add_device] user and device confirmation email sent to {created_user.email}")
                token = generate_token(created_user)
                activation_link = '{}/confirmation/{}'.format(DOMAIN, token)
                send_user_and_device_confirmation_email(email, password, activation_link, "User and device confirmation")

        new_device = Device(**payload.dict())
        db.add(new_device)
        db.commit()
        db.refresh(new_device)

        if is_true(is_admin):
            Device.activateDevice(new_device.id, db)
        
        return JSONResponse(content = {
            'status': 'ok',
            'token': token,
            'message': 'Device successfully created',
            'id': str(new_device.id),
            'i18n_code': 'device_created'
        }, status_code = 201)
    
    except HTTPException as e:
        return JSONResponse(content = {
            'status': 'ko',
            'message': e.detail,
            'i18n_code': e.detail,
            'cid': get_current_cid()
        }, status_code = e.status_code)


def confirm_device_by_token(token, db):
    if is_empty(token):
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Invalid token',
            'i18n_code': 'invalid_token',
            'cid': get_current_cid()
        }, status_code = 400)
    
    try:
        data = jwt_decode(token)
        user = User.getUserByEmail(data['email'], db)
        if not user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found', 
                'i18n_code': 'user_not_found',
                'cid': get_current_cid()
            }, status_code = 404)

        device = Device.getUserLatestInactiveDevice(user.email, db)
        if is_not_empty(device):
            Device.activateDevice(device.id, db)

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'Device successfully confirmed',
            'i18n_code': 'device_confirmed'
        }, status_code = 200)
    except Exception:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Invalid token',
            'i18n_code': 'invalid_token',
            'cid': get_current_cid()
        }, status_code = 400)
    
def get_user_devices(current_user, db):
    devices = Device.getUserDevices(current_user.email, db)
    return devices

def get_user_device_by_id(current_user, device_id, db):
    device = Device.getDeviceById(device_id, db)
    if not device:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Device not found',
            'i18n_code': 'device_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    if current_user.email != device.username:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Unauthorized',
            'i18n_code': 'unauthorized',
            'cid': get_current_cid()
        }, status_code = 401)
    
    return device

def delete_user_device_by_id(current_user, device_id, db):
    device = Device.getDeviceById(device_id, db)
    if not device:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Device not found',
            'i18n_code': 'device_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    if current_user.email != device.username:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Unauthorized',
            'i18n_code': 'unauthorized',
            'cid': get_current_cid()
        }, status_code = 401)
    
    Device.deleteDeviceById(device_id, db)
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'Device successfully deleted',
        'i18n_code': 'device_deleted'
    }, status_code = 200)
