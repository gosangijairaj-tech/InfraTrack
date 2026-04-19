import sys
import os
import logging
import logging.config

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.user_routes   import router as user_router
from backend.routes.report_routes import router as report_router
from backend.routes.admin_routes  import router as admin_router
from backend.error_handlers import register_exception_handlers

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "standard",
            "stream":    "ext://sys.stdout",
        },
        "file": {
            "class":       "logging.FileHandler",
            "formatter":   "standard",
            "filename":    "infratrack.log",
            "encoding":    "utf-8",
        },
    },
    "root": {
        "level":    "INFO",
        "handlers": ["console", "file"],
    },
    "loggers": {
        "uvicorn.error":  {"propagate": True},
        "uvicorn.access": {"propagate": True},
    },
}
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("infratrack")

app = FastAPI(
    title="InfraTrack API",
    description="Geotagged Infrastructure Monitoring System — production-ready backend",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(user_router)
app.include_router(report_router)
app.include_router(admin_router)


@app.get("/", tags=["Health"])
def root():
    return {"success": True, "message": "InfraTrack API v2.0 is running"}


@app.get("/health", tags=["Health"])
def health():
    try:
        from database.db import client
        client.admin.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"success": True, "status": "ok", "database": db_status}


@app.on_event("startup")
async def startup():
    logger.info("InfraTrack API started. Environment loaded.")


@app.on_event("shutdown")
async def shutdown():
    logger.info("InfraTrack API shutting down.")