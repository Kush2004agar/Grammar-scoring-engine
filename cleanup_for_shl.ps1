# PowerShell script to clean up project for SHL submission
# Run from grammar-scoring/ directory

Write-Host "Cleaning up project for SHL submission..." -ForegroundColor Green

# Remove virtual environment
if (Test-Path ".venv") {
    Write-Host "Removing .venv/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
}

# Remove audio files (large, provided by SHL)
if (Test-Path "data\train_audio") {
    Write-Host "Removing data/train_audio/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force data\train_audio
}
if (Test-Path "data\test_audio") {
    Write-Host "Removing data/test_audio/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force data\test_audio
}

# Remove generated/cached files
if (Test-Path "data\asr_cache") {
    Write-Host "Removing data/asr_cache/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force data\asr_cache
}
if (Test-Path "data\models") {
    Write-Host "Removing data/models/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force data\models
}
if (Test-Path "data\features") {
    Write-Host "Removing data/features/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force data\features
}
if (Test-Path "data\logs") {
    Write-Host "Removing data/logs/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force data\logs
}

# Remove Python cache
Write-Host "Removing Python cache files..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# Remove helper files (optional)
if (Test-Path "download_ffmpeg.py") {
    Write-Host "Removing download_ffmpeg.py..." -ForegroundColor Yellow
    Remove-Item download_ffmpeg.py
}
if (Test-Path "INSTALL_FFMPEG.md") {
    Write-Host "Removing INSTALL_FFMPEG.md..." -ForegroundColor Yellow
    Remove-Item INSTALL_FFMPEG.md
}

# Remove submission file (don't submit your predictions!)
if (Test-Path "submission\submission.csv") {
    Write-Host "Removing submission/submission.csv (don't submit predictions)..." -ForegroundColor Yellow
    Remove-Item submission\submission.csv
}

Write-Host "`nCleanup complete! Your project is ready for SHL submission." -ForegroundColor Green
Write-Host "Total size should now be < 10 MB (mostly code and notebooks)." -ForegroundColor Green

