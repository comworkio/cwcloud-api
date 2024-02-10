from fastapi import Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session

from schemas.User import UserSchema
from database.postgres_db import get_db
from schemas.Support import AdminSupportTicketSchema, SupportTicketReplySchema
from middleware.auth_guard import admin_required
from controllers.admin.admin_support import add_support_ticket, get_support_tickets, get_support_ticket, reply_support_ticket, delete_support_ticket

router = APIRouter()

@router.get("")
def get_all_support_tickets(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    return get_support_tickets(current_user, db)

@router.post("")
def add_ticket(current_user: Annotated[UserSchema, Depends(admin_required)], payload: AdminSupportTicketSchema, db: Session = Depends(get_db)):
    return add_support_ticket(current_user, payload, db)

@router.get("/{ticket_id}")
def get_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, db: Session = Depends(get_db)):
    return get_support_ticket(current_user, ticket_id, db)

@router.post("/{ticket_id}")
def reply_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, payload: SupportTicketReplySchema, db: Session = Depends(get_db)):
    return reply_support_ticket(current_user, ticket_id, payload, db)

@router.delete("/{ticket_id}")
def remove_support_ticket_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], ticket_id: str, db: Session = Depends(get_db)):
    return delete_support_ticket(current_user, ticket_id, db)
