
from entities.faas.Function import FunctionEntity
from entities.faas.Trigger import TriggerEntity
from utils.common import is_not_uuid
from fastapi import HTTPException

def object_type_user_content_check(current_user, payload, db):
    if is_not_uuid(payload.content.decoding_function):
        raise HTTPException(status_code=400, detail='Decoding function id is not valid')
    
    existed_function = FunctionEntity.findUserFunctionById(current_user.id, payload.content.decoding_function, db)
    if not existed_function:
        raise HTTPException(status_code=404, detail='Decoding function id not found')
    
    for trigger in payload.content.triggers:
        if is_not_uuid(trigger):
            raise HTTPException(status_code=400, detail='Trigger id is not valid')

        existed_trigger = TriggerEntity.findById (trigger, db)
        if not existed_trigger:
            raise HTTPException(status_code=404, detail=f'Trigger with id {trigger.id} not found')

def object_type_admin_content_check(payload, db):
    if is_not_uuid(payload.content.decoding_function):
        raise HTTPException(status_code=400, detail='Decoding function id is not valid')
    
    existed_function = FunctionEntity.findById(payload.content.decoding_function, db)
    if not existed_function:
        raise HTTPException(status_code=404, detail='Decoding function id not found')
    
    for trigger in payload.content.triggers:
        if is_not_uuid(trigger):
            raise HTTPException(status_code=400, detail='Trigger id is not valid')

        existed_trigger = TriggerEntity.findById(trigger, db)
        if not existed_trigger:
            raise HTTPException(status_code=404, detail=f'Trigger with id {trigger.id} not found')

