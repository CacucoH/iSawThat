import os
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv('./misc/config/bot.env')

### INITIALIZE USERBOT AND BOT ###
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
session_name = os.getenv('APP_NAME')

userbot = TelegramClient('./misc/session/' + session_name, api_id, api_hash) # Used for message tracking
bot = TelegramClient('./misc/session/' + session_name + "_bot", api_id, api_hash) # Used for settings & callbacks

logger.info("[+] Clients initialized")
### END OF INITIALIZATION ###
