from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.models.idea import IdeaCategory
# PyObjectId for MongoDB _id handling
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d21b4667d0d8992e610c85",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_admin": False,
                "created_at": "2023-01-01T00:00:00"
            }
        }
        
    class IdeaUpdate(BaseModel):
        title: Optional[str] = None
        description: Optional[str] = None
        category: Optional[IdeaCategory] = None
        location: Optional[str] = None

class UserInDB(User):
    hashed_password: str