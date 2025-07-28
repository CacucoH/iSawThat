import os
from telethon import TelegramClient, events
from telethon.tl.patched import Message
from telethon.tl.types import User 

from db.operations import AsyncSessionLocal
from db.schema import Message
from datetime import datetime


async def handle_new_message(event: events.NewMessage.Event):
    message: Message = event.message
    user_id = message.sender_id

    if not event.is_private:
        return

    print(f"New message from user ID: {user_id} {message.text}")
    async with AsyncSessionLocal() as session:
        # Get user info
        # user = await session.get(User, user_id)
        
        # is_filtered = await session.get(UserSettings)

        # if not user:
        #     user = User(id=user_id, username=event.sender.username)
        #     session.add(user)
        #     await session.commit()

        user: User = message.sender

        # Check if user is whitelisted
        # if user.status and user.status.is_whitelisted:
            # Save message to database then


        sender_id = str(message.sender_id)
        if user:
            sender_id = user.username

        message = Message(
            telegram_message_id=str(message.id),
            chat_id=str(message.chat_id),
            sender_id=sender_id,
            content=message.raw_text
        )
        session.add(message)
        await session.commit()
        print(f"Message from {sender_id} saved to the database.")

        # else:
        #     print(f"User {user.username} is not in whitelist, message not saved.")
