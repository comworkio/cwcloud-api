from database.postgres_db import Base
from sqlalchemy import Column, ForeignKey, String, Boolean, Integer, Text
from datetime import datetime

class SupportTicketLog(Base):
    __tablename__ = "support_change_status_log"
    id = Column(Integer, primary_key = True)
    status = Column(String(100), default = "await agent")
    is_admin = Column(Boolean, default = False)
    ticket_id = Column(Integer)
    message = Column(Text)
    creation_date = Column(String(100))
    change_date = Column(String(100))
    user_id = Column(Integer, ForeignKey("user.id"))

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getTicketLogs(ticket_id, db):
        ticket_logs = db.query(SupportTicketLog).filter(SupportTicketLog.ticket_id == ticket_id).all()
        return ticket_logs
    
    @staticmethod
    def getTicketLog(reply_id, db):
        ticket_log = db.query(SupportTicketLog).filter(SupportTicketLog.id == reply_id).first()
        return ticket_log
    
    @staticmethod
    def updateTicketLog(reply_id, message, db):
        change_date = datetime.now().isoformat()
        db.query(SupportTicketLog).filter(SupportTicketLog.id == reply_id).update({
            "message": message,
            "change_date": change_date
        })
        db.commit()

    @staticmethod
    def deleteTicketLog(reply_id, db):
        db.query(SupportTicketLog).filter(SupportTicketLog.id == reply_id).delete()
        db.commit()

    @staticmethod
    def deleteTicketReplies(ticket_id, db):
        db.query(SupportTicketLog).filter(SupportTicketLog.ticket_id == ticket_id).delete()
        db.commit()
