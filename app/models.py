"""
Data models for the DevOps Banking API
Following Clean Code principles with clear naming and single responsibility
"""
from pydantic import BaseModel, Field


class DevOpsRequest(BaseModel):
    """Request model for DevOps endpoint"""
    message: str = Field(..., min_length=1, description="Message content")
    to: str = Field(..., min_length=1, description="Recipient name")
    from_: str = Field(..., alias="from", min_length=1, description="Sender name")
    timeToLifeSec: int = Field(..., gt=0, description="Time to live in seconds")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "message": "This is a test",
                "to": "Juan Perez",
                "from": "Rita Asturia",
                "timeToLifeSec": 45
            }
        }


class DevOpsResponse(BaseModel):
    """Response model for DevOps endpoint"""
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello Juan Perez your message will be send"
            }
        }
