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
    
    # Đăng ký tài khoản trước vì DB trong CI hoàn toàn trống
    page.click('button:has-text("Đăng ký ngay")')
    
    # Scope to the register form to avoid strict mode violations
    register_form = page.locator('form').filter(has_text="Đăng ký")
    register_form.locator('input[type="text"]').fill("User E2E")
    register_form.locator('input[type="email"]').fill("test_e2e@example.com")
    register_form.locator('input[type="password"]').nth(0).fill("password123")
    register_form.locator('input[type="password"]').nth(1).fill("password123")
    register_form.locator('button[type="submit"]').click()
    
    # Chờ redirect tự động hoặc click lại nút Đăng nhập nếu email đã tồn tại
    page.wait_for_timeout(2000)
    if page.locator('button:has-text("Đăng nhập")').is_visible():
        page.locator('button:has-text("Đăng nhập")').click()
    
    # Điền thông tin đăng nhập
    login_form = page.locator('form').filter(has_text="Đăng nhập")
    login_form.locator('input[type="email"]').fill("test_e2e@example.com")
    login_form.locator('input[type="password"]').fill("password123")
    
    # Click nút đăng nhập
    login_form.locator('button[type="submit"]').click()
    
    # Chờ redirect sang trang dashboard/search
    page.wait_for_url(re.compile(r".*(search|dashboard)"), timeout=15000)
    
@pytest.mark.e2e
def test_login_failure_wrong_password(page: Page):
    """
    Test kịch bản đăng nhập thất bại (Negative Test).
    """
    page.goto(f"{FRONTEND_URL}/auth")
    
    login_form = page.locator('form').filter(has_text="Đăng nhập")
    login_form.locator('input[type="email"]').fill("test_e2e@example.com")
    login_form.locator('input[type="password"]').fill("WRONG_PASSWORD")
    login_form.locator('button[type="submit"]').click()
    
    # Kì vọng xuất hiện thông báo lỗi trên giao diện
    page.wait_for_timeout(2000)  # Wait for error to appear
    error_message = page.locator('[role="alert"], .error-message, .alert, .error')
    if error_message.count() > 0:
        expect(error_message.first).to_be_visible()
    else:
        # If no error message found, check if we stayed on auth page
        expect(page).to_have_url(re.compile(r".*/auth"))
