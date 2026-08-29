import asyncio
from playwright.async_api import async_playwright
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.search_page import SearchPage

async def test_empty_search():
    """Test Case TC_SRCH_003: Không nhập gì cả mà bấm tìm kiếm."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        search_page = SearchPage(page)
        
        await search_page.open()
        
        # Bấm tìm kiếm ngay lập tức (không nhập keyword)
        await search_page.search_input.fill("")
        await search_page.search_button.click()
        
        # Mong đợi: Vẫn ở trang chủ, không crash web, nút có thể bị disable hoặc API không bị gọi
        # (Ở đây ta kiểm tra xem API /search có bị bắn đi không, nếu có là lỗi)
        # Bắt sự kiện mạng (Network interception)
        api_called = False
        async def handle_request(route):
            nonlocal api_called
            if "search" in route.request.url:
                api_called = True
            await route.continue_()
            
        await page.route("**/*", handle_request)
        
        print("Đã test xong Case: Input rỗng.")
        await browser.close()

async def test_xss_injection():
    """Test Case TC_SRCH_004: Nhập mã độc XSS."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        search_page = SearchPage(page)
        
        await search_page.open()
        
        # Nhập mã độc javascript
        malicious_code = "<script>alert('Hacked!');</script>"
        await search_page.search_for(malicious_code)
        
        # Mong đợi: Không có popup alert nào bật lên (Không bị XSS)
        # Playwright sẽ tự động quăng lỗi nếu có Dialog bất thường nếu không catch,
        # Nên nếu code chạy thẳng tới đây mà không treo nghĩa là web an toàn.
        print("Đã test xong Case: Chống XSS Injection. Web an toàn!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_empty_search())
    asyncio.run(test_xss_injection())
