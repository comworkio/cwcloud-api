from database.postgres_db import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Float
from datetime import datetime

class RegisteredVoucher(Base):
    __tablename__ = "registered_voucher"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("user.id"))
    voucher_id = Column(Integer, ForeignKey("voucher.id"))
    credit =  Column(Float, nullable = False)
    created_at = Column(String(100), default = datetime.now().isoformat())

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getAll(db):
        registeredVouchers = db.query(RegisteredVoucher).all()
        return registeredVouchers

    @staticmethod
    def getUserRegisteredVouchers(user_id, db):
        registeredVouchers = db.query(RegisteredVoucher).filter(RegisteredVoucher.user_id == user_id).all()
        return registeredVouchers

    @staticmethod
    def getRegisteredVouchers(voucher_id, db):
        registeredVouchers = db.query(RegisteredVoucher).filter(RegisteredVoucher.voucher_id == voucher_id).all()
        return registeredVouchers

    @staticmethod
    def getUserRegisteredVoucher(user_id, voucher_id, db):
        registeredVoucher = db.query(RegisteredVoucher).filter(RegisteredVoucher.user_id == user_id, RegisteredVoucher.voucher_id == voucher_id).first()
        return registeredVoucher

    @staticmethod
    def updateRegisteredVoucherCredit(voucher_id, user_id, new_credit, db):
        db.query(RegisteredVoucher).filter(RegisteredVoucher.user_id == user_id, RegisteredVoucher.voucher_id == voucher_id).update({"credit": new_credit})
        db.commit()
