import logging
import traceback

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("infratrack")


def _error(error: str, detail: str = "", status: int = 500) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"success": False, "error": error, "detail": detail},
    )


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(
            f"HTTP {exc.status_code} on {request.method} {request.url.path} — {exc.detail}"
        )
        return _error(exc.detail, status=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        messages = "; ".join(
            f"{' → '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in errors
        )
        logger.warning(f"Validation error on {request.url.path}: {messages}")
        return _error(
            "Validation failed",
            detail=messages,
            status=422,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tb = traceback.format_exc()
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path}:\n{tb}"
        )
        return _error(
            "Internal server error",
            detail="An unexpected error occurred. Check server logs.",
            status=500,
        )
