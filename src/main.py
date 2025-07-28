import os
import logging
import uvloop

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.sessions import StringSession

# Загрузка переменных окружения
load_dotenv('./misc/config/passwd.env')
load_dotenv('./misc/config/settings.env')

uvloop.install()

# Настройка логов
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] - %(asctime)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    filename=f"./misc/logs/log.log",
    filemode="w"
)

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
session_name = os.getenv('APP_NAME')

client = TelegramClient('./misc/session/' + session_name, api_id, api_hash)


@client.on(events.MessageDeleted)
async def handle_message_deleted(event: events.messagedeleted.MessageDeleted.Event):
    """
    Handles the MessageDeleted event.
    """
    # event.message_ids contains a list of IDs of the deleted messages
    deleted_message_ids = event.deleted_ids
    if len(deleted_message_ids) > 1:
        print('several')

    print(f"Messages with IDs {deleted_message_ids} were deleted")

    # event.channel_id will be available for channels and supergroups
    if event.channel_id:
        print(f"Deleted in channel/supergroup ID: {event.channel_id}")
    else:
        print("Deleted in a private chat or small group (channel ID not available).")

async def main():
    await client.start()
    print("Client started. Listening for deleted messages...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())