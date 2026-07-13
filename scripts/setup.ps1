#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot '.venv'
$PythonLauncher = 'py'
$PythonVersion = '3.11'
$RequirementsFile = Join-Path $ProjectRoot 'requirements.txt'

Set-Location $ProjectRoot

Write-Host "RetailFlow Python setup (target: Python $PythonVersion)" -ForegroundColor Cyan

if (-not (Get-Command $PythonLauncher -ErrorAction SilentlyContinue)) {
    throw "Python launcher '$PythonLauncher' not found. Install Python $PythonVersion from https://www.python.org/downloads/"
}

$PythonExe = & $PythonLauncher "-$PythonVersion" -c "import sys; print(sys.executable)" 2>$null
if (-not $PythonExe) {
    throw "Python $PythonVersion is not installed. Run: py install $PythonVersion"
}

Write-Host "Using interpreter: $PythonExe"

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment at .venv ..."
    & $PythonLauncher "-$PythonVersion" -m venv $VenvPath
} else {
    Write-Host "Virtual environment already exists at .venv"
}

$VenvPython = Join-Path $VenvPath 'Scripts\python.exe'
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment is incomplete. Remove .venv and run this script again."
}

Write-Host "Upgrading pip ..."
& $VenvPython -m pip install --upgrade pip wheel setuptools

Write-Host "Installing dependencies from requirements.txt ..."
& $VenvPython -m pip install -r $RequirementsFile

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Activate the environment:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Verify:"
Write-Host "  python --version"
Write-Host "  python -c `"import pyspark; print(pyspark.__version__)`""
