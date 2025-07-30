"""
## Database operations for the iSawThat bot

This module provides functions to initialize the database and manage user settings

=== IMPORTANT ===
This DB is designed for only one host user

"""
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.schema import Base, UserSettings, Users, Message
from events.user_interaction.states import States


# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/test_db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db(me):
    logging.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create default settings if not set yet
    if not await get_user_settings():
        await default_user_settings(str(me.id))

    logging.info("Database initialized successfully.")


async def default_user_settings(self_id: str):
    """Creates default user settings if they do not exist"""
    async with AsyncSessionLocal() as session:
        user_settings = UserSettings(user_id=self_id, is_whitelist_mode=True)
        session.add(user_settings)
        await session.commit()
        logging.info("Default user settings created.")


async def get_user_settings():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings = result.scalar_one_or_none()
        return user_settings


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


async def update_whitelist_mode():
    """Updates whitelist mode"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings = result.scalar_one_or_none()

        user_settings.is_whitelist_mode = not user_settings.is_whitelist_mode
        await session.commit()


async def activate_bot():
    """Activates or deactivates the bot"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSettings))
        user_settings = result.scalar_one_or_none()

        # Switch bot state
        user_settings.bot_active = not user_settings.bot_active
        await session.commit()
        logging.info(f"Bot {'activated' if user_settings.bot_active else 'deactivated'}")


async def add_msg(tg_msg_id, chat_id, sender_id, content):
    async with AsyncSessionLocal() as session:
        message = Message(
            telegram_message_id=str(tg_msg_id),
            chat_id=str(chat_id),
            sender_id=sender_id,
            content=content
        )
        session.add(message)
        await session.commit()
        logging.info(f"Message from {sender_id} saved to the database.")


async def get_deleted_messages(deleted_message_ids):
    async with AsyncSessionLocal() as session:
        messages = []
        for message_id in deleted_message_ids:
            # Get message by ID
            message = await session.execute(
                select(Message).filter(Message.telegram_message_id == str(message_id))
            )
            message = message.scalar_one_or_none()
            
            # If message not found, log and continue
            if not message:
                logging.warning(f"Message with ID {message_id} not found in the database")
                continue

            messages.append(
                {
                    "id": message.id,
                    "telegram_message_id": message.telegram_message_id,
                    "chat_id": message.chat_id,
                    "sender_id": message.sender_id,
                    "content": message.content,
                    "date": message.date
                }
            )
        return messages


async def set_user_state(state: States):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserSettings))
        settings = res.scalar_one_or_none()

        settings.state = state.value
        await session.commit()


async def get_user_state() -> States:
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserSettings))
        settings = res.scalar_one_or_none()

        if settings and settings.state:
            return States(settings.state)
        return States.DEFAULT
    

async def toggle_pm_filter():
    """Toggles PM filter setting"""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserSettings))
        settings = res.scalar_one_or_none()

        settings.pm_filter = not settings.pm_filter
        await session.commit()
        logging.info(f"PM filter {'enabled' if settings.pm_filter else 'disabled'}")


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


async def search_user_by_id(user_id: str):
    """Searches for a user by their ID"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Users).filter(Users.user_id == user_id))
        user = result.scalar_one_or_none()
        return user