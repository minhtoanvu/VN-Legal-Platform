# 🎯 Bí Kíp Ôn Tập Phỏng Vấn: Dự Án AI Legal Platform

Dự án này là một "mỏ vàng" để phỏng vấn vì nó chứa đựng kiến thức của cả QA, Backend, và AI. Tùy thuộc vào việc bạn apply vị trí nào (QA Automation, Backend Engineer, hay System Analyst), bạn hãy focus mạnh vào phần tương ứng dưới đây.

---

## 1. Mảng Kỹ Sư Kiểm Thử (QA Automation / Tester) - *Trọng tâm Nhất*

Đây là "vũ khí sát thương" mạnh nhất của dự án. Đừng chỉ nói "em biết dùng Pytest", hãy kể câu chuyện bạn đã tối ưu hệ thống như thế nào.

### A. Performance Testing & Bottleneck Optimization (Kể chuyện)
> [!IMPORTANT]
> **Câu hỏi tiềm năng:** *Em đã dùng Locust như thế nào? Em có từng tìm ra lỗi hệ thống nào qua Load Test chưa?*

**Cách trả lời (Dựa trên dự án thật):**
- **Kịch bản:** Em dùng Locust giả lập 100 User đăng ký/đăng nhập cùng lúc (Concurrent Users).
- **Phát hiện lỗi:** Max Response Time vọt lên tới 73.9 giây, Error Rate 46% (Timeout).
- **Phân tích nguyên nhân (Root Cause):** FastAPI là Framework bất đồng bộ (Async). Tuy nhiên thuật toán băm mật khẩu `Bcrypt` lại là tác vụ chạy đồng bộ và ngốn CPU (CPU-bound). Khi 100 user gọi Bcrypt cùng lúc, nó làm "chết đứng" Event Loop, khiến các request khác (dù nhẹ như Search) cũng bị nghẽn theo.
- **Cách khắc phục:** Em sửa code Backend bằng cách bọc hàm `bcrypt` vào `run_in_threadpool` của Starlette. Việc này đẩy tác vụ băm mật khẩu ra một luồng (thread) riêng, giải phóng Event Loop.
- **Kết quả (Before/After):** RPS (Request per second) tăng từ 2.2 lên 45.5, Error Rate về 0%, tốc độ phản hồi giảm xuống còn ~450ms.

### B. E2E UI Testing (Playwright)
> [!TIP]
> **Câu hỏi tiềm năng:** *Tại sao em dùng Playwright mà không dùng Selenium? Cấu trúc test UI của em như thế nào?*

**Cách trả lời:**
- **Lý do:** Playwright hỗ trợ Async native, tự động Auto-wait (không phải dùng `time.sleep()`), và cài đặt CI/CD rất dễ qua WebKit/Chromium engine.
- **Cấu trúc:** Em áp dụng **POM (Page Object Model)**. Các selector (locator) được gom vào folder `pages/` để dễ maintain. Các kịch bản test nằm ở folder `tests/`.
- **Negative Testing:** Em không chỉ test luồng đúng (Happy path) mà còn viết các file như `test_search_negative.py` hoặc `test_auth_ui.py` để test luồng sai (nhập sai pass, nhập ký tự đặc biệt) xem UI có hiện đúng câu báo lỗi (Alert) không.

### C. Backend API Testing (Pytest)
- **Tư duy:** Chia test theo Domain (Auth, Search, Analytics).
- **Kỹ thuật:** Dùng `pytest-asyncio` vì FastAPI là async. Dùng `monkeypatch` để **Mocking** (giả lập) hàm gọi LLM Gemini (để không tốn tiền API thật khi chạy test).
- **Coverage:** Sử dụng `pytest-cov` đo lường được bao phủ 52% codebase.

---

## 2. Mảng Kiến Trúc & Backend (Backend Engineer / System Analyst)

### A. Clean Architecture & Modularization
> [!NOTE]
> **Câu hỏi tiềm năng:** *Cấu trúc thư mục FastAPI của em được thiết kế dựa trên nguyên lý nào?*

