from fastapi import FastAPI
from src.routes.api import api_router

app = FastAPI(title="AI Agent Call Assistant API")

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        loop="uvloop",
        log_level="info"
    )