from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    telegram_message_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    sender_id = Column(String, nullable=False)
    content = Column(Text)
    date = Column(DateTime, default=datetime.now(datetime.timezone.utc))


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(String, primary_key=True, index=True)
    retention_days = Column(Integer, nullable=True)