from sqlalchemy import Column, ForeignKey, String, Integer, BINARY
from datetime import datetime

from database.postgres_db import Base

class KubeConfigFile(Base):
    __tablename__ = "k8s_kubeconfig_files"
    id = Column(Integer, primary_key = True)
    content = Column(BINARY)
    created_at = Column(String(100), default = datetime.now().isoformat())
    owner_id = Column(Integer, ForeignKey("user.id"))

    def save(self, db):
        db.add(self)
        db.commit()

    def delete(self, db):
        db.delete(self)
        db.commit()
        
    @staticmethod
    def findOne(id, db):
        kubeconfigFile = db.query(KubeConfigFile).filter(KubeConfigFile.id == id).first()
        return kubeconfigFile
    
    @staticmethod
    def getAll(db):
        kubeconfigFiles = db.query(KubeConfigFile).all()
        return kubeconfigFiles
    
    @staticmethod
    def deleteOne(id, db):
        db.query(KubeConfigFile).filter(KubeConfigFile.id == id).delete()
        db.commit()
        
    @staticmethod
    def deleteAll(db):
        db.query(KubeConfigFile).delete()
        db.commit()
        
    @staticmethod
    def getUserKubeconfigFiles(user_id, db):
        kubeconfigFiles = db.query(KubeConfigFile).filter(KubeConfigFile.owner_id == user_id).all()
        return kubeconfigFiles   