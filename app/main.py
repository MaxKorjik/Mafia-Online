from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models, schemas, database
from app.auth import  get_current_user
from app.game_rooms.game_rooms import router as game_router
from app.auth import router as auth_router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Mafia Game")


app.include_router(game_router)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_room = models.Room(
        name=room.name,
        password=room.password,
        owner=current_user.id,
        max_players_number=room.max_players_number,
        is_private=room.is_private
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@app.delete("/api/rooms/{room_id}")
async def delete_room(
        room_id: int,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.owner != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this room")

    db.delete(room)
    db.commit()
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