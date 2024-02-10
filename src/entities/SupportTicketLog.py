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
    change_date = Column(String(100), default = datetime.now().isoformat())
    user_id = Column(Integer, ForeignKey("user.id"))

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getTicketLogs(ticket_id, db):
        ticket_logs = db.query(SupportTicketLog).filter(SupportTicketLog.ticket_id == ticket_id).all()
        return ticket_logs

    @staticmethod
    def deleteTicketReplies(ticket_id, db):
        db.query(SupportTicketLog).filter(SupportTicketLog.ticket_id == ticket_id).delete()
        db.commit()
