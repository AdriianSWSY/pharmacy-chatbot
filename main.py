from dotenv import load_dotenv

# Load environment variables from .env file (must be before other imports)
load_dotenv()

# Now import everything else
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from src.routes.api import api_router  # noqa: E402
from config.settings import settings  # noqa: E402

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    description="AI Agent Call Assistant - A FastAPI-based API service for managing pharmacy data with phone number search capabilities",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your security requirements
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        loop="uvloop",
        log_level=settings.server.log_level,
    )
