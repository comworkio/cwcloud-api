from sqlalchemy import Column, ForeignKey, String, Boolean
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL
from database.postgres_db import Base

class Device(Base):
    __tablename__ = 'device'
    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    typeobject_id = Column(GUID, ForeignKey("object_type.id"))
    username = Column(String, ForeignKey("user.email"))
    active = Column(Boolean, default = False)

    @staticmethod
    def getAllDevices(db):
        return db.query(Device).all()
    
    @staticmethod
    def getUserDevices(username, db):
        return db.query(Device).filter(Device.username == username).all()
    
    @staticmethod
    def getDeviceById(device_id, db):
        return db.query(Device).filter(Device.id == device_id).first()
    
    @staticmethod
    def getUserDeviceById(username, device_id, db):
        return db.query(Device).filter(Device.username == username, Device.id == device_id).first()
    
    @staticmethod
    def getUserLatestInactiveDevice(username, db):
        return db.query(Device).filter(Device.username == username, Device.active == False).first() # noqa

    @staticmethod
    def activateDevice(device_id, db):
        db.query(Device).filter(Device.id == device_id).update({"active": True})
        db.commit()
    
    @staticmethod
    def deleteDeviceById(device_id, db):
        db.query(Device).filter(Device.id == device_id).delete()
        db.commit()

    @staticmethod
    def transferAllDevicesOwnership(username, new_username, db):
        devices = db.query(Device).filter(Device.username == username).all()
        for device in devices:
            device.username = new_username
        db.commit()
