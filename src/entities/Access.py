from sqlalchemy import Column, ForeignKey, String, Integer
from datetime import datetime

from database.postgres_db import Base

class Access(Base):
    __tablename__ = "access"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("user.id"))
    object_id = Column(Integer)
    access_str = Column(String, default = "rw")
    object_type = Column(String(100))
    created_at = Column(String(100), default = datetime.now().isoformat())
    owner_id = Column(Integer, ForeignKey("user.id"))

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def findById(access_id, db):
        access = db.query(Access).filter(Access.id == access_id).first()
        return access

    @staticmethod
    def updateObjectAccessesOwner(object_type, object_id, owner_id, db):
        db.query(Access).filter(Access.object_type == object_type, Access.object_id == object_id).update({"owner_id": owner_id})
        db.commit()

    @staticmethod
    def updateObjectsAccessesOwner(object_type, object_ids, owner_id, db):
        db.query(Access).filter(Access.object_type == object_type, Access.object_id.in_(object_ids)).update({"owner_id": owner_id})
        db.commit()

    @staticmethod
    def getUserAccessesByType(user_id, type, db):
        accesses = db.query(Access).filter(Access.user_id == user_id, Access.object_type == type).all()
        return accesses

    @staticmethod
    def getUserAllAccesses(user_id, db):
        accesses = db.query(Access).filter(Access.user_id == user_id).all()
        return accesses

    @staticmethod
    def getUserAccessToObject(user_id, type, object_id, db):
        access = db.query(Access).filter(Access.user_id == user_id, Access.object_id == object_id, Access.object_type == type).first()
        return access

    @staticmethod
    def getOwnerAccesses(owner_id, db):
        access = db.query(Access).filter(Access.owner_id == owner_id).all()
        return access

    @staticmethod
    def deleteOne(access_id, db):
        db.query(Access).filter(Access.id == access_id).delete()
        db.commit()
