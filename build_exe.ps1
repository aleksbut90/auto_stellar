# Build script for creating standalone executable
# This script creates a clean virtual environment and builds the exe

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stellar OCR Automation - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Remove old venv if it exists
if (Test-Path "venv") {
    Write-Host "[1/6] Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
    Write-Host "      Old venv removed." -ForegroundColor Green
} else {
    Write-Host "[1/6] No old virtual environment found." -ForegroundColor Green
}
Write-Host ""

# Step 2: Create new virtual environment
Write-Host "[2/6] Creating new virtual environment..." -ForegroundColor Yellow
py -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR: Failed to create virtual environment!" -ForegroundColor Red
    exit 1
}
Write-Host "      Virtual environment created." -ForegroundColor Green
Write-Host ""

# Step 3: Activate virtual environment and install dependencies
Write-Host "[3/6] Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -m pip install --upgrade pip
& "venv\Scripts\pip.exe" install -r requirements_minimal.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}
Write-Host "      Dependencies installed." -ForegroundColor Green
Write-Host ""

# Step 4: Clean old build artifacts
Write-Host "[4/6] Cleaning old build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
Write-Host "      Build artifacts cleaned." -ForegroundColor Green
Write-Host ""

# Step 5: Build executable with PyInstaller
Write-Host "[5/6] Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "      This may take several minutes..." -ForegroundColor Cyan
& "venv\Scripts\pyinstaller.exe" main.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR: PyInstaller build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "      Executable built successfully." -ForegroundColor Green
Write-Host ""

# Step 6: Verify the executable exists
Write-Host "[6/6] Verifying build..." -ForegroundColor Yellow
if (Test-Path "dist\Stellar_and_Arrival_Automation.exe") {
    $fileSize = (Get-Item "dist\Stellar_and_Arrival_Automation.exe").Length / 1MB
    Write-Host "      SUCCESS! Executable created." -ForegroundColor Green
    Write-Host "      Location: dist\Stellar_and_Arrival_Automation.exe" -ForegroundColor Green
    Write-Host "      Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Executable not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the executable: .\dist\Stellar_and_Arrival_Automation.exe" -ForegroundColor White
Write-Host "2. Make sure the game is running before starting automation" -ForegroundColor White
Write-Host "3. The executable includes the Tesseract OCR engine" -ForegroundColor White
Write-Host ""