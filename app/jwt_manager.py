"""
JWT Manager for unique token validation per transaction
Implements in-memory cache with TTL for token tracking
"""
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
import secrets
import jwt
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class JWTManager:
    """
    Manages JWT validation and ensures uniqueness per transaction
    Uses in-memory cache with automatic cleanup
    """

    def __init__(self, secret_key: str = None, token_expiry_seconds: int = 300):
        """
        Initialize JWT Manager
        
        Args:
            secret_key: Secret key for JWT encoding/decoding
            token_expiry_seconds: Default token expiry time (5 minutes)
        """
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_expiry_seconds = token_expiry_seconds
        self._used_tokens: Dict[str, float] = {}
        self._cleanup_interval = 60  # Cleanup every minute
        self._last_cleanup = time.time()

    def generate_jwt(self, payload: Optional[Dict] = None) -> str:
        """
        Generate a unique JWT token
        
        Args:
            payload: Optional payload to include in JWT
            
        Returns:
            Encoded JWT token
        """
        if payload is None:
            payload = {}

        # Add unique identifier and timestamp
        payload.update({
            'jti': secrets.token_urlsafe(16),  # JWT ID (unique)
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry_seconds)
        })

        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        logger.info("Generated JWT with JTI: %s", payload['jti'])
        return token

    def validate_jwt(self, token: str) -> Dict:
        """
        Validate JWT and ensure it hasn't been used before
        
        Args:
            token: JWT token to validate
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid, expired, or already used
        """
        try:
            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])

            jti = payload.get('jti')
            if not jti:
                logger.warning("JWT missing unique identifier (jti)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid JWT: missing unique identifier"
                )

            # Check if token has already been used
            if jti in self._used_tokens:
                logger.warning("JWT already used: %s", jti)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT token already used"
                )

            # Mark token as used
            self._used_tokens[jti] = time.time()
            logger.info("JWT validated and marked as used: %s", jti)

            # Perform cleanup if needed
            self._cleanup_expired_tokens()

            return payload

        except jwt.ExpiredSignatureError as exc:
            logger.warning("JWT token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT token expired"
            ) from exc
        except jwt.InvalidTokenError as exc:
            logger.warning("Invalid JWT token: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT token"
            ) from exc

    def _cleanup_expired_tokens(self) -> None:
        """Remove expired tokens from cache"""
        current_time = time.time()

        # Only cleanup at intervals
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        expiry_threshold = current_time - self.token_expiry_seconds
        expired_tokens = [
            jti for jti, timestamp in self._used_tokens.items()
            if timestamp < expiry_threshold
        ]

        for jti in expired_tokens:
            del self._used_tokens[jti]

        if expired_tokens:
            logger.info("Cleaned up %d expired tokens", len(expired_tokens))

        self._last_cleanup = current_time

    def get_stats(self) -> Dict:
        """Get statistics about token usage"""
        return {
            'total_used_tokens': len(self._used_tokens),
            'last_cleanup': self._last_cleanup,
            'token_expiry_seconds': self.token_expiry_seconds
        }


# Global instance
jwt_manager = JWTManager()
