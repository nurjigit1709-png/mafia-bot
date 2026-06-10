import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from game import get_game, active_games
from database import db
from config import ROLES, MIN_PLAYERS

router = Router()

# Словарь для отслеживания взаимодействия пользователей
user_state = {}

def get_user_games(user_id: int) -> list:
    """Получить все игры, в которых участвует пользователь"""
    games = []
    for code, game in active_games.items():
        if user_id in game.players:
            games.append((code, game))
    return games

@router.message(Command("join_game"))
async def cmd_join_game(message: Message):
    """Обработчик команды /join_game с кодом"""
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.answer(
            "❌ Пожалуйста, укажите код игры:\n"
            "/join_game [КОД]"
        )
        return
    
    game_code = args[1].upper()
    game = get_game(game_code)
    
    if not game:
        await message.answer("❌ Игра с этим кодом не найдена!")
        return
    
    if game.status != "waiting":
        await message.answer("❌ Эта игра уже начата!")
        return
    
    username = message.from_user.username or "Unknown"
    first_name = message.from_user.first_name or "Player"
    
    if game.add_player(user_id, username, first_name):
        await message.answer(
            f"✅ Вы присоединились к игре!\n\n"
            f"<b>Код игры:</b> <code>{game_code}</code>\n"
            f"<b>Игроков в комнате:</b> {game.get_player_count()}/20",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Не удалось присоединиться к игре!")

@router.callback_query(F.data.startswith("join_"))
async def join_game_callback(query: CallbackQuery):
    """Присоединиться к игре через callback"""
    game_code = query.data.replace("join_", "").upper()
    user_id = query.from_user.id
    username = query.from_user.username or "Unknown"
    first_name = query.from_user.first_name or "Player"
    
    game = get_game(game_code)
    
    if not game:
        await query.answer("❌ Игра не найдена!", show_alert=True)
        return
    
    if game.status != "waiting":
        await query.answer("❌ Эта игра уже начата!", show_alert=True)
        return
    
    if game.add_player(user_id, username, first_name):
        players_list = "\n".join([
            f"• {player['first_name']} (@{player['username']})"
            for player in game.players.values()
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Присоединиться", callback_data=f"join_{game_code}")],
            [InlineKeyboardButton(text="▶️ Начать игру", callback_data=f"start_{game_code}")],
            [InlineKeyboardButton(text="🚪 Выйти из игры", callback_data=f"leave_{game_code}")],
        ])
        
        text = (
            f"🎮 <b>Комната игры</b>\n\n"
            f"<b>Код:</b> <code>{game_code}</code>\n"
            f"<b>Статус:</b> Ожидание (минимум {MIN_PLAYERS} игроков)\n\n"
            f"<b>Игроки ({game.get_player_count()}/20):</b>\n"
            f"{players_list}"
        )
        
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await query.answer("✅ Вы присоединились к игре!")
    else:
        await query.answer("❌ Не удалось присоединиться!", show_alert=True)

@router.callback_query(F.data.startswith("leave_"))
async def leave_game_callback(query: CallbackQuery):
    """Выйти из игры"""
    game_code = query.data.replace("leave_", "").upper()
    user_id = query.from_user.id
    
    game = get_game(game_code)
    
    if not game:
        await query.answer("❌ Игра не найдена!", show_alert=True)
        return
    
    if game.remove_player(user_id):
        await query.message.delete()
        await query.answer("👋 Вы вышли из игры!")
    else:
        await query.answer("❌ Ошибка при выходе из игры!", show_alert=True)

@router.callback_query(F.data.startswith("start_"))
async def start_game_callback(query: CallbackQuery):
    """Начать игру"""
    game_code = query.data.replace("start_", "").upper()
    user_id = query.from_user.id
    
    game = get_game(game_code)
    
    if not game:
        await query.answer("❌ Игра не найдена!", show_alert=True)
        return
    
    if game.creator_id != user_id:
        await query.answer("❌ Только создатель может начать игру!", show_alert=True)
        return
    
    if not game.can_start_game():
        await query.answer(
            f"❌ Недостаточно игроков!\n"
            f"Нужно минимум {MIN_PLAYERS}, сейчас {game.get_player_count()}",
            show_alert=True
        )
        return
    
    if game.start_game():
        await query.message.delete()
        await query.answer("✅ Игра начата!")
    else:
        await query.answer("❌ Ошибка при запуске игры!", show_alert=True)

@router.callback_query(F.data.startswith("choose_victim_"))
async def choose_victim(query: CallbackQuery):
    """Выбрать жертву ночью"""
    parts = query.data.split("_")
    game_code = parts[2]
    victim_id = int(parts[3])
    
    game = get_game(game_code)
    
    if not game:
        await query.answer("❌ Игра не найдена!", show_alert=True)
        return
    
    if query.from_user.id not in game.get_players_by_role("mafia"):
        await query.answer("❌ Только мафия может выбирать жертв!", show_alert=True)
        return
    
    # Сохранить выбор жертвы
    user_state[query.from_user.id] = {
        "game_code": game_code,
        "action": "night_kill",
        "target": victim_id
    }
    
    victim_name = game.players[victim_id]["first_name"]
    await query.answer(f"✅ Вы выбрали {victim_name} как жертву!", show_alert=True)