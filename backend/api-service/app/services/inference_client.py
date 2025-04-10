import httpx
import logging
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

class InferenceClient:
    """Client for communicating with the inference service."""
    
    def __init__(self):
        self.base_url = settings.INFERENCE_SERVICE_URL
        self.timeout = settings.INFERENCE_TIMEOUT
    
    async def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """
        Send image data to inference service for analysis.
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            Analysis results from inference service
            
        Raises:
            HTTPException: If inference service returns an error
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/inference/analyze",
                    json={"image": image_data}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while calling inference service: {e}")
            error_detail = await self._extract_error_detail(e.response)
            raise InferenceServiceError(
                status_code=e.response.status_code, 
                detail=error_detail or str(e)
            )
        except httpx.RequestError as e:
            logger.error(f"Error occurred while requesting inference service: {e}")
            raise InferenceServiceError(
                status_code=503,
                detail=f"Inference service unavailable: {str(e)}"
            )
    
    @staticmethod
    async def _extract_error_detail(response) -> Optional[str]:
        """Extract error detail from response if available."""
        try:
            error_data = await response.json()
            if isinstance(error_data, dict) and "detail" in error_data:
                return error_data["detail"]
            return None
        except Exception:
            return None


class InferenceServiceError(Exception):
    """Exception raised for errors in the inference service."""
    
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)