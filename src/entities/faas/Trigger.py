from datetime import datetime

from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import JSONB
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL

from database.postgres_db import Base

class TriggerEntity(Base):
    __tablename__ = 'faas_trigger'
    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    owner_id = Column(Integer, nullable=False)
    content = Column(JSONB, nullable=False)
    kind = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=datetime.now)
    updated_at = Column(String, nullable=False, default=datetime.now)

    @staticmethod
    def transferAllTriggersOwnership(owner_id, new_owner_id, db):
        triggers = db.query(TriggerEntity).filter(TriggerEntity.owner_id == owner_id).all()
        for trigger in triggers:
            trigger.owner_id = new_owner_id
        db.commit()

    @staticmethod
    def findById(trigger_id, db):
        return db.query(TriggerEntity).filter(TriggerEntity.id == trigger_id).first()
    
    @staticmethod
    def findUserTriggerById(user_id, trigger_id, db):
        return db.query(TriggerEntity).filter(TriggerEntity.owner_id == user_id, TriggerEntity.id == trigger_id).first()

    @staticmethod
    def findTriggersByFunctionId(function_id, db):
        return db.query(TriggerEntity).filter(TriggerEntity.content['function_id'].cast(String) == function_id).all()
