import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# BotFather'dan olgan koding
API_TOKEN = '8329938226:AAHLUFVE-w88RD06QcOV3PHJSlVTWCc6kdo'

# Bot va Dispatcher (Oddiy va stabil)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        "Assalomu alaykum! Sizni ko'rib turganimizdan xursandmiz.\n\n"
        "Buyurtma berish uchun havola ustiga bosing:\n"
        "**PREMIUM TOWELS** professional barberlar uchun!\n\n"
        "https://premium775.github.io/premium-towels/"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message()
async def auto_reply(message: types.Message):
    await message.answer("Buyurtmangiz qabul qilindi. Tez orada javob beramiz!")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
