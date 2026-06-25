# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends, Query
# from fastapi.websockets import WebSocketState
# import json
# from app.database import get_db
# from app.models import Messages, User, Room
# from sqlalchemy.orm import Session
# from jose import jwt, JWTError
# from app.auth import  get_user_by_email
# from app.config import SECRET_KEY, ALGORITHM
# import random, string
# from app.game_rooms.game_models import GameRoom, Player
# from app.game_rooms.room_storage import active_rooms
# import asyncio
# from datetime import datetime
# from typing import Dict

# router = APIRouter(tags=["Rooms"])

# # Словник для збереження обробників повідомлень
# message_handlers = {}

# # Помилка автентифікації
# credentials_exception = HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail="Не вдалося перевірити облікові дані",
#     headers={"WWW-Authenticate": "Bearer"},
# )

# # Декоратор для реєстрації обробників повідомлень за типом
# def register_handler(message_type):
#     def decorator(func):
#         print(f"Registered handler: {message_type} → {func.__name__}")
#         message_handlers[message_type] = func 
#         return func
#     return decorator

# # Отримуємо користувача за токеном
# async def get_user_by_token(token: str, db: Session):
#     try:
#         print(f"Decoding token: {token}")
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             print("No email found in token")
#             raise credentials_exception
#         user = get_user_by_email(db, email)
#         print(f"User found: {user}")
#         return user
#     except JWTError as e:
#         print(f"JWT Error: {e}")
#         raise credentials_exception

# # Генеруємо ім'я для гравця-гостя
# def generate_guest_name():
#     suffix = ''.join(random.choices(string.digits, k=8))
#     return f"Guest{suffix}"

# # WebSocket підключення до кімнати
# @router.websocket("/ws/room/{room_id}")
# async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str = Query(None), db: Session = Depends(get_db)):
#     """
#     WebSocket endpoint для кімнати
#     """
#     try:
#         print(f"WebSocket connection attempt for room {room_id}")
        
#         # Перевіряємо токен
#         if not token:
#             print("No token provided")
#             await websocket.close(code=4000)
#             return
            
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             user_email = payload.get("sub")
#             if not user_email:
#                 print("No email in token")
#                 await websocket.close(code=4000)
#                 return
#         except Exception as e:
#             print(f"Token verification error: {str(e)}")
#             await websocket.close(code=4000)
#             return

#         # Отримуємо користувача з бази даних
#         user = db.query(User).filter(User.email == user_email).first()
#         if not user:
#             print(f"User not found for email: {user_email}")
#             await websocket.close(code=4000)
#             return

#         # Перевіряємо чи існує кімната в базі даних
#         db_room = db.query(Room).filter(Room.id == room_id).first()
#         if not db_room:
#             print(f"Room {room_id} not found in database")
#             await websocket.close(code=4000)
#             return

#         # Перевіряємо чи існує кімната в активних кімнатах
#         room = active_rooms.get(room_id)
#         if not room:
#             # Якщо кімнати немає в active_rooms, створюємо її
#             room = GameRoom(
#                 id=db_room.id,
#                 name=db_room.name,
#                 owner_id=db_room.owner,
#                 min_players=db_room.min_players_number,
#                 max_players=db_room.max_players_number
#             )
#             active_rooms[room_id] = room
#             print(f"Created new room instance: {room.id}")

#         # Приймаємо з'єднання
#         await websocket.accept()
#         print(f"WebSocket connection accepted for user {user.id} in room {room_id}")

#         # Додаємо гравця до кімнати
#         player = Player(id=user.id, name=user.username, websocket=websocket)
#         if not room.add_player(player):
#             print(f"Cannot add player {user.id} to room {room_id}")
#             await websocket.close(code=4003)
#             return

#         # Відправляємо повідомлення про підключення
#         await room.broadcast({
#             "type": "player_joined",
#             "username": player.name,
#             "players": [p.to_dict() for p in room.players.values()]
#         })

