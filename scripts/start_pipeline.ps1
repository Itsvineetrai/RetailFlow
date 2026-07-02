Write-Host ""
Write-Host "========================================="
Write-Host " Starting AeroMart Data Platform"
Write-Host "========================================="
Write-Host ""

# -----------------------------------------
# Bronze - Online Sales
# -----------------------------------------

Start-Process powershell `
-NoExit `
-Command "python spark\bronze\run_online_sales.py"

Start-Sleep -Seconds 3

# -----------------------------------------
# Bronze - POS Batch
# -----------------------------------------

Start-Process powershell `
-NoExit `
-Command "python spark\bronze\run_pos_ingestion.py"

Start-Sleep -Seconds 3

# -----------------------------------------
# Data Generator
# -----------------------------------------

Start-Process powershell `
-NoExit `
-Command "python ingestion\generator.py"

Write-Host ""
Write-Host "========================================="
Write-Host " AeroMart Pipeline Started"
Write-Host "========================================="
Write-Host ""