# TRẠNG THÁI DỰ ÁN: NCKH - AI LEGAL INTELLIGENCE PLATFORM
*(File này dùng để tóm tắt lại toàn bộ tiến độ dự án, giúp AI ở các cuộc trò chuyện mới có thể đọc và hiểu ngay lập tức bối cảnh mà không cần hỏi lại).*

## 1. Mục tiêu cốt lõi
- Xây dựng một nền tảng Web App nội bộ (Modular Monolith) cho phép tìm kiếm và hỏi đáp pháp luật (Semantic Search + RAG).
- **Tuyệt đối không clone code từ project cũ (`D:\VN-Legal-Platform`)**, code phải được viết mới từ đầu.
- Phương pháp luận: Hướng đối tượng (Object-Oriented), KHÔNG dùng DFD.

## 2. Tài liệu nền tảng
Mọi đoạn code phải bám sát 100% vào file thiết kế: `PhanTichHeThong_v2_Fixed.docx`. Bao gồm:
- **Kiến trúc:** 3-tier (Frontend, Backend, Database).
- **Cơ sở dữ liệu (10 Bảng):** `users`, `organizations`, `documents`, `document_chunks`, `document_relations`, `collections`, `collection_documents`, `notes`, `query_logs`, `alembic_version`.

## 3. Tiến độ hiện tại

### ✅ Phase 1 — Nền tảng (HOÀN THÀNH)
- [x] `docker-compose.yml` — chỉ PostgreSQL+pgvector.
- [x] SQLAlchemy models: 10 bảng đầy đủ.
- [x] Alembic migration `ebcecd945d00` — tạo 10 bảng.
- [x] Migration `f794d49e846e` — fix query_logs (response JSONB, duration_ms).
- [x] ETL Pipeline: 1,004 documents trong PostgreSQL.
- [x] `start_dev.ps1` — script tự động hóa khởi động.

### ✅ Phase 2 Tuần 3 — Auth & Search API (HOÀN THÀNH)
- [x] `app/core/security.py` — bcrypt (raw, không qua passlib), JWT.
- [x] `app/core/dependencies.py` — get_current_user, get_optional_user.
- [x] `app/schemas/auth.py` — Register, Login, Token, User schemas.
- [x] `app/schemas/search.py` — SearchRequest (3 modes), SearchResponse.
- [x] `app/schemas/document.py` — DocumentListItem, DocumentDetail, Timeline.
- [x] `app/services/auth_service.py` — register, login, get_user_by_id.
- [x] `app/services/bm25_service.py` — PostgreSQL tsvector FTS + snippet.
- [x] `app/services/rrf_service.py` — Reciprocal Rank Fusion.
- [x] `app/services/semantic_service.py` — bkai embedding + HNSW query (lazy-load).
- [x] `app/routers/auth.py` — /auth/register, /login, /refresh, /me.
- [x] `app/routers/search.py` — /search (3 modes, semantic fallback BM25 nếu HNSW chưa ready).
- [x] `app/routers/documents.py` — /documents (list+filter) và /documents/{id} (detail+timeline).
- [x] `tests/test_auth.py` + `tests/test_search.py` + `pytest.ini`.

### ✅ Phase 2 Tuần 4 — RAG Engine & APIs (CODE XONG, CHƯA TEST)
- [x] `app/services/rag_service.py` — Retrieve → RRF → Augment → Generate (streaming + Circuit Breaker 10s).
- [x] `app/services/graph_service.py` — BFS Knowledge Graph, format Vis.js.
- [x] `app/services/analytics_service.py` — 5 aggregation metrics.
- [x] `app/routers/ai.py` — POST /ai/chat (SSE streaming), POST /ai/summarize.
- [x] `app/routers/graph.py` — GET /graph/{doc_id}?depth=2.
- [x] `app/routers/analytics.py` — GET /analytics/dashboard.

