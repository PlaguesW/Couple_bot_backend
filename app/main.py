from fastapi import FastAPI
from app.database import engine, Base, create_tables
from app.models import User, PartnerPair, Idea, DateEvent
from app.routers import users, pairs, ideas, events, admin
from alembic.config import Config
from alembic import command

print("Engine URL:", engine.url)

try:
    Base.metadata.create_all(bind=engine)
    print("Tables created")
except Exception as e:
    print("Error creating tables:", str(e))

app = FastAPI()

app.include_router(users.router)
app.include_router(pairs.router)
app.include_router(ideas.router)
app.include_router(events.router)

@app.on_event("startup")
async def startup_event():
    """Creatre database tables on startup."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        
@app.get("/")
async def root():
    return {"message": "Welcome to the Partner Pairing API!"}