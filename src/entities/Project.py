from database.postgres_db import Base
from sqlalchemy import Column, ForeignKey, String, Integer,CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

class Project(Base):
    __tablename__ = "project"
    __table_args__ = (
        CheckConstraint('type IN ("vm", "k8s")', name='type_check'),
    )
    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    url = Column(String(300))
    git_username = Column(String(300))
    access_token = Column(String(300))
    gitlab_host = Column(String(400))
    namespace_id = Column(String(100))
    created_at = Column(String(100), default = datetime.now().isoformat())
    userid = Column(Integer, ForeignKey('user.id'))
    type = Column(String(100),default = "vm", nullable = False)
    instances = relationship('Instance', backref = 'project', lazy = "select")

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getById(projectId, db) -> 'Project':
        project = db.query(Project).filter(Project.id == projectId).first()
        return project

    @staticmethod
    def getAll(db):
        projects = db.query(Project).all()
        return projects

    @staticmethod
    def findProjects(projectIds, db):
        projects = db.query(Project).filter(Project.id.in_(projectIds)).all()
        return projects

    @staticmethod
    def deleteOne(projectId, db):
        db.query(Project).filter(Project.id == projectId).delete()
        db.commit()

    @staticmethod
    def getProjectById(projectId, db):
        project = db.query(Project).filter(Project.id == projectId).first()
        return project

    @staticmethod
    def getProjectByName(projectName, db):
        project = db.query(Project).filter(Project.name == projectName).first()
        return project

    @staticmethod
    def getProjectByUrl(projectUrl, db):
        project = db.query(Project).filter(Project.url == projectUrl).first()
        return project

    @staticmethod
    def getAllProjects(db):
        projects = db.query(Project).all()
        return projects

    @staticmethod
    def getUserProjects(userId, db):
        projects = db.query(Project).filter(Project.userid == userId).all()
        return projects

    @staticmethod
    def getUserProjectsByType(userId, type, db):
        projects = db.query(Project).filter(Project.userid == userId, Project.type == type).all()
        return projects
    
    @staticmethod
    def getUserProject(projectId, userId, db):
        project = db.query(Project).filter(Project.id == projectId, Project.userid == userId).first()
        return project

    @staticmethod
    def getUserProjectByName(projectName, userId, db):
        project = db.query(Project).filter(Project.name == projectName, Project.userid == userId).first()
        return project

    @staticmethod
    def getUserProjectByUrl(projectUrl, userId, db):
        project = db.query(Project).filter(Project.url == projectUrl, Project.userid == userId).first()
        return project

    @staticmethod
    def updateOwner(project_id, owner_id, db):
        db.query(Project).filter(Project.id == project_id).update({"userid": owner_id})
        db.commit()
