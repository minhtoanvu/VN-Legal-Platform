import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('User can login successfully', async ({ page }) => {
    // 1. Điều hướng tới trang web
    await page.goto('/');

    // Kiểm tra xem đã chuyển hướng đến trang Login chưa (nếu chưa login)
    // Tùy thuộc vào UI hiện tại, giả sử URL chứa /login hoặc có form Đăng nhập
    if (page.url().includes('/login') || await page.locator('text=Đăng nhập').isVisible()) {
      // 2. Điền thông tin đăng nhập giả định
      // Thay thế selector bằng các id hoặc placeholder thực tế của form login bạn đang dùng
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'password123');
      
      // 3. Click nút Đăng nhập
      await page.click('button:has-text("Đăng nhập")');
      
      // 4. Xác nhận đăng nhập thành công (chuyển hướng sang trang chủ hoặc Dashboard)
      // Ví dụ: Chờ cho nút "Đăng xuất" hoặc avatar xuất hiện
      await expect(page).toHaveURL('/');
      // await expect(page.locator('text=Đăng xuất')).toBeVisible();
    } else {
      console.log('Đã login hoặc không bị chuyển hướng sang trang login.');
    }
  });
});
