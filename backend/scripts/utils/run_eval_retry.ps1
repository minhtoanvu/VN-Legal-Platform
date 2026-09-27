$max_retries = 10
for ($i = 1; $i -le $max_retries; $i++) {
    Write-Host "========================================"
    Write-Host "ĐANG CHẠY THỰC NGHIỆM - LẦN THỬ THỨ $i"
    Write-Host "========================================"
    
    # Chạy script và hứng toàn bộ log (cả stderr và stdout)
    $output = .\venv\Scripts\python.exe scripts\evaluate_contract_models.py 2>&1
    
    # In log ra màn hình
    $output | Out-String | Write-Host
    
    # Kiểm tra xem có bị lỗi RAM không
    $outStr = $output | Out-String
    if ($outStr -match "os error 1455" -or $outStr -match "The paging file is too small") {
        Write-Host "❌ Phát hiện lỗi tràn RAM (os error 1455). Đợi 3 giây rồi thử lại..."
        Start-Sleep -Seconds 3
    } else {
        Write-Host "✅ Hoàn thành mượt mà, KHÔNG BỊ TRÀN RAM!"
        break
    }
}
