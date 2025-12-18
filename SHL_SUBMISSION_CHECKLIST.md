# SHL Submission Cleanup Checklist

## Files/Folders to EXCLUDE from SHL Submission

### ❌ DO NOT INCLUDE (Large/Generated Data)
1. **`.venv/`** - Virtual environment (hundreds of MB)
2. **`data/train_audio/`** - Training audio files (provided by SHL, not needed)
3. **`data/test_audio/`** - Test audio files (provided by SHL, not needed)
4. **`data/asr_cache/`** - Cached ASR transcripts (can be regenerated)
5. **`data/models/`** - Trained model files (can be regenerated from code)
6. **`data/features/`** - Cached feature files (can be regenerated)
7. **`data/logs/`** - Log files (not needed)
8. **`submission/submission.csv`** - Your predictions (don't submit your own predictions!)

### ❌ DO NOT INCLUDE (Python Cache/IDE Files)
9. **`__pycache__/`** - Python bytecode cache
10. **`*.pyc`** - Compiled Python files
11. **`.ipynb_checkpoints/`** - Jupyter notebook checkpoints
12. **`.vscode/`** or **`.idea/`** - IDE settings (if present)
13. **`*.swp`**, **`*.swo`** - Editor swap files

### ❌ DO NOT INCLUDE (Temporary/Helper Files)
14. **`download_ffmpeg.py`** - Helper script (not needed)
15. **`INSTALL_FFMPEG.md`** - Installation docs (optional, but not required)

### ✅ DO INCLUDE (Essential Code)
- ✅ `src/` - All source code
- ✅ `notebooks/` - All Jupyter notebooks
- ✅ `submission/generate_submission.py` - Submission script
- ✅ `train_baseline.py` - Training script
- ✅ `requirements.txt` - Dependencies
- ✅ `README.md` - Documentation
- ✅ `data/train.csv` - Training labels (small file, OK to include)

---

## Quick Cleanup Commands

Run these from `grammar-scoring/` directory:

```powershell
# Remove virtual environment
Remove-Item -Recurse -Force .venv

# Remove audio files (large)
Remove-Item -Recurse -Force data\train_audio
Remove-Item -Recurse -Force data\test_audio

# Remove generated/cached files
Remove-Item -Recurse -Force data\asr_cache
Remove-Item -Recurse -Force data\models
Remove-Item -Recurse -Force data\features
Remove-Item -Recurse -Force data\logs

# Remove Python cache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Remove helper files (optional)
Remove-Item download_ffmpeg.py
Remove-Item INSTALL_FFMPEG.md

# Remove your submission file (don't submit predictions!)
Remove-Item submission\submission.csv
```

---

## What SHL Competition Needs

SHL competitions typically want:
1. **Code** - Your source code (`src/`, `notebooks/`, scripts)
2. **Documentation** - README explaining your approach
3. **Dependencies** - `requirements.txt`
4. **Reproducibility** - Code should be able to regenerate results

They **DO NOT** need:
- Pre-trained models (code should train them)
- Large data files (they provide the data)
- Virtual environments
- Cache files

---

## Final Submission Structure

Your cleaned submission should look like:

```
grammar-scoring/
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── asr.py
│   ├── text_cleaning.py
│   ├── feature_engineering.py
│   ├── model.py
│   ├── evaluation.py
│   └── error_analysis.py
├── notebooks/
│   ├── 01_problem_framing.ipynb
│   ├── 02_data_exploration.ipynb
│   ├── 03_asr_analysis.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_modeling.ipynb
│   └── 06_evaluation.ipynb
├── submission/
│   └── generate_submission.py
├── data/
│   └── train.csv  (small file, OK)
├── train_baseline.py
├── requirements.txt
└── README.md
```

Total size should be **< 10 MB** (mostly code and notebooks).