#         # Відправляємо початковий стан кімнати
#         await websocket.send_json({
#             "type": "room_state",
#             "room": room.to_dict(),
#             "players": [p.to_dict() for p in room.players.values()]
#         })
#         print(f"Sent initial room state to player {user.id}")

#         try:
#             while True:
#                 data = await websocket.receive_json()
#                 print(f"Received message from player {user.id}: {data}")

#                 if data["type"] == "chat":
#                     message = data.get("payload", {}).get("message", "")
#                     if message.strip():
#                         # Відправляємо повідомлення всім гравцям
#                         await room.broadcast({
#                             "type": "chat",
#                             "username": player.name,
#                             "message": message
#                         })
                        
#                         # Зберігаємо повідомлення в базі даних
#                         new_message = Messages(
#                             message=message,
#                             user_id=player.id,
#                             room_id=room.id
#                         )
#                         db.add(new_message)
#                         db.commit()
#                         print(f"Chat message saved: {message}")

#                 elif data["type"] == "toggle_ready":
#                     player.is_ready = not player.is_ready
#                     print(f"Player {user.id} ready state changed to {player.is_ready}")
                    
#                     # Перевіряємо загальний стан готовності
#                     all_ready = all(p.is_ready for p in room.players.values())
#                     print(f"All players ready: {all_ready}")
                    
#                     # Відправляємо оновлений стан всім гравцям
#                     await room.broadcast({
#                         "type": "player_ready",
#                         "player_id": player.id,
#                         "is_ready": player.is_ready,
#                         "players": [p.to_dict() for p in room.players.values()]
#                     })
                    
#                     # Відправляємо додаткове повідомлення про загальний стан готовності
#                     if all_ready:
#                         await room.broadcast({
#                             "type": "system",
#                             "message": "Всі гравці готові до початку гри!"
#                         })

#                 elif data["type"] == "start_game":
#                     print(f"Start game request from player {player.id}")
#                     if player.id != room.owner:
#                         print(f"Player {player.id} is not the owner (owner is {room.owner})")
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": "Тільки власник кімнати може почати гру"
#                         })
#                         continue

#                     if not room.can_start_game():
#                         print("Game cannot start: conditions not met")
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": "Не всі гравці готові або недостатньо гравців"
#                         })
#                         continue

#                     try:
#                         print("Starting game...")
#                         room.start_game()
#                         print("Game started successfully")
                        
#                         # Відправляємо ролі гравцям
#                         for p in room.players.values():
#                             role_info = {
#                                 "type": "role_assigned",
#                                 "role": p.role
#                             }
                            
#                             if p.role == "mafia":
#                                 other_mafia = [
#                                     {"id": m.id, "name": m.name}
#                                     for m in room.players.values()
#                                     if m.role == "mafia" and m.id != p.id
#                                 ]
#                                 role_info["other_mafia"] = other_mafia
                            
#                             await p.websocket.send_json(role_info)
#                             print(f"Sent role info to player {p.id}")
                        
#                         # Відправляємо оновлений стан кімнати
#                         await room.broadcast({
#                             "type": "game_started",
#                             "phase": room.phase,
#                             "round": room.round,
#                             "players": [p.to_dict() for p in room.players.values()]
#                         })
                        
#                         # Відправляємо повідомлення про нічну фазу
#                         await room.broadcast({
#                             "type": "phase_change",
#                             "phase": "night",
#                             "round": 1
#                         })
                        
#                         print(f"Game state broadcasted to all players")
#                     except Exception as e:
#                         print(f"Error starting game: {str(e)}")
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": f"Помилка при запуску гри: {str(e)}"
#                         })

#         except WebSocketDisconnect:
#             print(f"WebSocket disconnected for player {user.id}")
#             room.remove_player(player.id)
#             if not room.players:
#                 del active_rooms[room_id]
#                 print(f"Room {room_id} deleted as it's empty")
#             else:
#                 await room.broadcast({
#                     "type": "player_left",
#                     "username": player.name,
#                     "players": [p.to_dict() for p in room.players.values()]
#                 })
#                 print(f"Player {user.id} removed from room {room_id}")

