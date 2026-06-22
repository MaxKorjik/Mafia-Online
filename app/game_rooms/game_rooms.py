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
    try:
        print(f"WebSocket connection attempt for room {room_id}")
        
        # Перевіряємо токен
        if not token:
            print("No token provided")
            await websocket.close(code=4000)
            return
            
        # Отримуємо користувача
        try:
            user = await get_user_by_token(token, db)
        except Exception as e:
            print(f"Token or User verification error: {str(e)}")
            await websocket.close(code=4000)
            return
        
        if not user:
            print("User not found via token")
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
                id=db_room.id,
                name=db_room.name,
                owner_id=db_room.owner,
                min_players=db_room.min_players_number,
                max_players=db_room.max_players_number
            )
            active_rooms[room_id] = room
            print(f"Created new room instance: {room.id}")

        # Приймаємо з'єднання
        await websocket.accept()
        print(f"WebSocket connection accepted for user {user.id} in room {room_id}")

        # Додаємо гравця до кімнати
        player = Player(id=user.id, name=user.username, websocket=websocket)
        if not room.add_player(player):
            print(f"Cannot add player {user.id} to room {room_id}")
            await websocket.close(code=4003)
            return

        # Відправляємо повідомлення про підключення
        await room.broadcast({
            "type": "player_joined",
            "username": player.name,
            "players": [p.to_dict() for p in room.players.values()]
        })

        # Відправляємо початковий стан кімнати
        await websocket.send_json({
            "type": "room_state",
            "room": room.to_dict(),
        })
        print(f"Sent initial room state to player {user.id}")

        try:
            while True:
                data = await websocket.receive_json()
                print(f"Received message from player {user.id}: {data}")
                
                msg_type = data.get("type")
                payload = data.get("payload", {})
                
                handler = message_handlers.get(msg_type)
                    
                if handler:
                    await handler(
                        websocket=websocket, 
                        payload=payload, 
                        room_id=room_id, 
                        db=db, 
                        player=player,
                        room=room
                    )
                else:
                    print(f"Unknown message type: {msg_type}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Невідомий тип повідомлення: {msg_type}"
                    })

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for player {user.id}")
            room.remove_player(player.id)
            if not room.players:
                del active_rooms[room_id]
                print(f"Room {room_id} deleted as it's empty")
            else:
                await room.broadcast({
                    "type": "player_left",
                    "username": player.name,
                    "players": [p.to_dict() for p in room.players.values()]
                })
                print(f"Player {user.id} removed from room {room_id}")

    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        try:
            if websocket.client_state.CONNECTED:
                await websocket.close(code=1011)
        except Exception:
            pass
        
        
# Обробка чату   
@register_handler("chat")
async def handle_chat(payload: dict, db: Session, player: Player ,room: GameRoom, **kwargs):
    message = payload.get("message", "")
    if not message.strip():
        return

    # Відправляємо повідомлення всім гравцям
    await room.broadcast({
        "type": "chat",
        "username": player.name,
        "message": message
    })

    # Зберігаємо повідомлення в базі даних
    if player.id:  # Тільки для авторизованих користувачів
        new_message = Messages(
            message=message,
            user_id=player.id,
            room_id=room.id
        )
        db.add(new_message)
        db.commit()
    
    
# Обробка початку гри
@register_handler("start_game")
async def handler_start_game(websocket: WebSocket, payload: dict, player: Player, room: GameRoom, **kwargs):
    if room.owner != player.id:
        await websocket.send_json({
            "type": "error",
            "message": "Тільки власник кімнати може почати гру"
        })
        return
    
    if not room.can_start_game():
        print("Game cannot start: conditions not met")
        await websocket.send_json({
            "type": "error",
            "message": "Не всі гравці готові або недостатньо гравців"
            })
        return

    try:
        print("Starting game...")
        room.start_game()
        
        # Потім відправляємо інформацію про ролі
        for player in room.players.values():
            role_info = {
                    "type": "role_assigned",
                    "role": player.role
            }
            
            if player.role == "mafia":
                other_mafia = [
                    {"id": p.id, "name": p.name}
                    for p in room.players.values()
                    if p.role == "mafia" and p.id != player.id
                ]
                role_info["other_mafia"] = other_mafia
            
            await player.websocket.send_json(role_info)
            print(f"Sent role info to player {player.id}")

        # Відправляємо повідомлення про початок гри
        await room.broadcast({
            "type": "game_started",
            "phase": room.phase,
            "round": room.round,
            "players": [p.to_dict() for p in room.players.values()]
        })
        
        # Відправляємо повідомлення про нічну фазу
        await room.broadcast({
            "type": "phase_change",
            "phase": "night",
            "round": 1
        })
        
        print("Game started successfully")
    except Exception as e:
        print(f"Error starting game: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Помилка при початку гри: {str(e)}"
        })


