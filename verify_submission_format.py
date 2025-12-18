"""
Verify that the submission CSV format is correct.

This script checks:
1. CSV has correct columns: filename, label
2. Filenames don't have .wav extension
3. Labels are in valid range [1.0, 5.0]
4. All test files are included
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import pandas as pd
from src.config import paths
from src.data_loader import list_audio_files

def verify_submission_format(submission_path: Path) -> bool:
    """Verify submission CSV format is correct."""
    
    print("=" * 60)
    print("Verifying Submission CSV Format")
    print("=" * 60)
    
    # Check file exists
    if not submission_path.exists():
        print(f"ERROR: Submission file not found: {submission_path}")
        return False
    
    # Load submission
    try:
        df = pd.read_csv(submission_path)
    except Exception as e:
        print(f"ERROR: Could not read CSV: {e}")
        return False
    
    print(f"\n[1/5] Loaded submission with {len(df)} rows")
    
    # Check columns
    expected_cols = {"filename", "label"}
    actual_cols = set(df.columns)
    if actual_cols != expected_cols:
        print(f"ERROR: Expected columns {expected_cols}, got {actual_cols}")
        return False
    print(f"[2/5] Columns are correct: {actual_cols}")
    
    # Check filenames don't have .wav extension
    has_extension = df["filename"].str.endswith(".wav").any()
    if has_extension:
        print("ERROR: Some filenames have .wav extension")
        print("Sample filenames with extension:")
        print(df[df["filename"].str.endswith(".wav")]["filename"].head())
        return False
    print("[3/5] Filenames are correct (no .wav extension)")
    
    # Check label range
    min_label = df["label"].min()
    max_label = df["label"].max()
    if min_label < 1.0 or max_label > 5.0:
        print(f"ERROR: Labels out of range [1.0, 5.0]. Found: [{min_label}, {max_label}]")
        return False
    print(f"[4/5] Labels are in valid range: [{min_label:.2f}, {max_label:.2f}]")
    
    # Check all test files are included
    test_audio_files = list_audio_files("test")
    expected_filenames = {f.stem for f in test_audio_files}
    actual_filenames = set(df["filename"].values)
    
    missing = expected_filenames - actual_filenames
    extra = actual_filenames - expected_filenames
    
    if missing:
        print(f"WARNING: {len(missing)} test files missing from submission")
        print(f"Sample missing: {list(missing)[:5]}")
    
    if extra:
        print(f"WARNING: {len(extra)} extra filenames in submission")
        print(f"Sample extra: {list(extra)[:5]}")
    
    if not missing and not extra:
        print(f"[5/5] All {len(expected_filenames)} test files are included")
    else:
        print(f"[5/5] File count: Expected {len(expected_filenames)}, Got {len(actual_filenames)}")
    
    print("\n" + "=" * 60)
    if not missing and not extra and not has_extension:
        print("✓ Submission format is CORRECT!")
        print("=" * 60)
        return True
    else:
        print("⚠ Submission format has issues (see warnings above)")
        print("=" * 60)
        return False

if __name__ == "__main__":
    submission_path = paths.submissions_dir / "submission.csv"
    if len(sys.argv) > 1:
        submission_path = Path(sys.argv[1])
    
    success = verify_submission_format(submission_path)
    sys.exit(0 if success else 1)

