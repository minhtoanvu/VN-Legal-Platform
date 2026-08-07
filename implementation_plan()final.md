# Hệ thống Tra Cứu & Phân Tích Văn Bản Pháp Luật Việt Nam
## Vietnamese Legal Intelligence Platform (VN-LIP)

Xây dựng một nền tảng phân tích và tra cứu văn bản pháp luật Việt Nam hiện đại, kết hợp kiến trúc RAG (Retrieval-Augmented Generation), Knowledge Graph, Dashboard phân tích thống kê và **Workspace cá nhân**. Dữ liệu được lấy từ bộ dataset **153.420 văn bản pháp luật** đã có sẵn trên máy.

---

## 📐 Kiến Trúc Hệ Thống Tổng Thể

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React + Vite)                        │
│ Tra cứu │ AI Chat │ Knowledge Graph │ Dashboard │ Timeline │ Workspace  │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │ HTTPS / REST API / JWT Auth
┌──────────────────────▼──────────────────────────────────────────────────┐
│                       BACKEND (FastAPI + Python)                        │
│ /auth │ /search │ /chat │ /graph │ /stats │ /documents │ /workspace     │
└──┬──────────────┬──────────────┬───────────────┬────────────┬───────────┘
   │              │              │               │            │
   ▼              ▼              ▼               ▼            ▼
PostgreSQL   pgvector DB    Neo4j (Graph)   Redis (Cache)  PostgreSQL
(Metadata)   (Embeddings)   (Relations)    (Sessions)     (Users/Notes)
```

**Lý do chọn công nghệ:**
- **FastAPI**: Async, tự sinh OpenAPI docs, type-safe, cực nhanh
- **PostgreSQL + pgvector**: 1 DB duy nhất cho cả structured data và vector search → đơn giản hoá deployment
- **React + Vite**: HMR nhanh, ecosystem lớn (Recharts, Vis.js, TanStack Query)
- **Redis**: Cache API response giảm tải DB khi query lặp lại

> [!IMPORTANT]
> **Quyết định kiến trúc quan trọng:** Thay vì dùng Neo4j riêng (cần license, phức tạp), ta sẽ **lưu graph trong PostgreSQL** dưới dạng adjacency list (`relationships` table) và dùng **recursive CTE queries** để traverse. Tiết kiệm một service, giảm độ phức tạp deployment đáng kể.

---

## 📦 Cấu Trúc Project Mới

```
vn-legal-platform/
├── backend/
│   ├── app/
│   │   ├── api/               # Route handlers
│   │   │   ├── auth.py        # Đăng nhập, đăng ký JWT
│   │   │   ├── documents.py   # CRUD + search
│   │   │   ├── chat.py        # RAG AI assistant
│   │   │   ├── graph.py       # Knowledge graph
│   │   │   ├── stats.py       # Dashboard analytics
│   │   │   └── workspace.py   # Bookmark, ghi chú cá nhân
│   │   ├── core/
│   │   │   ├── config.py      # Settings (env vars)
│   │   │   ├── security.py    # JWT hashing, dependencies
│   │   │   └── database.py    # DB connection (SQLAlchemy async)
│   │   ├── models/
│   │   │   ├── user.py        # SQLAlchemy ORM (User, Bookmark, Note)
│   │   │   ├── document.py    # SQLAlchemy ORM models
│   │   │   └── schemas.py     # Pydantic response schemas
│   │   ├── services/
│   │   │   ├── search.py      # Full-text + vector search logic
│   │   │   ├── rag.py         # RAG pipeline (embed → retrieve → generate)
│   │   │   └── graph.py       # Graph traversal queries
│   │   └── main.py            # FastAPI app entry point
│   ├── scripts/
│   │   ├── ingest_metadata.py # Load metadata.parquet → PostgreSQL
│   │   ├── ingest_relations.py# Load relationships.parquet → PostgreSQL
│   │   └── ingest_embeddings.py# Chunk content → embed → pgvector
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Full pages
│   │   │   ├── Search.tsx     # Trang tra cứu
│   │   │   ├── Chat.tsx       # AI Legal Assistant
│   │   │   ├── Graph.tsx      # Knowledge Graph viewer
│   │   │   ├── Dashboard.tsx  # Analytics dashboard
│   │   │   └── Document.tsx   # Chi tiết văn bản
│   │   ├── hooks/             # Custom React hooks
│   │   └── lib/               # API client, utils
│   └── package.json
├── docker-compose.yml         # Orchestrate all services
└── README.md
```

---

## 🗓️ Kế Hoạch Thực Hiện Chi Tiết (7 Giai Đoạn)

---

### GIAI ĐOẠN 1 — Thiết Lập Infrastructure & Data Ingestion
**Ước tính: 2-3 ngày**

#### Bước 1.1 — Khởi tạo project
- Tạo thư mục `vn-legal-platform/`
- Khởi tạo Git repository (`git init`) + `.gitignore` (bỏ `*.parquet`, `*.env`, `__pycache__`)
- Tạo `docker-compose.yml` với 3 service: `postgres`, `redis`, `backend`
- Tạo `backend/requirements.txt`:
  ```
  fastapi, uvicorn, sqlalchemy[asyncio], asyncpg
  pgvector, pandas, pyarrow, sentence-transformers
  openai, redis, python-dotenv, beautifulsoup4
  ```

#### Bước 1.2 — Thiết kế Database Schema

```sql
-- Bảng chính chứa metadata
CREATE TABLE documents (
    id              BIGINT PRIMARY KEY,
    title           TEXT NOT NULL,
    so_ky_hieu      VARCHAR(100),
    ngay_ban_hanh   DATE,
    loai_van_ban    VARCHAR(100),
    ngay_co_hieu_luc DATE,
    ngay_het_hieu_luc DATE,
    nganh           TEXT,
    linh_vuc        TEXT,
    co_quan_ban_hanh TEXT,
    nguoi_ky        TEXT,
    tinh_trang_hieu_luc VARCHAR(100),
    -- Full-text search vector (auto-generated)
    search_vector   tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(so_ky_hieu,''))
    ) STORED
);

