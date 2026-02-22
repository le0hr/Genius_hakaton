from config import settings
import asyncio
import logging
import sys
import aiogram
from aiogram import html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import algo
import matplotlib.pyplot as plt
import io
from start import start
from list import buildings_router 
from statistic import statistic_router
from strategy import strategy_router
from settings import settings_router
TOKEN = settings.TOKEN


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = aiogram.Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = aiogram.Dispatcher()
    dp.include_router(start)
    dp.include_router(statistic_router)
    dp.include_router(buildings_router)
    dp.include_router(strategy_router)
    dp.include_router(settings_router)
    print("Бот запущений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())