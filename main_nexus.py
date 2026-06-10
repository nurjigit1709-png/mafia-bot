import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_nexus import BOT_TOKEN, LOG_LEVEL
from database_nexus import db
from handlers_nexus import start

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def main():
    logger.info("🚀 Запуск Nexus Economy Bot...")
    
    dp.include_router(start.router)
    
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот подключен: @{me.username}")
        logger.info(f"💰 Nexus Economy Bot готов!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен")