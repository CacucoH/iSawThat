import os
from telethon import TelegramClient, events
from sqlalchemy.future import select
from telethon.tl.types import User
from datetime import datetime

from db.operations import AsyncSessionLocal
from db.schema import Message


async def handle_message_deleted(event: events.MessageDeleted.Event):
    client: TelegramClient = event.client
    deleted_message_ids = event.deleted_ids
    print(f"Messages with IDs {deleted_message_ids} were deleted")
    async with AsyncSessionLocal() as session:
        for message_id in deleted_message_ids:
            # Получаем сообщение по ID
            message = await session.execute(
                select(Message).filter(Message.telegram_message_id == str(message_id))
            )
            message = message.scalar_one_or_none()

            if message:
                # Send data to saved messages
                await client.send_message('me', f"{message.sender_id} удалил сообщение в {message.chat_id}: {message.content}")