from database.postgres_db import Base
from sqlalchemy import Column, String, Integer, Float
from datetime import datetime

class Voucher(Base):
    __tablename__ = "voucher"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer)
    validity = Column(Integer)
    code = Column(String(100))
    price =  Column(Float, nullable = False)
    created_at = Column(String(100), default = datetime.now().isoformat())

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getAll(db):
        vouchers = db.query(Voucher).all()
        return vouchers

    @staticmethod
    def findVouchers(vouchersIds, db):
        vouchers = db.query(Voucher).filter(Voucher.id.in_(vouchersIds)).all()
        return vouchers

    @staticmethod
    def getByCode(code, db):
        voucher = db.query(Voucher).filter(Voucher.code == code).first()
        return voucher

    @staticmethod
    def getById(voucher_id, db):
        voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
        return voucher

    @staticmethod
    def deleteOne(voucher_id, db):
        db.query(Voucher).filter(Voucher.id == voucher_id).delete()
        db.commit()
