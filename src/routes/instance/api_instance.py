from fastapi import Depends, APIRouter, BackgroundTasks
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Instance import InstanceUpdateSchema, InstanceAttachSchema, InstanceProvisionSchema
from middleware.auth_guard import get_current_active_user
from controllers.instance import attach_instance, get_instance, get_instances, provision_instance, update_instance, remove_instance

router = APIRouter()

@router.get("/{provider}/{region}")
def get_all_instances(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, db: Session = Depends(get_db)):
    return get_instances(current_user, provider, region, db)

@router.get("/{provider}/{region}/{instance_id}")
def get_instance_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, instance_id: str, db: Session = Depends(get_db)):
    return get_instance(current_user, provider, region, instance_id, db)

@router.delete("/{provider}/{region}/{instance_id}")
def delete_instance(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, instance_id: str , db: Session = Depends(get_db)):
    return remove_instance(current_user, provider, region, instance_id, db, bt)

@router.patch("/{provider}/{region}/{instance_id}")
def update_instance_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: InstanceUpdateSchema, provider: str, region: str, instance_id: str , db: Session = Depends(get_db)):
    return update_instance(current_user, payload, provider, region, instance_id, db)

@router.post("/{provider}/{region}/{zone}/attach/{project_id}")
def attach_new_instance(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, zone: str, project_id: str, payload: InstanceAttachSchema, db: Session = Depends(get_db)):
    return attach_instance(bt, current_user, provider, region, zone, project_id, payload, db)

@router.post("/{provider}/{region}/{zone}/provision/{environment}")
def add_new_instance(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: InstanceProvisionSchema, provider: str, region: str, zone: str, environment: str , db: Session = Depends(get_db)):
    return provision_instance(current_user, payload, provider, region, zone, environment, db, bt)
