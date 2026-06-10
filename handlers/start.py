from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import db
import random
import string

router = Router()

def generate_game_code() -> str:
    """Генерировать уникальный код игры"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    first_name = message.from_user.first_name or "Player"
    
    # Добавить игрока в БД
    db.add_player(user_id, username, first_name)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Создать игру", callback_data="create_game")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="show_stats")],
        [InlineKeyboardButton(text="❓ Справка", callback_data="show_help")],
    ])
    
    await message.answer(
        f"👋 Привет, {first_name}!\n\n"
        "🎭 Добро пожаловать в игру <b>Мафия</b>!\n\n"
        "Это полнофункциональный Telegram бот для игры в Мафию с друзьями.\n\n"
        "<b>Как начать?</b>\n"
        "1️⃣ Нажмите 'Создать игру'\n"
        "2️⃣ Пригласите друзей по коду\n"
        "3️⃣ Начните игру\n\n"
        "<i>Удачи в игре! 🍀</i>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
<b>🎭 Правила игры Мафия:</b>

<b>🌙 Ночная фаза:</b>
• Мафия выбирает игрока для исключения
• Доктор может защитить одного игрока
• Комиссар может узнать роль одного игрока

<b>☀️ Дневная фаза:</b>
• Все игроки обсуждают и голосуют
• Игрок с наибольшим количеством голосов исключается

<b>🎪 Роли:</b>
🔴 <b>Мафия</b> - исключают днем или ночью
💊 <b>Доктор</b> - защищает игроков ночью
🔍 <b>Комиссар</b> - проверяет роли ночью
👨 <b>Мирный житель</b> - голосует днем

<b>🏆 Условие победы:</b>
✅ Мирные побеждают, если исключена вся мафия
✅ Мафия побеждает, если живых мафиози ≥ живых мирных

<b>📋 Команды:</b>
/start - Главное меню
/create_game - Создать новую игру
/stats - Посмотреть статистику
/help - Эта справка
"""
    await message.answer(help_text, parse_mode="HTML")

@router.callback_query(F.data == "create_game")
async def create_game_callback(query: CallbackQuery):
    """Создать новую игру"""
    from game import create_game
    
    user_id = query.from_user.id
    username = query.from_user.username or "Unknown"
    first_name = query.from_user.first_name or "Player"
    
    game_code = generate_game_code()
    
    try:
        create_game(user_id, game_code)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Присоединиться к игре", callback_data=f"join_{game_code}")],
            [InlineKeyboardButton(text="▶️ Начать игру", callback_data=f"start_{game_code}")],
            [InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel")],
        ])
        
        await query.message.edit_text(
            f"✅ <b>Игра создана!</b>\n\n"
            f"<b>Код игры:</b> <code>{game_code}</code>\n\n"
            f"📌 Поделитесь этим кодом с друзьями, чтобы они присоединились!\n\n"
            f"<b>Создатель:</b> {first_name}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        await query.answer(f"❌ Ошибка: {str(e)}", show_alert=True)

@router.callback_query(F.data == "show_stats")
async def show_stats(query: CallbackQuery):
    """Показать статистику"""
    user_id = query.from_user.id
    stats = db.get_player_stats(user_id)
    
    if not stats:
        stats_text = "📊 <b>Статистика:</b>\n\nВы еще не сыграли ни одной игры!"
    else:
        games, wins, losses, mafia_g, doctor_g, commissar_g, civilian_g = stats
        
        if games > 0:
            win_rate = (wins / games) * 100
        else:
            win_rate = 0
        
        stats_text = f"""
📊 <b>Ваша статистика:</b>

🎮 <b>Общие:</b>
• Всего игр: {games}
• Побед: {wins}
• Поражений: {losses}
• Процент побед: {win_rate:.1f}%

🎪 <b>По ролям:</b>
🔴 Мафия: {mafia_g} игр
💊 Доктор: {doctor_g} игр
🔍 Комиссар: {commissar_g} игр
👨 Мирный житель: {civilian_g} игр
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Создать игру", callback_data="create_game")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ])
    
    await query.message.edit_text(stats_text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "show_help")
async def show_help(query: CallbackQuery):
    """Показать справку"""
    help_text = """
<b>🎭 Правила игры Мафия:</b>

<b>🌙 Ночная фаза:</b>
• Мафия выбирает игрока для исключения
• Доктор может защитить одного игрока
• Комиссар может узнать роль одного игрока

<b>☀️ Дневная фаза:</b>
• Все игроки обсуждают и голосуют
• Игрок с наибольшим количеством голосов исключается

<b>🎪 Роли:</b>
🔴 <b>Мафия</b> - исключают днем или ночью
💊 <b>Доктор</b> - защищает игроков ночью
🔍 <b>Комиссар</b> - проверяет роли ночью
👨 <b>Мирный житель</b> - голосует днем

<b>🏆 Условие победы:</b>
✅ Мирные побеждают, если исключена вся мафия
✅ Мафия побеждает, если живых мафиози ≥ живых мирных
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ])
    
    await query.message.edit_text(help_text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery):
    """Вернуться в главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Создать игру", callback_data="create_game")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="show_stats")],
        [InlineKeyboardButton(text="❓ Справка", callback_data="show_help")],
    ])
    
    await query.message.edit_text(
        "🎭 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "cancel")
async def cancel_callback(query: CallbackQuery):
    """Отмена"""
    await query.message.delete()