#     except Exception as e:
#         print(f"Error in WebSocket connection: {str(e)}")
#         try:
#             if websocket.client_state.CONNECTED:
#                 await websocket.close(code=1011)
#         except Exception:
#             pass

# # Перевірка, чи існує кімната
# async def verify_room(websocket, room_id):
    
#     room = active_rooms.get(room_id)
    
#     if not room:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Кімната не знайдена"
#         })
#         return

#     return room
        
# # Обробка чату   
# @register_handler("chat")
# async def handle_chat(websocket: WebSocket, payload: dict, room_id: int, db: Session):
#     room = await verify_room(websocket=websocket, room_id=room_id)
#     if not room:
#         return

#     # Знаходимо гравця за WebSocket
#     player = next((p for p in room.players.values() if p.websocket == websocket), None)
#     if not player:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Гравець не знайдений"
#         })
#         return

#     message = payload.get("message", "")
#     if not message.strip():
#         return

#     # Відправляємо повідомлення всім гравцям
#     await room.broadcast({
#         "type": "chat",
#         "username": player.name,
#         "message": message
#     })

#     # Зберігаємо повідомлення в базі даних
#     if player.id:  # Тільки для авторизованих користувачів
#         new_message = Messages(
#             message=message,
#             user_id=player.id,
#             room_id=room.id
#         )
#         db.add(new_message)
#         db.commit()
    
# # Обробка початку гри
# @register_handler("start_game")
# async def handler_start_game(websocket, payload, room_id, **kwargs):
#     room = await verify_room(websocket=websocket, room_id=room_id)
#     if not room:
#         return
    
#     player = next((p for p in room.players.values() if p.websocket == websocket), None)
#     if not player:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Гравець не знайдений"
#         })
#         return

#     if room.owner != player.id:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Тільки власник кімнати може почати гру"
#         })
#         return

#     if len(room.players) < room.min_players:
#         await websocket.send_json({
#             "type": "error",
#             "message": f"Для початку гри потрібно щонайменше {room.min_players} гравців"
#         })
#         return
    
#     if room.phase != "waiting":
#         await websocket.send_json({
#             "type": "error",
#             "message": "Гра вже розпочата"
#         })
#         return
    
#     # Перевіряємо готовність всіх гравців
#     all_ready = all(p.is_ready for p in room.players.values())
#     print(f"Checking if all players are ready: {all_ready}")
#     print(f"Players ready states: {[(p.id, p.is_ready) for p in room.players.values()]}")
    
#     if not all_ready:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Не всі гравці готові"
#         })
#         return
    
#     try:
#         print("Starting game...")
#         room.phase = "night"  # Починаємо з ночі
#         room.round = 1
#         room.is_game_over = False
#         room.night_actions = {
#             "mafia": [],
#             "doctor": None,
#             "detective": None
#         }
#         room.votes = {}
        
#         # Роздаємо ролі
#         roles = ["mafia", "mafia", "doctor", "detective", "civilian", "civilian"]
#         random.shuffle(roles)
        
#         # Спочатку роздаємо ролі всім гравцям
#         for player, role in zip(room.players.values(), roles):
#             player.role = role
#             player.is_ready = False
#             player.is_alive = True
#             print(f"Assigned role {role} to player {player.id}")
        
#         # Потім відправляємо інформацію про ролі
#         for player in room.players.values():
#             role_info = {
#                     "type": "role_assigned",
#                     "role": player.role
#             }
            
#             if player.role == "mafia":
#                 other_mafia = [
#                     {"id": p.id, "name": p.name}
#                     for p in room.players.values()
#                     if p.role == "mafia" and p.id != player.id
#                 ]
#                 role_info["other_mafia"] = other_mafia
            
#             await player.websocket.send_json(role_info)
#             print(f"Sent role info to player {player.id}")

#         # Відправляємо повідомлення про початок гри
#         await room.broadcast({
#             "type": "game_started",
#             "phase": "night",
#             "round": 1,
#             "players": [p.to_dict() for p in room.players.values()]
#         })
        
