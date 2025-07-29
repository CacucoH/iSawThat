import os
import logging
import uvloop

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.sessions import StringSession

from events.handlers.message_handler import handle_new_message, handle_start_message
from events.handlers.delete_handler import handle_message_deleted
from events.user_interaction.callback_handler import callbacks_handler
from db.operations import init_db


# Загрузка переменных окружения
load_dotenv('./misc/config/passwd.env')
load_dotenv('./misc/config/settings.env')

uvloop.install()

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(asctime)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    # filename=f"./misc/logs/log.log",
    # filemode="w"
)


### INITIALIZE USERBOT AND BOT ###
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
session_name = os.getenv('APP_NAME')

userbot = TelegramClient('./misc/session/' + session_name, api_id, api_hash) # Used for message tracking
bot = TelegramClient('./misc/session/' + session_name + "_bot", api_id, api_hash) # Used for settings & callbacks

userbot.add_event_handler(handle_new_message, events.NewMessage())
userbot.add_event_handler(handle_message_deleted, events.MessageDeleted())

bot.add_event_handler(handle_start_message, events.NewMessage(pattern='/start'))
bot.add_event_handler(callbacks_handler, events.CallbackQuery())
### END OF INITIALIZATION ###


async def main():
    print(os.getenv('BOT_TOKEN'))
    await bot.start(bot_token=os.getenv('BOT_TOKEN'))  # Запускаем обычного бота
    await userbot.start(),  # Запускаем Userbot
    
    # Firstly initialize db
    me = await userbot.get_me()
    await init_db(me)

    logging.info("Client started. Listening for deleted messages...")
    
    await asyncio.gather(
        bot.run_until_disconnected(),       # Запускаем обычного бота до его отключения
        userbot.run_until_disconnected()    # Запускаем userbot до его отключения
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())