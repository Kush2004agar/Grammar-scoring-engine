"""
Generate the final submission file for the competition.

This script takes your trained model and generates predictions for all
the test audio files, then saves them in the format the competition expects.

Before running this:
1. Make sure you've trained the model (run train_baseline.py)
2. Make sure test audio files are transcribed (this will happen automatically)

The output is a CSV file with two columns: filename and label (the predicted score).
"""

from __future__ import annotations

import argparse
import sys
import joblib
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import ensure_directories, paths, training_config
from src.data_loader import list_audio_files
from src.asr import load_cached_transcripts, transcribe_split
from src.text_cleaning import clean_transcript
from src.feature_engineering import GrammarFeatureExtractor


def load_or_create_test_transcripts() -> pd.DataFrame:
    """Ensure we have ASR transcripts for the test set."""

    cached = load_cached_transcripts("test")
    if cached is not None:
        return cached

    audio_paths = list_audio_files("test")
    return transcribe_split(audio_paths, split="test")


def prepare_test_features() -> pd.DataFrame:
    """Run cleaning + feature extraction for the test set."""

    transcripts_df = load_or_create_test_transcripts()
    cleaned_texts = []
    for text in transcripts_df["transcript"].fillna(""):
        cleaned, _stats = clean_transcript(text)
        cleaned_texts.append(cleaned)

    extractor = GrammarFeatureExtractor()
    feat_df = extractor.transform(cleaned_texts)
    feat_df.insert(0, "filename", transcripts_df["filename"].values)
    return feat_df


def main(model_path: Path, output_path: Path) -> None:
    ensure_directories()

    artifacts = joblib.load(model_path)
    test_feats = prepare_test_features()
    feature_names = artifacts.feature_names

    X_test = test_feats[feature_names].values
    X_test_scaled = artifacts.scaler.transform(X_test)
    y_pred = artifacts.model.predict(X_test_scaled)

    # Clip to valid score range; we keep continuous predictions.
    y_pred = np.clip(y_pred, 1.0, 5.0)

    submission = pd.DataFrame(
        {
            "filename": test_feats["filename"],
            training_config.target_column: y_pred,
        }
    )
    submission.to_csv(output_path, index=False)
    print(f"Saved submission to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_path",
        type=Path,
        default=paths.models_dir / "final_baseline_model.joblib",
        help="Path to the trained model artifacts.",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        default=paths.submissions_dir / "submission.csv",
        help="Where to write the SHL submission CSV.",
    )
    args = parser.parse_args()
    main(args.model_path, args.output_path)


