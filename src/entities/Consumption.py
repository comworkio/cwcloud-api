from database.postgres_db import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Float, Date
from datetime import datetime

class Consumption(Base):
    __tablename__ = "consumption"
    id = Column(Integer, primary_key = True)
    instance_id = Column(Integer, ForeignKey('instance.id'))
    usage = Column(Float, nullable = False)
    instance_price = Column(Float, nullable = False)
    total_price = Column(Float, nullable = False)
    date_created = Column(Date, nullable = False, default = datetime.now().isoformat())
    from_date = Column(String(100))
    to_date = Column(String(100))
    user_id = Column(String, nullable = False)

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def getAllConsumptions(db):
        consumptions = db.query(Consumption).all()
        return consumptions

    def getUserAllConsumptions(user_id, db):
        consumptions = db.query(Consumption).filter(Consumption.user_id == user_id).all()
        return consumptions

    @staticmethod
    def getConsumptionById(id, db):
        consumption = db.query(Consumption).filter(Consumption.id == id).first()
        return consumption

    @staticmethod
    def getInstanceConsumptions(instance_id, db):
        consumptions = db.query(Consumption).filter(Consumption.instance_id == instance_id).all()
        return consumptions

    @staticmethod
    def updateConsumptionInstanceOwner(instances_ids, owner_id, db):
        db.query(Consumption).filter(Consumption.instance_id.in_(instances_ids)).update({"user_id": owner_id})
        db.commit()

    @staticmethod
    def getConsumptionsByDate(from_date, to_date, db):
        consumptions = db.query(Consumption).filter(
                        Consumption.date_created >= from_date,
                        Consumption.date_created <= to_date
                ).all()
        return consumptions

    @staticmethod
    def deleteConsumptionById(id, db):
        db.query(Consumption).filter(Consumption.id == id).delete()
        db.commit()