#         # Відправляємо повідомлення про нічну фазу
#         await room.broadcast({
#             "type": "phase_change",
#             "phase": "night",
#             "round": 1
#         })
        
#         print("Game started successfully")
#     except Exception as e:
#         print(f"Error starting game: {str(e)}")
#         await websocket.send_json({
#             "type": "error",
#             "message": f"Помилка при початку гри: {str(e)}"
#         })

# async def resolve_night(room: GameRoom):
#     mafia_targets = room.night_actions["mafia"]
#     doctor_save = room.night_actions["doctor"]
#     detective_check = room.night_actions["detective"]

#     # 1. Определяем жертву мафии (подсчитываем голоса)
#     victim = None
#     if mafia_targets:
#         victim_id = max(set(mafia_targets), key=mafia_targets.count)
#         victim = next((p for p in room.players.values() if p.id == victim_id), None)

#     # 2. Применяем ночные действия (убийство или спасение доктором)
#     if victim:
#         if doctor_save == victim.id:
#             await room.broadcast({
#                 "type": "player_saved",
#                 "message": f"Гравця {victim.name} намагались вбити, але лікар врятував його!"
#             })
#         else:
#             victim.is_alive = False
#             await room.broadcast({
#                 "type": "player_killed",
#                 "message": f"{victim.name} був вбитий цієї ночі."
#             })

#     # 3. Проверка комиссара/детектива
#     if detective_check:
#         checked = next((p for p in room.players.values() if p.id == detective_check), None)
#         if checked:
#             detective = next((p for p in room.players.values() if p.role == "detective"), None)
#             if detective:
#                 await detective.websocket.send_json({
#                     "type": "investigation_result",
#                     "target": checked.name,
#                     "is_mafia": checked.role == "mafia"
#                 })

#     # 4. Очищаем ночные действия и сбрасываем готовность для следующего раунда
#     room.night_actions = {
#         "mafia": [],
#         "doctor": None,
#         "detective": None
#     }

#     for p in room.players.values():
#         p.is_ready = False

#     # 5. Проверяем условия победы ПОСЛЕ того, как жертва официально погибла
#     winner = check_game_end(room)
#     if winner:
#         await room.broadcast({
#             "type": "game_over",
#             "winner": winner,
#             "message": f"Гру завершено! Перемогли { 'мирні' if winner == 'citizens' else 'мафія' }."
#         })
#         room.phase = "ended"
#         return

#     # 6. Если игра продолжается, переходим к дневной фазе
#     room.phase = "day"
#     await room.broadcast({
#         "type": "phase_change",
#         "phase": "day",
#         "round": room.round
#     })

# def check_game_end(room: GameRoom):
#     mafia_alive = [p for p in room.players.values() if p.role == "mafia" and p.is_alive]
#     citizens_alive = [p for p in room.players.values() if p.role != "mafia" and p.is_alive]
    
#     if not mafia_alive:
#         return "citizens"
#     if len(mafia_alive) >= len(citizens_alive):
#         return "mafia"
#     return None



# # Обробка нічних дій (наприклад, вбивство)
# @register_handler("night_action")
# async def night_action(websocket, payload, room_id, db, **kwargs):
#     """
#     payload = {
#         "actor_id": int,
#         "target_id": int
#     }
#     """
#     room = await verify_room(websocket, room_id)
#     if not room:
#         return
    
#     if room.is_game_over:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Гра вже завершена"
#         })
#         return
    
#     actor = next((p for p in room.players.values() if p.id == payload["actor_id"]), None)
#     target = next((p for p in room.players.values() if p.id == payload["target_id"]), None)

#     if not actor or not target:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Гравець не знайдений"
#         })
#         return

#     if not actor.is_alive:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Мертвий гравець не може діяти"
#         })
#         return

#     # Сохраняем действия
#     if actor.role == "mafia":
#         room.night_actions["mafia"].append(target.id)
#     elif actor.role == "doctor":
#         room.night_actions["doctor"] = target.id
#     elif actor.role == "detective":
#         room.night_actions["detective"] = target.id

