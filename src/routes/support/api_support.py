from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Support import SupportTicketSchema, SupportTicketReplySchema
from middleware.auth_guard import get_current_active_user
from controllers.support import get_support_tickets, add_support_ticket, get_support_ticket, reply_support_ticket, auto_close_tickets

from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "support"
_counter = create_counter("support_api", "Support API counter")

@router.get("")
def get_tickets(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return get_support_tickets(current_user, db)
    
@router.get("/auto-close")
def auto_close_support_tickets(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
   with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return auto_close_tickets(current_user, db)

@router.post("")
def add_ticket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_support_ticket(current_user, payload, db)

@router.get("/{ticket_id}")
def get_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_support_ticket(current_user, ticket_id, db)

@router.post("/{ticket_id}")
def reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketReplySchema, ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.REPLY)):
        increment_counter(_counter, Method.GET, Action.REPLY)
        return reply_support_ticket(current_user, payload, ticket_id, db)

