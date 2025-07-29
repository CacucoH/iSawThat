import os
from telethon import TelegramClient, events
from telethon.events.newmessage import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User 

from events.user_interaction.gui_settings import main_menu_buttons
from db.operations import add_msg, get_user_settings
from db.schema import Message


async def handle_new_message(event: events.NewMessage.Event):
    message: Message = event.message
    user_id = message.sender_id

    # In case bot is deactivated
    settings = await get_user_settings()
    if settings.bot_active is False:
        return

    # Skip msg if there is no sender or if the sender is a bot
    user: User = message.sender
    if not user or user.bot:
        return

    # Get minimal userinfo
    sender_id = str(message.sender_id)
    if user:
        sender_id = user.username

    await add_msg(
        tg_msg_id=message.id,
        chat_id=message.chat_id,
        sender_id=sender_id,
        content=message.text or "<No text content>"
    )
    
    print(f"New message from user ID: {user_id} {message.text}")


async def handle_start_message(event: NewMessage.Event, edit: bool = False):
    if edit:
        await event.edit("Выберете действие:", buttons=await main_menu_buttons())
        return
    
    await event.reply("Выберете действие:", buttons=await main_menu_buttons())