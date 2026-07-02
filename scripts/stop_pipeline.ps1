Write-Host ""
Write-Host "Stopping AeroMart Processes..."
Write-Host ""

Get-Process python -ErrorAction SilentlyContinue |
Stop-Process -Force

Write-Host ""
Write-Host "Python processes stopped."
Write-Host ""