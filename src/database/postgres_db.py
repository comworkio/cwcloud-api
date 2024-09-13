import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

postgres_db_name = os.getenv("POSTGRES_DB")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_pool_size = int(os.getenv("POSTGRES_SIZE_POOL", 30))

POSTGRES_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db_name}"

dbEngine = create_engine(POSTGRES_URL, echo = True, pool_size = postgres_pool_size)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = dbEngine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
