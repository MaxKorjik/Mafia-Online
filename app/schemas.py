from pydantic import BaseModel
from typing import List 

class UserBase(BaseModel):
    id: int 
    username: str 

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str 
    password: str 
    email: str 

class UserResponse(BaseModel):
    id: int 
    username: str 
    email: str 
    friends: List[int] = []

class UserLogin(UserCreate):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatMessage(BaseModel):
    message: str 

class AddFriend(BaseModel):
    friend_id: int