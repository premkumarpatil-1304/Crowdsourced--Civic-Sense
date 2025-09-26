from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from app.models.user import User
from app.models.idea import Idea
from app.api.deps import get_current_user
from app.core.database import db

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user["id"] = str(user["_id"])
    return User(**user)

@router.get("/{user_id}/ideas", response_model=List[Idea])
async def get_user_ideas(user_id: str):
    ideas = []
    cursor = db.ideas.find({"creator_id": user_id}).sort("created_at", -1)
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        ideas.append(Idea(**doc))
    return ideas