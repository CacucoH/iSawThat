import os
import logging
from telethon import events

from db.operations import get_edited_message, get_user_settings, update_msg
from db.schema import Message as StoredMessage
from logic.helper_funcs import beautify_logger_name
from logic.clients import bot
from logic.helper_funcs import message_sanitize

logger = logging.getLogger(beautify_logger_name(__name__))
MAX_MESSAGE_LEN = int(os.getenv('MAX_MESSAGE_LEN', 4096))


async def handle_message_edited(event: events.MessageEdited.Event):
    # Get necessary info
    settings = await get_user_settings()
    chat_id = str(event.chat_id)
    edited_msg_id = str(event._message_id)
    new_content = event.message.message
    old_message: StoredMessage = await get_edited_message(edited_msg_id, chat_id)
    
    if not old_message:
        return
    
    if message_sanitize(old_message.content) == message_sanitize(new_content):
        return

    full_name = old_message.sender_name or "Unknown User"
    username = f"@{old_message.sender_username}" if old_message.sender_username else "no username"

    if old_message.chat_id == old_message.sender_id:
        location = "личке"
    else:
        chat_title = old_message.chat_title or "Unknown Chat"
        location = f"чате {chat_title}" + (f" (@{old_message.chat_username})" if old_message.chat_username else "")

    old_message_text = old_message.content if old_message.content else "<No text content>"
    msg = f"⚠️ **{full_name}** ({username}) отредачил сообщентие в **{location}**:\n__{old_message_text} => {new_content}__\n\n{old_message.date}\n"
    await bot.send_message(int(settings.user_id), msg)
    logger.info(f"Message with ID {edited_msg_id} were edited")

    if old_message.attachment_location:
        await bot.send_file(int(settings.user_id), file=old_message.attachment_location, caption="Удалённый файл:")
        

    # Update message in the database
    await update_msg(edited_msg_id, chat_id, old_message.sender_id, new_content)