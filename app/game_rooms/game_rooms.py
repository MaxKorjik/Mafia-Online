from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends, Query
from fastapi.websockets import WebSocketState
import json
from app.database import get_db
from app.models import Messages, User, Room
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.auth import  get_user_by_email
from app.config import SECRET_KEY, ALGORITHM
import random, string
from app.game_rooms.game_models import GameRoom, Player
from app.game_rooms.room_storage import active_rooms
import asyncio
from datetime import datetime
from typing import Dict

router = APIRouter(tags=["Rooms"])

# Словник для збереження обробників повідомлень
message_handlers = {}

# Помилка автентифікації
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Не вдалося перевірити облікові дані",
    headers={"WWW-Authenticate": "Bearer"},
)

# Декоратор для реєстрації обробників повідомлень за типом
def register_handler(message_type):
    def decorator(func):
        print(f"Registered handler: {message_type} → {func.__name__}")
        message_handlers[message_type] = func 
        return func
    return decorator

# Отримуємо користувача за токеном
async def get_user_by_token(token: str, db: Session):
    try:
        print(f"Decoding token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            print("No email found in token")
            raise credentials_exception
        user = get_user_by_email(db, email)
        print(f"User found: {user}")
        return user
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception

# Генеруємо ім'я для гравця-гостя
def generate_guest_name():
    suffix = ''.join(random.choices(string.digits, k=8))
    return f"Guest{suffix}"

# WebSocket підключення до кімнати
@router.websocket("/ws/room/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str = Query(None), db: Session = Depends(get_db)):
    """
    WebSocket endpoint для кімнати
    """
    try:
        print(f"WebSocket connection attempt for room {room_id}")
        
        # Перевіряємо токен
        if not token:
            print("No token provided")
            await websocket.close(code=4000)
            return
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email = payload.get("sub")
            if not user_email:
                print("No email in token")
                await websocket.close(code=4000)
                return
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            await websocket.close(code=4000)
            return

        # Отримуємо користувача з бази даних
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            print(f"User not found for email: {user_email}")
            await websocket.close(code=4000)
            return

        # Перевіряємо чи існує кімната в базі даних
        db_room = db.query(Room).filter(Room.id == room_id).first()
        if not db_room:
            print(f"Room {room_id} not found in database")
            await websocket.close(code=4000)
            return

        # Перевіряємо чи існує кімната в активних кімнатах
        room = active_rooms.get(room_id)
        if not room:
            # Якщо кімнати немає в active_rooms, створюємо її
            room = GameRoom(
                room_id=db_room.id,
                room_name=db_room.name,
                min_players=db_room.min_players_number,
                max_players=db_room.max_players_number,
                is_private=db_room.is_private,
                owner=db_room.owner
            )
            active_rooms[room_id] = room
            print(f"Created new room instance: {room.room_id}")

        # Приймаємо з'єднання
        await websocket.accept()
        print(f"WebSocket connection accepted for user {user.id} in room {room_id}")

        # Додаємо гравця до кімнати
        player = Player(id=user.id, name=user.username, websocket=websocket, room=room)
        room.add_player(player)
        print(f"Player {user.id} added to room {room_id}")

        # Додаємо з'єднання до кімнати
        room.add_connection(websocket)
        print(f"Connection added for player {user.id} in room {room_id}")

        # Відправляємо початковий стан кімнати
        await websocket.send_json({
            "type": "room_state",
            "room": {
                "id": room.room_id,
                "name": room.room_name,
                "min_players": room.min_players,
                "max_players": room.max_players,
                "is_private": room.is_private,
                "owner": room.owner
            },
            "players": [p.to_dict() for p in room.players.values()]
        })
        print(f"Initial room state sent to player {user.id}")

        try:
            while True:
                data = await websocket.receive_json()
                print(f"Received message from player {user.id}: {data}")

                if data["type"] == "toggle_ready":
                    player.is_ready = not player.is_ready
                    # Відправляємо оновлений стан всім гравцям
                    await room.broadcast({
                        "type": "player_ready",
                        "player_id": player.id,
                        "is_ready": player.is_ready,
                        "players": [p.to_dict() for p in room.players.values()]
                    })
                    print(f"Player {user.id} ready state updated to {player.is_ready}")

                elif data["type"] == "start_game":
                    print(f"Start game request from player {player.id}")
                    if player.id != room.owner:
                        print(f"Player {player.id} is not the owner (owner is {room.owner})")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Тільки власник кімнати може почати гру"
                        })
                        continue

                    print(f"Checking if game can start: players={len(room.players)}, min_players={room.min_players}, all_ready={all(p.is_ready for p in room.players.values())}")
                    if not room.can_start_game():
                        print("Game cannot start: conditions not met")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Не всі гравці готові або недостатньо гравців"
                        })
                        continue

                    try:
                        print("Starting game...")
                        room.start_game()
                        print("Game started successfully")
                        
                        # Відправляємо оновлений стан кімнати
                        await room.broadcast({
                            "type": "game_started",
                            "phase": room.phase,
                            "round": room.round,
                            "players": [p.to_dict() for p in room.players.values()]
                        })
                        print(f"Game state broadcasted to all players")
                    except Exception as e:
                        print(f"Error starting game: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Помилка при запуску гри: {str(e)}"
                        })

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for player {user.id}")
            room.remove_connection(websocket)
            room.remove_player(player)
            if not room.players:
                del active_rooms[room_id]
                print(f"Room {room_id} deleted as it's empty")
            else:
                await room.broadcast({
                    "type": "player_left",
                    "player_id": player.id,
                    "players": [p.to_dict() for p in room.players.values()]
                })
                print(f"Player {user.id} removed from room {room_id}")

    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        try:
            await websocket.close(code=1011)
        except:
            pass

