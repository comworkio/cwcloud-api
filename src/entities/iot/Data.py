from sqlalchemy import Column, ForeignKey, String, Float
from sqlalchemy.dialects.postgresql import JSONB
from fastapi_utils.guid_type import GUID_SERVER_DEFAULT_POSTGRESQL
from database.postgres_db import Base
from database.types import CachedGUID

class Data(Base):
    __tablename__ = 'data'
    id = Column(CachedGUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    device_id = Column(String, ForeignKey("device.id"))
    normalized_content = Column(JSONB, nullable=False)
    created_at = Column(String, nullable=False)

    @staticmethod
    def getAllData(db):
        return db.query(Data).all()

class NumericData(Base):
    __tablename__ = 'numeric_data'
    id = Column(CachedGUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    data_id = Column(String, ForeignKey("data.id"))
    device_id = Column(String, ForeignKey("device.id"))
    key = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(String, nullable=False)

    @staticmethod
    def getAllNumericData(db):
        return db.query(NumericData).all()

class StringData(Base):
    __tablename__ = 'string_data'
    id = Column(CachedGUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    data_id = Column(String, ForeignKey("data.id"))
    device_id = Column(String, ForeignKey("device.id"))
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

    @staticmethod
    def getAllStringData(db):
        return db.query(StringData).all()
