# TỔNG HỢP QUÁ TRÌNH PHÁT TRIỂN DỰ ÁN
**Tên dự án:** AI Legal Intelligence Platform (VN-Legal-Platform)
**Mục tiêu:** Nền tảng tra cứu, phân tích và khai thác tri thức pháp lý dành cho doanh nghiệp Việt Nam.

Dưới đây là bức tranh toàn cảnh về toàn bộ hành trình chúng ta đã thực hiện để biến các yêu cầu trong tài liệu "Thiết kế hệ thống" và "Phân tích hệ thống" thành một hệ thống phần mềm hoàn chỉnh, mạnh mẽ và đạt chuẩn học thuật.

---

## 🏗️ Giai đoạn 1: Xây dựng Nền tảng và Kiến trúc Lõi (Core Architecture)
1. **Thiết lập Kiến trúc 3-Tier:**
   - **Backend:** Xây dựng bằng `FastAPI` (Python) với cơ chế Bất đồng bộ (Async) toàn diện để chịu tải cao.
   - **Database:** Sử dụng `PostgreSQL` kết hợp extension `pgvector` để lưu trữ cả dữ liệu truyền thống (SQL) và Vector nhúng (Embeddings) của văn bản luật. Sử dụng thuật toán HNSW để tối ưu tốc độ tìm kiếm vector.
   - **ORM:** Tích hợp `SQLAlchemy` (Async) để quản lý tương tác với Database.

2. **Quản lý Định danh & Bảo mật (Auth):**
   - Áp dụng mã hóa mật khẩu `Bcrypt`.
   - Cấp phát và xác thực `JWT Token` cho các API cần bảo mật (như lưu Note, Collection trong Workspace).

---

## 🧠 Giai đoạn 2: Phát triển Trái tim AI (RAG Pipeline & Hybrid Search)
Đây là giai đoạn phức tạp nhất, biến nền tảng thành một "Trợ lý pháp lý" thực thụ.

1. **Tìm kiếm Lai (Hybrid Search):**
   - Tích hợp **BM25 Search** (Tìm kiếm từ khóa chính xác).
   - Tích hợp **Semantic Search** (Tìm kiếm ngữ nghĩa) sử dụng mô hình nhúng `vietnamese-bi-encoder` chuyên biệt cho tiếng Việt.
   - Áp dụng thuật toán **Reciprocal Rank Fusion (RRF)** với hằng số `k=60` để kết hợp và xếp hạng lại kết quả từ 2 phương pháp trên (nằm trong file `rrf_service.py`).

2. **Quy trình RAG (Retrieval-Augmented Generation):**
   - Đưa các văn bản pháp luật tìm được vào ngữ cảnh (Context).
   - Viết **System Prompt nghiêm ngặt (Anti-hallucination)** ép buộc AI (Gemini 2.5 Flash) CHỈ được trả lời dựa trên văn bản luật, không được bịa đặt, và phải trích dẫn (Citations) chính xác Điều/Khoản.
   - Xây dựng cơ chế **Streaming Response** (trả lời từng chữ theo thời gian thực) mang lại trải nghiệm UX tuyệt vời.

---

## 🚀 Giai đoạn 3: Khai phá Dữ liệu Nâng cao (Data Mining & Knowledge Graph)
Để đáp ứng yêu cầu học thuật cao cấp của một đồ án tốt nghiệp, chúng ta đã bổ sung các tính năng khai phá dữ liệu chuyên sâu:

1. **Trực quan hóa Đồ thị Tri thức (Knowledge Graph):**
   - Backend cung cấp API xuất các mối quan hệ (Thay thế, Sửa đổi, Hướng dẫn) giữa các văn bản để Frontend vẽ đồ thị bằng Vis.js.

2. **Thuật toán Khai phá (Data Mining):**
   - **PageRank (NetworkX):** Chạy thuật toán đồ thị để tìm ra Top 10 "Văn bản rễ" (Các bộ luật gốc có tầm ảnh hưởng, được dẫn chiếu nhiều nhất).
   - **Louvain Community Detection:** Gom cụm tự động (Clustering) các nhóm lĩnh vực pháp luật thường xuyên đi kèm với nhau.
   - **Heatmap Calendar:** Phân tích tần suất ban hành văn bản theo từng tháng và năm để tìm ra tính chu kỳ hoặc sự kiện bất thường (Outliers).

---

## 🛡️ Giai đoạn 4: Tích hợp Đề tài NCKH (Hệ sinh thái Mở rộng)
- **Module Phân tích Hợp đồng (Contract Analysis):** Tích hợp công trình Nghiên cứu Khoa học (NCKH) về nhận diện rủi ro hợp đồng bằng kỹ thuật **Chain-of-Thought (CoT)** vào nền tảng, cho phép người dùng upload file PDF/Docx để AI soi lỗi hợp đồng.

---

## 🧪 Giai đoạn 5: Đảm bảo Chất lượng, Chịu lỗi & Đánh giá (QA & Resilience)
Giai đoạn cuối cùng nhằm biến đồ án thành một sản phẩm sẵn sàng cho môi trường thực tế (Production-ready).

1. **Cơ chế Chịu lỗi (Resilience):**
   - Tự tay viết một class **Circuit Breaker (Cầu dao điện)** (`circuit_breaker.py`) để ngắt kết nối tạm thời tới API của Google (Gemini) nếu nó phản hồi quá chậm, giúp Server không bị treo. Đi kèm với cơ chế Timeout 10s an toàn.

2. **Kiểm thử Toàn diện (Testing):**
   - **API Test (Pytest):** Đã sửa sạch các lỗi liên quan đến Event Loop (Async) và cấp phát Database Session. Coverage thành công.
   - **E2E Test (Playwright):** Viết kịch bản tự động giả lập người dùng mở trình duyệt, đăng nhập, gõ tìm kiếm. Bổ sung cơ chế `Graceful Failure` để không crash hệ thống khi test.
   - **Load Test (Locust):** Cấu hình giả lập 100 người dùng truy cập cùng lúc, qua đó phát hiện "nút thắt cổ chai" (Bottleneck) chính là hàm băm mật khẩu Bcrypt. Đã ghi chép đầy đủ vào Báo cáo (`testing_report.md`).

3. **Chấm điểm Trí tuệ Nhân tạo (RAG Benchmark):**
   - Viết kịch bản test thực tế (`real_benchmark.py`) quét qua Database.
   - Đánh giá khả năng tìm kiếm qua công thức Toán học: **MRR@5** và **Hit@5**.
   - Chứng minh được khả năng giải quyết các sai lệch ngữ nghĩa (Semantic Mismatch) trong thực tiễn (Ví dụ: Từ khóa "cao đẳng" vs "chuyên môn kỹ thuật").

---
**🏆 KẾT LUẬN:** 
Từ những trang tài liệu phân tích lý thuyết, chúng ta đã lập trình thành công một hệ thống **chạy được, chạy mượt và có hàm lượng chất xám cực cao**. Hệ thống không chỉ đáp ứng đủ các Use Case lõi mà còn vượt trội ở các tính năng Load Test, Circuit Breaker và Data Mining thuật toán Đồ thị.
