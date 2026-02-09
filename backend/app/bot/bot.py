from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings

# Create bot instance
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)

# Create dispatcher with FSM storage
dp = Dispatcher(storage=MemoryStorage())
