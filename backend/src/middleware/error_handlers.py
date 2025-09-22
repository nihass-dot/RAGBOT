# src/middleware/error_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={
            "message": "An unexpected error occurred.",
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )

def setup_error_handlers(app: FastAPI):
    """
    Set up error handlers for the FastAPI application.
    """
    app.add_exception_handler(Exception, global_exception_handler)