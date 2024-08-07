from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, File, UploadFile

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Support import SupportTicketSchema, SupportTicketReplySchema
from middleware.auth_guard import get_current_active_user
from controllers.support import attach_file_to_ticket_by_id, delete_file_from_ticket_by_id, delete_reply_support_ticket, download_file_from_ticket_by_id, get_support_tickets, add_support_ticket, get_support_ticket, reply_support_ticket, auto_close_tickets, update_reply_support_ticket, update_support_ticket

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

@router.get("/{ticket_id}")
def get_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return get_support_ticket(current_user, ticket_id, db)

@router.post("")
def add_ticket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return add_support_ticket(current_user, payload, db)
    
@router.post("/{ticket_id}")
def reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketReplySchema, ticket_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.REPLY)):
        increment_counter(_counter, Method.GET, Action.REPLY)
        return reply_support_ticket(current_user, payload, ticket_id, db)
    
@router.patch("/{ticket_id}/reply/{reply_id}")
def update_reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, reply_id: str, payload: SupportTicketReplySchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PATCH)):
        increment_counter(_counter, Method.PATCH)
        return update_reply_support_ticket(current_user, ticket_id, reply_id, payload, db)
    
@router.delete("/{ticket_id}/reply/{reply_id}")
def delete_reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, reply_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_reply_support_ticket(current_user, ticket_id, reply_id, db)
    
@router.patch("/{ticket_id}")
def update_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, payload: SupportTicketSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.PATCH)):
        increment_counter(_counter, Method.PATCH)
        return update_support_ticket(current_user, ticket_id, payload, db)

@router.post("/auto-close")
def auto_close_support_tickets(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
   with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.POST, Action.AUTOCLOSE)
        return auto_close_tickets(current_user, db)
   
@router.post("/attach-file/{ticket_id}")
def attach_file_to_ticket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        return attach_file_to_ticket_by_id(current_user, ticket_id, files, db)

@router.get("/attach-file/{ticket_id}")
def download_files_from_ticket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, attachment_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        return download_file_from_ticket_by_id(current_user, ticket_id, attachment_id, db)
    
@router.delete("/attach-file/{ticket_id}")
def delete_files_from_ticket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, attachment_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.DELETE)):
        increment_counter(_counter, Method.DELETE)
        return delete_file_from_ticket_by_id(current_user, ticket_id, attachment_id, db)
