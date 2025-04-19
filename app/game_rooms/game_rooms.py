from email import header
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import json
from database import get_db
from models import User, Messages, Room
from typing import Dict, List
from schemas import Token
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from auth import get_user_by_email
from config import SECRET_KEY, ALGORITHM
import random, string
from game_models import GameRoom, Player
from room_storage import active_rooms

router = APIRouter(prefix="/ws", tags=["Rooms"])

message_handlers = {}

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def register_handler(message_type):
    def decorator(func):
        print(f"Registered handler: {message_type} → {func.__name__}")
        message_handlers[message_type] = func 
        return func
    return decorator

async def get_user_by_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = get_user_by_email(db, email)
        return user
    except JWTError:
        raise credentials_exception

def generate_guest_name():
    suffix = ''.join(random.choices(string.digits, k=8))
    return f"Guest{suffix}"


@router.websocket('/room/{room_id}')
async def websocket_endpoint(websocket: WebSocket, room_id: int, db : Session = Depends(get_db)):
    
    await websocket.accept()
    try:
        room = active_rooms[room_id]
    except KeyError:
        await websocket.send_json({"type": "error", "message": "Room not found"})
        await websocket.close()
        return
        
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return
    
    user = await get_user_by_token(token=token, db=db)
    username = None
    if user:
        username = user.username
        room.add_player(name=username, websocket=websocket)
        await room.broadcast(f"Користувач {username} під'єднався")
    else:
        username = generate_guest_name()
        room.add_player(name=username, websocket=websocket)
        await room.broadcast(f"Користувач {username} під'єднався")
        
    while True:
        try:
            data = await websocket.receive_text()
            
            if data:
                try:
                    message = json.loads(data)
                    msg_type = message.get("type")
                    payload = message.get("payload", {})
                    
                    handler = message_handlers.get(msg_type)
                    if handler:
                        await handler(websocket, payload)
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}"
                        })
                        
                except (ValueError, KeyError):
                    await websocket.send_text("Невірний формат повідомлення.")
                    continue
                        
            
        except WebSocketDisconnect:
            if user:
                room.remove_player(name=user.username)
                await room.broadcast(f"Користувач {user.username} від'єднався")
            else:
                room.remove_player(name=username)
        
    
@register_handler("chat")
async def handle_chat(ws, payload):
    pass 