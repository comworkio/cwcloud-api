from database.postgres_db import Base
from sqlalchemy import Column, String, Integer

class Mfa(Base):
    __tablename__ = "mfa"
    id = Column(Integer, primary_key = True)
    otp_code = Column(String(100))
    type = Column(String(100))
    user_id = Column(Integer)
    name = Column(String(100))

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getUserMfaMethodsByType(user_id, type, db):
        methods = db.query(Mfa).filter(Mfa.user_id == user_id, Mfa.type == type).all()
        return methods

    @staticmethod
    def getUserMfaMethods(user_id, db):
        methods = db.query(Mfa).filter(Mfa.user_id == user_id).all()
        return methods

    @staticmethod
    def getUserMfaMethod(user_id, type, db):
        method = db.query(Mfa).filter(Mfa.user_id == user_id, Mfa.type == type).first()
        return method

    @staticmethod
    def updateUserMfaMethod(user_id, type, otp_code, db):
        db.query(Mfa).filter(Mfa.user_id == user_id, Mfa.type == type).update({"otp_code": otp_code})
        db.commit()

    @staticmethod
    def deleteOne(method_id, db):
        db.query(Mfa).filter(Mfa.id == method_id).delete()
        db.commit()

    @staticmethod
    def findOne(method_id, db):
        method = db.query(Mfa).filter(Mfa.id == method_id).first()
        return method

    @staticmethod
    def updateUserMfaMethod(user_id, type, otp_code, db):
        db.query(Mfa).filter(Mfa.user_id == user_id, Mfa.type == type).update({"otp_code": otp_code})
        db.commit()

    @staticmethod
    def deleteUserMethods(user_id, db):
        db.query(Mfa).filter(Mfa.user_id == user_id).delete()
        db.commit()

    @staticmethod
    def getUserByOtpCode(otpCode, db):
        users = db.query(Mfa).filter(Mfa.otp_code == otpCode).all()
        return users
