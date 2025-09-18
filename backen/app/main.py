from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.core.config import settings
from app.core.database import startup_db_client, shutdown_db_client
from app.api.endpoints import users, ideas, auth, admin, comments

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", startup_db_client)
app.add_event_handler("shutdown", shutdown_db_client)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(ideas.router, prefix="/api/ideas", tags=["ideas"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(comments.router, prefix="/api/ideas/{idea_id}/comments", tags=["comments"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}