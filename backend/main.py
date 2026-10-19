"""
Entry point proxying to production modular backend: backend.app.main:app
FastAPI is the sole production backend.
"""
from backend.app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8002, reload=True)
