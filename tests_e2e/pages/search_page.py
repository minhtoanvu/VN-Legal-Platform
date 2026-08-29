from .base_page import BasePage
from playwright.async_api import Page, Locator

class SearchPage(BasePage):
    """Mô hình hóa giao diện (Page Object Model) của trang Tìm Kiếm."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        # Khai báo các Element (Locators) trên trang
        self.search_input: Locator = page.get_by_placeholder("Nhập từ khóa tìm kiếm...")
        self.search_button: Locator = page.get_by_role("button", name="Tìm kiếm")
        self.result_card: Locator = page.locator(".result-card")

    async def open(self):
        """Mở trang tìm kiếm."""
        await self.navigate("http://localhost:5173/")

    async def search_for(self, keyword: str):
        """Thực hiện hành động gõ phím và bấm tìm kiếm."""
        await self.search_input.fill(keyword)
        await self.search_button.click()

    async def wait_for_results(self):
        """Đợi kết quả xuất hiện trên màn hình."""
        await self.result_card.first.wait_for(timeout=5000)
