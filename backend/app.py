import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.user_routes import router as user_router
from backend.routes.report_routes import router as report_router
from backend.routes.admin_routes import router as admin_router

app = FastAPI(
    title="InfraTrack API",
    description="Geotagged Infrastructure Monitoring System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(report_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "InfraTrack API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}