-- Index cho full-text search
CREATE INDEX idx_documents_fts ON documents USING GIN(search_vector);
CREATE INDEX idx_documents_loai ON documents(loai_van_ban);
CREATE INDEX idx_documents_linh_vuc ON documents(linh_vuc);
CREATE INDEX idx_documents_ngay ON documents(ngay_ban_hanh);
CREATE INDEX idx_documents_hieu_luc ON documents(tinh_trang_hieu_luc);

-- Bảng quan hệ giữa văn bản
CREATE TABLE relationships (
    doc_id      BIGINT REFERENCES documents(id),
    other_doc_id BIGINT,
    relationship VARCHAR(200),
    PRIMARY KEY (doc_id, other_doc_id, relationship)
);
CREATE INDEX idx_rel_doc ON relationships(doc_id);
CREATE INDEX idx_rel_other ON relationships(other_doc_id);

-- Bảng chunks + vector embeddings (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE document_chunks (
    id          SERIAL PRIMARY KEY,
    doc_id      BIGINT REFERENCES documents(id),
    chunk_index INT,
    chunk_text  TEXT,
    embedding   vector(768)  -- PhoBERT / multilingual-e5 dimension
);
CREATE INDEX idx_chunks_doc ON document_chunks(doc_id);
CREATE INDEX idx_chunks_embedding ON document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Bảng Người dùng & Workspace
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user'
);

CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    doc_id BIGINT REFERENCES documents(id),
    collection_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    doc_id BIGINT REFERENCES documents(id),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Bước 1.3 — Scripts nạp dữ liệu

**`scripts/ingest_metadata.py`** (chạy trước, nhanh):
- Đọc `data/metadata.parquet` (153.420 rows)
- Batch insert vào bảng `documents` (batch size 1000)
- Parse cột ngày tháng sang kiểu DATE
- Ước tính: **~5 phút**

**`scripts/ingest_relations.py`** (chạy tiếp):
- Đọc `data/relationships.parquet` (897.890 rows)
- Batch insert vào bảng `relationships`
- Ước tính: **~10 phút**

