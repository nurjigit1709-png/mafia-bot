import random
from typing import Dict, List, Optional
from config import ROLES, MIN_PLAYERS, MAX_PLAYERS
from database import db

class GameRoom:
    def __init__(self, game_id: int, creator_id: int, game_code: str):
        self.game_id = game_id
        self.creator_id = creator_id
        self.game_code = game_code
        self.players: Dict[int, Dict] = {}
        self.status = "waiting"  # waiting, running, finished
        self.phase = "day"  # day, night
        self.round = 0
        self.votes = {}
    
    def add_player(self, user_id: int, username: str, first_name: str):
        """Добавить игрока в комнату"""
        if len(self.players) >= MAX_PLAYERS:
            return False
        
        self.players[user_id] = {
            "username": username,
            "first_name": first_name,
            "role": None,
            "is_alive": True,
            "is_muted": False,
            "voted": False
        }
        db.add_player_to_game(self.game_id, user_id)
        return True
    
    def remove_player(self, user_id: int):
        """Удалить игрока из комнаты"""
        if user_id in self.players:
            del self.players[user_id]
            return True
        return False
    
    def get_player_count(self) -> int:
        """Получить количество игроков"""
        return len(self.players)
    
    def can_start_game(self) -> bool:
        """Проверить, можно ли начать игру"""
        return MIN_PLAYERS <= len(self.players) <= MAX_PLAYERS
    
    def distribute_roles(self):
        """Распределить роли среди игроков"""
        player_ids = list(self.players.keys())
        random.shuffle(player_ids)
        
        # Расчет ролей в зависимости от количества игроков
        player_count = len(player_ids)
        
        mafia_count = max(1, player_count // 3)
        doctor_count = 1 if player_count >= 5 else 0
        commissar_count = 1 if player_count >= 6 else 0
        civilian_count = player_count - mafia_count - doctor_count - commissar_count
        
        roles = (
            ["mafia"] * mafia_count +
            ["doctor"] * doctor_count +
            ["commissar"] * commissar_count +
            ["civilian"] * civilian_count
        )
        
        random.shuffle(roles)
        
        for user_id, role in zip(player_ids, roles):
            self.players[user_id]["role"] = role
        
        # Сохранить роли в БД
        roles_dict = {user_id: self.players[user_id]["role"] for user_id in player_ids}
        db.assign_roles(self.game_id, roles_dict)
    
    def start_game(self):
        """Начать игру"""
        if not self.can_start_game():
            return False
        
        self.distribute_roles()
        self.status = "running"
        self.phase = "night"
        self.round = 1
        
        db.update_game_status(self.game_id, "running", "night")
        return True
    
    def get_alive_players(self) -> List[int]:
        """Получить живых игроков"""
        return [uid for uid, data in self.players.items() if data["is_alive"]]
    
    def get_players_by_role(self, role: str) -> List[int]:
        """Получить игроков с определенной ролью"""
        return [uid for uid, data in self.players.items() 
                if data["role"] == role and data["is_alive"]]
    
    def add_vote(self, voter_id: int, voted_id: int):
        """Добавить голос"""
        self.players[voter_id]["voted"] = True
        db.add_vote(self.game_id, voter_id, voted_id, self.phase)
    
    def get_votes_result(self) -> Optional[int]:
        """Получить результаты голосования"""
        votes_data = db.get_votes(self.game_id, self.phase)
        
        if not votes_data:
            return None
        
        # Получить игрока с наибольшим количеством голосов
        top_voted = votes_data[0][0]  # user_id с наибольшим количеством голосов
        top_votes = votes_data[0][1]
        
        # Проверить на ничью
        tied = [v[0] for v in votes_data if v[1] == top_votes]
        
        if len(tied) > 1:
            return None  # Ничья
        
        return top_voted
    
    def eliminate_player(self, user_id: int):
        """Исключить игрока"""
        if user_id in self.players:
            self.players[user_id]["is_alive"] = False
            db.set_player_alive(self.game_id, user_id, 0)
            return True
        return False
    
    def reset_votes(self):
        """Сбросить голоса"""
        for player_data in self.players.values():
            player_data["voted"] = False
    
    def switch_phase(self):
        """Переключить фазу"""
        if self.phase == "day":
            self.phase = "night"
        else:
            self.phase = "day"
            self.round += 1
        
        db.update_game_status(self.game_id, "running", self.phase)
    
    def check_win_condition(self) -> Optional[str]:
        """Проверить условие победы"""
        alive_mafia = self.get_players_by_role("mafia")
        alive_civilians = [uid for uid, data in self.players.items() 
                          if data["is_alive"] and data["role"] != "mafia"]
        
        if len(alive_mafia) == 0:
            return "civilians"  # Мирные победили
        
        if len(alive_mafia) >= len(alive_civilians):
            return "mafia"  # Мафия победила
        
        return None  # Игра продолжается
    
    def end_game(self, winner: str):
        """Завершить игру"""
        self.status = "finished"
        
        # Обновить статистику
        if winner == "mafia":
            for user_id in self.get_players_by_role("mafia"):
                db.update_player_stats(user_id, "mafia", True)
        else:
            for user_id in self.get_alive_players():
                if self.players[user_id]["role"] != "mafia":
                    db.update_player_stats(user_id, self.players[user_id]["role"], True)
        
        # Обновить проигравших
        for user_id, player_data in self.players.items():
            if player_data["is_alive"]:
                if (winner == "mafia" and player_data["role"] != "mafia") or \
                   (winner == "civilians" and player_data["role"] == "mafia"):
                    db.update_player_stats(user_id, player_data["role"], False)
        
        return winner

# Глобальный словарь активных игр
active_games: Dict[str, GameRoom] = {}

def create_game(creator_id: int, game_code: str) -> str:
    """Создать новую игру"""
    game_id = db.create_game_room(creator_id, game_code)
    game = GameRoom(game_id, creator_id, game_code)
    active_games[game_code] = game
    return game_code

def get_game(game_code: str) -> Optional[GameRoom]:
    """Получить игру по коду"""
    return active_games.get(game_code)

def remove_game(game_code: str):
    """Удалить игру"""
    if game_code in active_games:
        del active_games[game_code]