# app/api/endpoints/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from app.api.deps import get_current_admin_user
from app.core.database import db

from app.models.user import User
from app.models.idea import Idea, IdeaStatus

router = APIRouter()

@router.get("/users", response_model=list[User], summary="Get all users (Admin Only)")
async def read_all_users(current_user: User = Depends(get_current_admin_user)):
    """
    Retrieve a list of all users.
    Accessible only by admin users.
    """
    users = []
    cursor = db.users.find({})
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        users.append(User(**doc))
    return users

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user (Admin Only)")
async def delete_user(user_id: str, current_user: User = Depends(get_current_admin_user)):
    """
    Delete a user by their ID.
    Accessible only by admin users.
    """
    # Check if the user to be deleted exists
    user_to_delete = await db.users.find_one({"_id": ObjectId(user_id)})
    if user_to_delete is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Optional: Prevent an admin from deleting themselves
    if str(user_to_delete["_id"]) == str(current_user.id):
        raise HTTPException(status_code=403, detail="Cannot delete your own admin account")

    # Delete the user and their associated data
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.ideas.delete_many({"creator_id": user_id})
    await db.votes.delete_many({"user_id": user_id})

    return {"status": "success"}

@router.delete("/ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an idea (Admin Only)")
async def delete_idea(idea_id: str, current_user: User = Depends(get_current_admin_user)):
    """
    Delete any idea by its ID.
    Accessible only by admin users.
    """
    # Check if the idea to be deleted exists
    idea_to_delete = await db.ideas.find_one({"_id": ObjectId(idea_id)})
    if idea_to_delete is None:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Delete the idea and all votes associated with it
    await db.ideas.delete_one({"_id": ObjectId(idea_id)})
    await db.votes.delete_many({"idea_id": idea_id})

    return {"status": "success"}

@router.patch("/ideas/{idea_id}/status", response_model=Idea)
async def update_idea_status(idea_id: str, new_status: IdeaStatus, current_user: User = Depends(get_current_admin_user)):
    """
    Update the status of an idea (Admin Only).
    """
    idea_to_update = await db.ideas.find_one({"_id": ObjectId(idea_id)})
    if idea_to_update is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    await db.ideas.update_one(
        {"_id": ObjectId(idea_id)},
        {"$set": {"status": new_status.value}}
    )
    
    updated_idea = await db.ideas.find_one({"_id": ObjectId(idea_id)})
    updated_idea["id"] = str(updated_idea["_id"])
    return updated_idea
