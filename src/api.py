"""
YATRA AI — Backend API Compatibility Shim
Maintains complete backward compatibility with existing tests and scripts
by delegating to the modular production backend in `backend.app.main`.
"""

import os
import sys

# Silence joblib/loky Windows CPU count warning
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.main import app

if __name__ == "__main__":
    import uvicorn
    from backend.app.config import settings
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
