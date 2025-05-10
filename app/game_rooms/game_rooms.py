from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.websockets import WebSocketState
import json
from app.database import get_db
from app.models import Messages
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.auth import  get_user_by_email
from app.config import SECRET_KEY, ALGORITHM
import random, string
from app.game_rooms.game_models import GameRoom, Player
from app.game_rooms.room_storage import active_rooms
from dataclasses import asdict
from app.models import Room
import asyncio

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

# Генеруємо ім’я для гравця-гостя
def generate_guest_name():
    suffix = ''.join(random.choices(string.digits, k=8))
    return f"Guest{suffix}"

# WebSocket підключення до кімнати
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
    print(f"Received token: {token}")
    guestname = websocket.query_params.get("guestname")

    user = None
    if token:
        user = await get_user_by_token(token=token, db=db)
    
    username = None
    if user:
        username = user.username
        await room.add_player(name=username, user_id=user.id, websocket=websocket, db=db)
        await room.broadcast(f"Користувач {username} під'єднався")
    else:
        if guestname:
            username = guestname
        else:
                username = generate_guest_name()
        await room.add_player(name=username, websocket=websocket, db=db)
        await room.broadcast(f"Користувач {username} під'єднався")
        
    while True:
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
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
            else:
                break             
            
        except WebSocketDisconnect:
            if user:
                room.remove_player(name=username, db=db)
                await room.broadcast(f"Користувач {username} від'єднався")
            else:
                room.remove_player(name=username, db=db)
                await room.broadcast(f"Користувач {username} від'єднався")
            break 
        




          
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
async def handle_chat(websocket, payload,room_id, db : Session = Depends(get_db)):
    username = payload.get("username")
    message = payload.get("message")

    
    room = await verify_room(websocket=websocket, room_id=room_id)
    if not room:
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
    room.assign_roles_and_characters()
    
    for player in room.players.values():
        await player.websocket.send_json({
            "type": "role_and_character_assigned",
            "role": player.role,
            "character": asdict(player.character)
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

    await room.generate_mini_event()

    for p in room.players.values():
        p.is_ready = False
    
    # Переход к дневной фазе
    room.phase = "day"
    
    # генерация супер ивента
    await asyncio.sleep(1)
    super_event = await room.generate_super_event()
    if super_event:
        await room.broadcast(super_event)

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
    payload : {
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
        print("room.night_actions['mafia'].append(target.id)")
    elif actor.role == "doctor":
        room.night_actions["doctor"] = target.id
        print("room.night_actions['doctor'] = target.id")
    elif actor.role == "detective":
        room.night_actions["detective"] = target.id
        print("room.night_actions['detective'] = target.id")

    actor.is_ready = True
    print("actor_is_ready")

    active_roles = [p for p in room.players.values() if p.role in {"mafia", "doctor", "detective"} and p.is_alive]
    print("Active roles and their readiness:")
    for p in active_roles:
        print(f"- {p.name} (role: {p.role}, is_ready: {p.is_ready})")

    if active_roles and all(p.is_ready for p in active_roles):
        await resolve_night(room)
        print("All active players ready — resolving night")
    
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
    

    await room.broadcast(json.dumps({
    "type": "phase_change",
    "phase": "day"
    }))
    
# async def start_vote_phase(room: GameRoom):
#     room.phase = "vote"
#     await room.broadcast(json.dumps({
#         "type": "phase_change",
#         "phase": "vote",
#         "duration": 120  # для фронта — сколько секунд есть
#     }))

#     await asyncio.sleep(120)

#     # завершаем голосование
#     room.phase = "waiting"
#     await room.broadcast(json.dumps({
#         "type": "phase_ended",
#         "phase": "vote",
#         "message": "Голосування завершено"
#     }))
    
    
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


# @register_handler("set_phase")
# async def handle_set_phase(websocket, payload, room_id: int, db: Session):
    # desired_phase = payload.get("phase")
    # room = await verify_room(websocket, room_id)
    # if not room:
    #     await websocket.send_json({
    #         "type": "error",
    #         "message": "Кімната не знайдена."
    #     })
    #     return

    # player = next((p for p in room.players.values() if p.websocket == websocket), None)
    # if not player:
    #     await websocket.send_json({
    #         "type": "error",
    #         "message": "Гравець не знайдений."
    #     })
    #     return

    # if player.name != room.owner:
    #     await websocket.send_json({
    #         "type": "error",
    #         "message": "Тільки власник кімнати може змінювати фазу вручну."
    #     })
    #     return

    # if desired_phase not in room.phases:
    #     await websocket.send_json({
    #         "type": "error",
    #         "message": f"Невідома фаза: {desired_phase}"
    #     })
    #     return

    # room.phase = desired_phase
    # room.phase_index = room.phases.index(desired_phase)

    # await room.broadcast(f"Фаза гри вручну змінена на: {desired_phase}")
    # await room.broadcast_json({
    #     "type": "phase_changed",
    #     "phase": desired_phase
    # })
