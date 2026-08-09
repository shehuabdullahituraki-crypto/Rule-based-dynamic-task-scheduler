"""
FastAPI application entry point.
Run with: uvicorn app.main:app --reload
Then open: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import tasks, auth, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rule-Based Dynamic Task Scheduling Engine",
    description="Rank, score, find-replaceable, and reallocate tasks dynamically.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(admin.router, tags=["admin"])


@app.get("/")
def root():
    return {"status": "ok", "message": "Scheduling engine API is running. Visit /docs for API docs."}