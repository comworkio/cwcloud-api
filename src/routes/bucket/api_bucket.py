from fastapi import Depends, status, APIRouter, BackgroundTasks
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from controllers.bucket import get_bucket, get_buckets, update_bucket, remove_bucket

router = APIRouter()

@router.get('/{provider}/{region}/{bucketId}', status_code = status.HTTP_200_OK)
def get(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, bucketId: str, db: Session = Depends(get_db)):
    return get_bucket(current_user, provider, region, bucketId, db)

@router.delete('/{provider}/{region}/{bucketId}')
def delete_bucket(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, bucketId: str, db: Session = Depends(get_db)):
    return remove_bucket(current_user, provider, region, bucketId, db, bt)

@router.patch('/{provider}/{region}/{bucketId}', status_code = status.HTTP_200_OK)
def patch_bucket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, bucketId, db: Session = Depends(get_db)):
    return update_bucket(current_user, provider, region, bucketId, db)

@router.get('/{provider}/{region}', status_code = status.HTTP_200_OK)
def get_all_buckets(current_user: Annotated[UserSchema, Depends(get_current_active_user)], provider: str, region: str, db: Session = Depends(get_db)):
    return get_buckets(current_user, provider, region, db)