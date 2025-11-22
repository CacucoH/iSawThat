import logging
import os
from telethon import events
from telethon.events.newmessage import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import PeerUser, PeerChannel

from db.schema import UserSettings
from events.user_interaction.states import States
from events.user_interaction.gui_settings import main_menu_buttons
from logic.logic import get_user_info, owner_only
from logic.clients import bot
from db.operations import add_msg, get_user_settings, set_user_state, update_userlist, search_user_by_id
from db.schema import Message


async def handle_new_message(event: events.NewMessage.Event):
    message: Message = event.message
    user_id = message.sender_id
    settings: UserSettings = await get_user_settings()

    # In case bot is deactivated
    if not settings.bot_active:
        return
    
    # Dont record messages from UI bot
    if str(user_id) == settings.bot_id:
        return

    if not isinstance(message.peer_id, PeerChannel):
        if message.sender and message.sender.bot:
            return

    # Check if the message is in the pending list update state
    if States(settings.state) == States.PENDING_LIST_UPDATE \
        and str(user_id) == str(settings.user_id):
        if message.text:
            usernames = message.text.replace(' ', '').split(',')
            users_info = await get_user_info(event.client, usernames)
            await update_userlist(users_info)
            await event.delete()
            # await event.respond("✅ Список обновлён!")
            await set_user_state(States.LIST_UPDATED)
            return

    # Skip messages if PM filtration is enabled and the message is not from a private chat
    if not event.is_private and settings.pm_filter:
        return

    # Get minimal userinfo and filter
    sender_id = str(message.sender_id)
    
    # Apply blacklist filtering
    if await search_user_by_id(sender_id) and not settings.is_whitelist_mode:
        return
    # Apply whitelist filtering
    elif not await search_user_by_id(sender_id) and settings.is_whitelist_mode:
        return

    await add_msg(
        tg_msg_id=message.id,
        chat_id=message.chat_id,
        sender_id=sender_id,
        content=message.text or "<No text content>"
    )
    
    logging.info(f"New message from user ID: {user_id} {message.text}")


@owner_only
async def handle_start_message(event: NewMessage.Event, edit: bool = False, message: str | None = None):
    """Handles the /start command and displays the main menu."""
    # settings = await get_user_settings()
    # sender = event.sender_id
    
    # if str(sender) != settings.user_id:
    #     GOODBYE_MSG = os.getenv("REPLY_UNKNOWN_USER", "Not authorized")
    #     logging.warning(f"ATTENTION! User {sender} has tried to gain access to bot. aborted")
    #     await bot.send_message(sender, GOODBYE_MSG)
    #     return

    await set_user_state(States.DEFAULT)
    if not message:
        message = "Давай настраивай, че как не свой:"

    if edit:
        await event.edit(message, buttons=await main_menu_buttons())
        return

    await event.reply(message, buttons=await main_menu_buttons())