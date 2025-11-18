#!/usr/bin/env python3

import os
import http.server
import socketserver
import webbrowser
from pathlib import Path

def run_frontend_server():
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    PORT = 3000
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(frontend_dir), **kwargs)
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Frontend server running at http://localhost:{PORT}")
            print("Press Ctrl+C to stop the server")
            
            # Automatically open the browser
            webbrowser.open(f'http://localhost:{PORT}')
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the frontend server...")

if __name__ == "__main__":
    run_frontend_server()