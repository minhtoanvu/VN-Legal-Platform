# Kế hoạch Kiểm thử (QA & Testing Strategy) - AILIP Project

Tài liệu này định nghĩa chiến lược và các hạng mục công việc của bộ phận Tester (QA) đối với dự án AI Legal Intelligence Platform (AILIP) sau khi code base đã cơ bản hoàn thiện.

## ⚠️ User Review Required
Trong phần UI Testing (E2E), tiêu chuẩn của AG Kit là dùng **Playwright**. Tuy nhiên, tôi cần biết bạn muốn tự chạy test thủ công (Manual Test) bằng tay trên trình duyệt, hay muốn tôi viết script Playwright/Selenium để test tự động?
*Lưu ý: Nếu chạy tự động, bạn cần cài đặt Playwright vào máy (`pip install playwright`).*

## Proposed QA Tasks

### 1. API & Backend Testing (Integration Tests)
*Đảm bảo Backend vững chắc, không crash khi nhận dữ liệu rác.*
- **Kịch bản:**
  - Chạy toàn bộ Test Suite hiện có (`pytest tests/test_search.py` và `test_auth.py`).
  - Phân tích Coverage (Độ phủ code) và xuất báo cáo Test Report.
  - Bổ sung test cases cho API `/ai/chat` (Kiểm tra SSE Streaming và cấu trúc Citations trả về).
  - Test Rate Limiting: Gửi 100 request liên tục xem API có chặn (HTTP 429) để bảo vệ quota Gemini không.

### 2. E2E UI Testing (Frontend)
*Đóng vai người dùng cuối (End-user) đi từ đầu đến cuối luồng.*
- **Kịch bản chính (Happy Path):**
  1. Vào trang chủ, nhập từ khóa tìm kiếm.
  2. Cuộn trang để kích hoạt Pagination (Load more).
  3. Click vào văn bản đầu tiên -> Mở trang chi tiết Văn bản.
  4. Click nút vẽ "Đồ thị tri thức", kiểm tra xem mạng nhện có bung ra đủ node không.
  5. Mở tab "Trợ lý AI", hỏi một câu hỏi pháp lý và chờ AI trả lời có highlight nguồn.
- **Công cụ đề xuất:** Viết 1 file `scripts/playwright_runner.py` để tự động mở Chrome và thao tác luồng này.

### 3. Khảo thí AI (RAG & CoT Evaluation)
*Test con AI xem nó có bịa đặt (Hallucinate) không - Đây là đặc thù của dự án này.*
- **Đo lường thời gian (Performance):** Đảm bảo API trả về token đầu tiên (TTFT) dưới 1.5 giây.
- **Đo lường độ chính xác (Accuracy):** 
  - Đặt câu hỏi bẫy: *"Năm 2026 luật lao động cho phép đánh nhân viên không?"*. 
  - Expectation: AI phải từ chối trả lời hoặc nói không có trong luật, TUYỆT ĐỐI KHÔNG ĐƯỢC tự bịa ra điều luật.
  - Kiểm tra Citations xem có link đúng mã ID văn bản không.

## Verification Plan (Báo cáo Lỗi)
- QA sẽ không tự ý sửa code Backend/Frontend.
- Nếu `pytest` thất bại (Failed) hoặc tìm thấy bug giao diện, QA sẽ ghi log lỗi vào file `BUG_REPORT.md` kèm theo mã lỗi, cách tái hiện (Steps to reproduce), và giao lại cho Dev (là bạn) sửa.
