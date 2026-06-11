"""FastAPI main application."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


from .db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Candidate Screening AI Backend...")

    # Create database tables
    init_db()

    print("Database initialized successfully")

    yield

    print("Shutting down Candidate Screening AI Backend...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title="Candidate Screening AI",
        description="AI-powered role-based candidate screening system",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    if cors_origins_env:
        origins = cors_origins_env.split(",")
    else:
        # Default allowed origins for local dev and production
        origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "https://candidate-screening-ai.vercel.app",
            "https://candidate-screening-kv460qcf4-yk47s-projects.vercel.app",
        ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Lazy-import the router — interview_service has lazy heavy deps already
    from .api.interview import router as interview_router
    app.include_router(interview_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "Candidate Screening AI Backend",
            "version": "1.0.0"
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )