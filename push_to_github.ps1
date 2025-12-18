# PowerShell script to prepare and push project to GitHub
# Run this from the grammar-scoring/ directory

param(
    [string]$GitHubUsername = "",
    [string]$RepositoryName = "grammar-scoring-engine",
    [switch]$SkipGitInit = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "GitHub Push Preparation Script" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "`n[OK] Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "`n[ERROR] Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "README.md")) {
    Write-Host "`n[ERROR] README.md not found. Are you in the grammar-scoring directory?" -ForegroundColor Red
    exit 1
}

Write-Host "`n[OK] Current directory: $(Get-Location)" -ForegroundColor Green

# Step 1: Initialize Git (if not already done)
if (-not $SkipGitInit) {
    if (-not (Test-Path ".git")) {
        Write-Host "`n[1/6] Initializing Git repository..." -ForegroundColor Yellow
        git init
        Write-Host "[OK] Git repository initialized" -ForegroundColor Green
    } else {
        Write-Host "`n[1/6] Git repository already exists" -ForegroundColor Green
    }
} else {
    Write-Host "`n[1/6] Skipping Git initialization" -ForegroundColor Yellow
}

# Step 2: Check .gitignore
Write-Host "`n[2/6] Checking .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Write-Host "[OK] .gitignore exists" -ForegroundColor Green
} else {
    Write-Host "[WARN] .gitignore not found - creating one..." -ForegroundColor Yellow
    # .gitignore should already exist, but just in case
}

# Step 3: Check what will be committed
Write-Host "`n[3/6] Checking files to be committed..." -ForegroundColor Yellow
git add .
$status = git status --short
$fileCount = ($status | Measure-Object).Count
Write-Host "[OK] $fileCount files staged for commit" -ForegroundColor Green

# Show some example files
Write-Host "`nSample files to be committed:" -ForegroundColor Cyan
$status | Select-Object -First 10 | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
}
if ($fileCount -gt 10) {
    Write-Host "  ... and $($fileCount - 10) more files" -ForegroundColor Gray
}

# Step 4: Create initial commit
Write-Host "`n[4/6] Creating initial commit..." -ForegroundColor Yellow
$commitMessage = @"
Initial commit: Grammar Scoring Engine for Spoken Audio

- Complete end-to-end pipeline from audio to grammar scores
- Whisper-based ASR transcription
- Interpretable grammar feature extraction
- Ridge regression baseline model
- Comprehensive evaluation and error analysis
- All visualizations and results documentation
- Full reproducibility with fixed random seeds
"@

try {
    git commit -m $commitMessage
    Write-Host "[OK] Initial commit created" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Commit may have failed or nothing to commit" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
}

# Step 5: Set up remote (if GitHub username provided)
if ($GitHubUsername -ne "") {
    Write-Host "`n[5/6] Setting up GitHub remote..." -ForegroundColor Yellow
    
    $remoteUrl = "https://github.com/$GitHubUsername/$RepositoryName.git"
    
    # Check if remote already exists
    $existingRemote = git remote get-url origin 2>$null
    if ($existingRemote) {
        Write-Host "[INFO] Remote 'origin' already exists: $existingRemote" -ForegroundColor Cyan
        $update = Read-Host "Update to $remoteUrl? (y/n)"
        if ($update -eq "y") {
            git remote set-url origin $remoteUrl
            Write-Host "[OK] Remote updated" -ForegroundColor Green
        }
    } else {
        git remote add origin $remoteUrl
        Write-Host "[OK] Remote added: $remoteUrl" -ForegroundColor Green
    }
    
    # Rename branch to main
    git branch -M main 2>$null
    
    Write-Host "`n[6/6] Ready to push!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Create repository on GitHub: https://github.com/new" -ForegroundColor Yellow
    Write-Host "   - Name: $RepositoryName" -ForegroundColor Yellow
    Write-Host "   - DO NOT initialize with README, .gitignore, or license" -ForegroundColor Yellow
    Write-Host "2. Push to GitHub:" -ForegroundColor Yellow
    Write-Host "   git push -u origin main" -ForegroundColor White
} else {
    Write-Host "`n[5/6] Skipping remote setup (no GitHub username provided)" -ForegroundColor Yellow
    Write-Host "`nTo set up remote manually:" -ForegroundColor Cyan
    Write-Host "  git remote add origin https://github.com/YOUR_USERNAME/$RepositoryName.git" -ForegroundColor White
    Write-Host "  git branch -M main" -ForegroundColor White
    Write-Host "  git push -u origin main" -ForegroundColor White
}

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "Preparation Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "`nRepository is ready to push to GitHub!" -ForegroundColor Green
Write-Host "See GITHUB_SETUP.md for detailed instructions." -ForegroundColor Cyan

