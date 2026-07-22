# PowerShell Build Script for AI Coders Proxy Fixer v2.1.0
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Building AI Coders Proxy Fixer v2.1.0 (Portable & Setup) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Clean previous build artifacts
Write-Host "[1/4] Cleaning old build directories..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

# 2. Build Portable Single-File Executable
Write-Host "[2/4] Building Standalone Portable Executable..." -ForegroundColor Yellow
pyinstaller --noconfirm --onefile --windowed --icon="assets/app_icon.ico" --name="AI_Coders_Proxy_Fixer" --distpath="dist\portable" --add-data "assets;assets/" "src\main.py"

# Zip Portable Release
if (Test-Path "dist\portable\AI_Coders_Proxy_Fixer.exe") {
    Compress-Archive -Path "dist\portable\AI_Coders_Proxy_Fixer.exe" -DestinationPath "dist\AI_Coders_Proxy_Fixer_v2.1.0_Portable.zip" -Force
    Write-Host "-> Portable ZIP created: dist\AI_Coders_Proxy_Fixer_v2.1.0_Portable.zip" -ForegroundColor Green
}

# 3. Build Installer Source Directory
Write-Host "[3/4] Building Installer Source Directory Payload..." -ForegroundColor Yellow
pyinstaller --noconfirm --windowed --icon="assets/app_icon.ico" --name="AI_Coders_Proxy_Fixer" --distpath="dist\installer_source" --add-data "assets;assets/" "src\main.py"

# 4. Compile Inno Setup Installer (if ISCC is installed)
Write-Host "[4/4] Checking Inno Setup Compiler (ISCC)..." -ForegroundColor Yellow
$isccPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Path
)

$isccFound = $false
foreach ($iscc in $isccPaths) {
    if ($iscc -and (Test-Path $iscc)) {
        Write-Host "Compiling installer.iss using ISCC at $iscc..." -ForegroundColor Green
        & $iscc "installer.iss"
        $isccFound = $true
        break
    }
}

if (-not $isccFound) {
    Write-Host "Notice: ISCC.exe not found locally. (GitHub Actions CI/CD will compile it automatically via choco install innosetup)." -ForegroundColor Magenta
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Build Process Completed Successfully! " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