### 🔄 Phase 2 Tuần 2 — Embedding Pipeline (ĐANG LÀM)
- [x] `scripts/etl/chunker.py` — **17,346 chunks đã tạo** trong document_chunks.
- [x] `scripts/etl/embedder.py` — Script sẵn sàng (chờ sentence-transformers cài xong).
- [x] `scripts/etl/build_index.py` — Script tạo HNSW index sẵn sàng.
- [ ] **⏳ Đang cài `sentence-transformers` (torch CPU ~200MB đang tải)**.
- [ ] Chạy `embedder.py` — embed 3,402 chunks (~15-30 phút CPU).
- [ ] Chạy `build_index.py` — tạo HNSW index.
- [ ] Test POST /search mode=semantic với embedding thật.

### 🔄 Phase 3 — Frontend (Tuần 5-7) — ĐANG HOÀN THÀNH
- [x] React + Vite + TypeScript + react-router-dom + zustand + recharts + vis-network
- [x] `src/types/index.ts` — TypeScript interfaces cho toàn bộ entities
- [x] `src/App.tsx` — Router: /auth (public), /search + /documents/:id + /analytics (protected)
- [x] `src/pages/AuthPage.tsx` — Login/Register với animated gradient blobs
- [x] `src/pages/SearchPage.tsx` — 3-mode search + filters + AI Chat sidebar
- [x] `src/pages/DocumentPage.tsx` — Detail + Relations + Knowledge Graph + AI Chat
- [x] `src/pages/AnalyticsPage.tsx` — Dashboard với PieChart + BarChart + Recent Queries
- [x] `src/components/layout/AppLayout.tsx` — Protected route wrapper
- [x] `src/components/layout/Sidebar.tsx` — Collapsible sidebar với user info
- [x] `src/components/auth/RegisterForm.tsx`
- [x] `src/components/search/SearchBar.tsx` — Ctrl+K shortcut
- [x] `src/components/search/SearchResults.tsx` — Skeleton loading
- [x] `src/components/search/DocumentCard.tsx` — Text highlighting
- [x] `src/components/document/StatusBadge.tsx`
- [x] `src/components/chat/AIChatPanel.tsx` — SSE streaming, sources, abort
- [x] `src/components/graph/KnowledgeGraph.tsx` — vis-network graph
- [ ] **⏳ Build verification đang chạy**

### 🔄 Phase 4 — CI/CD & Testing (ĐANG LÀM)
- [x] Sửa lỗi `backend-ci.yml`: Thêm cấu hình PostgreSQL services, fix cache Python dependencies, và fix lỗi namespace của `google-genai` bằng Virtual Environment.
- [x] Sửa lỗi `e2e-ci.yml`:
  - Khởi chạy Backend và Frontend ở chế độ background (IPv4 127.0.0.1).
  - Tách môi trường ảo (venv) cho Python để tránh xung đột thư viện Ubuntu.
  - Nâng cấp Node.js lên v20 để tương thích Vite 8 và Playwright mới nhất.
  - Sửa URL trong E2E tests thành `127.0.0.1` để tránh lỗi Playwright kết nối vào IPv6.
- [x] Sửa lỗi Backend test: Bổ sung thư viện `google-genai` vào `backend/requirements.txt` do bị thiếu dependency.

## 4. Config quan trọng
- **Khởi động nhanh nhất:**
  ```powershell
  cd D:\NCKH
  .\start_dev.ps1
  ```
- **API Docs:** http://localhost:8000/docs
- **DB:** PostgreSQL tại `localhost:5432`, DB `legal_db`, user `postgres`, password `password`.
- **Data:** 1,004 documents + 3,402 chunks trong DB.
- **Embedding:** Chờ `sentence-transformers` cài → chạy `embedder.py` → `build_index.py`.

## 5. Lưu ý quan trọng
- **RAM 8GB:** `OMP_NUM_THREADS=1`, `TOKENIZERS_PARALLELISM=false` — BẮT BUỘC.
- **Bcrypt:** Dùng thư viện `bcrypt` trực tiếp (KHÔNG dùng `passlib`) vì không tương thích bcrypt>=4.0.
- **Gemini API Key:** Chưa điền trong `.env`. AI Chat sẽ fallback khi không có key.
- **HNSW:** `m=16`, `ef_construction=128` theo thiết kế tài liệu.
- **Console encoding:** PowerShell hiển thị ký tự lỗi nhưng dữ liệu trong DB và API response hoàn toàn UTF-8 đúng.
