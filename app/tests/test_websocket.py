import pytest
import websockets
import json
from fastapi.testclient import TestClient
from app.main import app
import asyncio

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection():
    # логин/регистрция
    async with client:
        res = client.post("/auth/register", json={"username": "wsuser", "password": "pass"})
        assert res.status_code == 200
        login = client.post("/auth/login", json={"username": "wsuser", "password": "pass"})
        token = login.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        room_res = client.post("/rooms", headers=headers)
        room_id = room_res.json()["room_id"]

    # WS
    uri = f"ws://localhost:8000/ws/{room_id}?token={token}"
    async with websockets.connect(uri) as websocket:
        # сообщение отправить
        message = {"type": "chat", "text": "Hello WebSocket"}
        await websocket.send(json.dumps(message))

        # ехо
        response = await websocket.recv()
        data = json.loads(response)
        assert data["type"] == "chat"
        assert data["text"] == "Hello WebSocket"
