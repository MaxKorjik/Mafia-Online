import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Регистрация
        res = await ac.post("/auth/register", json={"username": "testuser", "password": "testpass"})
        assert res.status_code == 200
        assert res.json()["message"] == "User registered successfully"

        # Регистарция одного и того же чела
        res_dup = await ac.post("/auth/register", json={"username": "testuser", "password": "testpass"})
        assert res_dup.status_code == 400

        # Логин
        res_login = await ac.post("/auth/login", json={"username": "testuser", "password": "testpass"})
        assert res_login.status_code == 200
        assert "access_token" in res_login.json()
