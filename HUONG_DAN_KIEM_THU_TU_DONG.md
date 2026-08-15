# Huong Dan Kiem Thu Tu Dong (Automated Testing Guide)
## AI Legal Intelligence Platform - NCKH 2025-2026

> Muc tieu: Huong dan day du quy trinh kiem thu tu dong tu A-Z.  
> Phu hop cho sinh vien NCKH va ung tuyen vi tri **Automation Tester**.

---

## Muc Luc

1. [Tong quan Chien luoc Kiem thu](#1-tong-quan)
2. [Kien truc Tang Test (Testing Pyramid)](#2-testing-pyramid)
3. [Cai dat Moi truong](#3-cai-dat)
4. [Tang 1 - Unit Test](#4-unit-test)
5. [Tang 2 - Integration Test (pytest + httpx)](#5-integration-test)
6. [Tang 3 - E2E Test (Playwright)](#6-e2e-test)
7. [Chay Toan Bo Test Suite](#7-chay-test)
8. [Doc Bao Cao Coverage](#8-coverage)
9. [Cac Pattern Quan Trong](#9-patterns)
10. [Chien luoc Nang cao](#10-nang-cao)
11. [Checklist Automation Tester](#11-checklist)

---

## 1. Tong Quan

### Hai loai kiem thu trong project nay

| Loai | Cong cu | Muc tieu | Ai thuc hien |
|:-----|:--------|:---------|:------------|
| **Manual Testing** | File Excel `NCKH_TestCase.xlsx` | Kiem tra UI/UX, flow nghiep vu | Tester doc va lam tay |
| **Automated Testing** | pytest + Playwright | Kiem tra logic API, regression, security | May tinh tu chay |

### Nguyen tac AAA (Arrange - Act - Assert)

Moi test case deu phai tuan theo 3 buoc nay:

```python
async def test_login_success(client):
    # ARRANGE: Chuan bi du lieu
    payload = {"email": "user@test.com", "password": "Test@1234"}

    # ACT: Thuc hien hanh dong
    response = await client.post("/auth/login", json=payload)

    # ASSERT: Kiem tra ket qua
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## 2. Testing Pyramid

```
          /\
         /  \     Tang 3: E2E (Playwright)
        / E2E\    - Dieu khien Chrome that
       /------\   - Test giao dien + flow user
      /        \
     /Integration\ Tang 2: Integration Test (pytest + httpx)
    /  Test (API) \ - Goi API that cua FastAPI
   /--------------\ - Test endpoint, request/response, DB
  /                \
 /   Unit Tests     \ Tang 1: Unit Test
/--------------------- - Test ham, service thuan Python
```

**Trong project nay ap dung:**
- **70% Integration Test** - Core value nam o cac API endpoint
- **20% Unit Test** - Test thuat toan BM25, RRF scoring
- **10% E2E** - Test critical path: Login -> Search -> Chat AI

---

## 3. Cai Dat Moi Truong

### 3.1. Cai thu vien Python

```powershell
cd d:\NCKH\backend
.\venv\Scripts\activate
pip install pytest pytest-asyncio httpx anyio faker pytest-cov
```

| Thu vien | Vai tro |
|:---------|:--------|
| `pytest` | Framework test chinh |
| `pytest-asyncio` | Cho phep test ham async/await |
| `httpx` | Gui HTTP request gia lap (khong can server that) |
| `anyio` | Backend async engine cho pytest-asyncio |
| `faker` | Tao du lieu test ngau nhien |
| `pytest-cov` | Do code coverage |

### 3.2. Cai Playwright cho E2E Test

```powershell
pip install playwright
playwright install chromium
```

### 3.3. Cau hinh pytest - backend/pytest.ini

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
filterwarnings =
    ignore::DeprecationWarning
```

---

## 4. Tang 1 - Unit Test

### 4.1. Vi du: Unit Test thuat toan RRF Scoring

File: `tests/unit/test_rrf_scoring.py`

Thuat toan Reciprocal Rank Fusion la core logic cua Hybrid Search.
KHONG can DB, KHONG can network - chi test logic toan hoc.

```python
def rrf_score(bm25_rank: int, semantic_rank: int, k: int = 60) -> float:
    """Cong thuc RRF: score = 1/(k + rank_bm25) + 1/(k + rank_semantic)"""
    return (1 / (k + bm25_rank)) + (1 / (k + semantic_rank))


class TestRRFScoring:

    def test_higher_rank_gives_higher_score(self):
        """Van ban xep hang 1 phai co diem cao hon hang 10."""
        score_top    = rrf_score(bm25_rank=1,  semantic_rank=1)
        score_bottom = rrf_score(bm25_rank=10, semantic_rank=10)
        assert score_top > score_bottom

    def test_combined_ranking_better_than_single(self):
        """Ket hop ca 2 mode phai cho diem cao hon chi 1 mode."""
        score_combined = rrf_score(bm25_rank=1, semantic_rank=1)
        score_single   = 1 / (60 + 1)
        assert score_combined > score_single

    def test_same_rank_symmetric(self):
        """RRF(1,10) phai bang RRF(10,1) vi tinh doi xung."""
        assert rrf_score(1, 10) == rrf_score(10, 1)

    def test_k_parameter_effect(self):
        """k nho hon -> chenh lech diem giua cac hang lon hon."""
        assert rrf_score(1, 1, k=10) > rrf_score(1, 1, k=60)
```

---

## 5. Tang 2 - Integration Test

### 5.1. Co che hoat dong

```
pytest
  -> AsyncClient(transport=ASGITransport(app=fastapi_app))
       -> Gui request HTTP ao thang vao FastAPI
            -> FastAPI: Router -> Service -> Database (that)
                 -> Tra ve response -> pytest kiem tra
```

**Uu diem:** Khong can chay `uvicorn`, test trong bo nho, nhanh va on dinh.

### 5.2. conftest.py - Tim cua Test Suite

File `conftest.py` chua **fixtures** (du lieu/cong cu dung chung) cho tat ca test.
pytest tu dong load file nay - khong can import.

```python
# backend/tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from faker import Faker
from app.main import app

fake = Faker("vi_VN")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    """HTTP Client ao - khong can server that.
    scope="module" -> tao 1 lan dung cho ca 1 file test."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient):
    """Tao user moi va dang nhap -> tra ve header co Bearer token.
    scope="function" -> moi test co user RIENG -> khong bi anh huong lan nhau."""
    email    = f"test_{fake.uuid4()[:8]}@autotest.com"
    password = "AutoTest@1234"

    await client.post("/auth/register", json={
        "email": email, "password": password, "full_name": fake.name()
    })
    login = await client.post("/auth/login", json={
        "email": email, "password": password
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### 5.3. Test Auth API - test_auth.py (hien co san)

| Test | Mo ta | Expected |
|:-----|:------|:---------|
| `test_register_success` | Dang ky thanh cong | 201, co `access_token` |
| `test_register_duplicate_email` | Email da ton tai | 400/409 |
| `test_register_invalid_email` | Email sai format | 422 |
| `test_login_success` | Dang nhap dung | 200, co `access_token` |
| `test_login_wrong_password` | Sai mat khau | 401 |
| `test_get_me` | Lay thong tin user voi token | 200 |
| `test_get_me_no_token` | Khong co token | 401/403 |

### 5.4. Test Workspace API - Vi du nang cao

```python
# backend/tests/test_workspace.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from faker import Faker
from app.main import app

fake = Faker("vi_VN")


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def _make_user(client) -> dict:
    """Helper: tao user moi va tra ve auth headers."""
    email = f"ws_{fake.uuid4()[:8]}@test.com"
    pwd   = "WsTest@1234"
    await client.post("/auth/register", json={
        "email": email, "password": pwd, "full_name": fake.name()
    })
    r     = await client.post("/auth/login", json={"email": email, "password": pwd})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCollectionCRUD:

    @pytest.mark.anyio
    async def test_create_collection(self, client):
        """Tao collection moi -> 200/201, tra ve id va name."""
        headers = await _make_user(client)
        resp    = await client.post("/workspace/collections",
                                    headers=headers,
                                    json={"name": "Luat Lao Dong 2024"})
        assert resp.status_code in (200, 201)
        assert resp.json()["name"] == "Luat Lao Dong 2024"
        assert "id" in resp.json()

    @pytest.mark.anyio
    async def test_data_isolation_between_users(self, client):
        """User A tao collection, User B KHONG duoc thay -> test privacy."""
        headers_a = await _make_user(client)
        headers_b = await _make_user(client)

        await client.post("/workspace/collections",
                          headers=headers_a,
                          json={"name": "Private of User A"})

        resp_b  = await client.get("/workspace/collections", headers=headers_b)
        names_b = [c["name"] for c in resp_b.json()]
        assert "Private of User A" not in names_b

    @pytest.mark.anyio
    async def test_delete_collection(self, client):
        """Tao roi xoa -> khong con trong list."""
        headers = await _make_user(client)
        create  = await client.post("/workspace/collections",
                                    headers=headers,
                                    json={"name": "Will Be Deleted"})
        coll_id = create.json()["id"]

        await client.delete(f"/workspace/collections/{coll_id}", headers=headers)

        list_resp = await client.get("/workspace/collections", headers=headers)
        ids = [c["id"] for c in list_resp.json()]
        assert coll_id not in ids

    @pytest.mark.anyio
    async def test_requires_auth(self, client):
        """Khong co token -> 401."""
        resp = await client.post("/workspace/collections",
                                 json={"name": "No Auth"})
        assert resp.status_code in (401, 403)
```

---

## 6. Tang 3 - E2E Test (Playwright)

### 6.1. Page Object Model (POM) - Tieu chuan cong nghiep

Khong viet selector truc tiep trong test. Phai tao Page Class bao boc logic:

```python
# backend/tests/e2e/pages/login_page.py
from playwright.async_api import Page


class LoginPage:
    """Page Object cho trang Dang nhap.
    Neu UI thay doi, chi sua file nay - tat ca test van chay."""

    URL = "http://localhost:5173"

    def __init__(self, page: Page):
        self.page           = page
        self.email_input    = page.get_by_placeholder("Email")
        self.password_input = page.get_by_placeholder("Mat khau")
        self.login_button   = page.get_by_role("button", name="Dang nhap")
        self.error_message  = page.locator("[class*='error']")

    async def navigate(self):
        await self.page.goto(self.URL)
        await self.page.wait_for_load_state("networkidle")

    async def login(self, email: str, password: str):
        await self.email_input.fill(email)
        await self.password_input.fill(password)
        await self.login_button.click()

    async def get_error_text(self) -> str:
        await self.error_message.wait_for(state="visible", timeout=5000)
        return await self.error_message.text_content()
```

### 6.2. E2E Test Cases - Critical Path + Destructive

```python
# backend/tests/e2e/test_critical_flows.py
"""
Yeu cau: Frontend dang chay tai http://localhost:5173
Chay: pytest tests/e2e/ -v --headed
"""
import pytest
from playwright.async_api import Page, expect

from tests.e2e.pages.login_page import LoginPage

TEST_EMAIL    = "e2e_test@autotest.com"
TEST_PASSWORD = "E2eTest@1234"
BASE_URL      = "http://localhost:5173"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def browser():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        yield b
        await b.close()


@pytest.fixture(scope="function")
async def page(browser):
    """Tab moi cho moi test - dam bao co lap."""
    ctx  = await browser.new_context()
    page = await ctx.new_page()
    yield page
    await ctx.close()


class TestLoginFlow:

    @pytest.mark.anyio
    async def test_login_success_redirects_to_search(self, page: Page):
        """TC-E2E-01 SMOKE TEST: Dang nhap thanh cong -> chuyen den /search."""
        lp = LoginPage(page)
        await lp.navigate()
        await lp.login(TEST_EMAIL, TEST_PASSWORD)
        await expect(page).to_have_url(f"{BASE_URL}/search", timeout=10_000)

    @pytest.mark.anyio
    async def test_wrong_password_shows_error(self, page: Page):
        """TC-E2E-02: Sai mat khau -> hien thi loi."""
        lp = LoginPage(page)
        await lp.navigate()
        await lp.login(TEST_EMAIL, "WrongPassword!")
        err = await lp.get_error_text()
        assert len(err) > 0

    @pytest.mark.anyio
    async def test_protected_route_redirects_without_login(self, page: Page):
        """TC-E2E-03: Truy cap /search chua login -> redirect ve login."""
        await page.goto(f"{BASE_URL}/search")
        await page.wait_for_timeout(2000)
        assert "search" not in page.url or "login" in page.url.lower()


class TestDestructiveScenarios:
    """
    Test cac truong hop 'pha' he thong.
    Day la diem khac biet cua Automation Tester gioi.
    """

    @pytest.mark.anyio
    async def test_sql_injection_does_not_crash(self, page: Page):
        """TC-E2E-SEC-01: SQL injection -> khong crash, khong lo du lieu."""
        lp = LoginPage(page)
        await lp.navigate()
        await lp.login(TEST_EMAIL, TEST_PASSWORD)
        await expect(page).to_have_url(f"{BASE_URL}/search", timeout=10_000)

        search_input = page.get_by_placeholder("Tim kiem")
        await search_input.fill("'; DROP TABLE documents; SELECT '1'='1")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)

        body = await page.locator("body").text_content()
        assert "Internal Server Error" not in body

    @pytest.mark.anyio
    async def test_xss_payload_not_executed(self, page: Page):
        """TC-E2E-SEC-02: XSS payload -> khong execute JavaScript."""
        lp = LoginPage(page)
        await lp.navigate()
        await lp.login(TEST_EMAIL, TEST_PASSWORD)
        await expect(page).to_have_url(f"{BASE_URL}/search", timeout=10_000)

        dialog_appeared = False

        def on_dialog(dialog):
            nonlocal dialog_appeared
            dialog_appeared = True
            dialog.dismiss()

        page.on("dialog", on_dialog)

        search_input = page.get_by_placeholder("Tim kiem")
        await search_input.fill("<script>alert('XSS')</script>")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)

        assert not dialog_appeared, "XSS vulnerability detected!"
```

---

## 7. Chay Test Suite

```powershell
cd d:\NCKH\backend
.\venv\Scripts\activate

# Chay tat ca test
python -m pytest tests/ -v

# Chay 1 file
python -m pytest tests/test_auth.py -v

# Chay 1 test cu the
python -m pytest tests/test_auth.py::test_register_success -v

# Coverage report
python -m pytest tests/ -v --cov=app --cov-report=html
Start-Process "htmlcov\index.html"

# Dung ngay khi fail
python -m pytest tests/ -x -v

# Hien thi print() output
python -m pytest tests/ -v -s

# Chay E2E (can frontend dang chay)
python -m pytest tests/e2e/ -v --headed
```

### Output mau khi PASS

```
================================ test session starts ================================
collected 16 items

tests/test_auth.py::test_register_success              PASSED   [  6%]
tests/test_auth.py::test_register_duplicate_email      PASSED   [ 12%]
tests/test_auth.py::test_login_success                 PASSED   [ 25%]
tests/test_auth.py::test_login_wrong_password          PASSED   [ 31%]
tests/test_search.py::test_keyword_search_basic        PASSED   [ 50%]
...

================================ 16 passed in 4.23s ================================
```

### Output mau khi FAIL

```
FAILED tests/test_auth.py::test_login_wrong_password

>       assert resp.status_code == 401
E       AssertionError: assert 200 == 401

tests/test_auth.py:105: AssertionError
```

**Doc ket qua FAIL:** `assert 200 == 401` = code dang tra ve 200 khi sai mat khau.
Day la bug nghiem trong can sua ngay.

---

## 8. Coverage Report

```powershell
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
Start-Process "htmlcov\index.html"
```

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/routers/auth.py                  45      3    93%
app/routers/search.py                67     12    82%
app/routers/workspace.py            138     45    67%  <- Can bo sung test
app/services/rag_service.py          89     89     0%  <- CHUA CO TEST NAO!
-----------------------------------------------------
TOTAL                               395     159    60%
```

**Muc tieu:**
- >= 80%: Tot, du de nop bao cao NCKH
- 60-79%: Can bo sung
- < 60%: Chua dat tieu chuan

---

## 9. Cac Pattern Quan Trong

### Pattern 1: Parametrize - Test nhieu input 1 ham

```python
@pytest.mark.parametrize("bad_pwd,reason", [
    ("abc",     "qua ngan"),
    ("",        "rong"),
    ("a" * 129, "qua dai"),
])
@pytest.mark.anyio
async def test_invalid_passwords(client, bad_pwd, reason):
    resp = await client.post("/auth/register", json={
        "email": f"t_{id(bad_pwd)}@test.com",
        "password": bad_pwd,
        "full_name": "User"
    })
    assert resp.status_code == 422, f"Failed: {reason}"
```

### Pattern 2: Mock External Service (Gemini API)

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.anyio
async def test_ai_circuit_breaker_on_timeout(client, auth_headers):
    """Gia lap Gemini timeout -> khong can internet, khong ton tien."""
    with patch("app.services.rag_service.gemini_client.generate",
               new_callable=AsyncMock) as mock:
        mock.side_effect = TimeoutError("Gemini timeout")
        resp = await client.post("/ai/chat",
                                 headers=auth_headers,
                                 json={"message": "Test"})
        assert resp.status_code != 500
```

### Pattern 3: Fixture Chaining

```python
@pytest_asyncio.fixture
async def collection_id(client, auth_headers):
    """Tao collection san sang de cac test khac dung."""
    resp = await client.post("/workspace/collections",
                             headers=auth_headers,
                             json={"name": "Fixture Collection"})
    return resp.json()["id"]

# Test nay nhan collection_id da san sang - khong can tao lai
async def test_add_bookmark(client, auth_headers, collection_id):
    resp = await client.post(f"/workspace/collections/{collection_id}/docs",
                             headers=auth_headers,
                             json={"document_id": "some-uuid"})
    assert resp.status_code == 200
```

---

## 10. Chien Luoc Nang Cao

### 10.1. Performance Test - Kiem tra SLA

```python
import time

@pytest.mark.anyio
async def test_bm25_search_under_2_seconds(client):
    """SLA: BM25 phai phan hoi trong < 2000ms."""
    start = time.monotonic()
    resp  = await client.post("/search", json={
        "query": "hop dong lao dong", "mode": "keyword", "limit": 10
    })
    elapsed_ms = (time.monotonic() - start) * 1000

    assert resp.status_code == 200
    assert elapsed_ms < 2000, f"Qua cham: {elapsed_ms:.0f}ms"
    assert resp.json()["took_ms"] < 2000
```

### 10.2. Concurrency Test - 10 request dong thoi

```python
import asyncio

@pytest.mark.anyio
async def test_10_concurrent_searches(client):
    """He thong phai chiu duoc 10 request dong thoi."""
    async def search():
        return await client.post("/search", json={
            "query": "lao dong", "mode": "keyword", "limit": 5
        })

    responses = await asyncio.gather(*[search() for _ in range(10)])

    for i, resp in enumerate(responses):
        assert resp.status_code == 200, f"Request {i} that bai"
```

### 10.3. Security Test - OWASP Top 10

```python
@pytest.mark.parametrize("payload", [
    "' OR '1'='1",
    "'; DROP TABLE users;--",
    "<script>alert(1)</script>",
    "{{7*7}}",
    "../../../etc/passwd",
])
@pytest.mark.anyio
async def test_injection_protection(client, payload):
    """He thong KHONG crash voi cac payload tan cong pho bien."""
    resp = await client.post("/search", json={
        "query": payload, "mode": "keyword"
    })
    assert resp.status_code != 500, f"Server crashed on: {payload}"
    assert resp.status_code in (200, 400, 422)
```

---

## 11. Checklist Automation Tester

### Kien thuc Nen tang
- [ ] Hieu Testing Pyramid (Unit -> Integration -> E2E)
- [ ] Biet giai thich AAA Pattern (Arrange - Act - Assert)
- [ ] Phan biet Mock vs Stub vs Fake
- [ ] Hieu tai sao can Data Isolation giua cac test

### Cong Cu Thuc te
- [ ] Chay duoc pytest va doc output
- [ ] Biet dung conftest.py va fixtures
- [ ] Biet doc Coverage Report (htmlcov/)
- [ ] Biet cai va chay Playwright Python

### Ky Nang Viet Test
- [ ] Viet Integration Test cho REST API (pytest + httpx)
- [ ] Test ca happy path VA negative/edge cases
- [ ] Dung @pytest.mark.parametrize test nhieu input
- [ ] Dung unittest.mock.patch de mock external service
- [ ] Implement Page Object Model cho E2E test

### Kiem Thu Nang Cao
- [ ] Test hieu nang (SLA / Response time voi time.monotonic)
- [ ] Test dong thoi (asyncio.gather)
- [ ] Biet cac payload OWASP Top 10 (SQL injection, XSS, Path Traversal...)
- [ ] Hieu tai sao time.sleep() trong test la anti-pattern

### Tu Duy Cua Mot Tester Gioi
- [ ] Luon hoi: "Cai nay test cai gi? Dieu kien bien nao co the xay ra?"
- [ ] Viet bug report ro rang: Expected vs Actual vs Steps To Reproduce
- [ ] Tu duy "cynical" - luon nghi cach pha he thong, khong chi test happy path

---

## Tai Lieu Tham Khao

| Tai lieu | Link |
|:---------|:-----|
| pytest docs | https://docs.pytest.org |
| pytest-asyncio | https://pytest-asyncio.readthedocs.io |
| Playwright Python | https://playwright.dev/python |
| OWASP Testing Guide | https://owasp.org/www-project-web-security-testing-guide |
| httpx AsyncClient | https://www.python-httpx.org |

---

*Tai lieu duoc tao boi **Antigravity KIT** - QA Automation Engineer Agent*  
*Du an: AI Legal Intelligence Platform - NCKH 2025-2026*
