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
ADMIN_ID = 5588598964 # O'zingizni ID raqamingizni yozing!

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- FSM (Qadamlar) ---
class OrderSteps(StatesGroup):
    confirming_product = State()
    waiting_for_quantity = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_location = State()

# --- TUGMALAR ---
def product_keyboard():
    buttons = [[InlineKeyboardButton(text="⚪️ OQ SOCHIQNI TANLASH", callback_data="product_white")]]
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

def reorder_keyboard():
    # Yangi buyurtma uchun tugma
    buttons = [[InlineKeyboardButton(text="🔄 Qayta buyurtma berish", callback_data="reorder")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- HANDLERLAR ---

@dp.message(CommandStart())
@dp.callback_query(F.data == "reorder") # Qayta buyurtma tugmasi bosilganda ham ishlaydi
async def cmd_start(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    info_text = (
        "Assalomu alaykum! **PREMIUM TOWELS** botiga xush kelibsiz.\n\n"
        "⚪️ **50 x 90 razmerli oq sochiq**\n"
        "Tanlash uchun quyidagi tugmani bosing 👇"
    )
    
    if isinstance(event, types.Message):
        await event.answer(info_text, reply_markup=product_keyboard(), parse_mode="Markdown")
    else:
        await event.message.answer(info_text, reply_markup=product_keyboard(), parse_mode="Markdown")
        await event.answer()
        
    await state.set_state(OrderSteps.confirming_product)

@dp.callback_query(OrderSteps.confirming_product, F.data == "product_white")
async def product_confirmed(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(chosen_color="Oq (50x90 sm)")
    await callback.message.delete()
    await callback.message.answer(
        "Tanlandi: **50 x 90 razmerli oq sochiq**\n\n"
        "Nechta buyurtma bermoqchisiz? \n"
        "(Eng kam buyurtma: **25 ta**)", 
        parse_mode="Markdown"
    )
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
    
    admin_text = (
        f"🚀 **YANGI BUYURTMA!**\n\n"
        f"📏 **Mahsulot:** {data['chosen_color']}\n"
        f"🔢 **Soni:** {data['amount']} ta\n"
        f"👤 **Mijoz:** {data['full_name']}\n"
        f"📞 **Tel:** {data['phone']}"
    )
    
    await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    await bot.send_location(ADMIN_ID, lat, lon)
    
    # TASDIQLASH VA QAYTA BUYURTMA TUGMASI
    await message.answer(
        "✅ Rahmat! Buyurtmangiz qabul qilindi. Operator tez orada bog'lanadi.\n\nYana buyurtma bermoqchi bo'lsangiz, tugmani bosing:", 
        reply_markup=reorder_keyboard()
    )
    await state.clear()

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
