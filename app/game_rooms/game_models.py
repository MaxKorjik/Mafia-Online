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
    def __init__(self, id, name, websocket):
        self.id = id
        self.name = name
        self.websocket = websocket
        self.is_ready = False
        self.is_alive = True
        self.role = None
        self.vote = None
        self.night_action = None
        print(f"Created player {id} with name {name}")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.name,
            "is_ready": self.is_ready,
            "is_alive": self.is_alive,
            "role": self.role,
            "is_owner": False  # Буде встановлено в GameRoom
        }
    
    def reset(self):
        self.is_ready = False
        self.is_alive = True
        self.role = None
        self.vote = None
        self.night_action = None
        print(f"Reset player {self.id} state")
        
# Клас кімнати гри
class GameRoom:
    def __init__(self, id, name, owner_id, min_players=6, max_players=10, is_private = False):
        self.id = id
        self.name = name
        self.owner = owner_id
        self.min_players = min_players
        self.max_players = max_players
        self.players = {}
        self.phase = "waiting"  # waiting, night, day
        self.round = 0
        self.is_game_over = False
        self.is_private = is_private
        self.night_actions = {
            "mafia": [],
            "doctor": None,
            "detective": None
        }
        self.votes = {}
        print(f"Created game room {id} with name {name}")

    def add_player(self, player):
        if len(self.players) >= self.max_players:
            print(f"Cannot add player {player.id}: room is full")
            return False
        self.players[player.id] = player
        print(f"Added player {player.id} to room {self.id}")
        return True

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            if self.owner == player_id and self.players:
                self.owner = next(iter(self.players))
                print(f"New owner is {self.owner}")
            print(f"Removed player {player_id} from room {self.id}")
            return True
        return False
    
    def get_player(self, player_id):
        return self.players.get(player_id)
    
    def kill_player(self, player_id):
        player = self.get_player(player_id)
        if player:
            player.is_alive = False
            print(f"Player {player_id} was killed")
            return True
        return False

    def to_dict(self):
        players_list = []
        for p in self.players.values():
            p_dict = p.to_dict()
            p_dict["is_owner"] = (p.id == self.owner) # Динамически определяем владельца комнаты
            players_list.append(p_dict)
            
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "phase": self.phase,
            "round": self.round,
            "is_game_over": self.is_game_over,
            "players": players_list
        }

    async def broadcast(self, message):
        print(f"Broadcasting message to {len(self.players)} players in room {self.id}")
        for player in self.players.values():
            try:
                await player.websocket.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to player {player.id}: {str(e)}")
    
    def check_victory(self):
        if not self.is_game_over:
            mafia_count = sum(1 for p in self.players.values() if p.is_alive and p.role == "mafia")
            civilians_count = sum(1 for p in self.players.values() if p.is_alive and p.role != "mafia")
            
            print(f"Victory check: mafia={mafia_count}, civilians={civilians_count}")
            
            if mafia_count == 0:
                return "civilians"
            elif mafia_count >= civilians_count:
                return "mafia"
        return None

    def can_start_game(self) -> bool:
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
        print(f"Starting game in room {self.id}...")
        if not self.can_start_game():
            print("Cannot start game: conditions not met")
            raise ValueError("Cannot start game: conditions not met")
        
        print("Setting game state...")
        self.phase = "night"  # Починаємо з ночі
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
        
        print(f"Game started in room {self.id}")

    def assign_roles(self):
        print(f"Assigning roles in room {self.id}...")
        roles = ["mafia", "mafia", "doctor", "detective", "civilian", "civilian"]
        random.shuffle(roles)
        
        players_list = list(self.players.values())
        for player, role in zip(players_list, roles):
            player.role = role
            print(f"Assigned role {role} to player {player.id} ({player.name})")