# Перевірка, чи існує кімната
async def verify_room(websocket, room_id):
    
    room = active_rooms.get(room_id)
    
    if not room:
        await websocket.send_json({
            "type": "error",
            "message": "Кімната не знайдена"
        })
        return

    return room
        
# Обробка чату   
@register_handler("chat")
async def handle_chat(websocket: WebSocket, payload: dict, room_id: int, db: Session):
    room = await verify_room(websocket=websocket, room_id=room_id)
    if not room:
        return

    # Знаходимо гравця за WebSocket
    player = next((p for p in room.players.values() if p.websocket == websocket), None)
    if not player:
        await websocket.send_json({
            "type": "error",
            "message": "Гравець не знайдений"
        })
        return

    message = payload.get("message", "")
    if not message.strip():
        return

    # Відправляємо повідомлення всім гравцям
    await room.broadcast(json.dumps({
        "type": "chat",
        "username": player.name,
        "message": message
    }))

    # Зберігаємо повідомлення в базі даних
    if player.id:  # Тільки для авторизованих користувачів
        new_message = Messages(
            message=message,
            user_id=player.id,
            room_id=room.room_id
        )
        db.add(new_message)
        db.commit()
    
# Обробка початку гри
@register_handler("start_game")
async def handler_start_game(websocket, payload, room_id, **kwargs):
    # # должна назначить роли игроков, обозначить раунд...
    # {
    #     "type" : "start_game",
    #     "payload" : {
    #         "username" : "Guest1488"
    #         }
    # }
    
    room = await verify_room(websocket=websocket, room_id=room_id)
    if not room:
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
    

async def resolve_night(room: GameRoom):
    mafia_targets = room.night_actions["mafia"]
    doctor_save = room.night_actions["doctor"]
    detective_check = room.night_actions["detective"]

    # Подсчет голосов мафии
    if mafia_targets:
        victim_id = max(set(mafia_targets), key=mafia_targets.count)
        victim = next((p for p in room.players.values() if p.id == victim_id), None)

        if victim:
            if doctor_save == victim.id:
                await room.broadcast(json.dumps({
                    "type": "player_saved",
                    "message": f"Гравця {victim.name} намагались вбити, але лікар врятував його!"
                }))
            else:
                victim.is_alive = False
                await room.broadcast(json.dumps({
                    "type": "player_killed",
                    "message": f"{victim.name} був вбитий цієї ночі."
                }))

    if detective_check:
        checked = next((p for p in room.players.values() if p.id == detective_check), None)
        if checked:
            detective = next((p for p in room.players.values() if p.role == "detective"), None)
            if detective:
                await detective.websocket.send_json({
                    "type": "investigation_result",
                    "target": checked.name,
                    "is_mafia": checked.role == "mafia"
                })

    # Очистка на следующий раунд
    room.night_actions = {
        "mafia": [],
        "doctor": None,
        "detective": None
    }

    # Переход к дневной фазе
    room.phase = "day"

