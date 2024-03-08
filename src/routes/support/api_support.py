from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Support import SupportTicketSchema, SupportTicketReplySchema
from middleware.auth_guard import get_current_active_user
from controllers.support import get_support_tickets, add_support_ticket, get_support_ticket, reply_support_ticket

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "support"

@router.get("")
def get_tickets(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return get_support_tickets(current_user, db)

@router.post("")
def add_ticket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        return add_support_ticket(current_user, payload, db)

@router.get("/{ticket_id}")
def get_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        return get_support_ticket(current_user, ticket_id, db)

@router.post("/{ticket_id}")
def reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketReplySchema, ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post-reply".format(_span_prefix)):
        return reply_support_ticket(current_user, payload, ticket_id, db)
