"""FastAPI main application."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan — no heavy initialization at startup."""
    print("Starting Candidate Screening AI Backend...")
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
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,https://candidate-screening-ai.vercel.app").split(",")
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