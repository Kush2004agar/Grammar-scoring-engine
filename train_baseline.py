"""
Train the grammar scoring model from scratch.

This script does the whole pipeline:
1. Loads the training data (labels + audio files)
2. Converts audio to text using Whisper (or uses cached transcripts if available)
3. Cleans up the text (removes "um"s, stutters, etc.)
4. Extracts grammar features (error counts, sentence structure, etc.)
5. Trains a Ridge regression model to predict grammar scores
6. Saves everything so you can generate predictions later

Run this before generating submissions!

Usage:
    python train_baseline.py
"""

import sys
from pathlib import Path

# Add current directory to path so we can import src
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import joblib
import pandas as pd

from src.config import ensure_directories, paths
from src.data_loader import load_train_labels, list_audio_files
from src.asr import transcribe_split, load_cached_transcripts
from src.text_cleaning import clean_transcript
from src.feature_engineering import GrammarFeatureExtractor
from src.model import train_baseline_model, cross_validate_baseline

print("=" * 60)
print("Training the Grammar Scoring Model")
print("=" * 60)
print("(This might take a while, especially the ASR part...)")

# Ensure directories exist
ensure_directories()

# Step 1: Load labels
print("\n[1/5] Loading training labels...")
print("    (Reading the CSV file with all the scores)")
labels_df = load_train_labels()
print(f"    Loaded {len(labels_df)} training examples")

# Step 2: ASR transcription
print("\n[2/5] Running ASR transcription...")
print("    (Converting audio to text - this is the slow part)")
train_audio_paths = list_audio_files("train")
print(f"    Found {len(train_audio_paths)} audio files")

if len(train_audio_paths) == 0:
    raise ValueError(
        f"No audio files found in {paths.train_audio_dir}. "
        "Please copy audio files from dataset/audios/train/ to data/train_audio/"
    )

# Check for cached transcripts first
cached = load_cached_transcripts("train")
if cached is not None:
    # Check if cache is valid (has non-empty transcripts)
    # Handle NaN values properly
    non_empty = (cached["transcript"].fillna("").astype(str).str.strip() != "").sum()
    total = len(cached)
    print(f"    Found cached transcripts: {total} files, {non_empty} with non-empty text")
    
    if non_empty == 0:
        print(f"    WARNING: All cached transcripts are empty (likely from failed ASR run)")
        print(f"    Deleting bad cache and re-running ASR...")
        cache_path = paths.asr_cache_dir / "asr_train.csv"
        if cache_path.exists():
            cache_path.unlink()
        cached = None
    
if cached is not None:
    print(f"    Using cached transcripts ({len(cached)} files)")
    asr_df = cached
else:
    print("    Transcribing audio files (this may take a while)...")
    print(f"    This will process {len(train_audio_paths)} files - please be patient!")
    
    # Quick validation: test if we can read the first file
    if train_audio_paths:
        test_path = train_audio_paths[0]
        if not test_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {test_path}\n"
                "Please ensure audio files are copied to data/train_audio/"
            )
        print(f"    Validated: First audio file exists and is readable")
    
    asr_df = transcribe_split(train_audio_paths, split="train")
    print(f"    Transcribed {len(asr_df)} files")
    
    # Check for successful transcriptions
    successful = (asr_df["transcript"].fillna("").astype(str).str.strip() != "").sum()
    failed = (asr_df["error"].notna()).sum()
    print(f"    Successful: {successful}, Failed: {failed}")
    
    if successful == 0:
        print("\n    ERROR: All transcriptions failed!")
        if failed > 0:
            print(f"    Sample errors:")
            error_samples = asr_df[asr_df["error"].notna()][["filename", "error"]].head(3)
            for _, row in error_samples.iterrows():
                print(f"      {row['filename']}: {row['error']}")
        raise ValueError("ASR transcription failed for all files. Check audio file format and Whisper installation.")

if len(asr_df) == 0:
    raise ValueError("No ASR transcripts available. Check ASR step.")

# Step 3: Text cleaning
print("\n[3/5] Cleaning transcripts...")
print("    (Removing 'um's and stutters, but keeping grammar mistakes)")
cleaned_texts = []
cleaning_stats = []
for idx, transcript in enumerate(asr_df["transcript"].fillna("")):
    cleaned, stats = clean_transcript(transcript)
    cleaned_texts.append(cleaned)
    cleaning_stats.append(stats)
    if (idx + 1) % 50 == 0:
        print(f"    Cleaned {idx + 1}/{len(asr_df)} transcripts")

asr_df["transcript_clean"] = cleaned_texts
print(f"    Completed cleaning for {len(cleaned_texts)} transcripts")

# Step 4: Join with labels
print("\n[4/5] Joining transcripts with labels...")
print(f"    ASR transcripts: {len(asr_df)}")
print(f"    Labels: {len(labels_df)}")
print(f"    Sample ASR filenames: {asr_df['filename'].head().tolist()}")
print(f"    Sample label filenames: {labels_df['filename'].head().tolist()}")

train_df = asr_df.merge(labels_df, on="filename", how="inner")
print(f"    Joined dataset has {len(train_df)} examples with labels")

if len(train_df) == 0:
    raise ValueError(
        "No matching filenames between ASR transcripts and labels. "
        "Check that filename format matches (e.g., 'audio_173' vs 'audio_173.wav')."
    )

# Filter out any rows with empty cleaned transcripts
train_df = train_df[train_df["transcript_clean"].str.strip() != ""]
print(f"    After filtering empty transcripts: {len(train_df)} examples")

if len(train_df) == 0:
    raise ValueError(
        "All transcripts were filtered out as empty. "
        "Check text cleaning step or ASR output quality."
    )

# Step 5: Feature extraction
print("\n[5/5] Extracting grammar features...")
print("    (Counting errors, analyzing sentence structure, etc.)")
extractor = GrammarFeatureExtractor()
X = extractor.transform(train_df["transcript_clean"].tolist())
y = train_df["label"]
print(f"    Extracted {X.shape[1]} features for {X.shape[0]} examples")

if X.shape[0] == 0:
    raise ValueError(
        "Feature extraction produced 0 samples. "
        "Check that transcripts are not empty and feature extraction is working."
    )

# Step 6: Cross-validation (optional, for diagnostics)
print("\n[6/6] Running cross-validation...")
print("    (Testing the model 5 different ways to make sure it's not just lucky)")
cv_results = cross_validate_baseline(X, y, alpha=1.0)
print("    CV Results:")
for metric, value in cv_results.items():
    print(f"      {metric}: {value:.4f}")

# Step 7: Train final model on all data
print("\n[7/7] Training final model on all training data...")
print("    (Now we use everything to build the final model)")
artifacts = train_baseline_model(X, y, alpha=1.0)
print("    Model trained successfully")

# Step 8: Save model
model_path = paths.models_dir / "final_baseline_model.joblib"
joblib.dump(artifacts, model_path)
print(f"\n✓ Model saved to: {model_path}")

print("\n" + "=" * 60)
print("All done! 🎉")
print("=" * 60)
print("Now you can generate predictions with:")
print(f"  python submission/generate_submission.py")
print("=" * 60)

