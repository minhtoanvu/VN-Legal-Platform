# 🧪 QA & Testing Strategy

This document outlines the comprehensive quality assurance and testing strategy for the AI Legal Intelligence Platform (AILIP).

## 1. Test Coverage Matrix

Our testing architecture strictly follows the **Test Pyramid**, ensuring maximum reliability from individual functions up to the user interface.

| Module/Feature | Unit Test (Pytest) | Integration (Pytest) | E2E (Playwright) | Load Test (Locust) |
|----------------|--------------------|----------------------|------------------|--------------------|
| **Authentication** | ✅ | ✅ | ✅ | ✅ |
| **Hybrid Search** | ✅ | ✅ | ✅ | ✅ |
| **AI Assistant (RAG)** | ✅ (Mocked LLM) | ✅ (Real Stream) | ❌ (WIP) | ⚠️ (Rate Limited) |
| **Contract Analysis** | ✅ | ✅ | ⚠️ | ❌ |
| **Workspace/Notes** | ✅ | ✅ | ✅ | ❌ |

## 2. Testing Environments

- **Backend API:** Tested primarily using `pytest` combined with `pytest-asyncio` for asynchronous endpoints. Database interactions are rolled back automatically using isolated fixtures.
- **Frontend UI:** Tested using `Playwright` to simulate real-world user workflows (Login, Search, Note-taking).
- **Performance:** Tested using `Locust`, capable of simulating 100+ concurrent users against the FastApi server.

## 3. How to Write New Tests (Guidelines)

### A. Backend Integration Tests
1. **Use Fixtures:** Always use the `auth_client` fixture in `backend/tests/conftest.py` for testing protected routes.
2. **Mocking External APIs:** For AI endpoints, use the `monkeypatch` fixture to mock the Gemini LLM calls to prevent burning API quotas during CI/CD.
3. **Reference:** See `backend/tests/test_search.py` for a standard template.

### B. E2E Tests (Playwright)
1. Write tests in `tests_e2e/tests/`.
2. Follow the Page Object Model (POM) pattern for maintainability (place locators in `tests_e2e/pages/`).

## 4. Known Issues, SLAs & Benchmarks

### Service Level Agreements (SLAs)
- **BM25 / Keyword Search Latency:** `< 2000ms` (Target: `< 1s`)
- **Semantic / Vector Search Latency:** `< 5000ms`
- **RAG Generation Time to First Token (TTFT):** `< 3s`

### Known Bottlenecks
- **Authentication:** `bcrypt` hashing introduces a CPU bottleneck when simulated with >100 concurrent logins via Locust. 
- **Solution:** A `ThreadPoolExecutor` has been proposed for production to offload CPU-bound hashing from the main Async loop.