**`scripts/ingest_embeddings.py`** (chạy cuối, nặng nhất):
- Đọc `data/content.parquet` theo từng chunk để tránh OOM (file ~2GB)
- Parse HTML → plain text bằng BeautifulSoup
- Cắt text thành chunks 512 tokens (với overlap 50 tokens)
- Embed bằng model `VoVanPhuc/sup-SimCSE-Viet-roberta-base` (mô hình tiếng Việt tốt nhất)
- Insert vào bảng `document_chunks`
- **⚠️ Chạy offline 1 lần duy nhất, ước tính 2-4 tiếng tùy GPU/CPU**

---

### GIAI ĐOẠN 2 — Backend API Core
**Ước tính: 3-4 ngày**

#### Bước 2.1 — FastAPI App Foundation
- `app/main.py`: Khởi tạo app, CORS, lifespan events
- `app/core/config.py`: Settings từ `.env` (DB URL, Redis URL, OpenAI key)
- `app/core/database.py`: Async SQLAlchemy engine + session factory

#### Bước 2.2 — API: Tra cứu và Lọc (`/api/v1/documents`)

```
GET /api/v1/documents
    ?q=             # Full-text search (PostgreSQL tsvector)
    &loai_van_ban=  # Lọc theo loại
    &linh_vuc=      # Lọc theo lĩnh vực
    &co_quan=       # Lọc theo cơ quan
    &tu_ngay=       # Khoảng thời gian từ
    &den_ngay=      # Khoảng thời gian đến
    &hieu_luc=      # Trạng thái hiệu lực
    &page=1&size=20 # Pagination

GET /api/v1/documents/{id}         # Chi tiết 1 văn bản
GET /api/v1/documents/{id}/content # Nội dung HTML đầy đủ
GET /api/v1/documents/{id}/related # Văn bản liên quan
GET /api/v1/filters/options        # Lấy danh sách các giá trị để fill dropdown
```

**Logic search sẽ kết hợp:**
1. PostgreSQL Full-Text Search (`tsvector`) cho kết quả nhanh
2. Kết hợp với vector similarity (nếu user search ngữ nghĩa)
3. Hybrid scoring: `0.6 * bm25_score + 0.4 * cosine_sim`

#### Bước 2.3 — API: AI Legal Assistant (`/api/v1/chat`)

```
POST /api/v1/chat
Body: { "question": "Mức phạt vi phạm hành chính...", "session_id": "uuid" }

Pipeline RAG:
1. Embed câu hỏi → vector
2. Cosine search trong pgvector → top-k chunks liên quan nhất
3. Build prompt = [System] + [Context chunks] + [User question]
4. Gọi OpenAI GPT-4o-mini (hoặc Gemini Flash) → stream response
5. Trả về answer + danh sách văn bản nguồn (citations)
```

**System prompt được thiết kế để:**
- Chỉ trả lời dựa trên tài liệu được cung cấp (không hallucinate)
- Trích dẫn rõ số hiệu văn bản
- Cảnh báo khi không đủ dữ liệu

#### Bước 2.4 — API: Knowledge Graph (`/api/v1/graph`)

```
GET /api/v1/graph/{id}?depth=2
# Trả về: nodes + edges trong phạm vi depth=2 từ văn bản id
# Dùng PostgreSQL recursive CTE:
WITH RECURSIVE graph AS (
    SELECT doc_id, other_doc_id, relationship, 1 as depth
    FROM relationships WHERE doc_id = :id
    UNION ALL
    SELECT r.doc_id, r.other_doc_id, r.relationship, g.depth + 1
    FROM relationships r JOIN graph g ON r.doc_id = g.other_doc_id
    WHERE g.depth < :max_depth
)
SELECT * FROM graph;
```

#### Bước 2.5 — API: Dashboard Analytics (`/api/v1/stats`)

```
GET /api/v1/stats/by-year        # Số văn bản theo năm
GET /api/v1/stats/by-type        # Phân bố theo loại VB
GET /api/v1/stats/by-authority   # Top cơ quan ban hành
GET /api/v1/stats/by-status      # Tỷ lệ còn/hết hiệu lực
GET /api/v1/stats/by-sector      # Số văn bản theo lĩnh vực
```

Tất cả queries được **cache trong Redis 1 giờ** vì dữ liệu không thay đổi.

---

### GIAI ĐOẠN 3 — Frontend Foundation & Design System
**Ước tính: 2-3 ngày**

