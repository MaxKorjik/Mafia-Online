from email import header
from webbrowser import get
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import json
from database import get_db
from models import User, Messages, Room
from typing import Dict, List
from schemas import Token
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from auth import authenticate_user
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
        user = authenticate_user(db, email)
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
                        await handler(websocket=websocket, payload=payload, room_id=room_id, db=db)
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
async def handle_chat(websocket, payload,room_id, db : Session = Depends(get_db)):
    username = payload.get("username")
    message = payload.get("message")

    
    room = active_rooms.get(room_id)
    
    if not room:
        await websocket.send_json({
            "type": "error",
            "message": "Кімната не знайдена"
        })
        return

    # Получаем Player по username
    player = room.players.get(username)
    if not player:
        await websocket.send_json({
            "type": "error",
            "message": "Гравець не знайдений"
        })
        return


    # Рассылаем в комнату
    await room.broadcast(json.dumps({
        "type": "chat",
        "username": username,
        "message": message
    }))
    
    # Сохраняем в базу
    new_message = Messages(
        message=message,
        user_id=player.id,
        room_id=room.room_id
    )
    db.add(new_message)
    db.commit()
    
    
@register_handler("start_game")
async def handler_name(websocket, payload, room_id, **kwargs):
    # # должна назначить роли игроков, обозначить раунд...
    # payload = {
    #     "username" : str
    # }
    
    room = active_rooms.get(room_id)
    
    if not room:
        await websocket.send_json({
            "type": "error",
            "message": "Кімната не знайдена"
        })
        return
    
    username = payload["username"]
    
    if room.owner != username:
        await websocket.send_json({
            "type": "error",
            "message": "Кімната не знайдена"
        })
        return

    if len(room.players) < 6:
        await websocket.send_json({
            "type": "error",
            "message": "Для початку гри потрібно щонайменше 6 гравців"
        })
        return
    
    if room.phase != "waiting":
        await websocket.send_json({
            "type": "error",
            "message": "Гра вже розпочата"
        })
        return
    
    room.phase = "day"
    room.assign_roles()
    
    for player in room.players.values():
        await player.websocket.send_json({
            "type": "role_assigned",
            "role": player.role
        })

    await room.broadcast(json.dumps({
        "type": "game_started",
        "message": "Гру розпочато!"
    }))