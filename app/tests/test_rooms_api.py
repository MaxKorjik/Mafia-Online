import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_and_join_room():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        
        await ac.post("/auth/register", json={"username": "player1", "password": "pass"})
        login_res = await ac.post("/auth/login", json={"username": "player1", "password": "pass"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # зделать руму
        res_create = await ac.post("/rooms", headers=headers)
        assert res_create.status_code == 200
        room_id = res_create.json()["room_id"]

        res_join = await ac.post(f"/rooms/{room_id}/join", headers=headers)
        assert res_join.status_code == 200

        res_join_bad = await ac.post("/rooms/invalid_id/join", headers=headers)
        assert res_join_bad.status_code == 404
