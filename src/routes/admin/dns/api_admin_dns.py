from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from controllers.admin.admin_dns import (admin_create_dns_record,
                                         admin_delete_dns_record,
                                         admin_list_dns_records,
                                         admin_list_dns_zones)
from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.Dns import DnsRecordSchema, DnsDeleteSchema
from schemas.User import UserSchema
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format

router = APIRouter()

_span_prefix = "adm-dns"
_counter = create_counter("adm_dns_api", "Admin dns API counter")

@router.get("/{provider}/dns_zones")
def list_dns_zones(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
    return admin_list_dns_zones(current_user, provider, db)

@router.get("/{provider}/list")
def list_dns_records(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYUSER)):
        increment_counter(_counter, Method.GET, Action.BYUSER)
    return admin_list_dns_records(current_user, provider, db)


@router.post("/{provider}/create")
def create_dns_record(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, payload: DnsRecordSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST, Action.BYUSER)):
        increment_counter(_counter, Method.POST, Action.BYUSER)
    increment_counter(_counter, Method.POST)
    return admin_create_dns_record(current_user, provider, payload, db)

@router.patch("/{provider}/delete")
def delete_dns_record(current_user: Annotated[UserSchema, Depends(admin_required)], provider: str, payload: DnsDeleteSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE, Action.BYUSER)):
        increment_counter(_counter, Method.DELETE, Action.BYUSER)
    return admin_delete_dns_record(current_user, provider, payload, db)
