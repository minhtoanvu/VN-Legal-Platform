import re
import pytest
from playwright.sync_api import Page, expect

# Thay đổi URL tùy vào môi trường test của Frontend
FRONTEND_URL = "http://127.0.0.1:5173"

@pytest.mark.e2e
def test_login_success(page: Page):
    """
    Test kịch bản đăng nhập thành công.
    Yêu cầu: Frontend đang chạy ở localhost:5173 và Backend đang chạy.
    """
    page.goto(f"{FRONTEND_URL}/auth")
    
    # Assert tiêu đề trang - chấp nhận nhiều tiêu đề có thể
    expect(page).to_have_title(re.compile(r"Login|Đăng nhập|frontend|Vite \+ React", re.IGNORECASE))
    
    # Điền thông tin đăng nhập
    # Lưu ý: Các ID/Placeholder này cần khớp với DOM thực tế của UI
    page.fill('input[type="email"]', "test_e2e@example.com")
    page.fill('input[type="password"]', "password123")
    
    # Click nút đăng nhập
    page.click('button[type="submit"]')
    
    # Chờ redirect sang trang dashboard/search
    page.wait_for_url(re.compile(r".*(search|dashboard)"), timeout=10000)
    
@pytest.mark.e2e
def test_login_failure_wrong_password(page: Page):
    """
    Test kịch bản đăng nhập thất bại (Negative Test).
    """
    page.goto(f"{FRONTEND_URL}/auth")
    
    page.fill('input[type="email"]', "test_e2e@example.com")
    page.fill('input[type="password"]', "WRONG_PASSWORD")
    
    page.click('button[type="submit"]')
    
    # Kì vọng xuất hiện thông báo lỗi trên giao diện
    # Try multiple selectors for error message
    page.wait_for_timeout(2000)  # Wait for error to appear
    error_message = page.locator('[role="alert"], .error-message, .alert, .error')
    if error_message.count() > 0:
        expect(error_message.first).to_be_visible()
    else:
        # If no error message found, check if we stayed on auth page
        expect(page).to_have_url(re.compile(r".*/auth"))