**Cách trả lời:**
- Tuân thủ nguyên lý **SRP (Single Responsibility Principle)**.
- Không vứt hết code vào `main.py`. Em chia làm 3 tầng rõ rệt:
  1. **Routers (`app/routers/`):** Chỉ nhận HTTP Request và trả HTTP Response.
  2. **Services (`app/services/`):** Chứa Business Logic (Tìm kiếm, Gọi AI, Xử lý Đăng nhập). Router sẽ gọi Service.
  3. **Models / Core:** Chứa định nghĩa DB và cấu hình lõi (Security, DB Session).

### B. Mẫu Thiết Kế Chống Lỗi (Circuit Breaker Pattern)
> [!WARNING]
> **Câu hỏi tiềm năng:** *Hệ thống của em phụ thuộc API Gemini (Google). Nếu Google sập thì app em sập theo à?*

**Cách trả lời:**
- Để chống lỗi dây chuyền (Cascading failures), em tự code một **Circuit Breaker (Cầu dao điện)** trong `app/core/circuit_breaker.py`.
- **Cơ chế:** Nó là 1 State Machine (Cỗ máy trạng thái). Khi gọi Gemini thất bại 3 lần liên tiếp (do timeout hoặc Google sập), Cầu dao sẽ **MỞ (Open)**. Lúc này, mọi request chat AI tiếp theo sẽ lập tức bị từ chối trả về lỗi "Hệ thống AI đang bảo trì" *mà không cần đợi gửi request lên Google nữa*. Điều này giúp giữ băng thông và bảo vệ Server không bị treo. Sau 1 phút, nó chuyển sang **Half-Open** để thử gửi 1 request xem Google đã phục hồi chưa.

---

## 3. Mảng Dữ Liệu & AI (Data Engineer / AI Engineer)

Đây là mảng ăn điểm với các công ty làm AI.

### A. Hybrid Search & RRF
- Từ khóa: Thay vì chỉ tìm theo từ khóa (BM25 - Fulltext Search Postgres), em kết hợp với Tìm kiếm ngữ nghĩa (Semantic Search dùng `pgvector` HNSW index).
- Để ghép điểm của 2 thuật toán khác nhau, em dùng **Reciprocal Rank Fusion (RRF)**: Tính điểm dựa trên xếp hạng (Rank) thay vì điểm tuyệt đối.

### B. Anti-Hallucination (Chống ảo giác AI)
> [!CAUTION]
> **Câu hỏi tiềm năng:** *Làm sao em chắc chắn AI của em không bịa ra luật (Hallucination)?*

**Cách trả lời:**
- Kỹ thuật **Citation-grounded RAG**. Trong System Prompt, em ép LLM một quy tắc "Zero-Tolerance": *Chỉ được trả lời dựa trên Context đưa vào, nếu Context không có thông tin, phải trả lời 'Tôi không biết'. Khi trả lời phải trích dẫn (Citation) số thứ tự của tài liệu.*

### C. Đánh Giá AI bằng Toán Học (RAGAs Metrics)
Đừng nói "Em thấy nó trả lời khá đúng". Hãy nói:
- Em dùng Script để chạy tập Dataset 100 câu hỏi, đo lường bằng:
  - **Hit@5:** Văn bản luật đúng có xuất hiện trong Top 5 kết quả tìm kiếm không? (Ngưỡng pass: 85%).
  - **MRR@5:** Văn bản đúng nằm ở vị trí số mấy (số 1 điểm cao hơn số 5).
  - **Faithfulness:** Đầu ra của LLM có hoàn toàn khớp với đầu vào không, hay là bịa thêm. (Ngưỡng pass: 90%).

### D. Data Mining (Khai phá dữ liệu)
- **PageRank:** App của em dùng PageRank (thuật toán của Google) lên mạng lưới văn bản luật. Điều Luật nào được các Nghị định khác trích dẫn nhiều nhất sẽ có "điểm uy tín" cao nhất.
- **Louvain Clustering:** Dùng để gom nhóm (Cluster) các văn bản luật có liên kết chặt chẽ với nhau thành các "Cộng đồng pháp lý" (Ví dụ: Nhóm luật Đất đai, Nhóm luật Lao động) hoàn toàn tự động mà không cần dán nhãn thủ công.
