#!/usr/bin/env python3

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )