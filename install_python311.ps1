# PowerShell script to download and install Python 3.11
$ErrorActionPreference = "Stop"

Write-Host "=== Installing Python 3.11 for Interview Coach ===" -ForegroundColor Cyan
Write-Host ""

# Download Python 3.11.9
$url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
$installer = "$env:TEMP\python-3.11.9-amd64.exe"

Write-Host "[1/3] Downloading Python 3.11.9..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
Write-Host "Download complete: $installer" -ForegroundColor Green

# Install Python 3.11 silently
Write-Host "[2/3] Installing Python 3.11.9..." -ForegroundColor Yellow
$args = @("/quiet", "InstallAllUsers=1", "PrependPath=0", "Include_test=0")
$process = Start-Process $installer -ArgumentList $args -Wait -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host "Installation successful!" -ForegroundColor Green
} else {
    Write-Host "Installation exit code: $($process.ExitCode)" -ForegroundColor Yellow
}

# Clean up
Write-Host "[3/3] Cleaning up..." -ForegroundColor Yellow
Remove-Item $installer -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python 3.11 should now be installed in: C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Close and reopen this terminal"
Write-Host "  2. Run: py -3.11 --version"
Write-Host "  3. Create venv: py -3.11 -m venv venv"
Write-Host "  4. Activate: venv\Scripts\Activate.ps1"
Write-Host ""
