from typing import Dict
import asyncio

from fastapi import WebSocketDisconnect

class Player:
    def __init__(self, name: str, websocket):
        self.name: str = name
        self.websocket = websocket  
        self.role: str = None
        self.is_alive: bool = True
        self.is_sleeping: bool = False
        self.is_ready: bool = False  

    
    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "is_alive": self.is_alive,
            "is_sleeping": self.is_sleeping,
            "is_ready": self.is_ready
        }
        
        
class GameRoom:
    def __init__(self, room_id: int, max_players: int = 6, is_private: bool = False):
        self.room_id = room_id
        self.players: Dict[str, Player] = {}
        self.max_players = max_players
        self.is_private = is_private
        self.phase = "waiting"  # или 'day', 'night', 'vote'
        self.round = 0
        self.lock = asyncio.Lock()
        
    def add_player(self, name: str, websocket):
        if len(self.players) < self.max_players:
            self.players[name] = Player(name=name, websocket=websocket)

    def remove_player(self, name: str):
        if name in self.players:
            del self.players[name]
            
    async def broadcast(self, message: str):
        async with self.lock:
            for player in self.players.values():
                try:
                    await player.websocket.send_text(message)
                except WebSocketDisconnect:
                    return "Client disconected"