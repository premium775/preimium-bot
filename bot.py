import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.session.aiohttp import AiohttpSession # Qo'shildi

# 1. @BotFather'dan olgan tokeningni mana bu yerga qo'y:
API_TOKEN = '8329938226:AAHLUFVE-w88RD06QcOV3PHJSlVTWCc6kdo'

# Bot va Dispatcher ni sozlaymiz (Timeout bilan)
session = AiohttpSession() # Ulanishni barqaror qilish uchun
bot = Bot(token=API_TOKEN, session=session)
dp = Dispatcher()

# /start buyrug'i uchun handler
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        "Assalomu alaykum! Sizni ko'rib turganimizdan xursandmiz.\n\n"
        "Buyurtma berish uchun havola ustiga bosing:\n"
        "**PREMIUM TOWELS** professional barberlar uchun!\n\n"
        "https://premium775.github.io/premium-towels/"
    )
    # Linkni chiroyli ko'rinishda yuboramiz
    await message.answer(welcome_text, parse_mode="Markdown")

# Har qanday boshqa yozuvga javob beruvchi handler
@dp.message()
async def auto_reply(message: types.Message):
    await message.answer("Buyurtmangiz tayyorlanmoqda...")

# Botni yurgizish
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi!")
