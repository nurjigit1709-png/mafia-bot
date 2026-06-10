"""
Вспомогательные функции для бота
"""
from typing import List, Dict, Optional
from config import ROLES

def format_role(role: str) -> str:
    """Форматировать название роли"""
    return ROLES.get(role, role)

def format_player_list(players: Dict[int, Dict]) -> str:
    """Форматировать список игроков"""
    return "\n".join([
        f"• {player['first_name']} (@{player['username']}) - {'🔴 Жив' if player['is_alive'] else '⚫ Мертв'}"
        for player in players.values()
    ])

def calculate_win_rate(wins: int, total: int) -> float:
    """Рассчитать процент побед"""
    if total == 0:
        return 0.0
    return (wins / total) * 100

def get_role_emoji(role: str) -> str:
    """Получить emoji для роли"""
    emoji_map = {
        "mafia": "🔴",
        "doctor": "💊",
        "commissar": "🔍",
        "civilian": "👨"
    }
    return emoji_map.get(role, "❓")

def format_game_status(game_status: str, phase: str) -> str:
    """Форматировать статус игры"""
    if game_status == "waiting":
        return "⏳ Ожидание"
    elif game_status == "running":
        if phase == "day":
            return "☀️ День (голосование)"
        else:
            return "🌙 Ночь (действия)"
    else:
        return "✅ Завершена"

def get_alive_player_names(players: Dict[int, Dict]) -> List[str]:
    """Получить имена живых игроков"""
    return [
        player['first_name'] for player in players.values() 
        if player['is_alive']
    ]

def check_game_win(alive_mafia: int, alive_civilians: int) -> Optional[str]:
    """Проверить условие победы"""
    if alive_mafia == 0:
        return "civilians"
    elif alive_mafia >= alive_civilians:
        return "mafia"
    return None