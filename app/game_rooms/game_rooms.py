from email import header
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import json
from ..database import get_db
from ..models import User, Messages, Room
from typing import Dict, List
from ..schemas import Token
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import random, string
from .game_models import GameRoom, Player
from .room_storage import active_rooms
from ..config import SECRET_KEY

ALGORITHM = "HS256"

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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.query(User).filter(User.username == username).first()
        return user
    except JWTError:
        raise credentials_exception


def generate_guest_name():
    suffix = ''.join(random.choices(string.digits, k=8))
    return f"Guest{suffix}"


@router.websocket('/room/{room_id}')
async def websocket_endpoint(websocket: WebSocket, room_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        room = active_rooms[room_id]
    except KeyError:
        await websocket.send_json({"type": "error", "message": "Room not found"})
        await websocket.close()
        return

    token = websocket.query_params.get("token")
    username = None

    if token:
        try:
            user = await get_user_by_token(token=token, db=db)
            if user:
                username = user.username
                room.add_player(name=username, websocket=websocket)
                await room.broadcast(json.dumps({"type": "user_joined", "username": username}))
        except Exception:
            # If token validation fails, continue as guest
            pass

    if not username:
        username = generate_guest_name()
        room.add_player(name=username, websocket=websocket)
        await room.broadcast(json.dumps({"type": "user_joined", "username": username}))

    try:
        while True:
            data = await websocket.receive_text()

            if data:
                try:
                    message = json.loads(data)
                    msg_type = message.get("type")
                    payload = message.get("payload", {})

                    handler = message_handlers.get(msg_type)
                    if handler:
                        await handler(websocket, payload, room, username)
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}"
                        })

                except (ValueError, KeyError):
                    await websocket.send_text("Invalid message format.")
                    continue

    except WebSocketDisconnect:
        room.remove_player(name=username)
        await room.broadcast(json.dumps({"type": "user_left", "username": username}))


@register_handler("chat")
async def handle_chat(ws, payload, room, username):
    message = payload.get("message", "")
    if message:
        await room.broadcast(json.dumps({
            "type": "chat_message",
            "username": username,
            "message": message
        }))


@router.post("/create-room")
async def create_game_room(
        room_id: int,
        max_players: int = 6,
        is_private: bool = False
):
    if room_id in active_rooms:
        raise HTTPException(status_code=400, detail="Room with this ID already exists")

    active_rooms[room_id] = GameRoom(
        room_id=room_id,
        max_players=max_players,
        is_private=is_private
    )

    return {"message": "Room created successfully", "room_id": room_id}