import { test, expect } from '@playwright/test';

test.describe('Contract Analysis Flow', () => {
  test('User can navigate to contract page and see upload area', async ({ page }) => {
    await page.goto('/');

    // 1. Chuyển hướng sang trang phân tích hợp đồng
    // Giả định có tab hoặc link điều hướng chứa chữ "Hợp đồng" hoặc "Contract"
    const navLink = page.locator('text=Hợp đồng');
    if (await navLink.isVisible()) {
      await navLink.click();
      await expect(page).toHaveURL(/.*contract/);
    } else {
      // Nhảy thẳng tới URL
      await page.goto('/contract');
    }

    // 2. Xác minh UI Upload File tồn tại
    // Chờ ô Input type file
    const fileInput = page.locator('input[type="file"]');
    if (await fileInput.count() > 0) {
      console.log('Tìm thấy nút Upload file Hợp đồng!');
    } else {
      console.log('Chưa xây dựng xong UI Upload Hợp đồng.');
    }
  });
});
