import pytest
from httpx import AsyncClient, ASGITransport
import uuid

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Sử dụng chung 1 event loop cho toàn bộ test session (scope="session").
    Tránh lỗi 'Event loop is closed' khi SQLAlchemy engine connection pool cố gắng
    giữ kết nối qua lại giữa các test khác nhau.
    """
    return "asyncio"


@pytest.fixture(scope="function")
async def client():
    """
    Unauthenticated client cho các test không yêu cầu login (VD: /auth).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
async def auth_client(client: AsyncClient):
    """
    Authenticated client cho các test yêu cầu login (VD: /search, /analytics).
    Tự động tạo 1 user ảo, login và gắn JWT token vào headers.
    """
    uid = str(uuid.uuid4())[:8]
    await client.post("/auth/register", json={
        "email": f"test_user_{uid}@test.com",
        "password": "password123",
        "full_name": f"Test User {uid}"
    })
    
    resp = await client.post("/auth/login", json={
        "email": f"test_user_{uid}@test.com",
        "password": "password123"
    })
    token = resp.json().get("access_token")
    
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
