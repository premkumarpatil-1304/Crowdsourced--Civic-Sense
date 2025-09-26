import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_NAME]

async def startup_db_client():
    global client, db

    
    # Create collections if they don't exist
    collections = await db.list_collection_names()
    if "users" not in collections:
        await db.create_collection("users")
        await db.users.create_index("email", unique=True)
    
    if "ideas" not in collections:
        await db.create_collection("ideas")
    
    if "votes" not in collections:
        await db.create_collection("votes")
        await db.votes.create_index([("idea_id", 1), ("user_id", 1)], unique=True)


async def shutdown_db_client():
    global client
    if client:
        client.close()

def get_db():
    global db
    return db        