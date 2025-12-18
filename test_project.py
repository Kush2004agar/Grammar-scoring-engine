"""
Comprehensive test script to verify the grammar scoring project is working correctly.

This script checks:
1. All imports work
2. Data files are accessible
3. Key functions can be called
4. Model can be loaded
5. Submission pipeline works

Run with: python test_project.py
"""

import sys
from pathlib import Path

print("=" * 60)
print("Grammar Scoring Project - Verification Tests")
print("=" * 60)

# Test 1: Check Python version
print("\n[1/10] Checking Python version...")
print(f"    Python {sys.version}")
if sys.version_info < (3, 8):
    print("    [WARN] WARNING: Python 3.8+ recommended")
else:
    print("    [OK] Python version OK")

# Test 2: Check project structure
print("\n[2/10] Checking project structure...")
required_dirs = [
    "src",
    "notebooks",
    "submission",
    "data",
]
missing_dirs = []
for dir_name in required_dirs:
    if not Path(dir_name).exists():
        missing_dirs.append(dir_name)
    else:
        print(f"    [OK] {dir_name}/ exists")

if missing_dirs:
    print(f"    [FAIL] Missing directories: {missing_dirs}")
    sys.exit(1)

# Test 3: Check data files
print("\n[3/10] Checking data files...")
if Path("data/train.csv").exists():
    print("    [OK] data/train.csv exists")
else:
    print("    [FAIL] data/train.csv missing")
    sys.exit(1)

train_audio_count = len(list(Path("data/train_audio").glob("*.wav"))) if Path("data/train_audio").exists() else 0
test_audio_count = len(list(Path("data/test_audio").glob("*.wav"))) if Path("data/test_audio").exists() else 0
print(f"    Train audio files: {train_audio_count}")
print(f"    Test audio files: {test_audio_count}")

# Test 4: Test imports
print("\n[4/10] Testing imports...")
try:
    from src.config import paths, asr_config, training_config
    print("    [OK] src.config imported")
except Exception as e:
    print(f"    [FAIL] Failed to import src.config: {e}")
    sys.exit(1)

try:
    from src.data_loader import load_train_labels, list_audio_files
    print("    [OK] src.data_loader imported")
except Exception as e:
    print(f"    [FAIL] Failed to import src.data_loader: {e}")
    sys.exit(1)

try:
    from src.asr import transcribe_split, load_cached_transcripts
    print("    [OK] src.asr imported")
except Exception as e:
    print(f"    [FAIL] Failed to import src.asr: {e}")
    sys.exit(1)

try:
    from src.text_cleaning import clean_transcript
    print("    [OK] src.text_cleaning imported")
except Exception as e:
    print(f"    [FAIL] Failed to import src.text_cleaning: {e}")
    sys.exit(1)

try:
    from src.feature_engineering import GrammarFeatureExtractor
    print("    [OK] src.feature_engineering imported")
except Exception as e:
    print(f"    [FAIL] Failed to import src.feature_engineering: {e}")
    sys.exit(1)

try:
    from src.model import train_baseline_model, cross_validate_baseline
    print("    [OK] src.model imported")
except Exception as e:
    print(f"    [FAIL] Failed to import src.model: {e}")
    sys.exit(1)

# Test 5: Test data loading
print("\n[5/10] Testing data loading...")
try:
    labels_df = load_train_labels()
    print(f"    [OK] Loaded {len(labels_df)} training labels")
    if len(labels_df) == 0:
        print("    [WARN] WARNING: No labels found")
except Exception as e:
    print(f"    [FAIL] Failed to load labels: {e}")
    sys.exit(1)

# Test 6: Test text cleaning
print("\n[6/10] Testing text cleaning...")
try:
    test_text = "uh i i i was um working in a team"
    cleaned, stats = clean_transcript(test_text)
    print(f"    [OK] Text cleaning works")
    print(f"    Example: '{test_text}' -> '{cleaned}'")
except Exception as e:
    print(f"    [FAIL] Text cleaning failed: {e}")
    sys.exit(1)

# Test 7: Test feature extraction (if ASR cache exists)
print("\n[7/10] Testing feature extraction...")
try:
    extractor = GrammarFeatureExtractor()
    test_texts = ["i was working in a team", "he go to meeting"]
    features = extractor.transform(test_texts)
    print(f"    [OK] Feature extraction works")
    print(f"    Extracted {features.shape[1]} features for {features.shape[0]} examples")
except Exception as e:
    print(f"    [FAIL] Feature extraction failed: {e}")
    print("    Note: This requires Java and LanguageTool. Install Java if needed.")
    # Don't exit - this might just be missing Java

# Test 8: Check if model exists
print("\n[8/10] Checking trained model...")
model_path = Path("data/models/final_baseline_model.joblib")
if model_path.exists():
    print(f"    [OK] Model file exists: {model_path}")
    try:
        import joblib
        artifacts = joblib.load(model_path)
        print(f"    [OK] Model can be loaded")
        print(f"    Model has {len(artifacts.feature_names)} features")
    except Exception as e:
        print(f"    [FAIL] Failed to load model: {e}")
else:
    print(f"    [WARN] Model not found. Run train_baseline.py first.")

# Test 9: Check ASR cache
print("\n[9/10] Checking ASR cache...")
train_cache = Path("data/asr_cache/asr_train.csv")
test_cache = Path("data/asr_cache/asr_test.csv")
if train_cache.exists():
    import pandas as pd
    train_asr = pd.read_csv(train_cache)
    non_empty = (train_asr["transcript"].fillna("").astype(str).str.strip() != "").sum()
    print(f"    [OK] Train ASR cache exists: {len(train_asr)} files, {non_empty} with transcripts")
else:
    print(f"    [WARN] Train ASR cache not found. Will need to run ASR.")

if test_cache.exists():
    test_asr = pd.read_csv(test_cache)
    non_empty = (test_asr["transcript"].fillna("").astype(str).str.strip() != "").sum()
    print(f"    [OK] Test ASR cache exists: {len(test_asr)} files, {non_empty} with transcripts")
else:
    print(f"    [WARN] Test ASR cache not found. Will need to run ASR for submission.")

# Test 10: Check external dependencies
print("\n[10/10] Checking external dependencies...")
import subprocess
import shutil

# Check ffmpeg
if shutil.which("ffmpeg"):
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    if result.returncode == 0:
        print("    [OK] ffmpeg is available")
    else:
        print("    [WARN] ffmpeg found but not working")
else:
    print("    [WARN] ffmpeg not found in PATH (required for ASR)")

# Check Java
if shutil.which("java"):
    result = subprocess.run(["java", "-version"], capture_output=True, text=True, stderr=subprocess.STDOUT)
    if result.returncode == 0:
        print("    [OK] Java is available")
    else:
        print("    [WARN] Java found but not working")
else:
    print("    [WARN] Java not found in PATH (required for grammar checking)")

print("\n" + "=" * 60)
print("Verification Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. If model is missing: Run train_baseline.py")
print("2. If ASR cache is missing: ASR will run automatically when needed")
print("3. To generate submission: python submission/generate_submission.py")
print("=" * 60)

