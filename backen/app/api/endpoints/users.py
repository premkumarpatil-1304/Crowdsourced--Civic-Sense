from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.deps import get_current_user
from typing import List
from app.models.idea import Idea
from app.core.database import get_db  # <-- Add this import

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}/ideas", response_model=List[Idea])
async def get_user_ideas(user_id: str, db=Depends(get_db)):  # <-- Inject db here
    ideas = []
    cursor = db.ideas.find({"creator_id": user_id}).sort("created_at", -1)
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        ideas.append(Idea(**doc))
    return ideas