#     actor.is_ready = True

#     # Проверяем готовность только специальных ролей (мафия, доктор, детектив)
#     special_players = [p for p in room.players.values() 
#                       if p.role in ["mafia", "doctor", "detective"] and p.is_alive]
    
#     if all(p.is_ready for p in special_players):
#         print("Все ночные действия выполнены, разрешаем ночь")
#         await resolve_night(room)
        
#         # Проверяем условия победы после разрешения ночи
#         winner = check_game_end(room)
#         if winner:
#             await room.broadcast(json.dumps({
#                 "type": "game_over",
#                 "winner": winner,
#                 "message": f"Гру завершено! Перемогли { 'мирні' if winner == 'citizens' else 'мафія' }."
#             }))
#             room.phase = "ended"
#             room.is_game_over = True
            
#             db_room = db.query(Room).filter(Room.id == room_id).first()
#             if db_room:
#                 db_room.is_active = False
#                 db.commit()
                    
#             await room.broadcast(json.dumps({
#                     "type": "roles_reveal",
#                     "players": [
#                         {"name": p.name, "role": p.role, "is_alive": p.is_alive}
#                         for p in room.players.values()
#                     ]
#                 }))
#             return
    
# @register_handler("vote")
# async def vote(websocket, payload, room_id, db, **kwargs):
#     room = await verify_room(websocket, room_id)
#     if not room:
#         return
    
#     if room.is_game_over:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Гра вже завершена"
#         })
#         return
    
#     player = next((p for p in room.players.values() if p.id == int(payload["player_id"])), None)
#     if not player or not player.is_alive:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Невірний гравець або мертвий"
#         })
#         return
    
#     target_id = int(payload["target_id"])
#     room.votes[target_id] = room.votes.get(target_id, 0) + 1
#     player.is_ready = True
    
#     await room.broadcast(json.dumps({
#         "type": "vote_cast",
#         "from": player.name,
#         "to": next((p.name for p in room.players.values() if p.id == target_id), "невідомо")
#     }))
    
#     if all(p.is_ready for p in room.players.values() if p.is_alive):
#         # Підраховуємо голоси
#         vote_count = {}
#         for target_id in room.votes.values():
#             vote_count[target_id] = vote_count.get(target_id, 0) + 1
        
#         # Знаходимо гравця з найбільшою кількістю голосів
#         max_votes = max(vote_count.values())
#         eliminated_players = [pid for pid, votes in vote_count.items() if votes == max_votes]
        
#         if len(eliminated_players) == 1:
#             # Ліквідуємо гравця
#             eliminated_id = eliminated_players[0]
#             victim = next((p for p in room.players.values() if p.id == eliminated_id), None)
#         if victim:
#             victim.is_alive = False
#             await room.broadcast(json.dumps({
#                 "type": "player_killed_vote",
#                 "message": f"{victim.name} був повішений за результатами голосування."
#             }))
    
#         # Скидаємо голоси та статус готовності
#         room.votes = {}
#         for p in room.players.values():
#             p.is_ready = False
        
#         # Перевіряємо умови перемоги
#         winner = check_game_end(room)
#         if winner:
#             await room.broadcast(json.dumps({
#                 "type": "game_over",
#                 "winner": winner,
#                 "message": f"Гру завершено! Перемогли { 'мирні' if winner == 'citizens' else 'мафія' }."
#             }))
#             room.phase = "ended"
            
#             db_room = db.query(Room).filter(Room.id == room_id).first()
#             if db_room:
#                 db_room.is_active = False
#                 db.commit()
                
#             await room.broadcast(json.dumps({
#                     "type": "roles_reveal",
#                     "players": [
#                         {"name": p.name, "role": p.role, "is_alive": p.is_alive}
#                         for p in room.players.values()
#                     ]
#                 }))
#             return
        
