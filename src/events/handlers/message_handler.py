import logging
import os
from telethon import events
from telethon.events.newmessage import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import PeerChannel, Channel, User

from db.schema import UserSettings
from events.user_interaction.states import States
from events.user_interaction.gui_settings import main_menu_buttons
from logic.helper_funcs import beautify_logger_name
from logic.logic import get_user_info, owner_only
from logic.clients import bot
from db.operations import (add_msg, get_user_settings, set_user_state,
                           update_userlist, search_user_by_id)
from db.schema import Message


logger = logging.getLogger(beautify_logger_name(__name__))
DEFAULT_FDOWNLOAD_PATH = "./misc/data/files/"


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
    
    # Ignore messages from channels
    if isinstance(message.peer_id, Channel):
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
    user_found: User = await search_user_by_id(sender_id)
    
    # Apply blacklist filtering
    if user_found and not settings.is_whitelist_mode:
        return
    
    # Apply whitelist filtering
    elif not user_found and settings.is_whitelist_mode:
        return
    
    # If media is included - download it
    attachement_path = None
    if message.file:
        attachement_path = await handle_attachement(user_id, message.chat_id, message)

    await add_msg(
        tg_msg_id=message.id,
        chat_id=message.chat_id,
        sender_id=sender_id,
        content=message.text or "<No text content>",
        linked_attachment_location=attachement_path if attachement_path else None
    )
    
    logger.info(f"New message from user ID: {user_id}: \"{message.text}\" {f'with attachment: {attachement_path}' if message.file else ''} saved to the database.")


@owner_only
async def handle_start_message(event: NewMessage.Event, edit: bool = False, message: str | None = None):
    """Handles the /start command and displays the main menu."""
    # settings = await get_user_settings()
    # sender = event.sender_id
    
    # if str(sender) != settings.user_id:
    #     GOODBYE_MSG = os.getenv("REPLY_UNKNOWN_USER", "Not authorized")
    #     logger.warning(f"ATTENTION! User {sender} has tried to gain access to bot. aborted")
    #     await bot.send_message(sender, GOODBYE_MSG)
    #     return

    await set_user_state(States.DEFAULT)
    if not message:
        message = "Давай настраивай, че как не свой:"

    if edit:
        await event.edit(message, buttons=await main_menu_buttons())
        return

    await event.reply(message, buttons=await main_menu_buttons())


async def handle_attachement(user_id: str | int, chat_id: str | int, message: Message) -> str:
    """Downloads media"""
    generic_path = os.getenv("ATTACHEMENTS_DOWNLOAD_PATH", DEFAULT_FDOWNLOAD_PATH)
    targetted_path = os.path.join(generic_path, str(chat_id).replace('-', ''), str(user_id))

    os.makedirs(targetted_path, exist_ok=True)
    media_path = await message.download_media(file=targetted_path)
    # id = await add_attachment(media_path)
    logger.info(f"Attachment from user ID: {user_id}: downloaded to: {media_path}")
    return media_path
