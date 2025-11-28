"""
Banking DevOps Microservice API
Clean Code Architecture with TDD approach
Implements secure REST endpoint with header validation
"""
import logging
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import PlainTextResponse

from app.models import DevOpsRequest, DevOpsResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants following Clean Code principles
VALID_API_KEY = "2f5ae96c-b558-4c7b-a590-a501ae1c3f6c"
API_KEY_HEADER = "X-Parse-REST-API-Key"
JWT_HEADER = "X-JWT-KWY"

app = FastAPI(
    title="Banking DevOps API",
    description="Secure microservice for banking operations",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {"status": "healthy"}


def validate_security_headers(api_key: Optional[str], jwt_token: Optional[str]) -> None:
    """
    Validate required security headers
    
    Args:
        api_key: API Key from header
        jwt_token: JWT token from header
        
    Raises:
        HTTPException: If validation fails
    """
    if not api_key or api_key != VALID_API_KEY:
        logger.warning("Invalid or missing API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    if not jwt_token:
        logger.warning("Missing JWT token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing JWT token"
        )


def build_success_message(recipient_name: str) -> str:
    """
    Build success response message
    
    Args:
        recipient_name: Name of the message recipient
        
    Returns:
        Formatted success message
    """
    return f"Hello {recipient_name} your message will be send"


@app.post("/DevOps", response_model=DevOpsResponse, status_code=status.HTTP_200_OK)
async def devops_endpoint(
    request: DevOpsRequest,
    x_parse_rest_api_key: Optional[str] = Header(None, alias=API_KEY_HEADER),
    x_jwt_kwy: Optional[str] = Header(None, alias=JWT_HEADER)
) -> DevOpsResponse:
    """
    Main DevOps endpoint for processing banking messages
    
    Security:
        - Requires valid X-Parse-REST-API-Key header
        - Requires X-JWT-KWY header
    
    Args:
        request: DevOps request payload
        x_parse_rest_api_key: API Key header
        x_jwt_kwy: JWT token header
        
    Returns:
        DevOpsResponse with success message
        
    Raises:
        HTTPException: If security validation fails
    """
    # Validate security headers
    validate_security_headers(x_parse_rest_api_key, x_jwt_kwy)

    # Process request
    logger.info("Processing message for %s from %s", request.to, request.from_)

    # Build and return response
    response_message = build_success_message(request.to)
    return DevOpsResponse(message=response_message)


@app.api_route("/{path_name:path}", methods=["GET", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def catch_all(request: Request, path_name: str) -> PlainTextResponse:
    """
    Catch-all route for unsupported methods and paths
    Returns plain text "ERROR" for any non-POST /DevOps request
    
    Args:
        request: FastAPI request object
        path_name: Any path requested
        
    Returns:
        PlainTextResponse with "ERROR"
    """
    logger.warning("Unsupported request: %s %s", request.method, path_name)
    return PlainTextResponse(content="ERROR", status_code=status.HTTP_400_BAD_REQUEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
