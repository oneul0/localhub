from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.chatbot import router as chatbot_router
from .api.places import router as places_router
from .api.posts import router as posts_router
from .db.database import create_db_and_tables
from .core.config import settings

app = FastAPI(title="LocalHub Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins if origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_router)
app.include_router(places_router)
app.include_router(chatbot_router)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
