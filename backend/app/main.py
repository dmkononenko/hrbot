import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api.v1 import router as api_v1_router
from app.bot import bot, dp
from app.bot.handlers.start import router as start_router
from app.bot.handlers.survey import router as survey_router
from aiogram.types import Update

# Register bot handlers
dp.include_router(start_router)
dp.include_router(survey_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifespan - startup and shutdown."""
    # Startup
    await init_db()
    polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))

    yield

    # Shutdown
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    await bot.session.close()

# Create FastAPI app
app = FastAPI(
    title="HR Survey Bot API",
    description="API for HR Survey Telegram Bot",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    update = Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"status": "ok"}


# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")
