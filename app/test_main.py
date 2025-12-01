"""
Test suite for Banking DevOps API
Following TDD principles with comprehensive test coverage
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app, VALID_API_KEY
from app.jwt_manager import jwt_manager

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_jwt_manager():
    """Reset JWT manager cache before each test"""
    jwt_manager._used_tokens.clear()
    yield


def get_valid_jwt():
    """Generate a valid JWT token for testing"""
    return jwt_manager.generate_jwt()


# Test data constants
def get_valid_headers():
    """Get valid headers with fresh JWT"""
    return {
        "X-Parse-REST-API-Key": VALID_API_KEY,
        "X-JWT-KWY": get_valid_jwt()
    }

VALID_PAYLOAD = {
    "message": "This is a test",
    "to": "Juan Perez",
    "from": "Rita Asturia",
    "timeToLifeSec": 45
}


class TestDevOpsEndpointHappyPath:
    """Test cases for successful scenarios"""
    
    def test_post_devops_with_valid_credentials(self):
        """Test POST /DevOps with valid headers and payload returns success"""
        response = client.post(
            "/DevOps",
            json=VALID_PAYLOAD,
            headers=get_valid_headers()
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "message": "Hello Juan Perez your message will be send"
        }
    
    def test_response_message_is_dynamic(self):
        """Test that response message uses dynamic recipient name"""
        custom_payload = VALID_PAYLOAD.copy()
        custom_payload["to"] = "Maria Garcia"
        
        response = client.post(
            "/DevOps",
            json=custom_payload,
            headers=get_valid_headers()
        )
        
        assert response.status_code == 200
        assert "Maria Garcia" in response.json()["message"]
        assert response.json()["message"] == "Hello Maria Garcia your message will be send"


class TestSecurityValidation:
    """Test cases for security and authentication"""
    
    def test_missing_api_key_returns_401(self):
        """Test that missing API Key returns 401 Unauthorized"""
        headers = {"X-JWT-KWY": "valid_jwt_token"}
        
        response = client.post(
            "/DevOps",
            json=VALID_PAYLOAD,
            headers=headers
        )
        
        assert response.status_code == 401
    
    def test_invalid_api_key_returns_401(self):
        """Test that invalid API Key returns 401 Unauthorized"""
        headers = {
            "X-Parse-REST-API-Key": "invalid-key-12345",
            "X-JWT-KWY": "valid_jwt_token"
        }
        
        response = client.post(
            "/DevOps",
            json=VALID_PAYLOAD,
            headers=headers
        )
        
        assert response.status_code == 401
    
    def test_missing_jwt_token_returns_401(self):
        """Test that missing JWT token returns 401 Unauthorized"""
        headers = {"X-Parse-REST-API-Key": VALID_API_KEY}
        
        response = client.post(
            "/DevOps",
            json=VALID_PAYLOAD,
            headers=headers
        )
        
        assert response.status_code == 401
    
    def test_missing_both_headers_returns_401(self):
        """Test that missing both security headers returns 401"""
        response = client.post(
            "/DevOps",
            json=VALID_PAYLOAD
        )
        
        assert response.status_code == 401


class TestInvalidHttpMethods:
    """Test cases for unsupported HTTP methods"""
    
    def test_get_request_returns_error(self):
        """Test that GET request returns plain text ERROR"""
        response = client.get("/DevOps")
        
        assert response.status_code == 400
        assert response.text == "ERROR"
    
    def test_put_request_returns_error(self):
        """Test that PUT request returns plain text ERROR"""
        response = client.put(
            "/DevOps",
            json=VALID_PAYLOAD
        )
        
        assert response.status_code == 400
        assert response.text == "ERROR"
    
    def test_delete_request_returns_error(self):
        """Test that DELETE request returns plain text ERROR"""
        response = client.delete("/DevOps")
        
        assert response.status_code == 400
        assert response.text == "ERROR"
    
    def test_patch_request_returns_error(self):
        """Test that PATCH request returns plain text ERROR"""
        response = client.patch(
            "/DevOps",
            json=VALID_PAYLOAD
        )
        
        assert response.status_code == 400
        assert response.text == "ERROR"


class TestInvalidRoutes:
    """Test cases for invalid routes"""
    
    def test_invalid_route_returns_error(self):
        """Test that invalid route returns plain text ERROR"""
        response = client.get("/invalid-route")
        
        assert response.status_code == 400
        assert response.text == "ERROR"
    
    def test_root_path_returns_error(self):
        """Test that root path returns plain text ERROR"""
        response = client.get("/")
        
        assert response.status_code == 400
        assert response.text == "ERROR"


class TestDataValidation:
    """Test cases for request payload validation"""
    
    def test_missing_required_field_returns_422(self):
        """Test that missing required field returns 422 Unprocessable Entity"""
        invalid_payload = {
            "message": "Test",
            "to": "Juan Perez"
            # Missing 'from' and 'timeToLifeSec'
        }
        
        response = client.post(
            "/DevOps",
            json=invalid_payload,
            headers=get_valid_headers()
        )
        
        assert response.status_code == 422
    
    def test_invalid_time_to_life_returns_422(self):
        """Test that invalid timeToLifeSec returns 422"""
        invalid_payload = VALID_PAYLOAD.copy()
        invalid_payload["timeToLifeSec"] = -1
        
        response = client.post(
            "/DevOps",
            json=invalid_payload,
            headers=get_valid_headers()
        )
        
        assert response.status_code == 422


class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    def test_health_endpoint_returns_healthy(self):
        """Test that health check endpoint returns healthy status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestJWTValidation:
    """Test cases for JWT validation and uniqueness"""
    
    def test_jwt_token_can_only_be_used_once(self):
        """Test that JWT token can only be used for one transaction"""
        token = get_valid_jwt()
        headers = {
            "X-Parse-REST-API-Key": VALID_API_KEY,
            "X-JWT-KWY": token
        }
        
        # First request should succeed
        response1 = client.post("/DevOps", json=VALID_PAYLOAD, headers=headers)
        assert response1.status_code == 200
        
        # Second request with same token should fail
        response2 = client.post("/DevOps", json=VALID_PAYLOAD, headers=headers)
        assert response2.status_code == 401
        assert "already used" in response2.json()["detail"].lower()
    
    def test_generate_token_endpoint_requires_api_key(self):
        """Test that token generation requires valid API key"""
        response = client.post("/api/generate-token")
        assert response.status_code == 401
    
    def test_generate_token_with_valid_api_key(self):
        """Test token generation with valid API key"""
        headers = {"X-Parse-REST-API-Key": VALID_API_KEY}
        response = client.post("/api/generate-token", headers=headers)
        
        assert response.status_code == 200
        assert "token" in response.json()
        assert "expires_in" in response.json()
        assert response.json()["type"] == "Bearer"
    
    def test_token_stats_endpoint(self):
        """Test token statistics endpoint"""
        headers = {"X-Parse-REST-API-Key": VALID_API_KEY}
        response = client.get("/api/token-stats", headers=headers)
        
        assert response.status_code == 200
        assert "total_used_tokens" in response.json()
