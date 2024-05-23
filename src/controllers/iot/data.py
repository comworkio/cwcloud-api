from datetime import datetime
import json
from controllers.faas.invocations import invoke_sync
from entities.faas.Function import FunctionEntity
from entities.faas.Trigger import TriggerEntity
from entities.iot.Data import Data, NumericData, StringData
from entities.iot.ObjectType import ObjectType
from fastapi.responses import JSONResponse
from entities.iot.Device import Device
from schedule.crontabs import handle_trigger
from schemas.faas.Invocation import Invocation
from schemas.faas.InvocationArg import InvocationArgument
from schemas.faas.InvocationContent import InvocationContent
from utils.common import is_numeric, is_not_empty_key
from utils.encoder import AlchemyEncoder
from utils.observability.cid import get_current_cid

def add_data(current_user, user_auth, payload, db):
    existing_device = Device.getUserDeviceById(current_user.email, payload.device_id, db)
    if current_user.is_admin:
        existing_device = Device.getDeviceById(payload.device_id, db)
    if not existing_device:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Device not found',
            'i18n_code': 'device_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    if not existing_device.active:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'Device not active',
            'i18n_code': 'device_not_active',
            'cid': get_current_cid()
        }, status_code = 403)
       
    typeobject_id = existing_device.typeobject_id
    existing_object_type = ObjectType.findById(typeobject_id, db)
    if not existing_object_type:
        return JSONResponse(content = {
            'status': 'ko',
            'message': 'TypeObject not found',
            'i18n_code': 'typeobject_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    object_type_content = existing_object_type.content

    if is_not_empty_key(object_type_content, 'decoding_function'):
        existing_function = FunctionEntity.findById(object_type_content['decoding_function'], db)
        if not existing_function:
            return JSONResponse(content = {
                'status': 'ko',
                'message': 'Decoding function not found',
                'i18n_code': 'decoding_function_not_found',
                'cid': get_current_cid()
            }, status_code = 404)
        
        dumped_existing_function = json.loads(json.dumps(existing_function, cls = AlchemyEncoder))
        args = dumped_existing_function['content']['args']
        if args:
            if len(args) == 1:
                if args[0] != 'data':
                    return JSONResponse(content = {
                        'status': 'ko',
                        'message': "Decoding function key should be named 'data'",
                        'i18n_code': 'decoding_function_key_should_be_named_data',
                        'cid': get_current_cid()
                    }, status_code = 404)
            else:
                return JSONResponse(content = {
                    'status': 'ko',
                    'message': 'Decoding function has more than one argument',
                    'i18n_code': 'decoding_function_has_more_than_one_argument',
                    'cid': get_current_cid()
                }, status_code = 404)
        else:
            return JSONResponse(content = {
                'status': 'ko',
                'message': "Decoding function 'data' argument not found",
                'i18n_code': 'decoding_function_data_argument_not_found',
                'cid': get_current_cid()
            }, status_code = 404)
        
        invocation_payload = Invocation(
            invoker_id = current_user.id,
            content = InvocationContent(
                function_id = object_type_content['decoding_function'],
                args = [
                    InvocationArgument(
                        key = "data",
                        value = payload.content
                    )
                ]
            )
        )

        dumped_existing_object_type = json.loads(json.dumps(existing_object_type, cls = AlchemyEncoder))
        triggers = dumped_existing_object_type['content']['triggers']
        if triggers:
            for triggerId in triggers:
                trigger = TriggerEntity.findById(triggerId, db)
                dumped_trigger = json.loads(json.dumps(trigger, cls = AlchemyEncoder))
                handle_trigger(dumped_trigger)

        sync_invocation_result = invoke_sync(invocation_payload, current_user, user_auth, db)
        if sync_invocation_result['status'] == 'ko':
            return JSONResponse(content = {
                'status': 'ko',
                'message': sync_invocation_result['message'],
                'i18n_code': sync_invocation_result['i18n_code'],
                'cid': get_current_cid()
            }, status_code = sync_invocation_result['code'])
        dumped_result = json.loads(json.dumps(sync_invocation_result, cls = AlchemyEncoder))
        result = dumped_result['entity']['content']['result']
        data = Data()
        data.device_id = payload.device_id
        data.normalized_content = dumped_result
        data.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.add(data)
        db.commit()

        if is_numeric(result):
            numeric_data = NumericData()
            numeric_data.data_id = data.id
            numeric_data.device_id = payload.device_id
            numeric_data.key = "data"
            numeric_data.value = result
            numeric_data.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            db.add(numeric_data)
            db.commit()
        else:
            string_data = StringData()
            string_data.data_id = data.id
            string_data.device_id = payload.device_id
            string_data.key = "data"
            string_data.value = result
            string_data.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            db.add(string_data)
            db.commit()

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'Data added successfully',
            'cid': get_current_cid()
        }, status_code = 201)
