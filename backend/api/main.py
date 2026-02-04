"""
FastAPI main application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import init_db, close_db
from api.routes import (
    auth,
    pets,
    inventory,
    shop,
    games,
    friends,
    battles,
    quests,
    achievements,
    leaderboard,
    breeding,
    market,
    websocket,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Tamagotchi Bot API",
    description="API for Tamagotchi Telegram Bot Mini App",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(pets.router, prefix="/api/v1/pets", tags=["pets"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(shop.router, prefix="/api/v1/shop", tags=["shop"])
app.include_router(games.router, prefix="/api/v1/games", tags=["games"])
app.include_router(friends.router, prefix="/api/v1/friends", tags=["friends"])
app.include_router(battles.router, prefix="/api/v1/battles", tags=["battles"])
app.include_router(quests.router, prefix="/api/v1/quests", tags=["quests"])
app.include_router(achievements.router, prefix="/api/v1/achievements", tags=["achievements"])
app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["leaderboard"])
app.include_router(breeding.router, prefix="/api/v1/breeding", tags=["breeding"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["websocket"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Tamagotchi Bot API",
        "version": "1.0.0",
        "docs": "/docs",
    }
