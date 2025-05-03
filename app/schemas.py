from pydantic import BaseModel
from typing import List, Optional, Union

class UserBase(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    friends: List[int] = []
    matches: int = 0
    survivor_matches: int = 0
    mafia_matches: int = 0
    is_host: bool = False
    is_admin: bool = False

    class Config:
        from_attributes = True

class UserLogin(UserCreate):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatMessage(BaseModel):
    message: str

class AddFriend(BaseModel):
    friend_id: int

class RoomBase(BaseModel):
    name: str
    is_private: bool = False
    min_players_number : int = 6
    max_players_number: int = 6


class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    owner: int
    players_number: int = 0
    is_active: bool = True

    class Config:
        from_attributes = True