#         # Збільшуємо раунд та змінюємо фазу
#         room.round += 1
#         room.phase = "night"
#         await room.broadcast(json.dumps({
#             "type": "phase_change",
#             "phase": "night",
#             "round": room.round
#         }))

# @register_handler("toggle_ready")
# async def handle_toggle_ready(websocket: WebSocket, payload: dict, room_id: int, db: Session):
#     room = await verify_room(websocket=websocket, room_id=room_id)
#     if not room:
#         return

#     # Знаходимо гравця за WebSocket
#     player = next((p for p in room.players.values() if p.websocket == websocket), None)
#     if not player:
#         await websocket.send_json({
#             "type": "error",
#             "message": "Гравець не знайдений"
#         })
#         return

#     # Змінюємо статус готовності
#     player.is_ready = not player.is_ready
#     print(f"Player {player.id} ready state changed to {player.is_ready}")

#     # Перевіряємо загальний стан готовності
#     all_ready = all(p.is_ready for p in room.players.values())
#     print(f"All players ready: {all_ready}")

#     # Відправляємо оновлення всім гравцям
#     await room.broadcast({
#         "type": "player_ready",
#         "player_id": player.id,
#         "is_ready": player.is_ready,
#         "players": [{
#             "id": p.id,
#             "name": p.name,
#             "username": p.username,
#             "is_ready": p.is_ready,
#             "is_alive": p.is_alive,
#             "role": p.role,
#             "is_owner": p.id == room.owner
#         } for p in room.players.values()]
#     })
#     print(f"Broadcasted ready state update for player {player.id}")

#     # Відправляємо додаткове повідомлення про загальний стан готовності
#     if all_ready:
#         await room.broadcast({
#             "type": "system",
#             "message": "Всі гравці готові до початку гри!"
#         })

# async def handle_message(websocket: WebSocket, message: dict):
#     try:
#         message_type = message.get('type')
#         payload = message.get('payload', {})
        
#         if message_type == 'chat':
#             username = payload.get('username', 'Гість')
#             message_text = payload.get('message', '')
#             player_id = payload.get('player_id')
            
#             # Знаходимо гравця за ID або ім'ям
#             player = None
#             if player_id:
#                 player = next((p for p in self.players if p.id == player_id), None)
#             if not player:
#                 player = next((p for p in self.players if p.username == username), None)
            
#             if not player:
#                 await websocket.send_json({
#                     'type': 'error',
#                     'payload': {
#                         'message': 'Гравець не знайдений'
#                     }
#                 })
#                 return
            
#             # Відправляємо повідомлення всім гравцям
#             await self.broadcast({
#                 'type': 'chat',
#                 'payload': {
#                     'username': player.username,
#                     'message': message_text,
#                     'timestamp': datetime.now().isoformat()
#                 }
#             })
            
#         elif message_type == 'ready':
#             player = next((p for p in self.players if p.websocket == websocket), None)
#             if player:
#                 player.is_ready = not player.is_ready
#                 await self.broadcast({
#                     'type': 'player_ready',
#                     'payload': {
#                         'username': player.username,
#                         'is_ready': player.is_ready
#                     }
#                 })
                
#         elif message_type == 'start_game':
#             if len(self.players) >= self.min_players:
#                 await self.start_game()
#             else:
#                 await websocket.send_json({
#                     'type': 'error',
#                     'payload': {
#                         'message': 'Недостатньо гравців для початку гри'
#                     }
#                 })
#     except Exception as e:
#         print(f"Помилка обробки повідомлення: {str(e)}")
#         await websocket.send_json({
#             'type': 'error',
#             'payload': {
#                 'message': f'Помилка обробки повідомлення: {str(e)}'
#             }
#         })

# @router.get("/rooms/{room_id}/players")
# async def get_room_players(room_id: int, db: Session = Depends(get_db)):
#     """
#     Отримати список гравців у кімнаті
#     """
#     try:
#         print(f"Getting players for room {room_id}")
        
