from database.postgres_db import Base
from sqlalchemy import Column, String, Integer, BigInteger, Float, DateTime, func
from datetime import datetime

class Invoice(Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key = True)
    ref = Column(String(100))
    date_created = Column(DateTime, nullable = False, default = datetime.now().isoformat())
    from_date = Column(DateTime, nullable = False)
    to_date = Column(DateTime, nullable = False)
    user_id = Column(Integer, nullable = False)
    status = Column(String(100), default = "unpaid")
    total_price = Column(Float, nullable = False)

    @staticmethod
    def getUserTodayInvoices(user_id, db):
        now_date = datetime.now().strftime("%Y/%m/%d")
        invoices = db.query(Invoice).filter(
                Invoice.user_id == user_id,
                Invoice.date_created == now_date
        ).all()
        return invoices

    @staticmethod
    def getTodayInvoices(db):
        now_date = datetime.now().strftime("%Y/%m/%d")
        invoices = db.query(Invoice).filter(
                Invoice.date_created == now_date
        ).all()
        return invoices

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getAllInvoices(db):
        invoices = db.query(Invoice).all()
        return invoices

    @staticmethod
    def getInvoiceById(invoice_id, db):
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        return invoice

    @staticmethod
    def getInvoiceByIdAndUser(invoice_id, user_id, db):
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == user_id).first()
        return invoice

    @staticmethod
    def getInvoiceByRefAndUser(invoice_ref, user_id, db):
        invoice = db.query(Invoice).filter(Invoice.ref == invoice_ref, Invoice.user_id == user_id).order_by(Invoice.date_created.desc()).first()
        return invoice

    @staticmethod
    def getInvoicesByDate(from_date, to_date, db):
        invoices = db.query(Invoice).filter(
            Invoice.date_created >= from_date,
            Invoice.date_created <= to_date
        ).all()
        return invoices

    @staticmethod
    def getInstanceInvoicesByDate(instance_id, from_date, to_date, db):
        invoices = db.query(Invoice).filter(
            Invoice.instance_id == instance_id,
            Invoice.date_created  >= from_date,
            Invoice.date_created  <= to_date
        ).all()
        return invoices

    @staticmethod
    def getInstanceAllInvoices(instance_id, db):
        invoices = db.query(Invoice).filter(Invoice.instance_id == instance_id).all()
        return invoices

    @staticmethod
    def getUserInvoicesByDate(user_id, from_date, to_date, db):
        invoices = db.query(Invoice).filter(
            Invoice.user_id == user_id,
            Invoice.date_created >= from_date,
            Invoice.date_created <= to_date
        ).all()
        return invoices

    @staticmethod
    def getUserAllInvoices(user_id, db):
        invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
        return invoices

    @staticmethod
    def deleteInvoiceById(id, db):
        db.query(Invoice).filter(Invoice.id == id).delete()
        db.commit()

    @staticmethod
    def makeInvoiceAsPaid(invoice_id, db):
        db.query(Invoice).filter(Invoice.id == invoice_id).update({"status": "paid"})
        db.commit()

    @staticmethod
    def updateInvoiceStatus(invoice_id, status, db):
        db.query(Invoice).filter(Invoice.id == invoice_id).update({"status": status})
        db.commit()

    @staticmethod
    def updateInvoiceDetails(invoice_id, details, db):
        db.query(Invoice).filter(Invoice.id == invoice_id).update({ "details": details })
        db.commit()

    @staticmethod
    def updateInvoiceTotalPrice(invoice_id, total_price, db):
        db.query(Invoice).filter(Invoice.id == invoice_id).update({ "total_price": total_price })
        db.commit()

    @staticmethod
    def updateInvoiceRef(ref, new_ref, db):
        db.query(Invoice).filter(Invoice.ref == ref).update({ "ref": new_ref })
        db.commit()
        
    @staticmethod
    def getMaxInvoiceRef(current_year ,db):
        max_ref = db.query(Invoice).filter(Invoice.ref.like(f'{current_year}%')).order_by(func.cast(Invoice.ref, BigInteger).desc()).first()
        return max_ref.ref if max_ref else None
