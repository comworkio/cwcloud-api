from database.postgres_db import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Text
from datetime import datetime

class SupportTicket(Base):
    __tablename__ = "support_ticket"
    id = Column(Integer, primary_key = True)
    severity = Column(String(100))
    status = Column(String(100), default = "await agent")
    user_id = Column(Integer, ForeignKey("user.id"))
    selected_product = Column(String(200))
    subject = Column(String(200))
    message = Column(Text)
    created_at = Column(String(100), default = datetime.now().isoformat())
    last_update = Column(String(100), default = datetime.now().isoformat())
    gitlab_issue_id = Column(Integer)

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getUserSupportTickets(user_id, db):
        tickets = db.query(SupportTicket).filter(SupportTicket.user_id == user_id).all()
        return tickets

    @staticmethod
    def getUserSupportTicket(user_id, ticket_id, db):
        ticket = db.query(SupportTicket).filter(SupportTicket.user_id == user_id, SupportTicket.id == ticket_id).first()
        return ticket

    @staticmethod
    def getAllSupportTickets(db):
        tickets = db.query(SupportTicket).all()
        return tickets

    @staticmethod
    def getSupportTicket(ticket_id, db):
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        return ticket

    @staticmethod
    def updateTicketStatus(ticket_id, status, db):
        udpated_at = datetime.now().isoformat()
        db.query(SupportTicket).filter(SupportTicket.id == ticket_id).update({"status": status, "last_update": udpated_at})
        db.commit()

    @staticmethod
    def attach_gitlab_issue(ticket_id, gitlab_issue_id, db):
        db.query(SupportTicket).filter(SupportTicket.id == ticket_id).update({"gitlab_issue_id": gitlab_issue_id})
        db.commit()

    @staticmethod
    def deleteOne(ticket_id, db):
        db.query(SupportTicket).filter(SupportTicket.id == ticket_id).delete()
        db.commit()
