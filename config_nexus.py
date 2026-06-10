import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8703620753:AAFDY8FAAHFaRdTESaA36QNAv8S9m3bAdGM")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database
DATABASE_PATH = "nexus_economy.db"

# Economy Settings
STARTING_BALANCE = 5000
STARTING_REPUTATION = 0
STARTING_LEVEL = 1

SALARY_COOLDOWN = 86400
COLLECT_COOLDOWN = 3600

EARLY_LEAVE_PENALTY = 0.30

BUSINESS_TYPES = {
    "shop": {"name": "🏪 Маленький магазин", "land_required": 100, "startup_cost": 50000, "min_workers": 1, "income_per_hour": 2000},
    "coffee": {"name": "☕ Кофейня", "land_required": 150, "startup_cost": 100000, "min_workers": 2, "income_per_hour": 5000},
    "ore_mine": {"name": "⛏ Шахта", "land_required": 500, "startup_cost": 500000, "min_workers": 5, "resource_type": "ore"},
    "silver_mine": {"name": "🥈 Серебряная шахта", "land_required": 1000, "startup_cost": 2500000, "min_workers": 10, "resource_type": "silver"},
    "gold_mine": {"name": "🥇 Золотая шахта", "land_required": 2000, "startup_cost": 5000000, "min_workers": 15, "resource_type": "gold"},
}

LAND_PRICES = {100: 20000, 500: 90000, 1000: 170000, 5000: 800000}

RESOURCES = {"gold": "🥇 Золото", "silver": "🥈 Серебро", "ore": "⛏ Руда", "oil": "🛢 Нефть", "details": "⚙ Детали"}