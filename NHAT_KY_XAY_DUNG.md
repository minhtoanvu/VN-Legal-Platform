# 📚 NHẬT KÝ XÂY DỰNG DỰ ÁN
## AI Legal Intelligence Platform — NCKH

> Tài liệu này ghi lại toàn bộ quá trình thiết kế và xây dựng dự án từ đầu đến cuối theo thứ tự thời gian.

---

## 🎯 PHẦN 1: Xuất phát điểm & Mục tiêu

Dự án ra đời từ yêu cầu thực tiễn: hệ thống tra cứu pháp luật Việt Nam hiện tại phụ thuộc vào **tìm kiếm từ khóa đơn giản**, dẫn đến tỷ lệ bỏ sót văn bản liên quan rất cao, đặc biệt khi câu hỏi được diễn đạt theo ngôn ngữ tự nhiên.

**Mục tiêu cốt lõi:**
1. Xây dựng một nền tảng Web App nội bộ cho phép tìm kiếm pháp luật theo **ngữ nghĩa (Semantic Search)**.
2. Tích hợp **trợ lý AI (RAG Engine)** có thể trả lời câu hỏi pháp lý dựa trên điều luật thực tế, **không bịa đặt (Anti-hallucination)**.
3. Toàn bộ code viết mới từ đầu, tuân theo **phương pháp luận Hướng đối tượng (OOP)**.
4. Tài liệu nền tảng: `PhanTichHeThong_v2_Fixed.docx` (tài liệu phân tích hệ thống chính thức của nhóm).

---

## 🏗️ PHẦN 2: Quyết định Kiến trúc

Trước khi viết một dòng code nào, nhóm đã đưa ra các quyết định kiến trúc quan trọng sau:

| Thành phần | Lựa chọn | Lý do |
|:---|:---|:---|
| **Kiến trúc tổng thể** | Modular Monolith (3-tier) | Đủ phức tạp để chứng minh kỹ năng, không over-engineering |
| **Backend Framework** | FastAPI (Python) | Async-native, hiệu năng cao, tự động sinh Swagger API Docs |
| **Database** | PostgreSQL 16 + pgvector | Vừa làm DB quan hệ, vừa lưu trữ và tìm kiếm Vector — giảm 1 công cụ |
| **ORM** | SQLAlchemy 2.0 (Async) | Chuẩn OOP, an toàn với async, tránh N+1 query |
| **Schema Migration** | Alembic | Quản lý phiên bản DB theo lịch sử, có thể rollback |
| **Frontend Framework** | React 18 + Vite + TypeScript | Hiệu năng build tốt nhất, TypeScript giúp phát hiện lỗi sớm |
| **State Management** | Zustand | Nhỏ gọn, không boilerplate như Redux |
| **AI Model (Embedding)** | `bkai-foundation-models/vietnamese-bi-encoder` | Mô hình Bi-Encoder tiếng Việt tốt nhất, chạy được offline |
| **LLM Brain** | Google Gemini Flash-Lite (API) | Nhanh, rẻ, đủ thông minh cho domain pháp lý |
| **Containerization** | Docker + docker-compose | Khởi động toàn bộ DB chỉ bằng 1 lệnh |

---

## 📅 PHẦN 3: Lịch sử Xây dựng theo từng Phase

### ⚙️ Phase 1 — Nền tảng Hệ thống (HOÀN THÀNH ✅)

Đây là phase xây dựng "bộ khung xương" của dự án. Không có tính năng nào thực sự chạy được, nhưng mọi thứ được đặt nền móng chắc chắn.

**1.1. Cơ sở dữ liệu (Database Schema)**

Thiết kế **10 bảng dữ liệu** theo đúng tài liệu phân tích hệ thống:

```
users                 — Tài khoản người dùng (bcrypt password)
organizations         — Tổ chức/cơ quan
documents             — Văn bản pháp luật gốc
document_chunks       — Các đoạn nhỏ (chunks) để tạo Vector
document_relations    — Quan hệ giữa các văn bản (Căn cứ, Sửa đổi...)
collections           — Thư mục lưu trữ cá nhân (Workspace)
collection_documents  — Mapping giữa Collection và Document
notes                 — Ghi chú cá nhân trên văn bản
query_logs            — Lịch sử tìm kiếm của người dùng
alembic_version       — Quản lý phiên bản migration (tự động)
```

**1.2. ETL Pipeline — Bước 1: Tải và Làm sạch Dữ liệu**

```
Nguồn dữ liệu: Hugging Face dataset "tmquan/phapdien-moj-gov-vn"
Lĩnh vực: Lao động + Thuế
Số lượng: ~3,400 điều luật gốc
Script: download_data.py → normalize.py → load_db.py
Kết quả: 1,004 documents chính thức trong PostgreSQL
```

**1.3. Script khởi động nhanh**

Tạo file `start_dev.ps1` để khởi động cả Backend lẫn Frontend chỉ bằng 1 lệnh PowerShell, giúp quá trình demo trở nên mượt mà.

---

### 🔐 Phase 2 Tuần 3 — Auth & Search Engine (HOÀN THÀNH ✅)

