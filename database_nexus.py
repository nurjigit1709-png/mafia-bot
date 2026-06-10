import sqlite3
from datetime import datetime
from config_nexus import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 5000,
                reputation INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_salary_at TIMESTAMP,
                is_banned INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                balance INTEGER DEFAULT 0,
                land_used INTEGER DEFAULT 0,
                workers_count INTEGER DEFAULT 0,
                income_per_hour INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                salary_per_day INTEGER NOT NULL,
                contract_days INTEGER NOT NULL,
                required_workers INTEGER NOT NULL,
                hired_workers INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                salary_per_day INTEGER NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS land (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                size_m2 INTEGER NOT NULL,
                price_bought INTEGER,
                is_for_sale INTEGER DEFAULT 0,
                sale_price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                gold INTEGER DEFAULT 0,
                silver INTEGER DEFAULT 0,
                ore INTEGER DEFAULT 0,
                oil INTEGER DEFAULT 0,
                details INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                resource_type TEXT,
                quantity INTEGER DEFAULT 1,
                price_per_unit INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users(id),
                FOREIGN KEY (to_user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, telegram_id, username, full_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (telegram_id, username, full_name, balance) VALUES (?, ?, ?, 5000)', (telegram_id, username, full_name))
            user_id = cursor.lastrowid
            cursor.execute('INSERT INTO resources (user_id) VALUES (?)', (user_id,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
    
    def get_user(self, telegram_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_balance(self, telegram_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET balance = balance + ? WHERE telegram_id = ?', (amount, telegram_id))
        conn.commit()
        conn.close()
    
    def set_balance(self, telegram_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET balance = ? WHERE telegram_id = ?', (amount, telegram_id))
        conn.commit()
        conn.close()
    
    def get_resources(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resources WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def add_resource(self, user_id, resource_type, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE resources SET {resource_type} = {resource_type} + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()
    
    def get_top_users(self, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT telegram_id, username, balance, level FROM users WHERE is_banned = 0 ORDER BY balance DESC LIMIT ?', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def create_company(self, owner_id, name, company_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO companies (owner_id, name, type) VALUES (?, ?, ?)', (owner_id, name, company_type))
        conn.commit()
        company_id = cursor.lastrowid
        conn.close()
        return company_id
    
    def get_user_companies(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM companies WHERE owner_id = ?', (user_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_total_land(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(size_m2) as total FROM land WHERE owner_id = ? AND is_for_sale = 0', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result['total'] or 0
    
    def buy_land(self, user_id, size_m2, price):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO land (owner_id, size_m2, price_bought) VALUES (?, ?, ?)', (user_id, size_m2, price))
        conn.commit()
        conn.close()
    
    def add_transaction(self, from_user_id, to_user_id, trans_type, amount, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO transactions (from_user_id, to_user_id, type, amount, description) VALUES (?, ?, ?, ?, ?)', (from_user_id, to_user_id, trans_type, amount, description))
        conn.commit()
        conn.close()

db = Database()