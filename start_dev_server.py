#!/usr/bin/env python
"""Start DocuAssist AI development server"""

import subprocess
import sys
import os

os.chdir(r'd:\AI Capstone\Task')
print("\n" + "="*50)
print("  DocuAssist AI - Development Server")
print("="*50)
print("\nStarting FastAPI server...")
print("Server will be available at: http://localhost:8000")
print("API Documentation: http://localhost:8000/api/docs")
print("ReDoc: http://localhost:8000/api/redoc")
print("\nPress Ctrl+C to stop the server\n")

subprocess.run([
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--reload",
    "--host", "0.0.0.0",
    "--port", "8000"
])
