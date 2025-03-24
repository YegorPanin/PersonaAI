from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bot(Base):
    __tablename__ = 'bots'
    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True)
    description = Column(Text)
    created_at = Column(DateTime)

class Story(Base):
    __tablename__ = 'stories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    bot_id = Column(Integer)
    user_message = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime)