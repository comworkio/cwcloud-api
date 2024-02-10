from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from database.postgres_db import Base
from utils.list import marshall_list_string

class Environment(Base):
    __tablename__ = "environment"
    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    path = Column(String(100))
    description = Column(String(1000))
    is_private = Column(Boolean)
    logo_url = Column(String(500))
    created_at = Column(String(100), default = datetime.now().isoformat())
    environment_template = Column(String(3000))
    doc_template = Column(String(3000))
    roles = Column(String(300))
    subdomains = Column(String(300))
    instances = relationship('Instance', backref = 'environment', lazy = "select")

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getById(envId, db):
        env = db.query(Environment).filter(Environment.id == envId).first()
        return env

    @staticmethod
    def getAvailableEnvironmentById(envId, db):
        env = db.query(Environment).filter(Environment.id == envId, Environment.is_private == False).first()
        return env

    @staticmethod
    def getByPath(path, db):
        env = db.query(Environment).filter(Environment.path == path).first()
        return env

    @staticmethod
    def getAll(db):
        env = db.query(Environment).all()
        return env

    @staticmethod
    def getAllAvailableEnvironments(db):
        env = db.query(Environment).filter(Environment.is_private == False).all()
        return env

    @staticmethod
    def deleteOne(envId, db):
        db.query(Environment).filter(Environment.id == envId).delete()
        db.commit()

    @staticmethod
    def updateEnvironment(id, name, path, description, roles, subdomains, environment_template, doc_template, is_private, logo_url, db):
        db.query(Environment).filter(Environment.id == id).update({"name": name, "path": path, "description": description, "roles": marshall_list_string(roles), "subdomains": marshall_list_string(subdomains), "environment_template": environment_template, "doc_template": doc_template, "is_private": is_private, "logo_url": logo_url})
        db.commit()
