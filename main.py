"""
🎭 Telegram Mafia Bot
Полнофункциональный бот для игры в Мафию
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from config import BOT_TOKEN, LOG_LEVEL
from handlers.start import router as start_router
from handlers.game import router as game_router
from handlers.stats import router as stats_router

# Настройка логирования
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(game_router)
dp.include_router(stats_router)

async def main():
    """Главная функция"""
    logger.info("🚀 Запуск Telegram Mafia Bot...")
    logger.info(f"Bot token: {BOT_TOKEN[:10]}...")
    
    try:
        # Получить информацию о боте
        me = await bot.get_me()
        logger.info(f"✅ Бот подключен: @{me.username} ({me.first_name})")
        
        # Запустить polling
        logger.info("🎮 Ожидание сообщений...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")