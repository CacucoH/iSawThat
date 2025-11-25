import os
import logging

from dotenv import load_dotenv
from telethon import events
from logic.logging_conf import setup_logging

setup_logging() # Initialize logging before loading other modules

from db.deleter import start_message_deleter_service
from events.handlers.message_handler import handle_new_message, handle_start_message
from events.handlers.delete_handler import handle_message_deleted
from events.handlers.edit_handler import handle_message_edited
from events.user_interaction.callback_handler import callbacks_handler
from db.operations import init_db
from logic.clients import userbot, bot

# Загрузка переменных окружения
# в docker не нужно
load_dotenv('./misc/config/settings')

userbot.add_event_handler(handle_new_message, events.NewMessage())
userbot.add_event_handler(handle_message_deleted, events.MessageDeleted())
userbot.add_event_handler(handle_message_edited, events.MessageEdited())

bot.add_event_handler(handle_start_message, events.NewMessage(pattern='/start'))
bot.add_event_handler(callbacks_handler, events.CallbackQuery())


async def main():
    logger = logging.getLogger(__name__)
    logger.info(">> Starting app...")

    logger.info("[+] Starting bots")
    await bot.start(bot_token=os.getenv('BOT_TOKEN'))  # Запускаем обычного бота
    await userbot.start()  # Запускаем Userbot

    logger.info("[+] Initializing db")
    await init_db(str(userbot._self_id), str(bot._self_id))

    logger.info("[i] Client started. Listening")
    # await bot.send_message(userbot._self_id, '✅ Бот успешно запущен')
    await asyncio.gather(
        bot.run_until_disconnected(),       # Запускаем обычного бота до его отключения
        userbot.run_until_disconnected(),    # Запускаем userbot до его отключения
        start_message_deleter_service()
    )
    logger.info(">> Clients disconnected. Exiting...")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())