import sys
import os# Sets up middleware, routes, and error handling

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.controllers.rag_controller import router as rag_controller
from src.middleware.error_handlers import setup_error_handlers

def create_app() -> FastAPI:
    app = FastAPI(
        title="India RAG System",
        description="A Retrieval-Augmented Generation system for information about India",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers directly
    app.include_router(rag_controller, prefix="/api/rag", tags=["rag"])
    
    # Set up error handlers
    setup_error_handlers(app)
    
    return app