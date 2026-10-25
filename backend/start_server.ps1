Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  GetGoals PCAT + NCD Adaptive Placement Engine" -ForegroundColor Cyan
Write-Host "  API Server running on: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" "pcat_server.py"
