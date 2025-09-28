import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env в окружение процесса
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")