def check_game_end(room: GameRoom):
    mafia_alive = [p for p in room.players.values() if p.role == "mafia" and p.is_alive]
    citizens_alive = [p for p in room.players.values() if p.role != "mafia" and p.is_alive]
    
    if not mafia_alive:
        return "citizens"
    if len(mafia_alive) >= len(citizens_alive):
        return "mafia"
    return None



# Обробка нічних дій (наприклад, вбивство)
@register_handler("night_action")
async def night_action(websocket, payload, room_id, db, **kwargs):
    """
    payload = {
        "actor_id": int,
        "target_id": int
    }
    """
    room = await verify_room(websocket, room_id)
    if not room:
        return
    
    if room.is_game_over:
        await websocket.send_json({
            "type": "error",
            "message": "Гра вже завершена"
        })
        return
    
    actor = next((p for p in room.players.values() if p.id == payload["actor_id"]), None)
    target = next((p for p in room.players.values() if p.id == payload["target_id"]), None)

    if not actor or not target:
        await websocket.send_json({
            "type": "error",
            "message": "Гравець не знайдений"
        })
        return

    if not actor.is_alive:
        await websocket.send_json({
            "type": "error",
            "message": "Мертвий гравець не може діяти"
        })
        return

    # Сохраняем действия
    if actor.role == "mafia":
        room.night_actions["mafia"].append(target.id)
    elif actor.role == "doctor":
        room.night_actions["doctor"] = target.id
    elif actor.role == "detective":
        room.night_actions["detective"] = target.id

    actor.is_ready = True

    if all(p.is_ready for p in room.players.values() if p.role in {"mafia", "doctor", "detective"} and p.is_alive):
        await resolve_night(room)
        
    winner = check_game_end(room)
    if winner:
        await room.broadcast(json.dumps({
            "type": "game_over",
            "winner": winner,
            "message": f"Гру завершено! Перемогли { 'мирні' if winner == 'citizens' else 'мафія' }."
        }))
        room.phase = "ended"
        room.is_game_over = True
        
        db_room = db.query(Room).filter(Room.id == room_id).first()
        if db_room:
            db_room.is_active = False
            db.commit()
                
        await room.broadcast(json.dumps({
                "type": "roles_reveal",
                "players": [
                    {"name": p.name, "role": p.role, "is_alive": p.is_alive}
                    for p in room.players.values()
                ]
            }))
        return
    
    for p in room.players.values():
        p.is_ready = False

    await room.broadcast(json.dumps({
    "type": "phase_change",
    "phase": "day"
    }))
    
@register_handler("vote")
async def vote(websocket, payload, room_id, db, **kwargs):
    # payload = {
    #     "player_id" : int,
    #     "target_id" : int
    # }
    
    room = await verify_room(websocket, room_id)
    if not room:
        return
    
    if room.is_game_over:
        await websocket.send_json({
            "type": "error",
            "message": "Гра вже завершена"
        })
        return
    
    player = next((p for p in room.players.values() if p.id == int(payload["player_id"])), None)
    if not player or not player.is_alive:
        await websocket.send_json({
            "type": "error",
            "message": "Невірний гравець або мертвий"
        })
        return
    
    target_id = int(payload["target_id"])
    room.votes[target_id] = room.votes.get(target_id, 0) + 1
    player.is_ready = True
    
    await room.broadcast(json.dumps({
        "type": "vote_cast",
        "from": player.name,
        "to": next((p.name for p in room.players.values() if p.id == target_id), "невідомо")
    }))
    
    if all(p.is_ready for p in room.players.values() if p.is_alive):

        victim_id = max(room.votes.items(), key=lambda x: x[1])[0]
        victim = next((p for p in room.players.values() if p.id == victim_id), None)
        if victim:
            victim.is_alive = False
            await room.broadcast(json.dumps({
                "type": "player_killed_vote",
                "message": f"{victim.name} був повішений за результатами голосування."
            }))
    
        for p in room.players.values():
            p.is_ready = False
        
        winner = check_game_end(room)
        if winner:
            await room.broadcast(json.dumps({
                "type": "game_over",
                "winner": winner,
                "message": f"Гру завершено! Перемогли { 'мирні' if winner == 'citizens' else 'мафія' }."
            }))
            room.phase = "ended"
            
            db_room = db.query(Room).filter(Room.id == room_id).first()
            if db_room:
                db_room.is_active = False
                db.commit()
                
            await room.broadcast(json.dumps({
                    "type": "roles_reveal",
                    "players": [
                        {"name": p.name, "role": p.role, "is_alive": p.is_alive}
                        for p in room.players.values()
                    ]
                }))
            return
        
        room.votes = {}
        room.phase = "night"
        await room.broadcast(json.dumps({
            "type": "phase_change",
            "phase": "night"
        }))

