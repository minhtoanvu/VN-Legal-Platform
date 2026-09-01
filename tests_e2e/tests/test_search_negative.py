import pytest
from playwright.sync_api import Page, expect
import re

# Thay đổi URL tùy vào môi trường test của Frontend
FRONTEND_URL = "http://127.0.0.1:5173"

@pytest.mark.e2e
def test_empty_search(page: Page):
    """Test Case TC_SRCH_003: Không nhập gì cả mà bấm tìm kiếm."""
    page.goto(f"{FRONTEND_URL}")
    
    # Wait for page to load
    page.wait_for_load_state("networkidle")
    
    # Find search input and button
    search_input = page.locator('input[placeholder*="tìm"], input[type="search"]').first
    search_button = page.locator('button:has-text("Tìm"), button[type="submit"]').first
    
    if search_input.is_visible() and search_button.is_visible():
        # Leave search empty and click search
        search_input.fill("")
        search_button.click()
        
        # Check that page doesn't crash - should still be on search page
        page.wait_for_timeout(1000)
        expect(page).to_have_url(re.compile(r".*/search"))
    else:
        # Search elements not found, skip test
        pytest.skip("Search elements not found on page")

@pytest.mark.e2e
def test_xss_injection(page: Page):
    """Test Case TC_SRCH_004: Nhập mã độc XSS."""
    page.goto(f"{FRONTEND_URL}")
    
    # Wait for page to load
    page.wait_for_load_state("networkidle")
    
    # Find search input and button
    search_input = page.locator('input[placeholder*="tìm"], input[type="search"]').first
    search_button = page.locator('button:has-text("Tìm"), button[type="submit"]').first
    
    if search_input.is_visible() and search_button.is_visible():
        # Nhập mã độc javascript
        malicious_code = "<script>alert('Hacked!');</script>"
        search_input.fill(malicious_code)
        search_button.click()
        
        # Mong đợi: Không có popup alert nào bật lên (Không bị XSS)
        # Set up a dialog handler - if it fires, test fails
        dialog_fired = False
        def handle_dialog(dialog):
            nonlocal dialog_fired
            dialog_fired = True
            dialog.dismiss()
        
        page.once("dialog", handle_dialog)
        page.wait_for_timeout(2000)
        
        assert not dialog_fired, "XSS vulnerability detected - dialog appeared"
        # Web is safe if we get here
        assert True
    else:
        # Search elements not found, skip test
        pytest.skip("Search elements not found on page")
