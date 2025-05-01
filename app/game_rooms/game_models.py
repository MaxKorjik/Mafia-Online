import asyncio
import random
from typing import List, Dict

from fastapi import WebSocketDisconnect
from websockets import broadcast

# Клас гравця, що представляє окремого користувача в грі
class Player:
    def __init__(self, name: str, websocket,  id: int = None):
        self.id : int  = id  # Унікальний ідентифікатор користувача
        self.name: str = name  # Ім'я гравця
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
            "is_alive": self.is_alive,
            "is_sleeping": self.is_sleeping,
            "is_ready": self.is_ready
        }
        
        
# Клас кімнати гри
class GameRoom:
    def __init__(self, room_id: int, room_name: str, min_players : int = 6,max_players: int = 6, is_private: bool = False, owner_name : str = None):
        self.room_id = room_id  # Унікальний ID кімнати
        self.room_name = room_name
        self.players: Dict[str, Player] = {}  # Список гравців у кімнаті
        self.owner : str = owner_name  # Ім’я власника кімнати
        self.min_players = min_players
        self.max_players = max_players  # Максимальна кількість гравців
        self.is_private = is_private  # Приватність кімнати
        self.phase = "waiting"  # Поточна фаза гри
        self.round = 0  # Лічильник раундів
        self.lock = asyncio.Lock()  # Блокування для асинхронних операцій
        self.night_actions = {
                "mafia": [],
                "doctor": None,
                "detective": None
            }
        self.votes: Dict[int, int] = {}
        self.is_game_over = False
        
    # Додаємо гравця до кімнати
    async def add_player(self, name: str, websocket, user_id=None):
        if len(self.players) < self.max_players:
            player = Player(name=name, websocket=websocket, id=user_id)
            self.players[name] = player
        else:
            await websocket.send_text(f"Кімната вже заповнена!")

    # Видаляємо гравця з кімнати
    def remove_player(self, name: str):
        if name in self.players:
            del self.players[name]
            
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
    def assign_roles(self):
        roles = ["mafia", "mafia", "doctor", "detective"]  # Наявні спеціальні ролі
        default_role = "citizen"  # Роль за замовчуванням
        
        players_list = list(self.players.values())
        random.shuffle(players_list)  # Перемішуємо гравців для випадкового розподілу ролей

        for i, player in enumerate(players_list):
            if i < len(roles):
                player.role = roles[i]  # Призначаємо спеціальну роль
            else:
                player.role = default_role  # Інші гравці — мирні жителі
                
    def kill_player(self, player_id):
        for p in self.players.values():
            if p.id == player_id:
                p.is_alive = False
                break

