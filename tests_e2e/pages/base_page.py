from playwright.async_api import Page

class BasePage:
    """Lớp nền tảng (Base Class) chứa các hàm dùng chung cho mọi trang web."""
    def __init__(self, page: Page):
        self.page = page

    async def navigate(self, url: str):
        """Điều hướng tới một URL cụ thể."""
        await self.page.goto(url)

    async def get_title(self) -> str:
        """Lấy tiêu đề trang."""
        return await self.page.title()
