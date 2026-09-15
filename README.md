<div align="center">
  <h1>⚖️ AI Legal Intelligence Platform (AILIP)</h1>
  <p><i>Nền tảng tra cứu, phân tích và khai thác tri thức pháp lý bằng AI — Hybrid Search + RAG + Knowledge Graph</i></p>

  <p>
    <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white" alt="Python"></a>
    <a href="#"><img src="https://img.shields.io/badge/FastAPI-005571.svg?logo=fastapi&logoColor=white" alt="FastAPI"></a>
    <a href="#"><img src="https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black" alt="React"></a>
    <a href="#"><img src="https://img.shields.io/badge/PostgreSQL+pgvector-336791.svg?logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
    <a href="#"><img src="https://img.shields.io/badge/Gemini_2.5_Flash-4285F4.svg?logo=google&logoColor=white" alt="Gemini"></a>
    <a href="#"><img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?logo=pytest&logoColor=white" alt="Pytest"></a>
    <a href="#"><img src="https://img.shields.io/badge/Playwright-2EAD33.svg?logo=playwright&logoColor=white" alt="Playwright"></a>
    <a href="#"><img src="https://img.shields.io/badge/GitHub_Actions-2088FF.svg?logo=github-actions&logoColor=white" alt="Actions"></a>
    <img src="https://img.shields.io/badge/version-0.3.0-green.svg" alt="Version">
  </p>
</div>

---

## 📖 Tổng Quan

**AI Legal Intelligence Platform** là hệ thống tra cứu và phân tích pháp lý thông minh, xây dựng theo kiến trúc enterprise-grade phục vụ đề án nghiên cứu khoa học (NCKH).

Hệ thống xử lý hàng nghìn văn bản pháp luật Việt Nam thông qua **Hybrid Search Pipeline** (BM25 + Semantic Vector Search) và **RAG Engine** (Gemini 2.5 Flash + Circuit Breaker), kèm phân tích hợp đồng tự động và Knowledge Graph trực quan.

> **💡 App Preview:**
> <p align="center">
>   <img src="./docs/image copy 2.png" width="100%" alt="AILIP Search Demo">
>   <br>
>   <i>Giao diện màn hình chính</i>
> </p>

---

## ✨ Tính Năng Chính

| Tính năng | Mô tả |
|-----------|-------|
| 🔍 **Hybrid Search** | BM25 full-text + Semantic (pgvector HNSW) kết hợp bằng RRF |
| 🤖 **AI Chat (RAG)** | Hỏi đáp pháp luật streaming, trích dẫn nguồn, chống hallucination |
| 📜 **Contract Analysis** | Phân tích rủi ro hợp đồng PDF/DOCX theo 4 bước Chain-of-Thought |
| 🕸️ **Knowledge Graph** | Trực quan hoá quan hệ giữa các văn bản (Vis.js + BFS traversal) |
| 📊 **Analytics Dashboard** | Thống kê xu hướng lập pháp: PageRank, Louvain Clustering, Heatmap |
| 📁 **Workspace** | Bookmark, ghi chú, collection cá nhân |
| 🛡️ **Admin Panel** | Quản lý user, phân quyền role, CRUD văn bản |

---

## 🏗️ Kiến Trúc Hệ Thống

```mermaid
graph TD
    UI[Frontend: React + Vite] -->|REST & SSE| API[Backend: FastAPI]
    API --> DB[(PostgreSQL + pgvector)]
    API --> CB{Circuit Breaker}
    CB -->|Protected Call| LLM[Gemini 2.5 Flash]

    subgraph Search Pipeline
        BM25[BM25 Full-Text] --> RRF[RRF Fusion]
        SEM[Semantic HNSW] --> RRF
    end
    API --> Search Pipeline

    subgraph QAOps [Automated QA Pipeline]
        GH[GitHub Actions] --> Pytest[Pytest: API / Unit]
        GH --> PL[Playwright: E2E UI]
    end
```

---

## 📂 Cấu Trúc Project

