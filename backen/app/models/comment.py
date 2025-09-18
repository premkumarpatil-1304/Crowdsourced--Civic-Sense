# app/models/comment.py
from pydantic import BaseModel, Field
from datetime import datetime

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str
    idea_id: str
    user_id: str
    user_name: str
    created_at: datetime