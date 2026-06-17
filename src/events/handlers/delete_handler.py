import os
import logging
from telethon import events

from db.schema import Message
from db.operations import get_deleted_messages, get_user_settings
from logic.helper_funcs import beautify_logger_name
from logic.clients import bot
# from logic.logic import owner_only

logger = logging.getLogger(beautify_logger_name(__name__))
MAX_MESSAGE_LEN = int(os.getenv('MAX_MESSAGE_LEN', 4096))


async def handle_message_deleted(event: events.MessageDeleted.Event):
    settings = await get_user_settings()
    msg_buffer = ""
    # track_users = await get_victims_list()

    deleted_messages_ids = event.deleted_ids
    logger.info(f"Messages with IDs {deleted_messages_ids} were deleted")
    messages = await get_deleted_messages(deleted_messages_ids)
    current_len = 0 # message length counter

    for iter in range(0, len(messages)):
        message: Message = messages[iter]

        full_name = message.sender_name or "Unknown User"
        username = f"@{message.sender_username}" if message.sender_username else "no username"
        text_content = message.content if message.content else "<No text content>"

        if message.chat_id == message.sender_id:
            location = "личке"
        else:
            chat_title = message.chat_title or "Unknown Chat"
            location = f"чате {chat_title}" + (f" (@{message.chat_username})" if message.chat_username else "")

        msg = f"🚨 **{full_name}** ({username}) удалил сообщение в **{location}**: {text_content}\n\nот {message.date}\n"
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