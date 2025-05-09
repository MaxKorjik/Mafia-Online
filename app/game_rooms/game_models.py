import asyncio
import random
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Room
from itertools import count
from fastapi import WebSocket, WebSocketDisconnect

from websockets import broadcast

# Клас гравця, що представляє окремого користувача в грі
class Player:
    def __init__(self, id: int, name: str, websocket: WebSocket = None, room = None):
        self.id = id
        self.name = name
        self.websocket = websocket
        self.room = room
        self.role = None
        self.is_alive = True
        self.is_sleeping = False
        self.is_ready = False
        print(f"Created player {id} with name {name}")

    # Представлення гравця у вигляді словника (для передачі на фронт)
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "is_alive": self.is_alive,
            "is_sleeping": self.is_sleeping,
            "is_ready": self.is_ready,
            "is_owner": self.room and self.id == self.room.owner
        }
        
        
# Клас кімнати гри
class GameRoom:
    def __init__(self, room_id: int, room_name: str, min_players: int, max_players: int, is_private: bool, owner: int):
        self.room_id = room_id
        self.room_name = room_name
        self.min_players = min_players
        self.max_players = max_players
        self.is_private = is_private
        self.owner = owner
        self.players = {}
        self.connections = set()
        self.phase = "waiting"  # waiting, day, night, ended
        self.round = 0
        self.is_game_over = False
        self.night_actions = {
            "mafia": [],
            "doctor": None,
            "detective": None
        }
        self.votes = {}
        print(f"GameRoom initialized: id={room_id}, name={room_name}, owner={owner}")

    def add_player(self, player: Player):
        """Додати гравця до кімнати"""
        if len(self.players) >= self.max_players:
            raise ValueError("Room is full")
        if player.id in self.players:
            raise ValueError("Player already in room")
        
        self.players[player.id] = player
        print(f"Player {player.id} added to room {self.room_id}")
        return player

    def remove_player(self, player: Player):
        """Видалити гравця з кімнати"""
        if player.id in self.players:
            del self.players[player.id]
            print(f"Player {player.id} removed from room {self.room_id}")

    def add_connection(self, websocket: WebSocket):
        """Додати WebSocket з'єднання до кімнати"""
        self.connections.add(websocket)
        print(f"Connection added to room {self.room_id}")

    def remove_connection(self, websocket: WebSocket):
        """Видалити WebSocket з'єднання з кімнати"""
        self.connections.discard(websocket)
        print(f"Connection removed from room {self.room_id}")

    async def broadcast(self, message: dict):
        """Відправити повідомлення всім підключеним клієнтам"""
        if not self.connections:
            print(f"No connections to broadcast to in room {self.room_id}")
            return

        disconnected = set()
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                print(f"Error broadcasting to connection: {str(e)}")
                disconnected.add(connection)

        # Видаляємо відключені з'єднання
        for connection in disconnected:
            self.connections.discard(connection)

    def can_start_game(self) -> bool:
        print(f"Checking if game can start:")
        print(f"- Phase: {self.phase}")
        print(f"- Players count: {len(self.players)}")
        print(f"- Min players required: {self.min_players}")
        print(f"- All players ready: {all(player.is_ready for player in self.players.values())}")
        
        if self.phase != "waiting":
            print("Game cannot start: wrong phase")
            return False
        if len(self.players) < self.min_players:
            print("Game cannot start: not enough players")
            return False
        if not all(player.is_ready for player in self.players.values()):
            print("Game cannot start: not all players are ready")
            return False
        print("Game can start!")
        return True

    def start_game(self):
        print("Starting game...")
        if not self.can_start_game():
            print("Cannot start game: conditions not met")
            raise ValueError("Cannot start game: conditions not met")
        
        print("Setting game state...")
        self.phase = "day"
        self.round = 1
        self.is_game_over = False
        self.night_actions = {
            "mafia": [],
            "doctor": None,
            "detective": None
        }
        self.votes = {}
        
        print("Assigning roles...")
        self.assign_roles()
        
        print("Resetting player states...")
        for player in self.players.values():
            player.is_ready = False
            player.is_alive = True
            print(f"Player {player.id} ({player.name}): role={player.role}, is_alive={player.is_alive}")
        
        print(f"Game started in room {self.room_id}")

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

