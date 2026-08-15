"""
Tests cho Search API — pytest-asyncio
Chạy: cd backend && pytest tests/test_search.py -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# ---------- Keyword Search ----------

@pytest.mark.anyio
async def test_keyword_search_basic(client: AsyncClient):
    """POST /search keyword mode → results + took_ms."""
    resp = await client.post("/search", json={
        "query": "lao dong",
        "mode": "keyword",
        "limit": 5,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert "took_ms" in data
    assert data["mode"] == "keyword"


@pytest.mark.anyio
async def test_keyword_search_performance(client: AsyncClient):
    """Keyword search phải < 2000ms (SLA: <1s, margin x2 cho test)."""
    resp = await client.post("/search", json={
        "query": "nghi phep",
        "mode": "keyword",
        "limit": 10,
    })
    assert resp.status_code == 200
    assert resp.json()["took_ms"] < 2000, f"Too slow: {resp.json()['took_ms']}ms"


@pytest.mark.anyio
async def test_keyword_search_empty_results(client: AsyncClient):
    """Query không tồn tại → results rỗng, không lỗi."""
    resp = await client.post("/search", json={
        "query": "xyzxyzxyz_not_exist_12345",
        "mode": "keyword",
        "limit": 5,
    })
    assert resp.status_code == 200
    # Không lỗi 500, dù kết quả 0
    assert isinstance(resp.json()["results"], list)


@pytest.mark.anyio
async def test_get_search(client: AsyncClient):
    """GET /search?q=... cũng hoạt động."""
    resp = await client.get("/search?q=lao+dong&mode=keyword&limit=3")
    assert resp.status_code == 200
    assert resp.json()["mode"] == "keyword"


# ---------- Hybrid / Semantic Search ----------

@pytest.mark.anyio
async def test_hybrid_search(client: AsyncClient):
    """Hybrid search trả về kết quả (BM25 fallback nếu chưa có HNSW)."""
    resp = await client.post("/search", json={
        "query": "thu viec toi da bao nhieu ngay",
        "mode": "hybrid",
        "limit": 5,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "hybrid"
    assert isinstance(data["results"], list)


@pytest.mark.anyio
async def test_semantic_search(client: AsyncClient):
    """Semantic search không lỗi (fallback BM25 nếu HNSW chưa ready)."""
    resp = await client.post("/search", json={
        "query": "nghi phep nam bao nhieu ngay",
        "mode": "semantic",
        "limit": 5,
    })
    assert resp.status_code == 200
    assert isinstance(resp.json()["results"], list)


# ---------- Validation ----------

@pytest.mark.anyio
async def test_invalid_mode(client: AsyncClient):
    """Mode không hợp lệ → 422."""
    resp = await client.post("/search", json={
        "query": "test",
        "mode": "invalid_mode",
    })
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_empty_query(client: AsyncClient):
    """Query rỗng → 422."""
    resp = await client.post("/search", json={
        "query": "",
        "mode": "keyword",
    })
    assert resp.status_code == 422


# ---------- Analytics ----------

@pytest.mark.anyio
async def test_analytics_dashboard(client: AsyncClient):
    """GET /analytics/dashboard trả về 5 metrics."""
    resp = await client.get("/analytics/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "kpi" in data
    assert "documents_by_field" in data
    assert "documents_by_type" in data
    assert "documents_by_status" in data
    assert "documents_by_year" in data
    assert data["kpi"]["total_documents"] > 0