**2.1. Hệ thống Xác thực (Authentication)**

- **Mã hóa mật khẩu:** Dùng thư viện `bcrypt` trực tiếp (không qua `passlib`) vì có vấn đề tương thích phiên bản. Đây là một quyết định kỹ thuật quan trọng được ghi nhận.
- **JWT Token:** Cặp token `access_token` (thời hạn ngắn) + khả năng refresh.
- **Route Protection:** Middleware `get_current_user` và `get_optional_user` (cho phép xem trang không cần login).

**2.2. Bộ máy Tìm kiếm — Thiết kế Lai (Hybrid Search)**

Đây là **trái tim kỹ thuật** của đồ án. Hệ thống được xây dựng 3 service riêng biệt, sau đó kết hợp lại:

```
bm25_service.py     → Tìm kiếm Toàn văn bằng PostgreSQL tsvector (Exact match + snippet)
semantic_service.py → Tìm kiếm Ngữ nghĩa bằng Vector HNSW (Meaning-based)
rrf_service.py      → Chấm điểm tổng hợp bằng thuật toán RRF (Reciprocal Rank Fusion)
```

**Cơ chế Hybrid Search:**
> Khi người dùng tìm kiếm, hệ thống chạy **song song** cả BM25 lẫn Semantic search bằng `asyncio.gather`. Hai danh sách kết quả trả về được hợp nhất và tính điểm lại bằng RRF — đảm bảo kết quả vừa khớp từ khóa, vừa hiểu đúng ý nghĩa câu hỏi.

**2.3. ETL Pipeline — Bước 2: Chunking (Cắt nhỏ văn bản)**

```
Công cụ: LangChain RecursiveCharacterTextSplitter
Cấu hình: chunk_size=500 ký tự, chunk_overlap=50 ký tự
Kết quả: 1,004 documents → 15,746 chunks trong document_chunks
Lý do cắt nhỏ: Mô hình AI có Token Limit, cần đoạn ngắn mới đủ chính xác
```

---

### 🤖 Phase 2 Tuần 4 — RAG Engine & Các API phụ (HOÀN THÀNH ✅)

**3.1. Luồng RAG (Retrieval-Augmented Generation)**

Đây là pipeline xử lý câu hỏi AI hoàn chỉnh theo trình tự:

```
Câu hỏi người dùng
    ↓
[RETRIEVE] Tìm 20 đoạn liên quan nhất từ DB (BM25 + Semantic song song)
    ↓
[RERANK] Dùng RRF chọn lọc còn 5 đoạn tốt nhất
    ↓
[AUGMENT] Nhét 5 đoạn đó vào Prompt, kèm hướng dẫn chống hallucination
    ↓
[GENERATE] Gọi Gemini API → Streaming kết quả từng chữ qua SSE
    ↓
[CITE] Đính kèm ID văn bản nguồn vào cuối phản hồi
```

**Circuit Breaker:** Nếu Gemini không trả lời trong 10 giây, hệ thống tự ngắt và thông báo lỗi — tránh người dùng chờ vô tận.

**3.2. Knowledge Graph Engine**

```
graph_service.py: Duyệt đồ thị bằng BFS (Breadth-First Search) đến độ sâu 2 cấp
Loại quan hệ: Căn cứ, Hướng dẫn thi hành, Sửa đổi, Bổ sung, Thay thế
Output: JSON format chuẩn cho Vis.js render
```

**3.3. Analytics Engine**

Thu thập 5 chỉ số thống kê: tổng số tìm kiếm, tỷ lệ từng lĩnh vực văn bản, câu hỏi phổ biến nhất, lịch sử 30 ngày, phân phối theo loại tài liệu.

---

### 🖥️ Phase 3 Tuần 5-7 — Frontend (HOÀN THÀNH ✅)

Toàn bộ giao diện người dùng được xây dựng từ đầu với phong cách **Dark Glassmorphism** (kính mờ tối, hiệu ứng gradient hiện đại).

**Danh sách các trang (Pages):**

| File | Tính năng |
|:---|:---|
| `AuthPage.tsx` | Đăng nhập / Đăng ký với animated gradient blobs |
| `SearchPage.tsx` | Trang chính — 3 chế độ tìm kiếm + AI Chat sidebar |
| `DocumentPage.tsx` | Xem chi tiết văn bản + Knowledge Graph + AI Chat |
| `AnalyticsPage.tsx` | Dashboard với PieChart và BarChart (Recharts) |
| `WorkspacePage.tsx` | Quản lý Collection/Note cá nhân |

**Danh sách các component đáng chú ý:**

| Component | Kỹ thuật |
|:---|:---|
| `AIChatPanel.tsx` | Kết nối AI qua Server-Sent Events (SSE), hỗ trợ abort/cancel |
| `KnowledgeGraph.tsx` | Vis.js network graph tương tác, kéo thả node |
| `SearchBar.tsx` | Phím tắt `Ctrl+K` để focus tức thì |
| `DocumentCard.tsx` | Highlight đoạn text trùng khớp từ khóa tìm kiếm |