#### Bước 3.1 — Khởi tạo React + Vite project

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
npm install @tanstack/react-query axios react-router-dom
npm install recharts vis-network lucide-react
npm install framer-motion  # animations
```

#### Bước 3.2 — Design System (Global CSS)

Xây dựng hệ thống thiết kế theo phong cách **"Legal Dark Pro"**:
- **Màu sắc chủ đạo:** Dark navy (`#0A0F1E`) + Accent gold (`#E8C547`) — gợi cảm giác uy quyền, chuyên nghiệp
- **Typography:** `Inter` (UI) + `Lora` (serif cho nội dung văn bản pháp lý)
- **Glassmorphism** cho sidebar và cards
- **Animations:** Fade-in khi scroll, skeleton loading, typing effect cho AI chat

#### Bước 3.3 — Layout & Navigation

```
Header: Logo + Search bar + Navigation tabs
Sidebar: Bộ lọc (Loại VB, Lĩnh vực, Cơ quan, Thời gian, Hiệu lực)
Main content: Thay đổi theo tab đang active
```

---

### GIAI ĐOẠN 4 — Trang Tra Cứu & Chi Tiết Văn Bản
**Ước tính: 2-3 ngày**

#### Trang Search:
- Search bar nổi bật với auto-suggest (debounce 300ms)
- Sidebar bộ lọc đa chiều (checkbox, date range picker)
- Kết quả dạng card có highlight từ khóa tìm kiếm
- Pagination + infinite scroll
- Badge màu sắc cho `tinh_trang_hieu_luc` (xanh = còn hiệu lực, đỏ = hết)

#### Trang Chi Tiết Văn Bản:
- Header thông tin metadata đầy đủ + **Nút Bookmark/Lưu vào Collection**
- Tab: [Nội dung] [Timeline Hiệu lực] [Knowledge Graph mini] [Ghi chú cá nhân]
- Render HTML content của văn bản (sanitize XSS bằng DOMPurify)
- **Timeline Component**: Hiển thị quá trình văn bản được ban hành -> sửa đổi -> hết hiệu lực theo chiều dọc thời gian.
- **Ghi chú Component**: Khung soạn thảo Markdown để người dùng (HR/Pháp chế) tự note lại ý quan trọng của văn bản này.

---

### GIAI ĐOẠN 5 — AI Legal Assistant (RAG Chat)
**Ước tính: 2-3 ngày**

#### UI Chat:
- Giao diện chat 2 cột: [Cuộc hội thoại] | [Sources Panel]
- Streaming response (hiệu ứng typing real-time bằng SSE)
- Citations: Mỗi câu trả lời kèm danh sách văn bản nguồn có thể click vào
- Suggested questions để người dùng bắt đầu nhanh
- Lịch sử hội thoại (lưu trong localStorage hoặc Redis theo session_id)

#### Ví dụ tương tác:
```
User: "Mức phạt vi phạm quy định về đóng BHXH là bao nhiêu?"
AI: "Theo Nghị định 12/2022/NĐ-CP (Điều 38, Khoản 2), mức phạt...
     [Nguồn: Nghị định 12/2022/NĐ-CP] [Thông tư 06/2021/TT-BLĐTBXH]"
```

---

### GIAI ĐOẠN 6 — Knowledge Graph Viewer
**Ước tính: 2 ngày**

#### Sử dụng thư viện `vis-network`:
- Node màu khác nhau theo loại văn bản (Luật, Nghị định, Thông tư...)
- Edge label hiện loại quan hệ (sửa đổi, hướng dẫn, thay thế, bãi bỏ...)
- Điều khiển: Zoom, pan, click vào node để xem chi tiết
- Slider `depth` để điều chỉnh mức độ mở rộng đồ thị (1-3 bậc)
- Nút "Focus" để căn giữa vào văn bản đang xem

---

### GIAI ĐOẠN 7 — Analytics Dashboard
**Ước tính: 2 ngày**

#### Sử dụng thư viện `Recharts`:
| Biểu đồ | Loại | Dữ liệu |
|---|---|---|
| Văn bản theo năm | Area Chart | `stats/by-year` |
| Phân bố loại VB | Pie/Donut Chart | `stats/by-type` |
| Top cơ quan ban hành | Horizontal Bar | `stats/by-authority` |
| Tỷ lệ hiệu lực | Ring Chart | `stats/by-status` |
| Treemap theo lĩnh vực | Treemap | `stats/by-sector` |

