import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
try:
    SECURE_USER_ID = int(os.getenv('MY_CHAT_ID', '0'))
except ValueError:
    SECURE_USER_ID = 0

CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CONFIG_FILE = 'config.json'
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
PROCESSED_FILE = 'processed.json'
