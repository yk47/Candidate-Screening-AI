"""LangSmith configuration and utilities for tracing."""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LangSmithConfig:
    """Configuration for LangSmith tracing."""
    
    # LangSmith environment variables
    TRACING_ENABLED = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    PROJECT = os.getenv("LANGSMITH_PROJECT", "candidate-screening-ai")
    CALLBACKS_BACKGROUND = os.getenv("LANGCHAIN_CALLBACKS_BACKGROUND", "true").lower() == "true"
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if LangSmith tracing is enabled."""
        return LangSmithConfig.TRACING_ENABLED and bool(LangSmithConfig.API_KEY)
    
    @staticmethod
    def get_config_dict() -> Dict[str, Any]:
        """Get LangSmith configuration as dictionary."""
        return {
            "tracing_enabled": LangSmithConfig.TRACING_ENABLED,
            "api_key_set": bool(LangSmithConfig.API_KEY),
            "endpoint": LangSmithConfig.ENDPOINT,
            "project": LangSmithConfig.PROJECT,
            "callbacks_background": LangSmithConfig.CALLBACKS_BACKGROUND,
        }
    
    @staticmethod
    def log_config():
        """Log LangSmith configuration."""
        if LangSmithConfig.is_enabled():
            print("✓ LangSmith Tracing Enabled")
            print(f"  - Project: {LangSmithConfig.PROJECT}")
            print(f"  - Endpoint: {LangSmithConfig.ENDPOINT}")
            print(f"  - Background Callbacks: {LangSmithConfig.CALLBACKS_BACKGROUND}")
        else:
            print("✗ LangSmith Tracing Disabled")


def get_langsmith_callbacks():
    """Get LangSmith callbacks if enabled.
    
    Returns:
        List of LangSmith callbacks or empty list if not enabled.
    """
    if not LangSmithConfig.is_enabled():
        return []
    
    try:
        from langchain.callbacks.tracers.langchain import LangChainTracer
        from langsmith import Client
        
        client = Client(
            api_key=LangSmithConfig.API_KEY,
            api_url=LangSmithConfig.ENDPOINT,
        )
        
        tracer = LangChainTracer(
            project_name=LangSmithConfig.PROJECT,
            client=client,
        )
        
        return [tracer]
    except ImportError:
        print("Warning: langsmith package not installed. Install with: pip install langsmith")
        return []
    except Exception as e:
        print(f"Warning: Failed to initialize LangSmith tracer: {e}")
        return []
