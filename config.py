import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8703620753:AAFDY8FAAHFaRdTESaA36QNAv8S9m3bAdGM")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Game Configuration
MIN_PLAYERS = 4
MAX_PLAYERS = 20
NIGHT_DURATION = 60  # seconds
DAY_DURATION = 120   # seconds

# Game Roles
ROLES = {
    "mafia": "🔴 Мафия",
    "doctor": "💊 Доктор",
    "commissar": "🔍 Комиссар",
    "civilian": "👨 Мирный житель"
}

# Database
DATABASE_PATH = "mafia_bot.db"