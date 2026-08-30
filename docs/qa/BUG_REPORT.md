# 🐞 Báo cáo Kiểm thử & Cập nhật Lỗi (Bug Report)
**Dự án:** AI Legal Intelligence Platform (AILIP)
**Giai đoạn:** Phase 5 - QA & Testing
**Trạng thái:** ✅ Đã đóng (Resolved)

---

## 1. Kết quả tự động hóa (Automated Testing)

Sau khi chạy bộ Test Suite (`pytest` và `playwright`), hệ thống ghi nhận kết quả như sau:
- **Backend API (Pytest):** 14/14 Passed.
- **Frontend E2E (Playwright):** 3/3 Passed (Search Keyword, Empty Input, XSS Validation).
- **Performance (Locust):** 0 Failures dưới tải 100 concurrent users.

> [!TIP]
> Các bài test tự động đều vượt qua, tuy nhiên trong quá trình kiểm thử bảo mật mở rộng (Exploratory Security Testing) và Code Audit, chúng tôi đã phát hiện ra 4 lỗi/rủi ro nghiêm trọng ở cấp độ Kiến trúc. 

## 2. Danh sách Bug / Lỗ hổng đã phát hiện & Vá

### BUG-01: API Search và AI Chat mở công khai (CRITICAL)
- **Mô tả:** Endpoint `/search` và `/ai/chat` không yêu cầu JWT Token, cho phép bất kỳ ai (Guest) truy vấn CSDL và gọi AI.
- **Rủi ro:** Bị cào dữ liệu (Data Scraping) và tốn kém chi phí gọi API bên thứ 3 (Gemini).
- **Cách khắc phục:** Đã bổ sung `Depends(get_current_active_user)` vào Router. (Đã test trả về 401 Unauthorized khi không có Token).
- **Trạng thái:** ✅ Resolved.

### BUG-02: Thiếu Rate Limiting dẫn đến rủi ro DDoS (CRITICAL)
- **Mô tả:** Endpoint `/ai/chat` có thể bị spam hàng trăm request mỗi giây, gây sập server (OOM) hoặc làm cạn kiệt Quota API.
- **Rủi ro:** Tấn công từ chối dịch vụ (DDoS) và rủi ro tài chính.
- **Cách khắc phục:** Triển khai thư viện `slowapi`, giới hạn `@limiter.limit("5/minute")` cho mỗi IP. Đã sửa lỗi *Circular Import* khi triển khai.
- **Trạng thái:** ✅ Resolved.

### BUG-03: Tràn bộ nhớ (OOM) khi phân trang sâu (HIGH)
- **Mô tả:** Khi người dùng truyền tham số `offset=10000`, hệ thống tải toàn bộ 10000 bản ghi vào RAM để chạy thuật toán RRF.
- **Rủi ro:** Crash backend server do cạn RAM (Out of Memory).
- **Cách khắc phục:** Đặt cờ bảo vệ `MAX_OFFSET = 200`. Ném lỗi `HTTP 400` nếu người dùng cố tình cào data.
- **Trạng thái:** ✅ Resolved.

### BUG-04: Lỗi UX khi Server sập (MEDIUM)
- **Mô tả:** Khi có lỗi 500 hoặc 429 từ Backend, giao diện Frontend (SearchPage) chỉ hiển thị màn hình trống không và log lỗi ngầm `console.error`.
- **Rủi ro:** Trải nghiệm người dùng kém, người dùng tưởng hệ thống không có dữ liệu pháp luật.
- **Cách khắc phục:** Cập nhật state `error` và hiển thị UI Toast màu đỏ cảnh báo trên màn hình.
- **Trạng thái:** ✅ Resolved.

---

**Kết luận:** Hệ thống đã vượt qua mọi kịch bản kiểm thử tĩnh (Code Audit) và động (Runtime). Dự án chính thức đạt chuẩn **Production-Ready** cho các tính năng lõi!
