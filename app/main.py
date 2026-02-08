"""FastAPI application setup for DocuAssist AI."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from app.config import settings
from app.api import chat_router, documents_router, feedback_router
from app.utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description="A RAG-based customer support chatbot powered by semantic search and LLMs",
    version=settings.api_version,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Event Handlers ==============

@app.on_event("startup")
async def startup_event():
    """Initialize components on app startup."""
    try:
        logger.info(f"Starting {settings.api_title} v{settings.api_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info("All components initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    try:
        logger.info("Shutting down DocuAssist AI gracefully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


# ============== Routes ==============

@app.get("/", tags=["root"])
async def root():
    """Serve the chat interface HTML."""
    try:
        frontend_dir = Path(__file__).parent.parent / "frontend"
        index_file = frontend_dir / "index.html"
        
        if not index_file.exists():
            logger.error(f"Frontend index.html not found at {index_file}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Frontend interface not found"}
            )
        
        return FileResponse(index_file)
    except Exception as e:
        logger.error(f"Error serving frontend: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Error loading interface"}
        )


@app.get("/api/health", tags=["health"])
async def health_check():
    """System health check endpoint."""
    try:
        return {
            "status": "healthy",
            "service": settings.api_title,
            "version": settings.api_version
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "detail": "Service unavailable"}
        )


@app.get("/styles.css", tags=["static"])
async def get_styles():
    """Serve CSS stylesheet."""
    try:
        frontend_dir = Path(__file__).parent.parent / "frontend"
        css_file = frontend_dir / "styles.css"
        
        if not css_file.exists():
            return JSONResponse(status_code=404, content={"detail": "Stylesheet not found"})
        
        return FileResponse(css_file, media_type="text/css")
    except Exception as e:
        logger.error(f"Error serving CSS: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Error loading stylesheet"})


@app.get("/script.js", tags=["static"])
async def get_script():
    """Serve JavaScript file."""
    try:
        frontend_dir = Path(__file__).parent.parent / "frontend"
        js_file = frontend_dir / "script.js"
        
        if not js_file.exists():
            return JSONResponse(status_code=404, content={"detail": "Script not found"})
        
        return FileResponse(js_file, media_type="application/javascript")
    except Exception as e:
        logger.error(f"Error serving JavaScript: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Error loading script"})


# Include routers
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(feedback_router)


# ============== Error Handlers ==============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request data",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
