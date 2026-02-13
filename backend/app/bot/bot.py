from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.bot.storage import SQLiteStorage

# Create bot instance
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Create dispatcher with FSM storage
storage = SQLiteStorage(db_path="./hrbot.db")
dp = Dispatcher(storage=storage)