# Головна логіка роботи нічних дій
async def resolve_night(room: GameRoom, db: Session ):
    mafia_targets = room.night_actions["mafia"]
    doctor_save = room.night_actions["doctor"]
    detective_check = room.night_actions["detective"]

    # 1. Определяем жертву мафии (подсчитываем голоса)
    victim = None
    if mafia_targets:
        victim_id = max(set(mafia_targets), key=mafia_targets.count)
        victim = room.players.get(victim_id)

    # 2. Применяем ночные действия (убийство или спасение доктором)
    if victim:
        if doctor_save == victim.id:
            await room.broadcast({
                "type": "player_saved",
                "message": f"Гравця {victim.name} намагались вбити, але лікар врятував його!"
            })
        else:
            room.kill_player(victim.id)
            await room.broadcast({
                "type": "player_killed",
                "message": f"{victim.name} був вбитий цієї ночі."
            })

    # 3. Проверка комиссара/детектива
    if detective_check:
        checked = room.players.get(detective_check)
        if checked:
            detective = next((p for p in room.players.values() if p.role == "detective"), None)
            if detective:
                await detective.websocket.send_json({
                    "type": "investigation_result",
                    "target": checked.name,
                    "is_mafia": checked.role == "mafia"
                })

    # 4. Очищаем ночные действия и сбрасываем готовность для следующего раунда
    room.night_actions = {
        "mafia": [],
        "doctor": None,
        "detective": None
    }

    for p in room.players.values():
        p.is_ready = False

    # 5. Проверяем условия победы ПОСЛЕ того, как жертва официально погибла
    winner = room.check_victory()
    if winner:
        room.phase = "ended"
        room.is_game_over = True
        
        # Обновляем статус в БД
        db_room = db.query(Room).filter(Room.id == room.id).first()
        if db_room:
            db_room.is_active = False
            db.commit()

        await room.broadcast({
            "type": "game_over",
            "winner": winner,
            "message": f"Гру завершено! Перемогли { 'мирні' if winner == 'civilians' else 'мафія' }."
        })
        
        # Вскрываем карты
        await room.broadcast({
            "type": "roles_reveal",
            "players": [{"name": p.name, "role": p.role, "is_alive": p.is_alive} for p in room.players.values()]
        })
        return

    # 6. Если игра продолжается, переходим к дневной фазе
    room.phase = "day"
    await room.broadcast({
        "type": "phase_change",
        "phase": "day",
        "round": room.round
    })


# Обробка нічних дій (наприклад, вбивство)
@register_handler("night_action")
async def night_action(websocket: WebSocket, payload: dict, db: Session, room_id:int, player: Player, room: GameRoom, **kwargs):
    """
    payload = {
        "actor_id": int,
        "target_id": int
    }
    """
    if room.is_game_over:
        await websocket.send_json({
            "type": "error",
            "message": "Гра вже завершена"
        })
        return
    
    if not player.is_alive:
        await websocket.send_json({"type": "error", "message": "Мертвий гравець не може діяти"})
        return
    
    target_id = payload.get("target_id")
    target = room.get_player(target_id)

    if not target:
        await websocket.send_json({"type": "error", "message": "Ціль не знайдена"})
        return

    # Сохраняем действия
    if player.role == "mafia":
        room.night_actions["mafia"].append(target.id)
    elif player.role == "doctor":
        room.night_actions["doctor"] = target.id
    elif player.role == "detective":
        room.night_actions["detective"] = target.id

    player.is_ready = True

    # Проверяем готовность только специальных ролей (мафия, доктор, детектив)
    special_players = [p for p in room.players.values() 
                      if p.role in ["mafia", "doctor", "detective"] and p.is_alive]
    
    if all(p.is_ready for p in special_players):
        print("Всі нічні дії виконані, переходимо до розв'язання ночі...")
        await resolve_night(room, db)
        
    
