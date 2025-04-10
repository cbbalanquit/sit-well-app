from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.endpoints import inference
from app.core.config import settings
from app.core.errors import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Register exception handlers
    register_exception_handlers(application)

    # Include API routes
    application.include_router(inference.router, prefix="/api/inference", tags=["Inference"])

    @application.get("/", tags=["Health"])
    async def health_check():
        """Root endpoint for health checks."""
        return {"status": "ok", "message": "Inference service is running"}

    @application.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        logger.info("Initializing YOLO model...")
        from app.services.pose_detector import get_pose_detector
        detector = get_pose_detector()
        logger.info(f"YOLO model initialized: {detector.model_name}")

    return application

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)