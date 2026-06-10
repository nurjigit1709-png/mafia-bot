from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database_nexus import db
from keyboards_nexus import main_menu, back_keyboard, work_menu, business_menu, land_menu, market_menu, top_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    full_name = message.from_user.first_name or "Player"
    
    db.add_user(user_id, username, full_name)
    
    welcome_text = f"""💰 <b>Добро пожаловать в Nexus Economy!</b>

🎮 Экономический симулятор для Telegram

✅ Работайте и зарабатывайте NC
✅ Создавайте свой бизнес
✅ Покупайте землю
✅ Торгуйте ресурсами
✅ Соревнитесь в рейтингах

🎁 Стартовый капитал: <b>5000 NC</b>
"""
    
    await message.answer(welcome_text, reply_markup=main_menu(), parse_mode="HTML")

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start")
        return
    
    resources = db.get_resources(user['id'])
    land = db.get_total_land(user['id'])
    
    profile_text = f"""👤 <b>Профиль: {user['full_name']}</b>

💰 Баланс: {user['balance']:,} NC
⭐ Уровень: {user['level']}
🏆 Репутация: {user['reputation']}
🌍 Земля: {land} м²

🥇 Золото: {resources['gold'] if resources else 0}
🥈 Серебро: {resources['silver'] if resources else 0}
⛏ Руда: {resources['ore'] if resources else 0}
"""
    
    await message.answer(profile_text, reply_markup=main_menu(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """❓ <b>СПРАВКА</b>

📋 /start - Начать
👤 /profile - Профиль
💼 /jobs - Вакансии
🏢 /mybusiness - Мои бизнесы
🌍 /myland - Моя земля
🛒 /market_gold - Рынок золота
🏆 /top_balance - Топ игроков
"""
    
    await message.answer(help_text, reply_markup=back_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "back_menu")
async def back_menu(query: CallbackQuery):
    await query.message.edit_text("📋 <b>Главное меню</b>", reply_markup=main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "profile")
async def profile_callback(query: CallbackQuery):
    user = db.get_user(query.from_user.id)
    if not user:
        await query.answer("❌ Профиль не найден")
        return
    
    resources = db.get_resources(user['id'])
    land = db.get_total_land(user['id'])
    
    profile_text = f"""👤 <b>Профиль: {user['full_name']}</b>

💰 Баланс: {user['balance']:,} NC
⭐ Уровень: {user['level']}
🏆 Репутация: {user['reputation']}
🌍 Земля: {land} м²

🥇 Золото: {resources['gold'] if resources else 0}
🥈 Серебро: {resources['silver'] if resources else 0}
⛏ Руда: {resources['ore'] if resources else 0}
"""
    
    await query.message.edit_text(profile_text, reply_markup=main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "top_menu")
async def top_menu_callback(query: CallbackQuery):
    top_text = "🏆 <b>Топ 10 по балансу</b>\n\n"
    
    top_users = db.get_top_users(10)
    for i, user in enumerate(top_users, 1):
        top_text += f"{i}. {user['username']} - {user['balance']:,} NC\n"
    
    await query.message.edit_text(top_text, reply_markup=back_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "help_menu")
async def help_menu_callback(query: CallbackQuery):
    help_text = """❓ <b>СПРАВКА</b>

📋 /help - Полная информация
👤 /profile - Мой профиль
💼 /jobs - Вакансии
🏆 /top_balance - Рейтинги
"""
    await query.message.edit_text(help_text, reply_markup=back_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "work_menu")
async def work_menu_callback(query: CallbackQuery):
    await query.message.edit_text("💼 <b>Раздел Работа</b>", reply_markup=work_menu(), parse_mode="HTML")

@router.callback_query(F.data == "business_menu")
async def business_menu_callback(query: CallbackQuery):
    await query.message.edit_text("🏢 <b>Раздел Бизнес</b>", reply_markup=business_menu(), parse_mode="HTML")

@router.callback_query(F.data == "land_menu")
async def land_menu_callback(query: CallbackQuery):
    await query.message.edit_text("🌍 <b>Раздел Земля</b>", reply_markup=land_menu(), parse_mode="HTML")

@router.callback_query(F.data == "market_menu")
async def market_menu_callback(query: CallbackQuery):
    await query.message.edit_text("🛒 <b>Раздел Рынок</b>", reply_markup=market_menu(), parse_mode="HTML")

@router.callback_query(F.data == "resources_menu")
async def resources_menu_callback(query: CallbackQuery):
    user = db.get_user(query.from_user.id)
    if not user:
        await query.answer("❌ Профиль не найден")
        return
    
    resources = db.get_resources(user['id'])
    
    resources_text = f"""📦 <b>Мои Ресурсы</b>

🥇 Золото: {resources['gold'] if resources else 0}
🥈 Серебро: {resources['silver'] if resources else 0}
⛏ Руда: {resources['ore'] if resources else 0}
🛢 Нефть: {resources['oil'] if resources else 0}
⚙ Детали: {resources['details'] if resources else 0}
"""
    
    await query.message.edit_text(resources_text, reply_markup=back_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "top_balance")
async def top_balance_callback(query: CallbackQuery):
    top_text = "🏆 <b>Топ 10 по балансу</b>\n\n"
    
    top_users = db.get_top_users(10)
    for i, user in enumerate(top_users, 1):
        top_text += f"{i}. {user['username']} - {user['balance']:,} NC (уровень {user['level']})\n"
    
    await query.message.edit_text(top_text, reply_markup=back_keyboard(), parse_mode="HTML")