#         # Перевіряємо чи існує кімната в базі даних
#         db_room = db.query(Room).filter(Room.id == room_id).first()
#         if not db_room:
#             print(f"Room {room_id} not found in database")
#             raise HTTPException(status_code=404, detail="Кімнату не знайдено")

#         # Перевіряємо чи існує кімната в активних кімнатах
#         room = active_rooms.get(room_id)
#         if not room:
#             print(f"Room {room_id} not found in active rooms")
#             # Повертаємо порожній список, якщо кімнати немає в активних
#             return []

#         # Формуємо список гравців
#         players_list = []
#         for player in room.players.values():
#             try:
#                 player_dict = player.to_dict()
#                 players_list.append(player_dict)
#             except Exception as e:
#                 print(f"Error converting player to dict: {str(e)}")
#                 continue

#         print(f"Returning players list for room {room_id}: {players_list}")
#         return players_list

#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Error in get_room_players: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Внутрішня помилка сервера: {str(e)}")

# def get_room(room_id: int):
#     return active_rooms.get(room_id)

# @router.get("/rooms/{room_id}/messages")
# async def get_room_messages(room_id: int, db: Session = Depends(get_db)):
#     """
#     Отримати історію повідомлень кімнати
#     """
#     try:
#         print(f"Getting messages for room {room_id}")
        
#         # Перевіряємо чи існує кімната
#         room = db.query(Room).filter(Room.id == room_id).first()
#         if not room:
#             print(f"Room {room_id} not found")
#             raise HTTPException(status_code=404, detail="Кімнату не знайдено")
            
#         # Отримуємо повідомлення з бази даних
#         messages = db.query(Messages).filter(Messages.room_id == room_id).order_by(Messages.writing_time.desc()).limit(50).all()
#         print(f"Found {len(messages)} messages")
        
#         # Формуємо список повідомлень
#         messages_list = []
#         for msg in reversed(messages):  # Перевертаємо список, щоб старі повідомлення були зверху
#             try:
#                 user = db.query(User).filter(User.id == msg.user_id).first()
#                 messages_list.append({
#                     "id": msg.id,
#                     "message": msg.message,
#                     "username": user.username if user else "Гість",
#                     "created_at": msg.writing_time.isoformat() if msg.writing_time else None
#                 })
#             except Exception as e:
#                 print(f"Error processing message {msg.id}: {str(e)}")
#                 continue
            
#         print(f"Returning {len(messages_list)} messages")
#         return messages_list

#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Error in get_room_messages: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Внутрішня помилка сервера: {str(e)}")

# async def start_game(self):
#     print("Starting game...")
#     if not self.can_start_game():
#         print("Cannot start game: conditions not met")
#         raise ValueError("Cannot start game: conditions not met")
    
#     print("Setting game state...")
#     self.phase = "day"
#     self.round = 1
#     self.is_game_over = False
#     self.night_actions = {
#         "mafia": [],
#         "doctor": None,
#         "detective": None
#     }
#     self.votes = {}
    
#     print("Assigning roles...")
#     self.assign_roles()
    
#     print("Resetting player states...")
#     for player in self.players.values():
#         player.is_ready = False
#         player.is_alive = True
#         print(f"Player {player.id} ({player.name}): role={player.role}, is_alive={player.is_alive}")
    
#     # Відправляємо ролі гравцям
#     for player in self.players.values():
#         try:
#             # Базова інформація про роль
#             role_info = {
#                 "type": "role_assigned",
#                 "role": player.role
#             }
            
#             # Якщо гравець мафія, додаємо інформацію про інших мафій
#             if player.role == "mafia":
#                 other_mafia = [
#                     {"id": p.id, "name": p.name}
#                     for p in self.players.values()
#                     if p.role == "mafia" and p.id != player.id
#                 ]
#                 role_info["other_mafia"] = other_mafia
            
#             await player.websocket.send_json(role_info)
#             print(f"Sent role {player.role} to player {player.id}")
#         except Exception as e:
#             print(f"Error sending role to player {player.id}: {str(e)}")
    
