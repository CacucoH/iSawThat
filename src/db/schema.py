import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from dateutil.relativedelta import relativedelta

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

    user_id = Column(String, primary_key=True, index=True)  # Root user's id
    bot_id = Column(String, nullable=False)                 # Root bot's id
    is_whitelist_mode = Column(Boolean, default=True)       # Defines whether white or blacklist mode enabled for this session
    bot_active = Column(Boolean, default=True)              # Defines whether bot is active or not
    state = Column(String, default="DEFAULT")               # Current state of the bot (e.g., DEFAULT, PENDING_LIST_UPDATE, etc.)
    pm_filter = Column(Boolean, default=False)              # Defines whether PM filtration is enabled or not
    message_deletion_delta = Column(String, default='7')    # Time delta that defines frequency of DB cleaning; Stored as string since there is no relativedelta DT in PG
    message_deletion_delta_id = Column(Integer, default=2)  # ID of timedelta is defined in db.operations module


class Users(Base):
    """
        Represents a list of (white/black)listed from tracking Telegram users
    """
    __tablename__ = 'tg_users'

    user_id = Column(String, primary_key=True, index=True)
    user_full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    username = Column(String, nullable=True)