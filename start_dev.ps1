# start_dev.ps1 — Khởi động toàn bộ môi trường dev AI Legal Platform
# Chạy: .\start_dev.ps1

$env:PYTHONIOENCODING = "utf-8"
$env:OMP_NUM_THREADS = "1"
$env:TOKENIZERS_PARALLELISM = "false"

Write-Host "=== AI Legal Platform - Dev Startup ===" -ForegroundColor Cyan

# 1. Mở Docker Desktop nếu chưa chạy
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[1/4] Dang mo Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "      Cho Docker khoi dong (30 giay)..."
    Start-Sleep -Seconds 30
} else {
    Write-Host "[1/4] Docker Desktop da san sang." -ForegroundColor Green
}

# 2. Khởi động PostgreSQL container
Write-Host "[2/4] Khoi dong PostgreSQL container..." -ForegroundColor Yellow
docker-compose up -d 2>$null
Start-Sleep -Seconds 8

# Kiểm tra container healthy
$status = docker ps --format "{{.Names}}\t{{.Status}}" | Select-String "legal_pgvector"
Write-Host "      $status" -ForegroundColor Green

# 3. Apply migrations
Write-Host "[3/4] Apply Alembic migrations..." -ForegroundColor Yellow
Set-Location backend
.\venv\Scripts\activate
alembic upgrade head 2>&1 | Select-String "Running upgrade|up to date" | Write-Host -ForegroundColor Green

# 4. Khởi động FastAPI
Write-Host "[4/4] Khoi dong FastAPI server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Swagger UI: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Health:     http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
uvicorn app.main:app --host 0.0.0.0 --port 8000
