from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import db

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    user_id = message.from_user.id
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
• Побед: {wins} ✅
• Поражений: {losses} ❌
• Процент побед: {win_rate:.1f}%

🎪 <b>По ролям:</b>
🔴 Мафия: {mafia_g} игр
💊 Доктор: {doctor_g} игр
🔍 Комиссар: {commissar_g} игр
👨 Мирный житель: {civilian_g} игр
"""
    
    await message.answer(stats_text, parse_mode="HTML")

@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: Message):
    """Обработчик команды /leaderboard"""
    # Эта функция требует получения всех игроков из БД
    # и сортировки по количеству побед
    # Реализация опциональна
    await message.answer(
        "📊 <b>Таблица лидеров</b>\n\n"
        "Эта функция будет реализована в следующей версии!",
        parse_mode="HTML"
    )