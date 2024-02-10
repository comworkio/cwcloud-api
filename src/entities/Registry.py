from database.postgres_db import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Text
from datetime import datetime

class Registry(Base):
    __tablename__ = "registry"
    id = Column(Integer, primary_key = True)
    hash = Column(String(10))
    name = Column(String(200))
    type = Column(String(50))
    created_at = Column(String(100), default = datetime.now().isoformat())
    access_key = Column(Text)
    secret_key = Column(Text)
    status = Column(String(50), default = "starting")
    endpoint = Column(String(300))
    user_id = Column(Integer, ForeignKey("user.id"))
    region = Column(String(100))
    provider = Column(String(100))

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def findById(id, db):
        registry = db.query(Registry).filter(Registry.id == id, Registry.status!= "deleted").first()
        return registry

    @staticmethod
    def findRegistriesByRegion(registryIds, provider, region, db):
        registries = db.query(Registry).filter(Registry.id.in_(registryIds), Registry.provider == provider, Registry.region == region, Registry.status!= "deleted").all()
        return registries

    @staticmethod
    def updateStatus(id, status, db):
        db.query(Registry).filter(Registry.id == id).update({"status": status})
        db.commit()

    @staticmethod
    def update(id, endpoint, access_key, secret_key, status, db):
        db.query(Registry).filter(Registry.id == id).update({"endpoint": endpoint, "access_key": access_key, "secret_key": secret_key , "status": status})
        db.commit()

    @staticmethod
    def updateInfo(id, provider, region, registry_type, status, root_dns_zone, db):
        current_date = datetime.now().isoformat()
        db.query(Registry).filter(Registry.id == id).update({"provider": provider, "region": region, "type": registry_type, "status": status, "root_dns_zone": root_dns_zone})
        db.commit()

    @staticmethod
    def updateType(id, type, db):
        current_date = datetime.now().isoformat()
        db.query(Registry).filter(Registry.id == id).update({"type": type})
        db.commit()

    @staticmethod
    def updateCredentials(id, access_key, secret_key, db):
        db.query(Registry).filter(Registry.id == id).update({"access_key": access_key, "secret_key": secret_key})
        db.commit()

    @staticmethod
    def updateSingleCred(id, endpoint, access_key, status, db):
        db.query(Registry).filter(Registry.id == id).update({"endpoint": endpoint,  "access_key": access_key, "status": status})
        db.commit() 

    @staticmethod
    def updateAccessKey(id, access_key, db):
        db.query(Registry).filter(Registry.id == id).update({"access_key": access_key})
        db.commit()

    @staticmethod
    def getRegistryAccessKey(provider, region, id, db):
        access_key = db.query(Registry.access_key).filter(Registry.provider == provider, Registry.region == region, Registry.id == id).first()
        return str(access_key)

    @staticmethod
    def getAllUserRegistriesByRegion(provider, region, user_id, db):
        registries = db.query(Registry).filter(Registry.provider == provider, Registry.region == region, Registry.user_id == user_id, Registry.status!= "deleted").all()
        return registries

    @staticmethod
    def getAllUserRegistries(user_id, db):
        registries = db.query(Registry).filter(Registry.user_id == user_id, Registry.status!= "deleted").all()
        return registries

    @staticmethod
    def getAllRegistriesByRegion(provider, region, db):
        registries = db.query(Registry).filter(Registry.provider == provider, Registry.region == region, Registry.status!= "deleted").all()
        return registries

    @staticmethod
    def findUserRegistry(provider, userId, registry_id, region, db):
        registry = db.query(Registry).filter(Registry.id == registry_id, Registry.provider == provider, Registry.region == region, Registry.user_id == userId, Registry.status!= "deleted").first()
        return registry

    @staticmethod
    def findRegistry(provider, region, registryId, db):
        registry = db.query(Registry).filter(Registry.id == registryId, Registry.provider == provider, Registry.region == region, Registry.status!= "deleted").first()
        return registry

    @staticmethod
    def patch(registry_id, changes, db):
        db.query(Registry).filter(Registry.id == registry_id).update(changes)
        db.commit()
