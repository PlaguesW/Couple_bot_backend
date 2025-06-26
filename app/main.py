from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, pairs, ideas, events, admin

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(pairs.router)
app.include_router(ideas.router)
app.include_router(events.router)
app.include_router(admin.router)