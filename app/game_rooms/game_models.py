import asyncio
import random
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Room
from itertools import count
from app.characters import Surgeon, Teacher, TheaterActor, SciFiWriter,  ExSoldier,  MechanicalEngineer, Agronomist, ChildPsychologist, Pharmacist, Programmer, Event, super_events, mini_events
from fastapi import WebSocketDisconnect
from websockets import broadcast
from dataclasses import asdict
# Клас гравця, що представляє окремого користувача в грі
class Player:
    def __init__(self, name: str, websocket,  id: int = None):
        self.id : int  = id  # Унікальний ідентифікатор користувача
        self.name: str = name  # Ім'я гравця
        self.character = None
        self.websocket = websocket  # WebSocket з'єднання
        self.role: str = "citizen"  # Роль у грі за замовчуванням — мирний житель
        self.have_resist : bool = False  # Чи є захист від вбивства
        self.is_alive: bool = True  # Статус життя
        self.is_sleeping: bool = False  # Статус "спить" для нічних фаз
        self.is_ready: bool = False  # Чи готовий до гри

    # Представлення гравця у вигляді словника (для передачі на фронт)
    def to_dict(self):
        return {
            "id" : self.id,
            "name": self.name,
            "role": self.role,
            "character": asdict(self.character),
            "is_alive": self.is_alive,
            "is_sleeping": self.is_sleeping,
            "is_ready": self.is_ready
        }
        
        
# Клас кімнати гри
class GameRoom:
    def __init__(self, room_id: int, room_name: str, min_players : int = 6,max_players: int = 6, is_private: bool = False, owner_name : str = None):
        self.room_id = room_id  # Унікальний ID кімнати
        self.room_name = room_name
        self.guest_id_counter = count(-1, -1)
        self.players: Dict[str, Player] = {}  # Список гравців у кімнаті
        self.owner : str = owner_name  # Ім’я власника кімнати
        self.min_players = min_players
        self.max_players = max_players  # Максимальна кількість гравців
        self.is_private = is_private  # Приватність кімнати
        self.phases = ["waiting", "day", "vote", "night"]
        self.phase_index = 0
        self.phase = self.phases[self.phase_index]
        self.round = 0  # Лічильник раундів
        self.lock = asyncio.Lock()  # Блокування для асинхронних операцій
        self.night_actions = {
                "mafia": [],
                "doctor": None,
                "detective": None
            }
        self.event_history = []
        self.event_generated = False
        self.votes: Dict[int, int] = {}
        self.is_game_over = False
        
    # Додаємо гравця до кімнати
    async def add_player(self, name: str, websocket, user_id=None, db : Session = None):
        if len(self.players) < self.max_players:
            if user_id:
                player_id = user_id
            else:
                player_id = next(self.guest_id_counter)

            player = Player(name=name, websocket=websocket, id=player_id)
            self.players[name] = player
            if db:
                room_in_db = db.query(Room).filter(Room.id == self.room_id).first()
                if room_in_db:
                    room_in_db.players_number = len(self.players)
                    db.commit()
            print(f"[Room {self.room_id}] Додано гравця: {name} (ID: {player_id})")
        else:
            await websocket.send_text(f"Кімната вже заповнена!")

    # Видаляємо гравця з кімнати
    def remove_player(self, name: str, db : Session = None):
        if name in self.players:
            del self.players[name]
        if db:
            room_in_db = db.query(Room).filter(Room.id == self.room_id).first()
            if room_in_db:
                room_in_db.players_number = len(self.players)
                db.commit()
            
    # Розсилаємо повідомлення усім гравцям у кімнаті
    async def broadcast(self, message: str):
        disconnected = []
        async with self.lock:
            for name, player in self.players.items():
                try:
                    await player.websocket.send_text(message)
                except WebSocketDisconnect:
                    # Якщо з'єднання втрачено, запам’ятовуємо, кого видалити
                    disconnected.append(name)

        # Видаляємо гравців з розірваним з'єднанням
        for name in disconnected:
            self.remove_player(name)
                
    # Призначаємо ролі гравцям випадковим чином
    def assign_roles_and_characters(self):
        roles = ["mafia", "mafia", "doctor", "detective"]  # Наявні спеціальні ролі
        characters = [Surgeon, Teacher, TheaterActor, SciFiWriter,  ExSoldier,  MechanicalEngineer, Agronomist, ChildPsychologist, Pharmacist, Programmer]
        default_role = "citizen"  # Роль за замовчуванням
        
        players_list = list(self.players.values())
        random.shuffle(players_list)  # Перемішуємо гравців для випадкового розподілу ролей

        assigned_characters = random.sample(characters, len(players_list))

        for i, player in enumerate(players_list):
            player.role = roles[i] if i < len(roles) else default_role
            player.character = assigned_characters[i]()
                
    def kill_player(self, player_id):
        for p in self.players.values():
            if p.id == player_id:
                p.is_alive = False
                break

    async def generate_super_event(self):
        if self.phase != "night" or self.event_generated:
            return None
        self.event_generated = True 
        
        
        is_super_event = random.random() < 0.25 # Супер івент - івент який може прямо вказати на вбивцю
        is_real = random.random() < 0.6 # Чи реальноо - прапорець який визначае з яким шансом супер івент буде вказувати на правильного гравця

        if is_super_event:
            if is_real:
                mafia_players = [p for p in self.players.values() if p.role == "mafia"]
                if not mafia_players:
                    return None
                target = random.choice(mafia_players)
            else:
                innocent_players = [p for p in self.players.values() if p.role != "mafia"]
                if not innocent_players:
                    return None
                target = random.choice(innocent_players)
                
            character_name = target.character.name if target.character else None
            matched_events = [e for e in super_events if e.related_to == character_name]
            
            
            if matched_events:
                selected_event = random.choice(matched_events)
                self.event_history.append(selected_event.description)
                return {
                    "type": "super_event",
                    "description": selected_event.description
                }
                
        return None
    
    async def generate_mini_event(self):
        if self.phase == "night":

            if random.random() < 0.8: # Звичайний івент по типу "Почув шелест/розмову вночі"
                observer = random.choice(list(self.players.values()))
                flavor = random.choice(mini_events)
                self.event_history.append(flavor)
                await observer.websocket.send_json({
                    "type": "mini_event",
                    "mini_event": flavor
                })
                
                
                
    def next_phase(self):
        if self.phase == "waiting":
            self.phase_index = 1  # skip to "day"
        else:
            self.phase_index = (self.phase_index + 1) % len(self.phases[1:])
        self.phase = self.phases[self.phase_index]
        return self.phase

