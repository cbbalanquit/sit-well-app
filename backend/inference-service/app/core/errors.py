import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)

class ModelError(Exception):
    """Exception raised for errors in the ML model inference."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)

class ImageProcessingError(Exception):
    """Exception raised for errors in image processing."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)

class NoPersonDetectedError(Exception):
    """Exception raised when no person is detected in the image."""
    
    def __init__(self, detail: str = "No person detected in the image"):
        self.detail = detail
        self.status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(self.detail)

def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the application."""
    
    @app.exception_handler(ModelError)
    async def model_error_handler(request: Request, exc: ModelError):
        """Handle model errors."""
        logger.error(f"Model Error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(ImageProcessingError)
    async def image_processing_error_handler(request: Request, exc: ImageProcessingError):
        """Handle image processing errors."""
        logger.error(f"Image Processing Error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(NoPersonDetectedError)
    async def no_person_detected_error_handler(request: Request, exc: NoPersonDetectedError):
        """Handle no person detected errors."""
        logger.warning(f"No Person Detected: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            })
        
        logger.error(f"Validation error: {errors}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error", "errors": errors}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )