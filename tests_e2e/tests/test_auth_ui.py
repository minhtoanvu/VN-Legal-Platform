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
    page.goto(f"{FRONTEND_URL}/login")
    
    # Assert tiêu đề trang
    expect(page).to_have_title(re.compile(r"Login|Đăng nhập", re.IGNORECASE))
    
    # Điền thông tin đăng nhập
    # Lưu ý: Các ID/Placeholder này cần khớp với DOM thực tế của UI
    page.fill('input[type="email"]', "test_e2e@example.com")
    page.fill('input[type="password"]', "password123")
    
    # Click nút đăng nhập
    page.click('button[type="submit"]')
    
    # Chờ redirect sang trang dashboard/search
    expect(page).to_have_url(re.compile(r".*/(search|dashboard)"))
    
@pytest.mark.e2e
def test_login_failure_wrong_password(page: Page):
    """
    Test kịch bản đăng nhập thất bại (Negative Test).
    """
    page.goto(f"{FRONTEND_URL}/login")
    
    page.fill('input[type="email"]', "test_e2e@example.com")
    page.fill('input[type="password"]', "WRONG_PASSWORD")
    
    page.click('button[type="submit"]')
    
    # Kì vọng xuất hiện thông báo lỗi trên giao diện
    error_message = page.locator('.error-message, [role="alert"]')
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text(re.compile(r"sai|không đúng|invalid", re.IGNORECASE))

import re
