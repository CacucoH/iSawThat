import os
import logging

from dotenv import load_dotenv
from telethon import events

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


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(asctime)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
    # filename=log_file,
    # filemode="w" if log_file else None
)


userbot.add_event_handler(handle_new_message, events.NewMessage())
userbot.add_event_handler(handle_message_deleted, events.MessageDeleted())
userbot.add_event_handler(handle_message_edited, events.MessageEdited())

bot.add_event_handler(handle_start_message, events.NewMessage(pattern='/start'))
bot.add_event_handler(callbacks_handler, events.CallbackQuery())


async def main():
    logging.info("Starting app...")

    logging.info("[+] Starting bots")
    await bot.start(bot_token=os.getenv('BOT_TOKEN'))  # Запускаем обычного бота
    await userbot.start()  # Запускаем Userbot

    logging.info("[+] Initializing db")
    await init_db(str(userbot._self_id), str(bot._self_id))

    logging.info("Client started. Listening for deleted messages")
    # await bot.send_message(userbot._self_id, '✅ Бот успешно запущен')
    await asyncio.gather(
        bot.run_until_disconnected(),       # Запускаем обычного бота до его отключения
        userbot.run_until_disconnected(),    # Запускаем userbot до его отключения
        start_message_deleter_service()
    )
    logging.info("Clients disconnected. Exiting...")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())