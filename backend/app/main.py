from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api.v1 import router as api_v1_router
from app.bot import bot, dp
from app.bot.handlers import start, survey
from aiogram.types import Update

# Register bot handlers
dp.include_router(start.router)
dp.include_router(survey.router)

# Create FastAPI app
app = FastAPI(
    title="HR Survey Bot API",
    description="API for HR Survey Telegram Bot",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close bot session on shutdown."""
    await bot.session.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "HR Survey Bot API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/bot/webhook")
async def bot_webhook(request: Request):
    """
    Telegram webhook endpoint.
    Receives updates from Telegram and passes them to Aiogram dispatcher.
    """
    update = await request.json()
    telegram_update = Update(**update)
    await dp.feed_web_update(bot, telegram_update)
    return {"status": "ok"}


# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")
