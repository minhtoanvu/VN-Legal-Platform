"""
Tests cho Auth API — pytest-asyncio
Chạy: cd backend && pytest tests/test_auth.py -v
"""
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient, ASGITransport

from app.main import app


# ---------- Register ----------

@pytest.mark.anyio
async def test_register_success(client: AsyncClient):
    """Đăng ký user mới thành công."""
    import uuid
    uid = str(uuid.uuid4())[:8]
    test_email = f"pytest_user_{uid}@test.com"
    resp = await client.post("/auth/register", json={
        "email": test_email,
        "password": "pytest123",
        "full_name": "Pytest User",
        "organization": "Test Org",
    })
    # 201 Created hoặc 200 OK
    assert resp.status_code in (200, 201), f"Got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_email

  
@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient):
    """Đăng ký email trùng → 409 hoặc 400."""
    await client.post("/auth/register", json={
        "email": "dup@test.com",
        "password": "abc123",
        "full_name": "Dup User",
    })
    resp = await client.post("/auth/register", json={
        "email": "dup@test.com",
        "password": "abc123",
        "full_name": "Dup User 2",
    })
    assert resp.status_code in (400, 409), f"Expected error, got {resp.status_code}"


@pytest.mark.anyio
async def test_register_invalid_email(client: AsyncClient):
    """Email sai format → 422."""
    resp = await client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "abc123",
        "full_name": "Bad Email",
    })
    assert resp.status_code == 422

# ---------- Login ----------

@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    """Login thành công trả về token."""
    import uuid
    uid = str(uuid.uuid4())[:8]
    test_email = f"login_test_{uid}@test.com"
    # Đăng ký trước
    await client.post("/auth/register", json={
        "email": test_email,
        "password": "loginpass",
        "full_name": "Login User",
    })
    resp = await client.post("/auth/login", json={
        "email": test_email,
        "password": "loginpass",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient):
    """Login sai password → 401."""
    await client.post("/auth/register", json={
        "email": "wrongpass@test.com",
        "password": "correct",
        "full_name": "Wrong Pass",
    })
    resp = await client.post("/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "WRONG",
    })
    assert resp.status_code == 401


# ---------- /me ----------

@pytest.mark.anyio
async def test_get_me(client: AsyncClient):
    """GET /auth/me với valid token → user info."""
    import uuid
    uid = str(uuid.uuid4())[:8]
    test_email = f"me_test_{uid}@test.com"
    reg = await client.post("/auth/register", json={
        "email": test_email,
        "password": "metest123",
        "full_name": "Me Test",
    })
    token = reg.json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == test_email


@pytest.mark.anyio
async def test_get_me_no_token(client: AsyncClient):
    """GET /auth/me không có token → 401/403."""
    resp = await client.get("/auth/me")
    assert resp.status_code in (401, 403)
