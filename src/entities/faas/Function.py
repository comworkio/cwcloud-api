from datetime import datetime

from sqlalchemy import Column, Boolean, String, Integer
from sqlalchemy.dialects.postgresql import JSONB
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL

from database.postgres_db import Base

class FunctionEntity(Base):
    __tablename__ = 'faas_function'
    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    is_public = Column(Boolean, nullable=False)
    content = Column(JSONB, nullable=False)
    created_at = Column(String, nullable=False, default=datetime.now)
    updated_at = Column(String, nullable=False, default=datetime.now)
    owner_id = Column(Integer, nullable=False)

    @staticmethod
    def transferAllFunctionsOwnership(owner_id, new_owner_id, db):
        functions = db.query(FunctionEntity).filter(FunctionEntity.owner_id == owner_id).all()
        for function in functions:
            function.owner_id = new_owner_id
        db.commit()

    @staticmethod
    def findById(function_id, db):
        return db.query(FunctionEntity).filter(FunctionEntity.id == function_id).first()
    
    @staticmethod
    def findUserFunctionById(user_id, function_id, db):
        return db.query(FunctionEntity).filter(FunctionEntity.owner_id == user_id, FunctionEntity.id == function_id).first()
