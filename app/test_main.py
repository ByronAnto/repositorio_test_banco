"""
Test suite for Banking DevOps API
Following TDD principles with comprehensive test coverage
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app, VALID_API_KEY

client = TestClient(app)

# Test data constants
VALID_HEADERS = {
    "X-Parse-REST-API-Key": VALID_API_KEY,
    "X-JWT-KWY": "valid_jwt_token_here"
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
            headers=VALID_HEADERS
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
            headers=VALID_HEADERS
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
        response = client.get("/DevOps", headers=VALID_HEADERS)
        
        assert response.status_code == 400
        assert response.text == "ERROR"
    
    def test_put_request_returns_error(self):
        """Test that PUT request returns plain text ERROR"""
        response = client.put(
            "/DevOps",
            json=VALID_PAYLOAD,
            headers=VALID_HEADERS
        )
        
        assert response.status_code == 400
        assert response.text == "ERROR"
    
    def test_delete_request_returns_error(self):
        """Test that DELETE request returns plain text ERROR"""
        response = client.delete("/DevOps", headers=VALID_HEADERS)
        
        assert response.status_code == 400
        assert response.text == "ERROR"
    
    def test_patch_request_returns_error(self):
        """Test that PATCH request returns plain text ERROR"""
        response = client.patch(
            "/DevOps",
            json=VALID_PAYLOAD,
            headers=VALID_HEADERS
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
            headers=VALID_HEADERS
        )
        
        assert response.status_code == 422
    
    def test_invalid_time_to_life_returns_422(self):
        """Test that invalid timeToLifeSec returns 422"""
        invalid_payload = VALID_PAYLOAD.copy()
        invalid_payload["timeToLifeSec"] = -1
        
        response = client.post(
            "/DevOps",
            json=invalid_payload,
            headers=VALID_HEADERS
        )
        
        assert response.status_code == 422


class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    def test_health_endpoint_returns_healthy(self):
        """Test that health check endpoint returns healthy status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
