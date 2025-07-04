from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG 
)

# Create sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for db sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()