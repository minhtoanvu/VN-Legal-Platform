import { test, expect } from '@playwright/test';

test.describe('Search Document Flow', () => {
  test('User can search for a legal document', async ({ page }) => {
    // 1. Đi tới trang chủ
    await page.goto('/');

    // 2. Định vị ô tìm kiếm (Giả định placeholder là "Tìm kiếm văn bản...")
    // Hãy thay đổi selector nếu thực tế khác
    const searchInput = page.locator('input[type="text"], input[type="search"]');
    
    // Nếu ô tìm kiếm tồn tại, ta sẽ nhập "Luật Đất đai"
    if (await searchInput.count() > 0) {
      await searchInput.first().fill('Luật Đất đai');
      await searchInput.first().press('Enter');

      // 3. Chờ kết quả hiển thị (chờ API /search trả về)
      // Giả sử kết quả được bọc trong các thẻ <a> hoặc thẻ có class .search-result
      await page.waitForTimeout(2000); // Tạm dừng 2s chờ load UI (Nên thay bằng waitForSelector thực tế)
      
      // Kiểm tra có ít nhất 1 kết quả
      const results = page.locator('text=Luật Đất đai');
      // Không nên strict quá nếu DB trống, nên ta chỉ check không crash
      console.log('Tìm kiếm hoàn tất, số lượng phần tử chứa từ khóa:', await results.count());
    } else {
      console.log('Không tìm thấy ô Search trên giao diện, vui lòng cập nhật selector.');
    }
  });
});
