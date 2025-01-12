from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from database.postgres_db import Base
from entities.Instance import Instance

from utils.list import marshall_list_string

class Environment(Base):
    __tablename__ = "environment"
    __table_args__ = (
        CheckConstraint('type IN ("vm", "k8s")', name='type_check'),
    )
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
    external_roles = Column(Text)
    type = Column(String(25),default = "vm", nullable = False)
    subdomains = Column(String(300))
    args = Column(JSONB)
    instances = relationship("Instance", backref = "environment", lazy = "select")

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getById(envId, db):
        env = db.query(Environment).filter(Environment.id == envId).first()
        return env

    @staticmethod
    def getAvailableEnvironmentById(envId, db):
        env = db.query(Environment).filter(Environment.id == envId, Environment.is_private is False).first()
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
    def getByType(type, db):
        env = db.query(Environment).filter(Environment.type == type).all()
        return env

    @staticmethod
    def getAllPaginated(start_index, max_results, db):
        env = db.query(Environment).limit(int(max_results)).offset(int(start_index)).all()
        return env

    def getByTypePaginated(type, start_index, max_results, db):
        env = db.query(Environment).filter(Environment.type == type).limit(int(max_results)).offset(int(start_index)).all()
        return env

    @staticmethod
    def getAllAvailableEnvironments(db):
        env = db.query(Environment).filter(Environment.is_private is False).all()
        return env

    @staticmethod
    def getAllAvailableEnvironmentsPaged(start_index, max_results, db):
        env = db.query(Environment).filter(Environment.is_private is False).limit(int(max_results)).offset(int(start_index)).all()
        return env

    @staticmethod
    def getAllAvailableEnvironmentsByType(type, db):
        env = db.query(Environment).filter(Environment.is_private is False, Environment.type == type).all()
        return env

    @staticmethod
    def getAllAvailableEnvironmentsByTypePaged(type, start_index, max_results, db):
        env = db.query(Environment).filter(Environment.is_private is False, Environment.type == type).limit(int(max_results)).offset(int(start_index)).all()
        return env

    @staticmethod
    def deleteOne(envId, db):
        db.query(Environment).filter(Environment.id == envId).delete()
        db.commit()

    @staticmethod
    def updateEnvironment(id, name, path, description, roles, subdomains, environment_template, doc_template, is_private, logo_url, args, db):
        db.query(Environment).filter(Environment.id == id).update({"name": name, "path": path, "description": description, "roles": marshall_list_string(roles), "subdomains": marshall_list_string(subdomains), "environment_template": environment_template, "doc_template": doc_template, "is_private": is_private, "logo_url": logo_url, "args": args})
        db.commit()
