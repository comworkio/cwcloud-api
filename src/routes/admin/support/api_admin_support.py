from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Support import AdminSupportTicketSchema, SupportTicketReplySchema, SupportTicketSchema
from controllers.admin.admin_support import add_support_ticket, delete_reply_support_ticket, get_support_tickets, get_support_ticket, reply_support_ticket, delete_support_ticket, update_reply_support_ticket, update_support_ticket

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "adm-support"
_counter = create_counter("adm_support_api", "Admin support API counter")

@router.get("")
def get_all_support_tickets(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return get_support_tickets(current_user, db)
    
@router.get("/{ticket_id}")
def get_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_support_ticket(current_user, ticket_id, db)

@router.post("")
def add_ticket(current_user: Annotated[UserSchema, Depends(admin_required)], payload: AdminSupportTicketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_support_ticket(current_user, payload, db)

@router.post("/{ticket_id}")
def reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, payload: SupportTicketReplySchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST, Action.REPLY)):
        increment_counter(_counter, Method.POST, Action.REPLY)
        return reply_support_ticket(current_user, ticket_id, payload, db)

@router.delete("/{ticket_id}/reply/{reply_id}")
def delete_reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, reply_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_reply_support_ticket(current_user, ticket_id, reply_id, db)

@router.patch("/{ticket_id}")
def update_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, payload: SupportTicketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PATCH)):
        increment_counter(_counter, Method.PATCH)
        return update_support_ticket(current_user, ticket_id, payload, db)
    
@router.patch("/{ticket_id}/reply/{reply_id}")
def update_reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, reply_id: str, payload: SupportTicketReplySchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PATCH)):
        increment_counter(_counter, Method.PATCH)
        return update_reply_support_ticket(current_user, ticket_id, reply_id, payload, db)

@router.delete("/{ticket_id}")
def remove_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_support_ticket(current_user, ticket_id, db)
