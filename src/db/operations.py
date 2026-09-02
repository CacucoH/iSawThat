"""
## Database operations for the iSawThat bot
This module provides functions to initialize the database and manage user settings

=== IMPORTANT ===
This DB is designed for only one host user

"""
import logging
import os

from dotenv import load_dotenv
from typing import Set
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dateutil.relativedelta import relativedelta
from datetime import datetime

from db.schema import Base, UserSettings, Users, Message
from events.user_interaction.states import States
from logic.helper_funcs import beautify_logger_name


logger = logging.getLogger(beautify_logger_name(__name__))
load_dotenv("./misc/config/settings")

DEVMODE = os.getenv("DEVMODE", "False").strip().lower() == "true"
DATABASE_URL = "postgresql+asyncpg://postgres:your_new_password@localhost/test_db" if DEVMODE else os.getenv("DATABASE_URL")
TIMEDELTA_ARRAY = ['1', '3', '7', '14']

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


### INIT ###
async def init_db(self_id: str, bot_id: str):
    logger.info(">> Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create default settings if not set yet, otherwise keep owner/bot ids in sync
    # with whichever accounts are currently logged in
    settings = await get_user_settings()
    if not settings:
        await default_user_settings(self_id, bot_id)
    elif settings.user_id != self_id or settings.bot_id != bot_id:
        await sync_user_settings_ids(self_id, bot_id)

    logger.info("[+] Database initialized successfully.")


async def sync_user_settings_ids(self_id: str, bot_id: str):
    """Updates the stored owner/bot ids to match the currently logged-in accounts"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings = result.scalar_one_or_none()
        user_settings.user_id = self_id
        user_settings.bot_id = bot_id
        await session.commit()
        logger.info("[+] Synced owner/bot ids with the current session.")


async def default_user_settings(self_id: str, bot_id: str):
    """Creates default user settings if they do not exist"""
    async with AsyncSessionLocal() as session:
        user_settings = UserSettings(user_id=self_id, bot_id=bot_id, is_whitelist_mode=True)
        session.add(user_settings)
        await session.commit()
        logger.info("[+] Default user settings created.")


### SETTERS ###
async def add_msg(tg_msg_id, chat_id, sender_id, content, linked_attachment_location=None,
                   sender_name=None, sender_username=None, chat_title=None, chat_username=None) -> int:
    async with AsyncSessionLocal() as session:
        message = Message(
            telegram_message_id=str(tg_msg_id),
            chat_id=str(chat_id),
            sender_id=sender_id,
            sender_name=sender_name,
            sender_username=sender_username,
            chat_title=chat_title,
            chat_username=chat_username,
            content=content,
            attachment_location = linked_attachment_location
        )
        session.add(message)
        await session.commit()
        logger.debug(f"[+] Message from {sender_id} is saved to the database.")

        return message.id
    

async def activate_bot():
    """Activates or deactivates the bot"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings = result.scalar_one_or_none()

        # Switch bot state
        user_settings.bot_active = not user_settings.bot_active
        await session.commit()
        logger.debug(f"[+] Bot {'activated' if user_settings.bot_active else 'deactivated'}")


async def toggle_pm_filter():
    """Toggles PM filter setting"""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserSettings))
        settings = res.scalar_one_or_none()

        settings.pm_filter = not settings.pm_filter
        await session.commit()
        logger.debug(f"[+] PM filter {'enabled' if settings.pm_filter else 'disabled'}")


async def set_user_state(state: States):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserSettings))
        settings = res.scalar_one_or_none()

        settings.state = state.value
        await session.commit()
    
    
