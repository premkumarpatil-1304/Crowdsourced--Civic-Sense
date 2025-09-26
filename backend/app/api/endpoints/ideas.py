from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

import httpx
from app.models.idea import IdeaCreate, Idea, IdeaUpdate, IdeaStatus
from app.models.user import User
from app.api.deps import get_current_user
from app.core.database import db # Correctly import the global db client

router = APIRouter()




@router.post("/", response_model=Idea)
async def create_idea(
    idea: IdeaCreate, # This model now includes latitude and longitude
    current_user: User = Depends(get_current_user)
):
    idea_data = idea.model_dump()
    # New: Geocode the location string to get coordinates
    coordinates = await get_coordinates(idea_data["location"])
    if coordinates:
        idea_data["latitude"] = coordinates["latitude"]
        idea_data["longitude"] = coordinates["longitude"]
    else:
        # If geocoding fails, set coordinates to None
        idea_data["latitude"] = None
        idea_data["longitude"] = None
        
    idea_data["creator_id"] = str(current_user.id)
    idea_data["creator_name"] = current_user.full_name
    idea_data["created_at"] = datetime.utcnow()
    idea_data["status"] = IdeaStatus.READ
    idea_data["vote_score"] = 0

    result = await db.ideas.insert_one(idea_data)
    created_idea = await db.ideas.find_one({"_id": result.inserted_id})
    created_idea["id"] = str(created_idea["_id"])

    return Idea(**created_idea)

@router.get("/", response_model=List[Idea])
async def read_ideas(
    skip: int = 0,
    limit: int = 10
):
    ideas = []
    cursor = db.ideas.find().skip(skip).limit(limit)
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        ideas.append(Idea(**doc))
    return ideas

@router.get("/{idea_id}", response_model=Idea)
async def read_idea(
    idea_id: str
):
    idea = await db.ideas.find_one({"_id": ObjectId(idea_id)})
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea["id"] = str(idea["_id"])
    return Idea(**idea)

@router.post("/{idea_id}/vote")
async def vote_on_idea(
    idea_id: str,
    vote_type: str,
    current_user: User = Depends(get_current_user)
):
    if vote_type not in ["upvote", "downvote"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")

    existing_vote = await db.votes.find_one({
        "idea_id": idea_id,
        "user_id": current_user.id
    })

    vote_change = 1 if vote_type == "upvote" else -1

    if existing_vote:
        old_vote = 1 if existing_vote["vote_type"] == "upvote" else -1
        if old_vote != vote_change:
            await db.votes.update_one(
                {"_id": existing_vote["_id"]},
                {"$set": {"vote_type": vote_type}}
            )
            await db.ideas.update_one(
                {"_id": ObjectId(idea_id)},
                {"$inc": {"vote_score": vote_change - old_vote}}
            )
    else:
        await db.votes.insert_one({
            "idea_id": idea_id,
            "user_id": current_user.id,
            "vote_type": vote_type,
            "created_at": datetime.utcnow()
        })
        await db.ideas.update_one(
            {"_id": ObjectId(idea_id)},
            {"$inc": {"vote_score": vote_change}}
        )

    return {"status": "success", "message": f"Successfully {vote_type}d"}

@router.patch("/{idea_id}", response_model=Idea)
async def update_idea(
    idea_id: str,
    idea_update: IdeaUpdate,
    current_user: User = Depends(get_current_user)
):
    idea = await db.ideas.find_one({"_id": ObjectId(idea_id)})
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    if str(idea["creator_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this idea")

    update_data = {k: v for k, v in idea_update.model_dump(exclude_unset=True).items()}
    await db.ideas.update_one({"_id": ObjectId(idea_id)}, {"$set": update_data})

    updated_idea = await db.ideas.find_one({"_id": ObjectId(idea_id)})
    updated_idea["id"] = str(updated_idea["_id"])
    return Idea(**updated_idea)


# Helper function to get coordinates from a location string
async def get_coordinates(location: str):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    
    headers = {
        "User-Agent": "CivicIdeaPlatform/1.0 (your-email@example.com)"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, headers=headers)
            data = response.json()
            if data and len(data) > 0:
                return {
                    "latitude": float(data[0]["lat"]),
                    "longitude": float(data[0]["lon"])
                }
            return None
    except httpx.RequestError as e:
        print(f"An error occurred while geocoding: {e}")
        return None