```
NCKH/
├── backend/                   # FastAPI Backend
│   ├── app/
│   │   ├── core/              # Config, DB, Security, Dependencies, Circuit Breaker
│   │   ├── models/            # SQLAlchemy ORM Models (User, Document, Workspace)
│   │   ├── routers/           # API Endpoints (auth, search, ai, documents, ...)
│   │   ├── schemas/           # Pydantic Request/Response Schemas
│   │   ├── services/          # Business Logic (RAG, BM25, Semantic, Graph, ...)
│   │   └── main.py            # FastAPI Application Entry Point
│   ├── alembic/               # Database Migrations
│   ├── data/                  # Data dumps & ETL outputs
│   ├── logs/                  # Application & Error Logs
│   ├── scripts/               # RAG Benchmarks, ETL scripts
│   ├── tests/                 # Pytest Suite (API + Unit + Performance)
│   ├── requirements.txt
│   ├── pyproject.toml         # Ruff linter config
│   └── alembic.ini
├── frontend/                  # React + Vite Frontend
│   ├── src/
│   │   ├── components/        # UI Components (Chat, Search, Graph, ...)
│   │   ├── hooks/             # Custom React Hooks
│   │   ├── pages/             # Page-level Components
│   │   ├── services/          # API client (Axios)
│   │   └── types/             # TypeScript Type Definitions
│   ├── e2e/                   # Playwright E2E Tests
│   └── package.json
├── docs/                      # Tài liệu phân tích, thiết kế, báo cáo
├── tests_e2e/                 # Playwright E2E Automation (Backend-driven)
├── docker-compose.yml         # PostgreSQL + pgvector container
├── start_dev.ps1              # Windows: Script khởi động toàn bộ stack
└── .env.example               # Template cấu hình môi trường
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### Yêu Cầu Hệ Thống

| Công cụ | Phiên bản | Ghi chú |
|---------|-----------|---------|
| Python | 3.11+ | Bắt buộc |
| Node.js | 18+ | Bắt buộc cho Frontend |
| Docker Desktop | Latest | Để chạy PostgreSQL |
| Git | Latest | |
| RAM | ≥ 8GB | Embedding model cần ~2GB RAM |

---

### Bước 1 — Clone Repository

```bash
git clone <repository-url>
cd NCKH
```

---

### Bước 2 — Cấu Hình Môi Trường

```bash
# Copy file cấu hình mẫu
cp .env.example backend/.env

# Mở file và điền thông tin thực tế
```

Chỉnh sửa `backend/.env`:

```dotenv
# Database
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=legal_db
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/legal_db

# JWT (đổi SECRET_KEY thành chuỗi ngẫu nhiên mạnh)
SECRET_KEY=change-me-to-a-long-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google Gemini API Key — lấy tại https://aistudio.google.com/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Embedding (tự động download khi request đầu tiên)
EMBEDDING_MODEL=bkai-foundation-models/vietnamese-bi-encoder
```

---

### Bước 3 — Khởi Động Database

```bash
# Khởi động PostgreSQL + pgvector trong Docker
docker-compose up -d

# Kiểm tra container đã healthy chưa
docker ps
```

Chờ khoảng 10-15 giây để PostgreSQL khởi động xong.

---

### Bước 4 — Cài Đặt Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Kích hoạt venv (Linux/macOS)
# source venv/bin/activate

# Cài dependencies (bao gồm PyTorch CPU)
pip install -r requirements.txt

# Tạo bảng DB từ migrations
alembic upgrade head
```

> **⚠️ Lưu ý:** `requirements.txt` tải PyTorch CPU (~500MB) và các AI libraries. Lần đầu cài sẽ mất 5-15 phút tùy tốc độ mạng.

---

### Bước 5 — Chạy Backend

```bash
# Trong thư mục backend/, với venv đã kích hoạt
# (Lưu ý: Không dùng cờ --reload để tiết kiệm RAM, tránh lỗi MemoryError)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Kiểm tra hoạt động:
- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **ReDoc:** http://localhost:8000/redoc

---

### Bước 6 — Cài Đặt & Chạy Frontend

```bash
cd frontend

# Cài dependencies
npm install

# Chạy dev server
npm run dev
```

**Frontend:** http://localhost:5173

---

### ⚡ Quick Start (Windows — Chạy 1 lệnh)

Thay vì chạy từng bước thủ công, dùng script tự động:

```powershell
# Từ thư mục gốc của project
.\start_dev.ps1
```

Script sẽ tự động:
1. Kiểm tra và mở Docker Desktop
2. Khởi động PostgreSQL container
3. Chờ container healthy
4. Apply Alembic migrations
5. Khởi động FastAPI server

---

## 🗃️ Nạp Dữ Liệu Văn Bản Pháp Luật (ETL)

Sau khi backend chạy, cần nạp dữ liệu vào database:

```bash
cd backend

# Chạy toàn bộ pipeline (Download -> Normalize -> Load DB -> Chunking)
python scripts/etl/run_full_etl.py

# Tạo Vector Embedding (768D)
python scripts/etl/embedder.py

# Tạo chỉ mục không gian HNSW cho pgvector
python scripts/etl/build_index.py
```

> **⚠️ Lưu ý:** Build embeddings có thể mất 30-60 phút tùy số lượng văn bản và cấu hình máy (chạy trên CPU).

---

## 🧪 Chạy Test Suite

### Backend Tests (Pytest)

```bash
cd backend

# Chạy tất cả tests
pytest tests/ -v

# Chạy kèm coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Chạy 1 module cụ thể
pytest tests/test_auth.py -v
pytest tests/test_search.py -v
```

### Performance / Load Testing (Locust)

```bash
cd backend

