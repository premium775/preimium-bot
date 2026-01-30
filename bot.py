import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton
)
from aiohttp import web

# --- SOZLAMALAR ---
API_TOKEN = '8329938226:AAHLUFVE-w88RD06QcOV3PHJSlVTWCc6kdo'
ADMIN_ID = 6611780155  # O'zingizning ID raqamingizni yozing!

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- FSM (Qadamlar) ---
class OrderSteps(StatesGroup):
    choosing_color = State()
    waiting_for_quantity = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_location = State()

# --- TUGMALAR ---
def color_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⚪️ OQ", callback_data="color_oq")],
        [InlineKeyboardButton(text="⚫️ QORA", callback_data="color_qora")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

def location_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

# --- HANDLERLAR ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! **PREMIUM TOWELS** botiga xush kelibsiz.\n"
        "Iltimos, sochiq rangini tanlang:",
        reply_markup=color_keyboard()
    )
    await state.set_state(OrderSteps.choosing_color)

@dp.callback_query(OrderSteps.choosing_color, F.data.startswith("color_"))
async def color_chosen(callback: types.CallbackQuery, state: FSMContext):
    color = "Oq" if callback.data == "color_oq" else "Qora"
    await state.update_data(chosen_color=color)
    await callback.message.delete()
    await callback.message.answer(f"Tanlandi: {color}\n\nNechta buyurtma bermoqchisiz? \n(Eng kam buyurtma: **25 ta**)", parse_mode="Markdown")
    await state.set_state(OrderSteps.waiting_for_quantity)

@dp.message(OrderSteps.waiting_for_quantity)
async def quantity_step(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat son kiriting (masalan: 25):")
        return
    
    quantity = int(message.text)
    if quantity < 25:
        await message.answer("❌ Kechirasiz, eng kam buyurtma **25 ta** bo'lishi kerak. Iltimos, qaytadan kiriting:", parse_mode="Markdown")
        return

    await state.update_data(amount=quantity)
    await message.answer(f"Rahmat! {quantity} ta buyurtma qabul qilindi.\n\nEndi ism va familiyangizni yozing:")
    await state.set_state(OrderSteps.waiting_for_name)

@dp.message(OrderSteps.waiting_for_name)
async def name_step(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())
    await state.set_state(OrderSteps.waiting_for_phone)

@dp.message(OrderSteps.waiting_for_phone, F.contact)
async def phone_step(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Lokatsiyangizni yuboring:", reply_markup=location_keyboard())
    await state.set_state(OrderSteps.waiting_for_location)

@dp.message(OrderSteps.waiting_for_location, F.location)
async def location_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lat = message.location.latitude
    lon = message.location.longitude
    
    # Adminga yuboriladigan tozalangan xabar
    admin_text = (
        f"🚀 **YANGI BUYURTMA!**\n\n"
        f"🎨 **Rangi:** {data['chosen_color']}\n"
        f"🔢 **Soni:** {data['amount']} ta\n"
        f"👤 **Mijoz:** {data['full_name']}\n"
        f"📞 **Tel:** {data['phone']}"
    )
    
    # Adminga xabar va lokatsiya yuborish
    await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    await bot.send_location(ADMIN_ID, lat, lon)
    
    # Mijozga tasdiqlash
    await message.answer("✅ Rahmat! Buyurtmangiz qabul qilindi. Operator tez orada bog'lanadi.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

# --- RENDER PORT SOZLAMASI ---
async def handle(request):
    return web.Response(text="Bot is running")

async def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
