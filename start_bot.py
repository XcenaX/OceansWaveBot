from Bot import Bot
from pathlib import Path

#BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = ""

TELEGRAM = {
    'bot_token': '1895297659:AAFdRK2iPvGAQeOCB8auCqOshuE3VKomenQ',
    'channel_name': 'oceanswavenews',
    "BASE_DIR": BASE_DIR,
}

TELEGRAM_BOT = Bot(TELEGRAM)
while True:
    try:
        TELEGRAM_BOT.start_bot()
    except Exception as e:
        print(e)
        pass