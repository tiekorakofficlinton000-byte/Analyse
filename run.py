#!/usr/bin/env python3
import sys
import os

# Add local libraries and backend to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(base_dir, "lib")
backend_dir = os.path.join(base_dir, "backend")

if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn

if __name__ == "__main__":
    print(f"🚀 QuantBet Platform starting on 0.0.0.0:8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
