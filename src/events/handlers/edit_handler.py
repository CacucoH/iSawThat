import os
import logging
from telethon import events
from telethon.tl.types import User, Channel

from db.operations import get_edited_message, get_user_settings, update_msg
from logic.clients import bot, userbot
from logic.helper_funcs import message_sanitize

MAX_MESSAGE_LEN = int(os.getenv('MAX_MESSAGE_LEN', 4096))


async def handle_message_edited(event: events.MessageEdited.Event):
    # Get necessary info
    settings = await get_user_settings()
    chat_id = str(event.chat_id)
    edited_msg_id = str(event._message_id)
    new_content = event.message.message
    old_message = await get_edited_message(edited_msg_id, chat_id)
    
    if not old_message:
        return
    
    if message_sanitize(old_message.content) == message_sanitize(new_content):
        return

    logging.info(f"Message with ID {edited_msg_id} were edited")
    user = await userbot.get_entity(int(old_message.sender_id))
    
    # Ignore messages from channels
    if isinstance(user, Channel):
        return

    full_name = user.first_name + (' ' + user.last_name if user.last_name else '')

    if old_message.chat_id == old_message.sender_id:
        location = "личке"
    else:
        chat_info = await userbot.get_entity(int(old_message.chat_id))
        if isinstance(chat_info, User):
            location = f"чате {chat_info.first_name} (@{chat_info.username})"
        else:
            location = f"чате {chat_info.title} (@{chat_info.username})"
    
    msg = f"⚠️ **{full_name if user else 'Unknown User'}** (@{user.username}) отредачил сообщентие в **{location}**: __{old_message.content} => {new_content}__; {old_message.date}\n"
    await bot.send_message(int(settings.user_id), msg)

    if old_message.attachment_location:
        await bot.send_file(int(settings.user_id), file=old_message.attachment_location, caption="Удалённый файл:")
        

    # Update message in the database
    await update_msg(edited_msg_id, chat_id, old_message.sender_id, new_content)