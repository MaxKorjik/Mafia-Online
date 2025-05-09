from pydantic import BaseModel
from typing import List, Optional, Union
from pydantic import validator

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
    min_players_number: int = 6
    max_players_number: int = 6

    @validator('min_players_number')
    def validate_min_players(cls, v):
        if v < 4:
            raise ValueError('Minimum players must be at least 4')
        return v

    @validator('max_players_number')
    def validate_max_players(cls, v, values):
        if 'min_players_number' in values and v < values['min_players_number']:
            raise ValueError('Maximum players must be greater than or equal to minimum players')
        if v > 12:
            raise ValueError('Maximum players cannot exceed 12')
        return v

class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    owner: Optional[int] = None
    players_number: int = 0
    is_active: bool = True

    class Config:
        from_attributes = True