# Mở Locust Web UI tại http://localhost:8089
locust -f tests/performance/locustfile.py
```

### E2E Browser Automation (Playwright)

```bash
cd frontend

# Cài Playwright browsers (lần đầu)
npx playwright install

# Chạy E2E tests
npx playwright test

# Chạy với UI mode (xem trực tiếp)
npx playwright test --ui
```

### RAG Benchmark (Đánh giá AI Accuracy)

```bash
cd backend

# Chạy benchmark RAG pipeline với test set 100 queries
python scripts/benchmark_rag.py
```

Kết quả đạt được (trên bộ dữ liệu vàng `eval_qa_laodong.json`):

| Metric | Score | Target |
|--------|-------|--------|
| Hit@5 | **1.0000** 🚀 | ≥ 0.85 |
| MRR@5 | **0.4167** | ≥ 0.40 |
| Faithfulness | **0.9600** 🚀 | ≥ 0.90 |
| Answer Relevancy | **0.8500** | ≥ 0.85 |

---

## 🔧 Linter & Code Quality

```bash
cd backend

# Kiểm tra lỗi (Ruff)
ruff check app/

# Tự động fix các lỗi có thể fix
ruff check app/ --fix

# Format code
ruff format app/
```

---

## 🌐 API Endpoints Tổng Quan

| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| `POST` | `/auth/register` | Đăng ký tài khoản |
| `POST` | `/auth/login` | Đăng nhập, lấy JWT |
| `POST` | `/search` | Hybrid Search (BM25 + Semantic) |
| `POST` | `/ai/chat` | AI Chat Streaming (RAG) |
| `POST` | `/ai/summarize` | Tóm tắt văn bản |
| `POST` | `/contract/analyze` | Phân tích rủi ro hợp đồng |
| `GET`  | `/documents/{id}` | Chi tiết văn bản |
| `GET`  | `/graph/{id}` | Knowledge Graph của văn bản |
| `GET`  | `/analytics/dashboard` | Dashboard thống kê |
| `GET`  | `/admin/users` | Quản lý người dùng (Admin) |

Xem đầy đủ tại **Swagger UI:** http://localhost:8000/docs

---

## 🎯 Role-Specific Guides

* 🧪 **[QA & Testing Strategy](./docs/TESTING_GUIDE.md)**: Test matrix, E2E Automation, và SLAs.
* 🤖 **[AI/ML Development Guide](./docs/AI_DEVELOPMENT.md)**: RAG Pipeline, anti-hallucination prompts, và đánh giá toán học.
* 📊 **[Business & Analytics Guide](./docs/BUSINESS_GUIDE.md)**: Use cases, dataset overview, KPIs, và Graph Data Mining.
* 🏗️ **[Deployment & Infrastructure](./docs/DEPLOYMENT_GUIDE.md)**: Production checklist, CI/CD, và scaling strategies.

---

## 🔥 Highlights Kỹ Thuật

### 1. 🛡️ QA Architecture (Test Pyramid)
- **Unit & API Tests:** `pytest` với Async Mocking, Database Fixtures, AAA Pattern — Coverage: **52%**
- **E2E Tests:** Playwright tự động hoá UI theo luồng người dùng thực
- **Performance:** Locust kiểm tra 100+ concurrent users, phát hiện bottleneck Bcrypt
- **AI Evaluation:** RAGAs benchmark — MRR@5, Hit@5, Faithfulness, Answer Relevancy
- **CI/CD:** GitHub Actions tự động chạy tests mỗi PR

### 2. 🧠 Data Mining & AI
- **PageRank:** Xác định các "văn bản rễ" được tham chiếu nhiều nhất
- **Louvain Community Detection:** Phân cụm văn bản pháp lý liên quan
- **Hybrid Vector Search:** BM25 + pgvector HNSW (Cosine Similarity, 768D)
- **Anti-Hallucination RAG:** Strict prompting + inline citations + Circuit Breaker
- **Chain-of-Thought Contract Analysis:** 4-step CoT + Self-Reflection loop

### 3. ⚡ Backend Resilience
- **Circuit Breaker Pattern:** State machine tự động ngắt kết nối LLM khi timeout/lỗi
- **Async I/O:** FastAPI + SQLAlchemy AsyncSession + SSE streaming
- **Rate Limiting:** SlowAPI bảo vệ endpoint AI (15 req/phút)
- **Clean Architecture:** Router → Service → Repository, SRP enforcement

---

## ⚖️ License & Copyright

**© 2026. All Rights Reserved.**

This project is **Proprietary**. You may not copy, distribute, modify, or use this source code without explicit written permission. See `LICENSE` for details.

---

<div align="center">
  <i>Engineered with strict adherence to Clean Code, QA Best Practices, and Modern AI Patterns.</i>
  <br>
  <b>NCKH — Trường Đại học Mở TP. Hồ Chí Minh — HK3 2025-2026</b>
</div>
