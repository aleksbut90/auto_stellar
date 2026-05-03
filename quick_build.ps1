# Quick build script - uses existing venv if available
# Use this if you already have a clean venv set up

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Build (using existing venv)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run build_exe.ps1 first to create a clean venv." -ForegroundColor Yellow
    exit 1
}

# Step 1: Clean old build artifacts (НО НЕ dataset!)
Write-Host "[1/2] Cleaning old build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
# Никогда не удаляем dist/dataset!
if (Test-Path "dist\Stellar_Automation.exe") {
    Remove-Item -Force "dist\Stellar_Automation.exe"
}
if (Test-Path "dist\Stellar_Automation") {
    Remove-Item -Recurse -Force "dist\Stellar_Automation"
}
Write-Host "      Build artifacts cleaned." -ForegroundColor Green
Write-Host ""

# Step 2: Build executable with PyInstaller
Write-Host "[2/2] Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "      This may take several minutes..." -ForegroundColor Cyan
& "venv\Scripts\pyinstaller.exe" main.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR: PyInstaller build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "      Executable built successfully." -ForegroundColor Green
Write-Host ""

# Verify the executable exists
if (Test-Path "dist\Stellar_Automation.exe") {
    $fileSize = (Get-Item "dist\Stellar_Automation.exe").Length / 1MB
    Write-Host "SUCCESS! Executable created." -ForegroundColor Green
    Write-Host "Location: dist\Stellar_Automation.exe" -ForegroundColor Green
    Write-Host "Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "ERROR: Executable not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""