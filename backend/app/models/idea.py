from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

class IdeaCategory(str, Enum):
    WASTE = "waste"
    POTHOLES = "potholes"  
    HEALTH = "health"
    TRANSPORT = "transport"
    PARKS = "parks"
    SAFETY = "safety"
    ENVIRONMENT = "environment"
    INFRASTRUCTURE = "infrastructure"

class IdeaBase(BaseModel):
    title: str
    description: str
    category: IdeaCategory
    location: str
    # New: Add latitude and longitude
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[IdeaCategory] = None
    location: str = ""
    status: Optional[str] = None


# Move IdeaStatus outside the Idea class
class IdeaStatus(str, Enum):
    OPEN = "OPEN"
    READ = "read"
    SENT_TO_DEPT = "sent_to_dept"
    WORK_IN_PROGRESS = "work_in_progress"
    RESOLVED = "resolved"

class Idea(IdeaBase):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: IdeaCategory
    location: Optional[str] = Field(None, max_length=200)
    id: str = Field(default_factory=lambda: str(ObjectId()))
    creator_id: str
    creator_name: str
    status: IdeaStatus = IdeaStatus.READ
    vote_score: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d21b4667d0d8992e610c85",
                "title": "Improve City Parks",
                "description": "Add more benches and trees",
                "category": "ENVIRONMENT",
                "location": "Central Park",
                "creator_id": "60d21b4667d0d8992e610c85",
                "creator_name": "John Doe",
                "status": "read",
                "vote_score": 0,
                "created_at": "2023-01-01T00:00:00",
                "latitude": 40.785091,
                "longitude": -73.968285
            }
        }

