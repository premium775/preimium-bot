import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web # Port ochish uchun kerak

API_TOKEN = '8329938226:AAHLUFVE-w88RD06QcOV3PHJSlVTWCc6kdo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = "Assalomu alaykum! Bot hozir stabil ishlayapti. ✅"
    await message.answer(welcome_text)

# Render uchun "yolg'onchi" server yaratamiz
async def handle(request):
    return web.Response(text="Bot is running")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Botni ishga tushirish
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))

    # 2. Render kutayotgan portni ochish
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render beradigan portni olamiz yoki 10000-portni ishlatamiz
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    print(f"Port {port} ochildi. Bot ishlamoqda...")
    await site.start()

    # Botni to'xtab qolmasligi uchun cheksiz kutish
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
