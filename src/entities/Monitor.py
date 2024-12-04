from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from fastapi_utils.guid_type import GUID_SERVER_DEFAULT_POSTGRESQL
from database.postgres_db import Base
from database.types import CachedGUID

class Monitor(Base):
    __tablename__ = 'monitor'
    id = Column(CachedGUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    family = Column(String)
    url = Column(Text, nullable=False)
    method = Column(String, default='GET')
    body = Column(Text)
    expected_http_code = Column(String, default='20*')
    expected_contain = Column(String)
    timeout = Column(Integer, default=30)
    username = Column(String)
    password = Column(String)
    headers = Column(JSONB, default=dict)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    status = Column(String, default='failure')
    response_time = Column(String, default='')
    
    def save(self, db):
        db.add(self)
        db.commit()
        
    @staticmethod
    def getAllMonitors(db):
        monitors = db.query(Monitor).all()
        return monitors
        
    @staticmethod
    def getUserMonitors(userId, db):
        monitors = db.query(Monitor).filter(Monitor.user_id == userId).all()
        return monitors
    
    @staticmethod
    def findMonitorById(monitor_id, db):
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        return monitor

    @staticmethod
    def findUserMonitorById(userId, monitorId, db):
        monitor = db.query(Monitor).filter(Monitor.id == monitorId, Monitor.user_id == userId).first()
        return monitor
    
    @staticmethod
    def _serialize_headers(headers):
        """Convert Header objects to dictionaries"""
        if not headers:
            return []
        return [{"name": header.name, "value": header.value} for header in headers]
    
    @staticmethod
    def _prepare_update_data(payload):
        return {
            'name': payload.name,
            'family': payload.family,
            'url': payload.url,
            'method': payload.method,
            'body': payload.body,
            'expected_http_code': payload.expected_http_code,
            'expected_contain': payload.expected_contain,
            'timeout': payload.timeout,
            'username': payload.username,
            'password': payload.password,
            'headers': Monitor._serialize_headers(payload.headers),
            'updated_at': datetime.now().date().strftime('%Y-%m-%d')
        }
    
    @staticmethod
    def _perform_update(db, monitor_id, update_data):
        db.query(Monitor).filter(Monitor.id == monitor_id).update(update_data)
        db.commit()
    
    @staticmethod
    def adminUpdateInfo(payload, monitor_id, db):
        update_data = Monitor._prepare_update_data(payload)
        update_data['user_id'] = payload.user_id
        Monitor._perform_update(db, monitor_id, update_data)
    
    @staticmethod
    def updateInfo(payload, monitor_id, db):
        update_data = Monitor._prepare_update_data(payload)
        Monitor._perform_update(db, monitor_id, update_data)
        
    @staticmethod
    def deleteUserMonitor(userId, monitorId, db):
        monitor = db.query(Monitor).filter(Monitor.id == monitorId, Monitor.user_id == userId).first()
        db.delete(monitor)
        db.commit()
        
    @staticmethod
    def deleteMonitor(monitorId, db):
        monitor = db.query(Monitor).filter(Monitor.id == monitorId).first()
        db.delete(monitor)
        db.commit()
        
    @staticmethod
    def updateMonitorStatus(monitor_id, status, response_time, db):
        db.query(Monitor).filter(Monitor.id == monitor_id).update({'status': status, 'response_time': response_time})
        db.commit()