@register_handler("toggle_ready")
async def handle_toggle_ready(websocket: WebSocket, payload: dict, room_id: int, db: Session):
    room = await verify_room(websocket=websocket, room_id=room_id)
    if not room:
        return

    # Знаходимо гравця за WebSocket
    player = next((p for p in room.players.values() if p.websocket == websocket), None)
    if not player:
        await websocket.send_json({
            "type": "error",
            "message": "Гравець не знайдений"
        })
        return

    # Змінюємо статус готовності
    player.is_ready = not player.is_ready

    # Відправляємо оновлення всім гравцям
    await room.broadcast(json.dumps({
        "type": "player_ready",
        "username": player.name,
        "is_ready": player.is_ready,
        "players": [p.to_dict() for p in room.players.values()]
    }))

async def handle_message(websocket: WebSocket, message: dict):
    try:
        message_type = message.get('type')
        payload = message.get('payload', {})
        
        if message_type == 'chat':
            username = payload.get('username', 'Гість')
            message_text = payload.get('message', '')
            player_id = payload.get('player_id')
            
            # Знаходимо гравця за ID або ім'ям
            player = None
            if player_id:
                player = next((p for p in self.players if p.id == player_id), None)
            if not player:
                player = next((p for p in self.players if p.username == username), None)
            
            if not player:
                await websocket.send_json({
                    'type': 'error',
                    'payload': {
                        'message': 'Гравець не знайдений'
                    }
                })
                return
            
            # Відправляємо повідомлення всім гравцям
            await self.broadcast({
                'type': 'chat',
                'payload': {
                    'username': player.username,
                    'message': message_text,
                    'timestamp': datetime.now().isoformat()
                }
            })
            
        elif message_type == 'ready':
            player = next((p for p in self.players if p.websocket == websocket), None)
            if player:
                player.is_ready = not player.is_ready
                await self.broadcast({
                    'type': 'player_ready',
                    'payload': {
                        'username': player.username,
                        'is_ready': player.is_ready
                    }
                })
                
        elif message_type == 'start_game':
            if len(self.players) >= self.min_players:
                await self.start_game()
            else:
                await websocket.send_json({
                    'type': 'error',
                    'payload': {
                        'message': 'Недостатньо гравців для початку гри'
                    }
                })
    except Exception as e:
        print(f"Помилка обробки повідомлення: {str(e)}")
        await websocket.send_json({
            'type': 'error',
            'payload': {
                'message': f'Помилка обробки повідомлення: {str(e)}'
            }
        })

@router.get("/rooms/{room_id}/players")
async def get_room_players(room_id: int, db: Session = Depends(get_db)):
    """
    Отримати список гравців у кімнаті
    """
    try:
        print(f"Getting players for room {room_id}")
        
        # Перевіряємо чи існує кімната в базі даних
        db_room = db.query(Room).filter(Room.id == room_id).first()
        if not db_room:
            print(f"Room {room_id} not found in database")
            raise HTTPException(status_code=404, detail="Кімнату не знайдено")

        # Перевіряємо чи існує кімната в активних кімнатах
        room = active_rooms.get(room_id)
        if not room:
            print(f"Room {room_id} not found in active rooms")
            # Повертаємо порожній список, якщо кімнати немає в активних
            return []

        # Формуємо список гравців
        players_list = []
        for player in room.players.values():
            try:
                player_dict = player.to_dict()
                players_list.append(player_dict)
            except Exception as e:
                print(f"Error converting player to dict: {str(e)}")
                continue

        print(f"Returning players list for room {room_id}: {players_list}")
        return players_list

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_room_players: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутрішня помилка сервера: {str(e)}")

def get_room(room_id: int):
    return active_rooms.get(room_id)