Tất cả biểu đồ có tooltip, legend, và **responsive** (tự co giãn theo màn hình).

---

### GIAI ĐOẠN 8 — Workspace & Authentication
**Ước tính: 2 ngày**

#### Backend (JWT Auth):
- Triển khai login/register API, cấp phát Access Token.
- Protect các route thuộc workspace, yêu cầu token hợp lệ.

#### Frontend (Workspace UI):
- Quản lý trạng thái đăng nhập bằng React Context.
- Trang "Workspace của tôi": Quản lý danh sách các Collection, xem lại các văn bản đã bookmark và ghi chú.

---

## 🛠️ Tech Stack Tổng Hợp

| Layer | Công nghệ | Lý do |
|---|---|---|
| **Frontend** | React 18 + Vite + TypeScript | Ecosystem lớn, DX tốt |
| **UI Animations** | Framer Motion | Micro-animations mượt |
| **Charts** | Recharts | Dễ dùng, đẹp, responsive |
| **Graph Viz** | vis-network | Tốt nhất cho network graphs |
| **State/Data** | TanStack Query | Cache, loading, error states tự động |
| **Backend** | FastAPI + Python 3.11 | Async, fast, tự sinh docs |
| **ORM** | SQLAlchemy 2.0 (async) | Type-safe, async support |
| **Database** | PostgreSQL 16 | Reliable, pgvector support |
| **Vector Search** | pgvector | Tích hợp trong PostgreSQL, không cần service riêng |
| **Cache** | Redis 7 | Cache API responses |
| **Embedding Model** | `VoVanPhuc/sup-SimCSE-Viet-roberta-base` | Mô hình embedding tiếng Việt tốt nhất, free |
| **LLM** | OpenAI GPT-4o-mini | Cost-effective, streaming support |
| **Containerization** | Docker + Docker Compose | Dễ deploy, reproducible |

---

## ⚠️ Open Questions

> [!IMPORTANT]
> **Câu hỏi 1 — LLM Provider:** Bạn có API Key của **OpenAI** hay muốn dùng **Google Gemini** (có free tier) cho phần AI Chat? Hai cái này tôi đều code được, nhưng cần biết để config đúng.

> [!IMPORTANT]
> **Câu hỏi 2 — Phạm vi dữ liệu:** Đề tài yêu cầu giới hạn trong lĩnh vực *Lao động* và *Thuế*. Bạn muốn:
> - **(A)** Chỉ nạp văn bản lĩnh vực đó vào DB (DB nhỏ, nhanh hơn)
> - **(B)** Nạp toàn bộ 153k văn bản (đầy đủ, nhưng cần DB lớn hơn ~10GB)

> [!NOTE]  
> **Câu hỏi 3 — Môi trường chạy:** Bạn đang chạy PostgreSQL trên Docker hay cài sẵn trên máy rồi? Điều này ảnh hưởng đến cách setup `docker-compose.yml`.

---

## ✅ Kế Hoạch Thực Hiện Timeline

```
Tuần 1: [G1] Infrastructure + Data Ingestion + [G2] Backend API
Tuần 2: [G3] Frontend Foundation + [G4] Trang tra cứu
Tuần 3: [G5] AI Chat + [G6] Knowledge Graph
Tuần 4: [G7] Dashboard + Testing + Polish + Viết báo cáo
```

---

## 📋 Verification Plan

### Automated Tests
- `pytest` cho tất cả API endpoints (kiểm tra response schema, status codes)
- Test RAG pipeline với bộ câu hỏi mẫu từ dataset `thangvip/vietnamese-legal-qa`

### Manual Verification
- Chạy `docker compose up` và kiểm tra tất cả services khởi động thành công
- Test search với các từ khóa: "thuế thu nhập cá nhân", "bảo hiểm xã hội"
- Test AI chat với ít nhất 5 câu hỏi pháp lý thực tế
- Kiểm tra Knowledge Graph hiển thị đúng quan hệ cho một văn bản Luật Lao động
