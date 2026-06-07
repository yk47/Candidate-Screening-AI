"""FastAPI main application."""

import os
import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .api.interview import router as interview_router
from .db.database import init_db
from .db.migrate import migrate
from .rag.ingest import KnowledgeBaseIngester

# Load environment variables at startup
load_dotenv()

# Initialize LangSmith tracing if configured
def _configure_langsmith():
    """Configure LangSmith tracing if API key is available."""
    if os.getenv("LANGCHAIN_TRACING_V2") == "true" and os.getenv("LANGCHAIN_API_KEY"):
        print("LangSmith tracing enabled")
        print(f"Project: {os.getenv('LANGSMITH_PROJECT', 'default')}")
    else:
        print("LangSmith tracing disabled")

_configure_langsmith()


async def ingest_knowledge_base_async() -> None:
    """Ingest knowledge base asynchronously in background."""
    try:
        knowledge_path = os.getenv("KNOWLEDGE_BASE_PATH", "./data/knowledge_base")
        base_path = Path(knowledge_path)
        if not base_path.exists():
            print(f"Knowledge base directory not found at {knowledge_path}. Skipping ingestion.")
            return

        print("Starting knowledge base ingestion in background...")
        ingester = KnowledgeBaseIngester()
        result = ingester.ingest_all_roles(str(base_path))
        print("Knowledge base ingestion completed:", result.get("status"))
    except Exception as e:
        print(f"Error during knowledge base ingestion: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup/shutdown."""
    from .services.langsmith_config import LangSmithConfig
    
    print("Starting Candidate Screening AI Backend...")
    
    # Log LangSmith configuration
    LangSmithConfig.log_config()
    
    init_db()
    print("Database initialized")
    
    # Run migrations
    try:
        migrate()
        print("Database migrations completed")
    except Exception as e:
        print(f"Warning: Migration check failed (may be normal): {e}")
    
    # Only ingest if knowledge base directory exists
    knowledge_path = os.getenv("KNOWLEDGE_BASE_PATH", "./data/knowledge_base")
    if Path(knowledge_path).exists():
        print("Knowledge base found. Deferring ingestion to background...")
        asyncio.create_task(ingest_knowledge_base_async())
    else:
        print("No knowledge base directory found. Skipping ingestion.")
    
    print("✓ Backend ready! Server is running.")
    
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
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(interview_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "Candidate Screening AI Backend"
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
