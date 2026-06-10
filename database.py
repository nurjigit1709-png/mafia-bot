import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица игроков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                mafia_games INTEGER DEFAULT 0,
                doctor_games INTEGER DEFAULT 0,
                commissar_games INTEGER DEFAULT 0,
                civilian_games INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица игровых комнат
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER,
                game_code TEXT UNIQUE,
                status TEXT DEFAULT 'waiting',
                phase TEXT DEFAULT 'day',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                winner TEXT
            )
        ''')
        
        # Таблица участников игры
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_players (
                game_id INTEGER,
                user_id INTEGER,
                role TEXT,
                is_alive INTEGER DEFAULT 1,
                is_muted INTEGER DEFAULT 0,
                PRIMARY KEY (game_id, user_id),
                FOREIGN KEY (game_id) REFERENCES game_rooms(room_id)
            )
        ''')
        
        # Таблица голосов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                game_id INTEGER,
                voter_id INTEGER,
                voted_id INTEGER,
                phase TEXT,
                PRIMARY KEY (game_id, voter_id, phase),
                FOREIGN KEY (game_id) REFERENCES game_rooms(room_id)
            )
        ''')
        
        # Таблица логов событий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                event_type TEXT,
                user_id INTEGER,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES game_rooms(room_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_player(self, user_id):
        """Получить информацию об игроке"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def add_player(self, user_id, username, first_name):
        """Добавить нового игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO players (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
    
    def create_game_room(self, creator_id, game_code):
        """Создать новую игровую комнату"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO game_rooms (creator_id, game_code, status)
            VALUES (?, ?, 'waiting')
        ''', (creator_id, game_code))
        conn.commit()
        game_id = cursor.lastrowid
        conn.close()
        return game_id
    
    def add_player_to_game(self, game_id, user_id):
        """Добавить игрока в игру"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO game_players (game_id, user_id, role)
                VALUES (?, ?, NULL)
            ''', (game_id, user_id))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
    
    def get_game_players(self, game_id):
        """Получить всех игроков в игре"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, role, is_alive FROM game_players 
            WHERE game_id = ?
        ''', (game_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def assign_roles(self, game_id, roles_dict):
        """Распределить роли игрокам"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for user_id, role in roles_dict.items():
            cursor.execute('''
                UPDATE game_players SET role = ? 
                WHERE game_id = ? AND user_id = ?
            ''', (role, game_id, user_id))
        conn.commit()
        conn.close()
    
    def update_game_status(self, game_id, status, phase=None):
        """Обновить статус игры"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if phase:
            cursor.execute('''
                UPDATE game_rooms SET status = ?, phase = ?, started_at = CURRENT_TIMESTAMP
                WHERE room_id = ?
            ''', (status, phase, game_id))
        else:
            cursor.execute('''
                UPDATE game_rooms SET status = ?
                WHERE room_id = ?
            ''', (status, game_id))
        conn.commit()
        conn.close()
    
    def get_game_by_code(self, game_code):
        """Получить игру по коду"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT room_id, creator_id, status, phase FROM game_rooms WHERE game_code = ?', (game_code,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def add_vote(self, game_id, voter_id, voted_id, phase):
        """Добавить голос"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO votes (game_id, voter_id, voted_id, phase)
            VALUES (?, ?, ?, ?)
        ''', (game_id, voter_id, voted_id, phase))
        conn.commit()
        conn.close()
    
    def get_votes(self, game_id, phase):
        """Получить голоса за фазу"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT voted_id, COUNT(*) as count FROM votes
            WHERE game_id = ? AND phase = ?
            GROUP BY voted_id
            ORDER BY count DESC
        ''', (game_id, phase))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def set_player_alive(self, game_id, user_id, alive):
        """Установить статус жизни игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE game_players SET is_alive = ?
            WHERE game_id = ? AND user_id = ?
        ''', (alive, game_id, user_id))
        conn.commit()
        conn.close()
    
    def update_player_stats(self, user_id, role, win):
        """Обновить статистику игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if win:
            cursor.execute('''
                UPDATE players SET games_played = games_played + 1, wins = wins + 1
                WHERE user_id = ?
            ''', (user_id,))
        else:
            cursor.execute('''
                UPDATE players SET games_played = games_played + 1, losses = losses + 1
                WHERE user_id = ?
            ''', (user_id,))
        
        role_field = f"{role}_games"
        cursor.execute(f'''
            UPDATE players SET {role_field} = {role_field} + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_player_stats(self, user_id):
        """Получить статистику игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT games_played, wins, losses, mafia_games, doctor_games, commissar_games, civilian_games
            FROM players WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result

# Создать экземпляр базы данных
db = Database()