from fastapi import Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Support import SupportTicketSchema, SupportTicketReplySchema
from middleware.auth_guard import get_current_active_user
from controllers.support import get_support_tickets, add_support_ticket, get_support_ticket, reply_support_ticket

router = APIRouter()

@router.get("")
def get_tickets(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return get_support_tickets(current_user, db)

@router.post("")
def add_ticket(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketSchema, db: Session = Depends(get_db)):
    return add_support_ticket(current_user, payload, db)

@router.get("/{ticket_id}")
def get_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], ticket_id: str, db: Session = Depends(get_db)):
    return get_support_ticket(current_user, ticket_id, db)

@router.post("/{ticket_id}")
def reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: SupportTicketReplySchema, ticket_id: str, db: Session = Depends(get_db)):
    return reply_support_ticket(current_user, payload, ticket_id, db)