# Голосування
@register_handler("vote")
async def vote(websocket: WebSocket, payload: dict, db: Session, player: Player, room: GameRoom, **kwargs):
    if room.is_game_over:
        await websocket.send_json({"type": "error", "message": "Гра вже завершена"})
        return
    
    if room.phase != "day":
        await websocket.send_json({"type": "error", "message": "Голосувати можна тільки вдень"})
        return
        
    if not player.is_alive:
        await websocket.send_json({"type": "error", "message": "Невірний гравець або мертвий"})
        return
    
    target_id = int(payload["target_id"])
    target = room.get_player(target_id)
    if not target or not target.is_alive:
        await websocket.send_json({"type": "error", "message": "Ціль голосування не знайдена або вже мертва"})
        return
    
    # Записуємо чий саме це голос (запобігає накрутці): ключ - ID голосуючого, значення - за кого
    room.votes[player.id] = target.id
    player.is_ready = True
    
    await room.broadcast({
        "type": "vote_cast",
        "from": player.name,
        "to": target.name
    })
    
    # Перевіряємо, чи всі живі проголосували
    alive_players = [p for p in room.players.values() if p.is_alive]
    if all(p.is_ready for p in alive_players):
        
        # Підраховуємо голоси
        vote_count = {}
        for voted_target_id in room.votes.values():
            vote_count[voted_target_id] = vote_count.get(voted_target_id, 0) + 1
        
        victim = None
        if vote_count:
            max_votes = max(vote_count.values())
            eliminated_players = [pid for pid, votes in vote_count.items() if votes == max_votes]
            
            # Поза судовим розглядом, якщо немає нічиєї
            if len(eliminated_players) == 1:
                eliminated_id = eliminated_players[0]
                victim = room.get_player(eliminated_id)
        
        if victim:
            room.kill_player(victim.id)
            await room.broadcast({
                "type": "player_killed_vote",
                "message": f"{victim.name} був повішений за результатами голосування."
            })
        else:
            await room.broadcast({
                "type": "vote_tie",
                "message": "Голоси розділилися порівну. Нікого не ліквідовано."
            })
    
        # Очищуємо голоси та готовність
        room.votes = {}
        for p in room.players.values():
            p.is_ready = False
        
        # Перевіряємо умови перемоги
        winner = room.check_victory()
        if winner:
            room.phase = "ended"
            room.is_game_over = True
            
            db_room = db.query(Room).filter(Room.id == room.id).first()
            if db_room:
                db_room.is_active = False
                db.commit()
                
            await room.broadcast({
                "type": "game_over",
                "winner": winner,
                "message": f"Гру завершено! Перемогли { 'мирні' if winner == 'civilians' else 'мафія' }."
            })
            await room.broadcast({
                "type": "roles_reveal",
                "players": [{"name": p.name, "role": p.role, "is_alive": p.is_alive} for p in room.players.values()]
            })
            return
        
        # Збільшуємо раунд і йдемо в ніч!
        room.round += 1
        room.phase = "night"
        
        for p in room.players.values():
            p.is_ready = False
                        
        await room.broadcast({
            "type": "phase_change",
            "phase": "night",
            "round": room.round
        })
        
        
# Змінюємо статус готовності
@register_handler("toggle_ready")
async def handle_toggle_ready(payload: dict, db: Session, room: GameRoom, player: Player, **kwargs):
    # Змінюємо статус готовності
    player.is_ready = not player.is_ready
    print(f"Player {player.id} ready state changed to {player.is_ready}")

    # Перевіряємо загальний стан готовності
    all_ready = all(p.is_ready for p in room.players.values())
    print(f"All players ready: {all_ready}")

    # Відправляємо оновлення всім гравцям
    await room.broadcast({
        "type": "player_ready",
        "player_id": player.id,
        "is_ready": player.is_ready,
        "players": [p.to_dict() for p in room.players.values()]
    })
    print(f"Broadcasted ready state update for player {player.id}")

    # Відправляємо додаткове повідомлення про загальний стан готовності
    if all_ready:
        await room.broadcast({
            "type": "system",
            "message": "Всі гравці готові до початку гри!"
        })


# Швидке повернення списку гравців в активній кімнаті для фронтенду
@router.get("/rooms/{room_id}/players")
async def get_room_players(room_id: int):
    """
    Швидке повернення списку гравців в активній кімнаті для фронтенду
    """
    room = active_rooms.get(room_id)
    if not room:
        # Кімната ще не створена в пам'яті або пуста
        return []

    # Повертаємо список підключених гравців
    return [player.to_dict() for player in room.players.values()]


# Отримати історію повідомлень кімнати (останні 50 повідомлень)
@router.get("/rooms/{room_id}/messages")
async def get_room_messages(room_id: int, db: Session = Depends(get_db)):
    """
    Отримати історію повідомлень кімнати (останні 50 повідомлень)
    """
    try:
        # Перевіряємо, чи існує кімната в БД
        db_room = db.query(Room).filter(Room.id == room_id).first()
        if not db_room:
            raise HTTPException(status_code=404, detail="Кімнату не знайдено")
            
        # Отримуємо повідомлення разом із користувачами (за допомогою join, щоб працювало миттєво)
        # Якщо у вас у моделі Messages немає зв'язку з User, можна залишити звичайний query, але цей варіант оптимальніший
        messages = (
            db.query(Messages)
            .filter(Messages.room_id == room_id)
            .order_by(Messages.writing_time.desc())
            .limit(50)
            .all()
        )
        
        messages_list = []
        # Перевертаємо, щоб старі повідомлення йшли спочатку (зверху вниз, як у звичайних чатах)
        for msg in reversed(messages):
            try:
                # Шукаємо автора повідомлення
                user = db.query(User).filter(User.id == msg.user_id).first()
                messages_list.append({
                    "id": msg.id,
                    "message": msg.message,
                    "username": user.username if user else "Гість",
                    "created_at": msg.writing_time.isoformat() if msg.writing_time else None
                })
            except Exception as e:
                print(f"Помилка обробки повідомлення {msg.id}: {str(e)}")
                continue
            
        return messages_list

    except HTTPException:
        raise
    except Exception as e:
        print(f"Помилка в get_room_messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")
