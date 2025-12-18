# Creating a Submission Package

## ✅ Safe to Create Submission Folder

**Yes, creating a final submission folder is safe and recommended!**

- ✅ **Won't affect your original project** - It's just copying files
- ✅ **Paths will still work** - The code uses relative paths calculated from file locations
- ✅ **Maintains structure** - As long as you keep the folder structure, everything works

---

## Quick Method: Use the Script

Run this from the `grammar-scoring/` directory:

```powershell
.\create_submission_package.ps1
```

This will create a `grammar-scoring-submission/` folder with:
- ✅ All source code (`src/`)
- ✅ All notebooks (`notebooks/`)
- ✅ Training script (`train_baseline.py`)
- ✅ Submission script (`submission/generate_submission.py`)
- ✅ Documentation (`README.md`, `requirements.txt`)
- ✅ Training labels (`data/train.csv`)
- ✅ Empty directories for data (will be created when code runs)
- ❌ **Excludes**: Large files, cache, models, audio files

---

## Manual Method

If you prefer to do it manually:

### 1. Create a new folder
```powershell
mkdir grammar-scoring-submission
cd grammar-scoring-submission
```

### 2. Copy essential files (maintaining structure)
```powershell
# From grammar-scoring/ directory
Copy-Item -Recurse src grammar-scoring-submission\
Copy-Item -Recurse notebooks grammar-scoring-submission\
Copy-Item -Recurse submission grammar-scoring-submission\
Copy-Item train_baseline.py grammar-scoring-submission\
Copy-Item requirements.txt grammar-scoring-submission\
Copy-Item README.md grammar-scoring-submission\
Copy-Item SHL_SUBMISSION_CHECKLIST.md grammar-scoring-submission\

# Create data directory and copy only train.csv
mkdir grammar-scoring-submission\data
Copy-Item data\train.csv grammar-scoring-submission\data\
```

### 3. Create empty directories (needed at runtime)
```powershell
cd grammar-scoring-submission
mkdir data\train_audio
mkdir data\test_audio
mkdir data\asr_cache
mkdir data\models
mkdir data\features
mkdir data\logs
```

### 4. Clean up cache files
```powershell
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
```

---

## What Gets Included

### ✅ Included:
- `src/` - All source code
- `notebooks/` - All Jupyter notebooks  
- `submission/generate_submission.py` - Submission script
- `train_baseline.py` - Training script
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `data/train.csv` - Training labels (small file)

### ❌ Excluded:
- `.venv/` - Virtual environment (too large)
- `data/train_audio/` - Training audio (provided by competition)
- `data/test_audio/` - Test audio (provided by competition)
- `data/asr_cache/` - Cached transcripts (regenerated)
- `data/models/` - Trained models (regenerated from code)
- `data/features/` - Cached features (regenerated)
- `submission/submission.csv` - Your predictions (don't submit!)
- `__pycache__/` - Python cache
- Helper scripts (`download_ffmpeg.py`, etc.)

---

## Why This Works

The project uses **relative paths** calculated from file locations:

```python
# In src/config.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
```

This means:
- ✅ Paths are calculated relative to where `config.py` is located
- ✅ Works in any folder as long as structure is maintained
- ✅ No hardcoded absolute paths
- ✅ Portable across different machines

---

## Testing the Submission Package

After creating the package, test it:

```powershell
cd grammar-scoring-submission

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Test imports
python -c "from src.config import paths; print('Config OK')"

# The package is ready!
```

---

## Final Size

Your submission package should be:
- **< 10 MB** (mostly code and notebooks)
- **Portable** (no absolute paths)
- **Reproducible** (can regenerate all results from code)

---

## Important Notes

1. **Don't include your predictions** - The competition will run your code to generate predictions
2. **Don't include trained models** - Your code should train them from scratch
3. **Don't include large data** - The competition provides the data
4. **Keep the folder structure** - Paths depend on relative structure

---

## Summary

✅ **Safe to create submission folder**  
✅ **Won't affect original project**  
✅ **Paths will work correctly**  
✅ **Use the script for convenience**

The submission package is a **clean copy** of your code - your original project remains untouched!

