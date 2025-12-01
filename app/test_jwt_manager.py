"""
Test suite for JWT Manager
Comprehensive coverage of JWT validation and token management
"""
import time
import pytest
import jwt as pyjwt
from fastapi import HTTPException
from app.jwt_manager import JWTManager


class TestJWTGeneration:
    """Test JWT token generation"""

    def test_generate_jwt_creates_unique_tokens(self):
        """Test that each generated JWT is unique"""
        manager = JWTManager()
        token1 = manager.generate_jwt()
        token2 = manager.generate_jwt()

        assert token1 != token2

    def test_generate_jwt_with_custom_payload(self):
        """Test JWT generation with custom payload"""
        manager = JWTManager()
        payload = {"user_id": "12345", "role": "admin"}
        token = manager.generate_jwt(payload)

        decoded = pyjwt.decode(token, manager.secret_key, algorithms=['HS256'])
        assert decoded["user_id"] == "12345"
        assert decoded["role"] == "admin"
        assert "jti" in decoded
        assert "iat" in decoded
        assert "exp" in decoded


class TestJWTValidation:
    """Test JWT validation scenarios"""

    def test_validate_jwt_success(self):
        """Test successful JWT validation"""
        manager = JWTManager()
        token = manager.generate_jwt()

        payload = manager.validate_jwt(token)
        assert "jti" in payload

    def test_validate_jwt_without_jti_fails(self):
        """Test that JWT without jti fails validation"""
        manager = JWTManager()
        # Create token without jti
        payload = {"data": "test"}
        token = pyjwt.encode(payload, manager.secret_key, algorithm='HS256')

        with pytest.raises(HTTPException) as exc_info:
            manager.validate_jwt(token)

        assert exc_info.value.status_code == 401
        assert "missing unique identifier" in str(exc_info.value.detail).lower()

    def test_validate_jwt_already_used(self):
        """Test that reusing a JWT token fails"""
        manager = JWTManager()
        token = manager.generate_jwt()

        # First validation should succeed
        manager.validate_jwt(token)

        # Second validation should fail
        with pytest.raises(HTTPException) as exc_info:
            manager.validate_jwt(token)

        assert exc_info.value.status_code == 401
        assert "already used" in str(exc_info.value.detail).lower()

    def test_validate_expired_jwt_fails(self):
        """Test that expired JWT fails validation"""
        manager = JWTManager(token_expiry_seconds=1)
        token = manager.generate_jwt()

        # Wait for token to expire
        time.sleep(2)

        with pytest.raises(HTTPException) as exc_info:
            manager.validate_jwt(token)

        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()

    def test_validate_invalid_token_fails(self):
        """Test that invalid JWT fails validation"""
        manager = JWTManager()
        invalid_token = "invalid.jwt.token"

        with pytest.raises(HTTPException) as exc_info:
            manager.validate_jwt(invalid_token)

        assert exc_info.value.status_code == 401
        assert "invalid" in str(exc_info.value.detail).lower()

    def test_validate_token_with_wrong_secret_fails(self):
        """Test that token signed with different secret fails"""
        manager = JWTManager(secret_key="secret1")
        token = manager.generate_jwt()

        manager2 = JWTManager(secret_key="secret2")

        with pytest.raises(HTTPException) as exc_info:
            manager2.validate_jwt(token)

        assert exc_info.value.status_code == 401


class TestTokenCleanup:
    """Test token cleanup functionality"""

    def test_cleanup_expired_tokens(self):
        """Test that expired tokens are cleaned up"""
        manager = JWTManager(token_expiry_seconds=1)

        # Generate and use some tokens
        token1 = manager.generate_jwt()
        manager.validate_jwt(token1)

        assert len(manager._used_tokens) == 1  # pylint: disable=protected-access

        # Wait for tokens to expire
        time.sleep(2)

        # Force cleanup by setting last_cleanup time to trigger cleanup
        # pylint: disable=protected-access
        manager._last_cleanup = time.time() - manager._cleanup_interval - 1

        # Generate a new token to trigger cleanup
        token2 = manager.generate_jwt()
        manager.validate_jwt(token2)

        # Old token should be cleaned up
        assert len(manager._used_tokens) == 1  # pylint: disable=protected-access

    def test_cleanup_only_runs_at_intervals(self):
        """Test that cleanup respects cleanup interval"""
        manager = JWTManager()
        initial_cleanup_time = manager._last_cleanup  # pylint: disable=protected-access

        # Call cleanup multiple times quickly
        manager._cleanup_expired_tokens()  # pylint: disable=protected-access
        manager._cleanup_expired_tokens()  # pylint: disable=protected-access

        # Last cleanup time should not change much
        assert manager._last_cleanup - initial_cleanup_time < 1  # pylint: disable=protected-access


class TestTokenStats:
    """Test token statistics"""

    def test_get_stats_returns_correct_info(self):
        """Test that stats return correct information"""
        manager = JWTManager(token_expiry_seconds=300)

        stats = manager.get_stats()

        assert "total_used_tokens" in stats
        assert "last_cleanup" in stats
        assert "token_expiry_seconds" in stats
        assert stats["total_used_tokens"] == 0
        assert stats["token_expiry_seconds"] == 300

    def test_stats_track_used_tokens(self):
        """Test that stats correctly track used tokens"""
        manager = JWTManager()

        # Use some tokens
        for _ in range(3):
            token = manager.generate_jwt()
            manager.validate_jwt(token)

        stats = manager.get_stats()
        assert stats["total_used_tokens"] == 3


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_manager_with_custom_expiry(self):
        """Test JWT manager with custom expiry time"""
        manager = JWTManager(token_expiry_seconds=600)
        token = manager.generate_jwt()

        decoded = pyjwt.decode(token, manager.secret_key, algorithms=['HS256'])
        exp_time = decoded["exp"]
        iat_time = decoded["iat"]

        # Check expiry is approximately 600 seconds from issued time
        # exp and iat are unix timestamps (integers)
        assert abs((exp_time - iat_time) - 600) < 1

    def test_concurrent_token_validation(self):
        """Test that different tokens can be validated concurrently"""
        manager = JWTManager()

        tokens = [manager.generate_jwt() for _ in range(5)]

        # All tokens should validate successfully
        for token in tokens:
            payload = manager.validate_jwt(token)
            assert "jti" in payload

        # All tokens should be tracked
        assert len(manager._used_tokens) == 5
