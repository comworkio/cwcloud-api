from fastapi import Depends, APIRouter, BackgroundTasks
from typing import Annotated
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Bucket import BucketSchema, BucketUpdateSchema
from controllers.admin.admin_bucket import admin_create_bucket, admin_get_bucket, admin_get_buckets, admin_get_user_buckets, admin_refresh_bucket, admin_remove_bucket, admin_update_bucket

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-bucket"

@router.get("/{provider}/{region}/all")
def get_all_buckets(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return admin_get_buckets(current_user, provider, region, db)

@router.get("/{provider}/{region}/{user_id}")
def get_all_buckets_by_user_id(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-byuser".format(_span_prefix)):
        return admin_get_user_buckets(current_user, provider, region, user_id, db)

@router.post("/{provider}/{region}/provision")
def create_bucket(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, payload: BucketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return admin_create_bucket(current_user, provider, region, payload, db, bt)

@router.post("/refresh/{bucket_id}")
def refresh_bucket(current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-refresh".format(_span_prefix)):
        return admin_refresh_bucket(current_user, bucket_id, db)

@router.get("/{bucket_id}")
def get_bucket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return admin_get_bucket(current_user, bucket_id, db)

@router.delete("/{bucket_id}")
def delete_bucket_by_id(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return admin_remove_bucket(current_user, bucket_id, db, bt)

@router.patch("/{bucket_id}")
def update_bucket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, payload: BucketUpdateSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-patch".format(_span_prefix)):
        return admin_update_bucket(current_user, bucket_id, payload, db)
