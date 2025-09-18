# Import FastAPI's APIRouter and create a basic router for comments endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from app.models.comment import CommentCreate, Comment
from app.models.user import User
from app.core.database import db
from app.api.deps import get_current_user

router = APIRouter()


# POST endpoint to add a comment to an idea
@router.post("/", response_model=Comment)
async def create_comment(
	comment: CommentCreate,
	idea_id: str = None,
	current_user: User = Depends(get_current_user)
):
	if not idea_id:
		raise HTTPException(status_code=400, detail="Missing idea_id in path.")
	comment_data = comment.model_dump()
	comment_data["idea_id"] = idea_id
	comment_data["user_id"] = str(current_user.id)
	comment_data["user_name"] = current_user.full_name
	comment_data["created_at"] = datetime.utcnow()

	result = await db.comments.insert_one(comment_data)
	created_comment = await db.comments.find_one({"_id": result.inserted_id})
	created_comment["id"] = str(created_comment["_id"])
	return Comment(**created_comment)

# GET endpoint to fetch all comments for an idea
@router.get("/", response_model=List[Comment])
async def get_comments_for_idea(idea_id: str = None):
	if not idea_id:
		raise HTTPException(status_code=400, detail="Missing idea_id in path.")
	comments = []
	cursor = db.comments.find({"idea_id": idea_id}).sort("created_at", 1)
	async for doc in cursor:
		doc["id"] = str(doc["_id"])
		comments.append(Comment(**doc))
	return comments
