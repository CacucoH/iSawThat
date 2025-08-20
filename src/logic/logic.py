import functools
import os
import logging
from telethon import TelegramClient, events

async def get_user_info(client: TelegramClient, users):
    """Fetches the full user information of the current user."""
    userdata = []
    for user_id in users:
        try:
            user = await client.get_entity(user_id)
            user_full_name = user.first_name + (' ' + user.last_name if user.last_name else '')

            userdata.append({
                "id": str(user.id),
                "full_name": user_full_name,
                "username": user.username
            })
        except Exception as e:
            logging.warning(f"Error fetching user {user_id}: {e}")
    return userdata


def owner_only(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        events = args[0] if args else None
        if not events:
            logging.error("No event provided to owner_only decorator.")
            return
        
        from db.operations import get_user_settings

        settings = await get_user_settings()
        sender = events.sender_id

        if str(sender) != settings.user_id:
            GOODBYE_MSG = os.getenv("REPLY_UNKNOWN_USER", "Not authorized")
            logging.warning(f"ATTENTION! User {sender} tried to access the bot. Aborted.")
            await events.client.send_message(sender, GOODBYE_MSG)
            return

        return await func(*args, **kwargs)
    return wrapper
