from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Support import AdminSupportTicketSchema, SupportTicketReplySchema
from controllers.admin.admin_support import add_support_ticket, get_support_tickets, get_support_ticket, reply_support_ticket, delete_support_ticket

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-support"

@router.get("")
def get_all_support_tickets(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return get_support_tickets(current_user, db)

@router.post("")
def add_ticket(current_user: Annotated[UserSchema, Depends(admin_required)], payload: AdminSupportTicketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return add_support_ticket(current_user, payload, db)

@router.get("/{ticket_id}")
def get_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return get_support_ticket(current_user, ticket_id, db)

@router.post("/{ticket_id}")
def reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, payload: SupportTicketReplySchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-reply".format(_span_prefix)):
        return reply_support_ticket(current_user, ticket_id, payload, db)

@router.delete("/{ticket_id}")
def remove_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        return delete_support_ticket(current_user, ticket_id, db)
