from time import sleep
from Bot import Bot
from pathlib import Path

#BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = ""

TELEGRAM = {
    'bot_token': '1895297659:AAFRKuWeovfOtshIsTNdd8tWDREtDUG8Gwo',
    'channel_name': 'oceanswavenews',
    "BASE_DIR": BASE_DIR,
}

TELEGRAM_BOT = Bot(TELEGRAM)
TELEGRAM_BOT.start_bot()
sleep(9999999999)