### GETTERS ###
async def search_user_by_id(user_id: str):
    """Searches for a user by their ID"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Users).filter(Users.user_id == user_id))
        user = result.scalar_one_or_none()
        return user


async def get_deleted_messages(deleted_message_ids: list[str] | list[int]):
    deleted_message_ids = map(str, deleted_message_ids)

    async with AsyncSessionLocal() as session:
        messages = []
        for message_id in deleted_message_ids:
            # Get message by ID
            message = await session.execute(
                select(Message).where(
                    (Message.telegram_message_id == message_id)
                )
            )
            message = message.scalar_one_or_none()

            # If message not found, log and continue
            if not message:
                logger.warning(f"[!] Message with ID {message_id} not found in the database")
                continue

            messages.append(message)
        return messages


async def get_edited_message(edited_msg_id: str | int, chat_id: str | int):
    edited_msg_id = str(edited_msg_id)
    chat_id = str(chat_id)

    async with AsyncSessionLocal() as session:
        message = await session.execute(
                select(Message).where(
                    (Message.telegram_message_id == edited_msg_id) 
                        &
                    (Message.chat_id == chat_id)
                )
            )
        message = message.scalar_one_or_none()
    return message


async def get_user_state() -> States:
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserSettings))
        settings = res.scalar_one_or_none()

        if settings and settings.state:
            return States(settings.state)
        return States.DEFAULT


async def get_victims_list():
    """Returns the list of users being tracked"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Users))
        users = result.scalars().all()
        return [
            {
                "user_id": user.user_id,
                "user_full_name": user.user_full_name,
                "username": user.username,
                "phone": user.phone
            }
        for user in users
    ]


async def get_user_settings():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings = result.scalar_one_or_none()
        return user_settings


### UPDATE METHODS ###
async def update_whitelist_mode():
    """Updates whitelist mode"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings = result.scalar_one_or_none()

        user_settings.is_whitelist_mode = not user_settings.is_whitelist_mode
        await session.commit()


async def update_userlist(userlist):
    """Updates userlist"""
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Users))  # Delete all existing users
        await session.commit()

        for user in userlist:
            new_user = Users(
                user_id=user["id"],
                user_full_name=user["full_name"],
                phone=user.get("phone"),
                username=user.get("username")
            )
            session.add(new_user)
        await session.commit()


async def update_msg(tg_msg_id, chat_id, sender_id, new_content):
    async with AsyncSessionLocal() as session:
        r = await session.execute(select(Message).where(
                (Message.telegram_message_id == str(tg_msg_id))
                    &
                (Message.chat_id == str(chat_id))
            )
        )
        message: Message = r.scalar_one_or_none()

        if not message:
            logger.warning(f"[!] Failed to update {sender_id}: message not found in the database.")
            return
        
        message.content = new_content
        await session.commit()
        logger.debug(f"[+] Message from {sender_id} was updated.")


async def update_time_delta(operation: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings: UserSettings = result.scalar_one_or_none()

        current_delta_id = user_settings.message_deletion_delta_id
        total_time_array_len = len(TIMEDELTA_ARRAY)

        match operation:
            case b"increase":
                next_idx = (current_delta_id + 1) % total_time_array_len
            
            case b"decrease":
                next_idx = (current_delta_id - 1 + total_time_array_len) % total_time_array_len
            
            case _:
                next_idx = 0
            
        new_delta = TIMEDELTA_ARRAY[next_idx]
        
        # Update data
        user_settings.message_deletion_delta = new_delta
        user_settings.message_deletion_delta_id = next_idx
        await session.commit()
        
        return new_delta


### DELETE ###
async def delete_messages_by_date(delete_after_date) -> list[Message]:
    """Deletes old messages. Returns list of deleted messages"""
    async with AsyncSessionLocal() as session:
        res = (await session.execute(select(Message).where(
            Message.date <= delete_after_date
        ))).scalars().all()

        await session.execute(delete(Message).where(
            Message.date <= delete_after_date
        ))
        
        logger.debug(f"[+] Deleted {len(res)} old messages from DB")
        
        # Also delete attachments linked to messages
        await delete_old_attachments(res)
        await session.commit()
        return res
    

async def delete_old_attachments(old_messages: list[str]) -> Set[str]:
    """Deletes old attachments. Returns list of deleted attachment paths"""
    deleted_attachments: Set[str] = set()
    for msg in old_messages:
        path = msg.attachment_location
        if path and os.path.exists(path):
            try:
                os.remove(path)
                deleted_attachments.add(path)
                logger.info(f"[+] Deleted attachment: {path}")
            except Exception as e:
                logger.warning(f"[!] Failed to delete attachment {path}: {e}")

    return deleted_attachments