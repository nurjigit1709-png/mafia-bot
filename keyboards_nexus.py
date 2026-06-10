from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💼 Работа", callback_data="work_menu"), InlineKeyboardButton(text="🏢 Бизнес", callback_data="business_menu")],
        [InlineKeyboardButton(text="🌍 Земля", callback_data="land_menu"), InlineKeyboardButton(text="🛒 Рынок", callback_data="market_menu")],
        [InlineKeyboardButton(text="📦 Ресурсы", callback_data="resources_menu"), InlineKeyboardButton(text="🏆 Топы", callback_data="top_menu")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help_menu")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])

def work_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Вакансии", callback_data="view_jobs")],
        [InlineKeyboardButton(text="📋 Моя работа", callback_data="my_job")],
        [InlineKeyboardButton(text="💰 Зарплата", callback_data="collect_salary")],
        [InlineKeyboardButton(text="🚪 Уволиться", callback_data="leave_job")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])

def business_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Мои бизнесы", callback_data="my_business")],
        [InlineKeyboardButton(text="✨ Создать", callback_data="create_business")],
        [InlineKeyboardButton(text="📊 Типы", callback_data="business_types_info")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])

def land_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Моя земля", callback_data="my_land")],
        [InlineKeyboardButton(text="🛒 Купить", callback_data="buy_land_menu")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])

def market_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🥇 Золото", callback_data="market_gold")],
        [InlineKeyboardButton(text="🥈 Серебро", callback_data="market_silver")],
        [InlineKeyboardButton(text="⛏ Руда", callback_data="market_ore")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])

def top_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Топ по балансу", callback_data="top_balance")],
        [InlineKeyboardButton(text="🥇 Топ по золоту", callback_data="top_gold")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")],
    ])