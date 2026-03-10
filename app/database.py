from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Render uses the /opt/render/project/src/data path for persistent disks usually,
# or simply /app/data if you mount it there in the Dockerfile.
# This ensures your 40-dancer roster survives a server restart.
DB_PATH = "/app/data/scheduler.db"

# Create the directory if it doesn't exist (useful for local docker testing)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()