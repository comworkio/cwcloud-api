from sqlalchemy import Column, ForeignKey, String, Integer, Text
from datetime import datetime
from database.postgres_db import Base

class Deployment(Base):
    __tablename__ = "k8s_deployment"
    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    description = Column(Text)
    hash = Column(String(10))
    cluster_id = Column(Integer, ForeignKey("k8s_cluster.id"))
    project_id = Column(Integer, ForeignKey("project.id"))
    env_id = Column(Integer, ForeignKey("environment.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(String(100), default = datetime.isoformat(datetime.now()))

    def save(self, db):
        db.add(self)
        db.commit()

    def delete(self, db):
        db.delete(self)
        db.commit()

    @staticmethod
    def findOne(id, db) -> "Deployment":
        app = db.query(Deployment).filter(Deployment.id == id).first()
        return app

    @staticmethod
    def getAll(db):
        apps = db.query(Deployment).all()
        return apps

    @staticmethod
    def getAllByClusterId(cluster_id, db) -> list["Deployment"]:
        apps = db.query(Deployment).filter(Deployment.cluster_id == cluster_id).all()
        return apps

    @staticmethod
    def getAllByUser(user_id, db) -> list["Deployment"]:
        apps = db.query(Deployment).filter(Deployment.user_id == user_id).all()
        return apps

    @staticmethod
    def getAllByProject(project_id, db) -> list["Deployment"]:
        apps = db.query(Deployment).filter(Deployment.project_id == project_id).all()
        return apps

    @staticmethod
    def getFirstByProject(project_id, db) -> "Deployment":
        app = db.query(Deployment).filter(Deployment.project_id == project_id).first()
        return app

    @staticmethod
    def deleteOne(id, db):
        db.query(Deployment).filter(Deployment.id == id).delete()
        db.commit()

    @staticmethod
    def deleteAll(db):
        db.query(Deployment).delete()
        db.commit()
