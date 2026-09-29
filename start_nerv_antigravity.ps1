# NERV-BREAK-Antigravity 1-Click Launcher
# Automatically launches proxy_relay.py (:8091) and configures Antigravity CLI / Environment

$PYTHON_CMD = "D:/Code/Python/Python313/python.exe"
$BASE_DIR = $PSScriptRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  NERV-BREAK-Antigravity 1-Click Proxy Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Stop old proxy instances
Write-Host "[1/3] Clearing existing proxy instances..." -ForegroundColor Yellow
Get-WmiObject Win32_Process -Filter "Name = 'python.exe'" | Where-Object { $_.CommandLine -like "*proxy_relay.py*" } | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

# 2. Start proxy_relay.py in background
Write-Host "[2/3] Starting proxy_relay.py on port 8091..." -ForegroundColor Yellow
Start-Process -FilePath $PYTHON_CMD -ArgumentList "$BASE_DIR/proxy_relay.py --port 8091" -WindowStyle Hidden

Start-Sleep -Seconds 2

# 3. Test Proxy Health
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8091/" -Method Get -TimeoutSec 3
    Write-Host "[SUCCESS] Proxy is ONLINE!" -ForegroundColor Green
    Write-Host $resp -ForegroundColor Gray
} catch {
    Write-Host "[WARNING] Proxy started, waiting for connection..." -ForegroundColor Yellow
}

# 4. Configure Environment Variables for CLI / Desktop Session
$env:OPENAI_BASE_URL = "http://127.0.0.1:8091/v1"
$env:OPENAI_API_KEY = "nerv-key"

Write-Host "`n[OK] Environment configured:" -ForegroundColor Green
Write-Host "     OPENAI_BASE_URL = $env:OPENAI_BASE_URL" -ForegroundColor White
Write-Host "     Proxy Dashboard  = http://127.0.0.1:8090" -ForegroundColor White
Write-Host "`nYou can now run 'agy' or connect Antigravity Desktop to http://127.0.0.1:8091/v1`n" -ForegroundColor Cyan
