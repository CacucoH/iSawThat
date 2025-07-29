import os
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.schema import Base, UserSettings, Users, Message


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

        for user_id, user_name_full in userlist:
            new_user = Users(user_id=user_id, user_full_name=user_name_full)
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
        print(f"Message from {sender_id} saved to the database.")

        # else:
        #     print(f"User {user.username} is not in whitelist, message not saved.")