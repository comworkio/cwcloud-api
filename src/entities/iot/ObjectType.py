from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from fastapi_utils.guid_type import GUID_SERVER_DEFAULT_POSTGRESQL
from database.postgres_db import Base
from database.types import CachedGUID

class ObjectType(Base):
    __tablename__ = 'object_type'
    id = Column(CachedGUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    user_id = Column(Integer, ForeignKey("user.id"))
    content = Column(JSONB, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    @staticmethod
    def getAllObjectTypes(db):
        object_types = db.query(ObjectType).all()
        return object_types

    @staticmethod
    def getUserObjectTypes(user_id, db):
        object_types = db.query(ObjectType).filter(ObjectType.user_id == user_id).all()
        return object_types
    
    @staticmethod
    def findById(object_type_id, db):
        object_type = db.query(ObjectType).filter(ObjectType.id == object_type_id).first()
        return object_type
    
    @staticmethod
    def findUserObjectTypeById(user_id, object_type_id, db):
        object_type = db.query(ObjectType).filter(ObjectType.user_id == user_id, ObjectType.id == object_type_id).first()
        return object_type
    
    @staticmethod
    def updateObjectType(object_type_id, payload, updated_at, db):
        db.query(ObjectType).filter(ObjectType.id == object_type_id).update(payload.dict())
        db.query(ObjectType).filter(ObjectType.id == object_type_id).update({'updated_at': updated_at})
        db.commit()

    @staticmethod
    def deleteObjectType(object_type_id, db):
        db.query(ObjectType).filter(ObjectType.id == object_type_id).delete()
        db.commit()
