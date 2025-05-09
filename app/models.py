from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    friends = Column(JSON, default = list)
    created_at = Column(DateTime, default=datetime.now)
    matches = Column(Integer, default=0)
    survivor_matches = Column(Integer, default=0)
    mafia_matches = Column(Integer, default=0)
    is_host = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


class Messages(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    user_id = Column(Integer, ForeignKey("user.id"))
    room_id = Column(Integer, ForeignKey("room.id"))
    room = relationship("Room")
    user = relationship("User")
    writing_time = Column(DateTime, default=datetime.now)


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    password = Column(String, nullable=True)
    owner = Column(Integer, ForeignKey("user.id"), nullable=True)
    players_number = Column(Integer, default=0)
    min_players_number = Column(Integer, default=6)
    max_players_number = Column(Integer, default=6)
    is_private = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.players_number = 0  # Ініціалізуємо кількість гравців як 0
