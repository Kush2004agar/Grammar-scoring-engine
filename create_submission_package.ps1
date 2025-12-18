# PowerShell script to create a clean submission package
# This creates a copy of the project with only necessary files for submission

param(
    [string]$OutputFolder = "grammar-scoring-submission"
)

$ErrorActionPreference = "Stop"

Write-Host "Creating submission package..." -ForegroundColor Green
Write-Host "Output folder: $OutputFolder" -ForegroundColor Yellow

# Get the project root (parent of this script)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SubmissionRoot = Join-Path $ProjectRoot $OutputFolder

# Remove existing submission folder if it exists
if (Test-Path $SubmissionRoot) {
    Write-Host "Removing existing submission folder..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $SubmissionRoot
}

# Create submission root
New-Item -ItemType Directory -Path $SubmissionRoot | Out-Null
Write-Host "Created: $SubmissionRoot" -ForegroundColor Green

# Files and folders to copy (maintaining structure)
$ItemsToCopy = @(
    @{Source = "src"; Dest = "src"; Type = "Directory"},
    @{Source = "notebooks"; Dest = "notebooks"; Type = "Directory"},
    @{Source = "submission"; Dest = "submission"; Type = "Directory"},
    @{Source = "train_baseline.py"; Dest = "train_baseline.py"; Type = "File"},
    @{Source = "requirements.txt"; Dest = "requirements.txt"; Type = "File"},
    @{Source = "README.md"; Dest = "README.md"; Type = "File"},
    @{Source = "SHL_SUBMISSION_CHECKLIST.md"; Dest = "SHL_SUBMISSION_CHECKLIST.md"; Type = "File"}
)

# Copy items
foreach ($item in $ItemsToCopy) {
    $sourcePath = Join-Path $ProjectRoot $item.Source
    $destPath = Join-Path $SubmissionRoot $item.Dest
    
    if (Test-Path $sourcePath) {
        if ($item.Type -eq "Directory") {
            Write-Host "Copying directory: $($item.Source)..." -ForegroundColor Cyan
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
        } else {
            Write-Host "Copying file: $($item.Source)..." -ForegroundColor Cyan
            Copy-Item -Path $sourcePath -Destination $destPath -Force
        }
    } else {
        Write-Host "Warning: $($item.Source) not found, skipping..." -ForegroundColor Yellow
    }
}

# Create data directory structure (but only copy train.csv)
Write-Host "Creating data directory structure..." -ForegroundColor Cyan
$dataDir = Join-Path $SubmissionRoot "data"
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null

# Copy only train.csv (small file, OK to include)
$trainCsv = Join-Path $ProjectRoot "data\train.csv"
if (Test-Path $trainCsv) {
    Copy-Item -Path $trainCsv -Destination (Join-Path $dataDir "train.csv") -Force
    Write-Host "Copied: data/train.csv" -ForegroundColor Green
}

# Create empty directories that will be needed at runtime
$emptyDirs = @(
    "data\train_audio",
    "data\test_audio",
    "data\asr_cache",
    "data\models",
    "data\features",
    "data\logs"
)

foreach ($dir in $emptyDirs) {
    $fullPath = Join-Path $SubmissionRoot $dir
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
}

# Remove Python cache files
Write-Host "Cleaning Python cache files..." -ForegroundColor Cyan
Get-ChildItem -Path $SubmissionRoot -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $SubmissionRoot -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# Remove .ipynb_checkpoints if any
Get-ChildItem -Path $SubmissionRoot -Recurse -Filter ".ipynb_checkpoints" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Create a .gitignore for the submission (optional but helpful)
$gitignoreContent = @"
# Python
__pycache__/
*.pyc

# Data (will be provided by competition)
data/train_audio/
data/test_audio/
data/asr_cache/
data/models/
data/features/
data/logs/

# Generated files
submission/submission.csv
"@

$gitignorePath = Join-Path $SubmissionRoot ".gitignore"
Set-Content -Path $gitignorePath -Value $gitignoreContent

# Calculate size
$totalSize = (Get-ChildItem -Path $SubmissionRoot -Recurse -File | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($totalSize / 1MB, 2)

Write-Host "`n" + "="*60 -ForegroundColor Green
Write-Host "Submission package created successfully!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green
Write-Host "Location: $SubmissionRoot" -ForegroundColor Yellow
Write-Host "Total size: $sizeMB MB" -ForegroundColor Yellow
Write-Host "`nStructure:" -ForegroundColor Cyan
Get-ChildItem -Path $SubmissionRoot -Recurse -Directory | Select-Object FullName | ForEach-Object {
    $relativePath = $_.FullName.Replace($SubmissionRoot, "").TrimStart("\")
    Write-Host "  $relativePath\" -ForegroundColor Gray
}

Write-Host "`nNext steps:" -ForegroundColor Green
Write-Host "1. Test the submission package:" -ForegroundColor Yellow
Write-Host "   cd $OutputFolder" -ForegroundColor White
Write-Host "   python -m venv .venv" -ForegroundColor White
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   pip install -r requirements.txt" -ForegroundColor White
Write-Host "2. The package is ready for submission!" -ForegroundColor Yellow
Write-Host "="*60 -ForegroundColor Green

