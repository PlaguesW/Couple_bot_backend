from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,                    # Количество соединений в пуле
    max_overflow=20,                 # Дополнительные соединения при нагрузке
    pool_pre_ping=True,             # Проверка соединения перед использованием
    pool_recycle=3600,              # Пересоздание соединений каждый час
    connect_args={
        "options": "-c timezone=utc",  # Устанавливаем UTC timezone
        "connect_timeout": 10,          # Таймаут подключения
        "application_name": "couple_bot_backend"  # Имя приложения в логах PostgreSQL
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency для получения сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Проверка подключения к базе данных."""
    try:
        with engine.connect() as connection:
            # Проверяем версию PostgreSQL
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL connection successful! Version: {version}")
            return True
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return False

def check_database_exists():
    """Проверяем, существует ли база данных."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"Connected to database: {db_name}")
            return True
    except Exception as e:
        print(f"Database check failed: {e}")
        return False