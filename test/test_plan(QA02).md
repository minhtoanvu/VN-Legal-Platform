# Master Test Plan: VN-Legal-Platform (QA-002)

Dựa trên cấu trúc Backend hiện hành (`ai.py`, `contract.py`, `workspace.py`, v.v.), dưới đây là Master Test Plan hoàn chỉnh. Mục tiêu là biến VN-Legal-Platform thành một dự án chuẩn chỉnh với Test Coverage > 80%, chứng minh năng lực QA Automation chuyên nghiệp.

## 1. Mục tiêu Kiểm thử (Testing Objectives)
1. **Đảm bảo tính ổn định (Reliability):** Tất cả core API không bao giờ trả về lỗi `500 Internal Server Error` với các input phổ biến hoặc invalid.
2. **Kiểm thử Tích hợp (Integration):** Xác minh luồng dữ liệu liên thông giữa `Database (PostgreSQL/pgvector) <-> API <-> LLM (Gemini)`.
3. **Mô phỏng Trải nghiệm người dùng (E2E):** Tự động hóa các kịch bản người dùng (User Journeys) chính trị trên trình duyệt.
4. **Hiệu suất (Performance):** Đảm bảo các tác vụ nặng (Tìm kiếm Semantic, AI RAG, Contract Analysis) đáp ứng dưới 3s.

---

## 2. Chiến lược Kiểm thử (Testing Strategy)

### Giai đoạn 1: Backend API Testing (Pytest + Asyncio)
*Tập trung vào Business Logic và Edge Cases.*

| Module | Phạm vi Kiểm thử (Test Scope) | Mức độ Ưu tiên |
| :--- | :--- | :--- |
| **AI & RAG** (`ai.py`) | - POST `/ai/chat`: Có context và không có context.<br>- Trả về chuẩn format Markdown/JSON.<br>- Xử lý khi LLM API timeout hoặc lỗi. | Cao |
| **Smart Contract** (`contract.py`) | - Upload file hợp lệ (PDF, DOCX) & không hợp lệ (EXE, JPG).<br>- Phân tích rủi ro hợp đồng (Mock LLM response).<br>- Giới hạn dung lượng file upload (Max 10MB). | Cao |
| **Workspace** (`workspace.py`) | - Lưu/Xóa Bookmark tài liệu.<br>- Ghi nhận lịch sử tìm kiếm (History).<br>- Phân quyền dữ liệu giữa các User khác nhau. | Trung bình |
| **Documents & Graph** | - Lấy metadata của văn bản pháp luật.<br>- Truy xuất node/edge trong Knowledge Graph. | Trung bình |

### Giai đoạn 2: Frontend E2E Testing (Playwright)
*Tập trung vào luồng UI/UX chính.*

1. **Auth Flow:** Đăng ký -> Đăng nhập -> Kiểm tra chuyển hướng vào Dashboard.
2. **Search Flow:** Nhập từ khóa -> Xem kết quả RRF -> Nhấp vào chi tiết văn bản.
3. **Contract Flow:** Kéo thả file PDF -> Đợi màn hình Loading -> Hiển thị biểu đồ phân tích rủi ro.

### Giai đoạn 3: Performance Testing (Locust)
*Tập trung vào Sức chịu tải (Load Test).*

1. **Search API (`/search`)**: Mô phỏng 100 concurrent users thực hiện Hybrid Search. Target: `< 1000ms`.
2. **Contract Analysis**: Khảo sát throughput xử lý file nặng.

---

## 3. Quản lý Môi trường Test
- **Database:** Sử dụng Transactions và `NullPool` để rollback dữ liệu tự động hoặc dọn dẹp sau khi chạy xong, đảm bảo **Zero Test Pollution**.
- **External API (Gemini):** Sử dụng thư viện `pytest-mock` (hoặc mock HTTP responses) để giả lập kết quả từ Google Gemini, tránh gọi API thật tốn tiền và rớt test khi mạng chậm.

## 4. User Review Required

Bạn hãy kiểm tra **Task List (bảng bên cạnh)** xem mình chia các task đã đúng thứ tự ưu tiên của bạn chưa. 
Nếu bạn đồng ý với Test Plan này, chúng ta sẽ bắt tay vào thực thi **Phase 1 (AI & Contract API)** ngay lập tức!
