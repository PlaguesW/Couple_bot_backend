from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import db
from app.routers import auth, users, couples, ideas, dates


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.init_db()
    yield
    # Shutdown
    await db.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(couples.router, prefix=settings.API_V1_STR)
app.include_router(ideas.router, prefix=settings.API_V1_STR)
app.include_router(dates.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Couple Bot API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}