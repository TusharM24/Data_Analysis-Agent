"""Main FastAPI application for the EDA Agent."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import upload_router, chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    print("🚀 Starting EDA Agent API...")
    
    # Create necessary directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.plots_dir, exist_ok=True)
    
    # Validate Groq API key
    if not settings.groq_api_key:
        print("⚠️  WARNING: GROQ_API_KEY not set. The agent will not work without it.")
    else:
        print("✅ Groq API key configured")
    
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📊 Plots directory: {settings.plots_dir}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down EDA Agent API...")


# Create FastAPI application
app = FastAPI(
    title="EDA Agent API",
    description="""
    An intelligent Exploratory Data Analysis agent that generates and executes 
    Python code to analyze your datasets.
    
    ## Features
    - Upload CSV/Excel files
    - Natural language queries about your data
    - Automatic code generation for analysis
    - Visualization generation
    - Secure code execution sandbox
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "EDA Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/upload",
            "chat": "POST /api/chat",
            "sessions": "GET /api/sessions",
            "plots": "GET /api/plots/{filename}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "groq_configured": bool(settings.groq_api_key)
    }


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

