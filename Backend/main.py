import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from database import create_tables

from routes import router
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield



app = FastAPI(
    title="YouTube Thumbnail Generator API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Fix: Added the 's' to allow_origins and quotes around *
    allow_credentials=False,   # Note: Must be False if origins is ["*"]
    allow_methods=["*"],      # Fix: Added quotes around *
    allow_headers=["*"],      # Fix: Added quotes around *
)


app.include_router(router)