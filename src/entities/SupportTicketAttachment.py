from sqlalchemy import Column, ForeignKey, String, Integer

from database.postgres_db import Base
from entities.SupportTicket import SupportTicket  # noqa: F401

class SupportTicketAttachment(Base):
    __tablename__ = "support_ticket_attachment"
    id = Column(Integer, primary_key = True)
    storage_key = Column(String(255))
    mime_type = Column(String(255))
    name = Column(String(255))
    support_ticket_id = Column(Integer, ForeignKey("support_ticket.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    def save(self, db):
        db.add(self)
        db.commit()
    
    @staticmethod
    def getAttachmentsByTicketId(ticket_id, db):
        return db.query(SupportTicketAttachment).filter(SupportTicketAttachment.support_ticket_id == ticket_id).all()
    
    @staticmethod
    def getAttachmentByTicketId(ticket_id, attachment_id, db):
        return db.query(SupportTicketAttachment).filter(SupportTicketAttachment.support_ticket_id == ticket_id, SupportTicketAttachment.id == attachment_id).first()
    
    @staticmethod
    def deleteAttachmentById(attachment_id, db):
        db.query(SupportTicketAttachment).filter(SupportTicketAttachment.id == attachment_id).delete()
        db.commit()
