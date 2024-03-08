from database.postgres_db import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Text
from datetime import datetime

class Bucket(Base):
    __tablename__ = "bucket"
    id = Column(Integer, primary_key = True)
    hash = Column(String(10))
    name = Column(String(200))
    type = Column(String(50))
    created_at = Column(String(100), default = datetime.now().isoformat())
    access_key = Column(String(150))
    secret_key = Column(Text)
    bucket_user_id = Column(String(150))
    endpoint = Column(String(300))
    status = Column(String(50), default = "starting")
    user_id = Column(Integer, ForeignKey("user.id"))
    region = Column(String(100))
    provider = Column(String(100))

    def save(self, db):
        db.add(self)
        db.commit()

    @staticmethod
    def findById(id, db):
        bucket = db.query(Bucket).filter(Bucket.id == id, Bucket.status!= "deleted").first()
        return bucket


    @staticmethod
    def findBucketsByRegion(bucketIds, provider, region, db):
        buckets = db.query(Bucket).filter(Bucket.id.in_(bucketIds), Bucket.provider == provider, Bucket.region == region, Bucket.status!= "deleted").all()
        return buckets

    @staticmethod
    def updateStatus(bucket_id, status, db):
        db.query(Bucket).filter(Bucket.id == bucket_id).update({"status": status})
        db.commit()

    @staticmethod
    def updateCredentials(bucket_id, access_key, secret_key, db):
        db.query(Bucket).filter(Bucket.id == bucket_id).update({"access_key": access_key, "secret_key": secret_key})
        db.commit()

    @staticmethod
    def getBucketAccessKey(provider, region, bucket_id, db):
        access_key = db.query(Bucket.access_key).filter(Bucket.provider == provider, Bucket.region == region, Bucket.id == bucket_id).first()
        return str(access_key)

    @staticmethod
    def update(id, endpoint, bucket_user_id, access_key, secret_key, status, db):
        db.query(Bucket).filter(Bucket.id == id).update({"endpoint": endpoint, "bucket_user_id": bucket_user_id, "access_key": access_key, "secret_key": secret_key, "status": status})
        db.commit()

    @staticmethod
    def getAllUserBucketsByRegion(provider, region, user_id, db):
        buckets = db.query(Bucket).filter(Bucket.provider == provider, Bucket.region == region, Bucket.user_id == user_id, Bucket.status!= "deleted").all()
        return buckets

    @staticmethod
    def getAllUserBuckets(user_id, db):
        buckets = db.query(Bucket).filter(Bucket.user_id == user_id, Bucket.status!= "deleted").all()
        return buckets

    @staticmethod
    def getAllBucketsByRegion(provider, region, db):
        buckets = db.query(Bucket).filter(Bucket.provider == provider, Bucket.region == region, Bucket.status!= "deleted").all()
        return buckets

    @staticmethod
    def findUserBucket(provider, userId, bucketId, region, db):
        bucket = db.query(Bucket).filter(Bucket.id == bucketId, Bucket.provider == provider, Bucket.region == region, Bucket.user_id == userId, Bucket.status != "deleted").first()
        return bucket

    @staticmethod
    def findBucket(provider, region, bucketId, db):
        bucket = db.query(Bucket).filter(Bucket.id == bucketId, Bucket.provider == provider, Bucket.region == region, Bucket.status != "deleted").first()
        return bucket

    @staticmethod
    def patch(bucket_id, changes, db):
        db.query(Bucket).filter(Bucket.id == bucket_id).update(changes)
        db.commit()

    @staticmethod
    def updateInfo(bucket_id, provider, region, bucket_type, status, db):
        db.query(Bucket).filter(Bucket.id == bucket_id).update({"provider": provider, "region": region, "type": bucket_type, "status": status})
        db.commit()

    @staticmethod
    def updateType(bucket_id, type, db):
        db.query(Bucket).filter(Bucket.id == bucket_id).update({"type": type})
        db.commit()