#     # Відправляємо повідомлення про початок гри
#     await self.broadcast({
#         "type": "game_started",
#         "phase": "day",
#         "round": 1,
#         "players": [p.to_dict() for p in self.players.values()]
#     })
    
#     print(f"Game started in room {self.room_id}")

# async def change_phase(self, new_phase):
#     """Зміна фази гри"""
#     self.phase = new_phase
#     await self.broadcast({
#         "type": "phase_change",
#         "phase": new_phase,
#         "round": self.round
#     })
    
#     # Якщо переходимо в нічну фазу
#     if new_phase == "night":
#         # Скидаємо голоси
#         self.votes = {}
#         # Скидаємо статус готовності для нічних дій
#         for player in self.players.values():
#             if player.role in ["mafia", "doctor", "detective"] and player.is_alive:
#                 player.is_ready = False
    
#     # Якщо переходимо в денну фазу
#     elif new_phase == "day":
#         # Скидаємо нічні дії
#         self.night_actions = {
#             "mafia": [],
#             "doctor": None,
#             "detective": None
#         }
#         # Скидаємо статус готовності для голосування
#         for player in self.players.values():
#             if player.is_alive:
#                 player.is_ready = False

# async def check_phase_completion(self):
#     """Перевірка завершення фази та зміна фази"""
#     if self.phase == "day":
#         # Перевіряємо чи всі живі гравці проголосували
#         alive_players = [p for p in self.players.values() if p.is_alive]
#         if len(self.votes) == len(alive_players):
#             # Підраховуємо голоси
#             vote_count = {}
#             for target_id in self.votes.values():
#                 vote_count[target_id] = vote_count.get(target_id, 0) + 1
            
#             # Знаходимо гравця з найбільшою кількістю голосів
#             max_votes = max(vote_count.values())
#             eliminated_players = [pid for pid, votes in vote_count.items() if votes == max_votes]
            
#             if len(eliminated_players) == 1:
#                 # Ліквідуємо гравця
#                 eliminated_id = eliminated_players[0]
#                 self.players[eliminated_id].is_alive = False
                
#                 # Перевіряємо умови перемоги
#                 if self.check_win_condition():
#                     return
                
#                 # Переходимо до ночі
#                 self.round += 1
#                 await self.change_phase("night")
#             else:
#                 # Якщо нічия, переходимо до ночі без ліквідації
#                 self.round += 1
#                 await self.change_phase("night")
    
#     elif self.phase == "night":
#         # Перевіряємо чи всі спеціальні ролі виконали свої дії
#         special_roles = [p for p in self.players.values() 
#                         if p.role in ["mafia", "doctor", "detective"] and p.is_alive]
        
#         if all(p.is_ready for p in special_roles):
#             # Виконуємо нічні дії
#             if self.night_actions["mafia"]:
#                 target_id = self.night_actions["mafia"][0]
#                 if target_id != self.night_actions["doctor"]:
#                     self.players[target_id].is_alive = False
            
#             # Перевіряємо умови перемоги
#             if self.check_win_condition():
#                 return
            
#             # Переходимо до дня
#             await self.change_phase("day")

# async def handle_message(self, websocket, message):
#     """Обробка повідомлень від клієнта"""
#     try:
#         data = json.loads(message)
#         message_type = data.get("type")
        
#         if message_type == "start_game":
#             await self.start_game()
#         elif message_type == "toggle_ready":
#             await self.toggle_ready(websocket, data["payload"]["is_ready"])
#         elif message_type == "vote":
#             await self.handle_vote(websocket, data["payload"])
#         elif message_type == "night_action":
#             await self.handle_night_action(websocket, data["payload"])
#             # Перевіряємо завершення фази після кожної нічної дії
#             await self.check_phase_completion()
#         elif message_type == "chat":
#             await self.broadcast({
#                 "type": "chat",
#                 "username": self.players[websocket].name,
#                 "message": data["payload"]["message"]
#             })
#     except Exception as e:
#         print(f"Error handling message: {str(e)}")
#         await websocket.send_json({
#             "type": "error",
#             "message": str(e)
#         })
