# run.py
import os#entry point
import sys
import uvicorn  # Add this import

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    
    uvicorn.run(#Auto-reload for development, configurable port and debug mode
        "run:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        reload_dirs=["src"]
    )