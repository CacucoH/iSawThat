import os
import logging
from telethon import events
from telethon.tl.types import User

from db.schema import Message
from db.operations import get_deleted_messages, get_user_settings
from logic.clients import bot, userbot
# from logic.logic import owner_only

MAX_MESSAGE_LEN = int(os.getenv('MAX_MESSAGE_LEN', 4096))


async def handle_message_deleted(event: events.MessageDeleted.Event):
    settings = await get_user_settings()
    msg_buffer = ""
    # track_users = await get_victims_list()

    deleted_messages_ids = event.deleted_ids
    logging.info(f"Messages with IDs {deleted_messages_ids} were deleted")
    messages = await get_deleted_messages(deleted_messages_ids)
    current_len = 0 # message length counter

    for iter in range(0, len(messages)):
        message: Message = messages[iter]

        # user = next((user for user in track_users if user.user_id == message.sender_id), None)
        user = await userbot.get_entity(int(message.sender_id))
        full_name = user.first_name + (' ' + user.last_name if user.last_name else '')

        if message.chat_id == message.sender_id:
            location = "личке"
        else:
            chat_info = await userbot.get_entity(int(message.chat_id))
            if isinstance(chat_info, User):
                location = f"чате {chat_info.first_name} (@{chat_info.username})"
            else:
                location = f"чате {chat_info.title} (@{chat_info.username})"
        
        # Check if text present
        if not message:
            continue
        
        msg = f"🚨 **{full_name if user else 'Unknown User'}** ({user.username}) удалил сообщение в **{location}**: {message.content} от {message.date}\n"
        current_len += len(msg)
        
        if current_len > MAX_MESSAGE_LEN:
            await bot.send_message(int(settings.user_id), msg_buffer)
            msg_buffer = "" # Flush buffer
            current_len = len(msg) # And assign new len value
        
        msg_buffer += msg
        if iter == len(messages) - 1:
            await bot.send_message(int(settings.user_id), msg_buffer)
        
        if message.attachment_location:
            await bot.send_file(int(settings.user_id), file=message.attachment_location, caption="Удалённый файл:")