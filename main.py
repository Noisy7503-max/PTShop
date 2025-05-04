import asyncio, logging
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import config 
from states.dispatcher import dp
from handlers import main_handler, buy_account, sell_account, cabinet, admin, error

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    bot = Bot(config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(main_handler.router)
    dp.include_router(cabinet.router)
    dp.include_router(admin.router)
    dp.include_router(sell_account.router)
    dp.include_router(buy_account.router)
    dp.include_router(error.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
