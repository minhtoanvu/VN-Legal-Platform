import asyncio
from playwright.async_api import async_playwright
import os
import sys

# Thêm đường dẫn để import được package pages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.search_page import SearchPage

async def run_test():
    """Chạy kịch bản test bằng cấu trúc Page Object Model."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        # Khởi tạo Page Object
        search_page = SearchPage(page)
        
        print("1. Mở trang chủ AILIP...")
        await search_page.open()
        
        print("2. Tìm kiếm với từ khóa 'nghỉ việc'...")
        await search_page.search_for("nghỉ việc")
        
        print("3. Chờ kết quả hiển thị...")
        await search_page.wait_for_results()
        
        print("✅ Test Passed! Chụp ảnh màn hình nghiệm thu.")
        await page.screenshot(path="qa_evidence_pom_search.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
