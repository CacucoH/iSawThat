from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
import datetime


Base = declarative_base()


class Message(Base):
    """    
        Contains messages from Telegram
    """
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    telegram_message_id = Column(String, nullable=False)
    chat_id = Column(String, nullable=False)
    sender_id = Column(String, nullable=False)
    content = Column(Text)
    date = Column(DateTime, default=(datetime.datetime.now(datetime.timezone.utc)).replace(tzinfo=None))


class UserSettings(Base):
    """
        User settings for the bot
    """
    __tablename__ = 'user_settings'

    user_id = Column(String, primary_key=True, index=True)
    is_whitelist_mode = Column(Boolean, default=True)


class UsersList(Base):
    """
        Represents a list of (white/black)listed from tracking Telegram users
    """
    __tablename__ = 'tg_users'

    user_id = Column(String, primary_key=True, index=True)