---

### 🗂️ Phase bổ sung — Workspace (HOÀN THÀNH ✅)

Sau khi core feature hoàn thiện, tính năng Workspace được thêm vào đáp ứng nhu cầu quản lý thông tin cá nhân của người dùng:

- **Collections:** Tạo, xem, xóa thư mục lưu trữ (CRUD đầy đủ).
- **Bookmarks:** Lưu văn bản vào Collection yêu thích (thêm/bỏ).
- **Notes:** Ghi chú riêng tư trên từng văn bản, lưu theo Collection.
- **Backend:** Toàn bộ API trong `workspace.py` router (~200 dòng code).
- **Frontend:** Giao diện `WorkspacePage.tsx` quản lý trực quan.

---

### 📊 Phase cuối — ETL Embedding (ĐÃ HOÀN THÀNH ✅)

Đây là bước cuối cùng để kích hoạt tính năng Semantic Search hoàn toàn:

```
embedder.py:    Đã đọc và mã hóa thành công 17,346 chunks (100%)
build_index.py: Đã tạo Index HNSW (m=16, ef_construction=128) siêu tốc cho pgvector.
Trạng thái: Semantic Search và RAG đã SẴN SÀNG trên toàn bộ 3000 văn bản!
```

---

## 📁 PHẦN 4: Sơ đồ cấu trúc thư mục (Bản đầy đủ)

```
NCKH/
│
├── docker-compose.yml          # Khởi động PostgreSQL+pgvector
├── start_dev.ps1               # Script bật backend + frontend 1 lệnh
├── README.md                   # Tài liệu GitHub dành cho nhà tuyển dụng
│
├── backend/
│   ├── .env                    # Biến môi trường (API keys, DB URL)
│   ├── requirements.txt        # Danh sách thư viện Python
│   ├── alembic/                # Lịch sử migration database
│   │
│   ├── app/
│   │   ├── main.py             # Điểm khởi động FastAPI, CORS config
│   │   ├── core/               # Cấu hình nền tảng
│   │   │   ├── database.py     # AsyncSessionLocal, engine
│   │   │   ├── security.py     # bcrypt hash, JWT encode/decode
│   │   │   └── dependencies.py # FastAPI Dependencies (get_current_user)
│   │   ├── models/             # SQLAlchemy ORM (ánh xạ DB table → Python class)
│   │   │   ├── user.py         # User, Organization
│   │   │   ├── document.py     # Document, DocumentChunk, DocumentRelation
│   │   │   └── workspace.py    # Collection, CollectionDocument, Note, QueryLog
│   │   ├── schemas/            # Pydantic Schemas (validate Request/Response)
│   │   ├── services/           # Business Logic (Tầng xử lý nghiệp vụ)
│   │   │   ├── auth_service.py
│   │   │   ├── bm25_service.py
│   │   │   ├── semantic_service.py
│   │   │   ├── rrf_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── graph_service.py
│   │   │   └── analytics_service.py
│   │   └── routers/            # FastAPI Routers (định tuyến HTTP)
│   │       ├── auth.py
│   │       ├── search.py
│   │       ├── documents.py
│   │       ├── ai.py
│   │       ├── graph.py
│   │       ├── analytics.py
│   │       └── workspace.py
│   │
│   ├── scripts/etl/            # Pipeline xử lý dữ liệu
│   │   ├── download_data.py    # Tải từ Hugging Face
│   │   ├── normalize.py        # Làm sạch, chuẩn hóa văn bản
│   │   ├── load_db.py          # Nạp vào PostgreSQL
│   │   ├── chunker.py          # Cắt nhỏ văn bản (15,746 chunks)
│   │   ├── embedder.py         # Tạo Vector 768D (đang chạy)
│   │   ├── build_index.py      # Tạo HNSW Index
│   │   └── run_full_etl.py     # Chạy toàn bộ pipeline 1 lệnh
│   │
│   └── tests/                  # Unit Tests (pytest)
│       ├── test_auth.py
│       └── test_search.py
│
└── frontend/
    └── src/
        ├── types/index.ts      # TypeScript interface cho toàn bộ entities
        ├── services/api.ts     # Axios client, JWT interceptor
        ├── App.tsx             # React Router (Public + Protected routes)
        ├── pages/              # 5 trang chính
        └── components/        # UI Components tái sử dụng
```

---

## 🎓 PHẦN 5: Tổng kết kỹ thuật

| Hạng mục | Con số |
|:---|:---|
| Tổng số file code | ~45 file |
| Tổng số dòng code (ước tính) | ~8,000 dòng |
| Số bảng database | 10 bảng |
| Số API endpoint | ~20 endpoint |
| Số trang Frontend | 5 trang |
| Văn bản pháp luật trong DB | 1,004 điều luật |
| Chunks được tạo ra | 15,746 đoạn |
| Chiều Vector mỗi chunk | 768 chiều |

---

*Tài liệu này được tổng hợp tự động từ toàn bộ source code và lịch sử xây dựng dự án tại `D:\NCKH`.*
