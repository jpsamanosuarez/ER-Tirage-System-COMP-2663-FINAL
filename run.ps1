# -------------------------------------
# Windows Startup Script for ER Triage
# -------------------------------------

Write-Host "Starting ER Triage & Queue Manager..." -ForegroundColor Cyan

# 1. Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow

$venvPath = ".\venv\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    & $venvPath
} else {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Red
    python -m venv venv
    & $venvPath
}

# 2. Install dependencies if needed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# 3. Run the main NiceGUI application
Write-Host "Launching application..." -ForegroundColor Green
python main.py
