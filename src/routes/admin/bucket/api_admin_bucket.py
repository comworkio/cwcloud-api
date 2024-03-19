from fastapi import Depends, APIRouter, BackgroundTasks
from typing import Annotated
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Bucket import BucketSchema, BucketUpdateSchema
from controllers.admin.admin_bucket import admin_create_bucket, admin_get_bucket, admin_get_buckets, admin_get_user_buckets, admin_refresh_bucket, admin_remove_bucket, admin_update_bucket

from utils.observability.otel import get_otel_tracer
from utils.observability.counter import create_counter, increment_counter
from utils.observability.traces import span_format
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "adm-bucket"
_counter = create_counter("adm_bucket_api", "Admin bucket API counter")

@router.get("/{provider}/{region}/all")
def get_all_buckets(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return admin_get_buckets(current_user, provider, region, db)

@router.get("/{provider}/{region}/{user_id}")
def get_all_buckets_by_user_id(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, user_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYUSER)):
        increment_counter(_counter, Method.GET, Action.BYUSER)
        return admin_get_user_buckets(current_user, provider, region, user_id, db)

@router.post("/{provider}/{region}/provision")
def create_bucket(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, region: str, payload: BucketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return admin_create_bucket(current_user, provider, region, payload, db, bt)

@router.post("/refresh/{bucket_id}")
def refresh_bucket(current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST, Action.REFRESH)):
        increment_counter(_counter, Method.POST, Action.REFRESH)
        return admin_refresh_bucket(current_user, bucket_id, db)

@router.get("/{bucket_id}")
def get_bucket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return admin_get_bucket(current_user, bucket_id, db)

@router.delete("/{bucket_id}")
def delete_bucket_by_id(bt: BackgroundTasks, current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return admin_remove_bucket(current_user, bucket_id, db, bt)

@router.patch("/{bucket_id}")
def update_bucket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], bucket_id: str, payload: BucketUpdateSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PATCH)):
        increment_counter(_counter, Method.PATCH)
        return admin_update_bucket(current_user, bucket_id, payload, db)
