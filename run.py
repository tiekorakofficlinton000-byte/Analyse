#!/usr/bin/env python3
"""
DuoSecur Pro - Production Entrypoint
"""

import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(base_dir, "lib")
backend_dir = os.path.join(base_dir, "backend")

if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 DuoSecur Pro Platform starting on port {port}...")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
