from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, database
from app.auth import  get_current_user
from app.game_rooms.game_rooms import router as game_router
from app.auth import router as auth_router
import random, string
models.Base.metadata.create_all(bind=database.engine)
from app.game_rooms.room_storage import active_rooms
from app.game_rooms.game_models import GameRoom
from typing import Optional
from sqlalchemy import delete

app = FastAPI(title="Mafia Game")

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL вашого фронтенду
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router, prefix="/api")
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# WebSocket тестовий ендпоінт
@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket test error: {e}")
        await websocket.close()

@app.get("/")
async def root():
    return {"message": "Welcome to Mafia Game API"}


@app.get("/api/rooms", response_model=list[schemas.RoomResponse])
async def get_active_rooms(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).filter(models.Room.is_active == True).all()
    return rooms


@app.get("/api/rooms/{room_id}", response_model=schemas.RoomResponse)
async def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@app.post("/api/rooms", response_model=schemas.RoomResponse)
async def create_room(
        room: schemas.RoomCreate,
        password: Optional[str] = Query(None),
        current_user: Optional[models.User] = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        print(f"Creating room with data: {room.dict()}")
        print(f"Current user: {current_user}")
        
        if room.is_private and not password: 
            raise HTTPException(status_code=400, detail="Password is required for private rooms")
        
        if current_user is None:
            guestname = ''.join(random.choices(string.digits, k=8))
            owner_id = None
        else:
            owner_id = current_user.id

        print(f"Creating room with owner_id: {owner_id}")

        db_room = models.Room(
            name=room.name,
            password=password,
            owner=owner_id,
            min_players_number=room.min_players_number,
            max_players_number=room.max_players_number,
            is_private=room.is_private,
            is_active=True  # Додаємо це поле
        )
        
        print(f"Created db_room object: {db_room.__dict__}")
        
        db.add(db_room)
        db.commit()
        db.refresh(db_room)

        print(f"Room saved to database with id: {db_room.id}")

        game_room = GameRoom(
            room_id=db_room.id,
            room_name=db_room.name,
            owner_id=owner_id,
            min_players=db_room.min_players_number,
            max_players=db_room.max_players_number,
            is_private=db_room.is_private,
        )
        
        print(f"Created game_room object: {game_room.__dict__}")
        
        active_rooms[db_room.id] = game_room
        return db_room
        
    except Exception as e:
        print(f"Error creating room: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@app.delete("/api/rooms/{room_id}")
async def delete_room(
        room_id: int,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    
    room = delete(models.Room).where(models.Room.id == room_id, models.Room.owner == current_user.id)
    db.execute(room)
    db.commit()

    if room_id in active_rooms: 
        del active_rooms[room_id]
    return {"message": "Room deleted successfully"}

# User profile routes
@app.get("/api/users/{user_id}", response_model=schemas.UserResponse)
async def get_user_profile(
        user_id: int,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/profile", response_model=schemas.UserResponse)
async def get_my_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/api/friends")
async def add_friend(
        friend_data: schemas.AddFriend,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    friend = db.query(models.User).filter(models.User.id == friend_data.friend_id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.friends:
        current_user.friends = []

    if friend_data.friend_id in current_user.friends:
        raise HTTPException(status_code=400, detail="User is already in your friends list")

    current_user.friends.append(friend_data.friend_id)
    db.commit()
    return {"message": "Friend added successfully"}


@app.get("/api/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    top_players = db.query(models.User).order_by(models.User.matches.desc()).limit(10).all()
    return [
        {
            "id": player.id,
            "username": player.username,
            "matches": player.matches,
            "survivor_matches": player.survivor_matches,
            "mafia_matches": player.mafia_matches
        }
        for player in top_players
    ]

# uvicorn app.main:app --reload