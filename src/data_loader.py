"""
Data loading utilities for the grammar scoring project.

This module is intentionally simple and focuses on:
- Loading SHL labels from ``data/train.csv``.
- Enumerating audio files in train/test folders.
- Providing joined views that downstream steps (ASR, features, modeling)
  can rely on.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from .config import paths


@dataclass
class DatasetSplits:
    """Container for core dataset pieces."""

    train_df: pd.DataFrame
    train_audio_paths: List[Path]
    test_audio_paths: List[Path]


def load_train_labels() -> pd.DataFrame:
    """Load SHL-provided training labels.

    Returns
    -------
    pd.DataFrame
        DataFrame with at least two columns:
        - ``filename``: audio id without extension
        - ``label``: human-assigned grammar score
    """

    df = pd.read_csv(paths.train_csv)
    expected_cols = {"filename", "label"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Train CSV missing expected columns: {missing}")
    return df


def list_audio_files(split: str) -> List[Path]:
    """List audio files for a given split.

    Parameters
    ----------
    split:
        Either ``\"train\"`` or ``\"test\"``.

    Returns
    -------
    list[Path]
        Paths to all ``.wav`` files in the corresponding folder.
    """

    if split == "train":
        base = paths.train_audio_dir
    elif split == "test":
        base = paths.test_audio_dir
    else:
        raise ValueError(f"Unknown split: {split!r}")

    return sorted(base.glob("*.wav"))


def load_dataset_splits() -> DatasetSplits:
    """Load labels and list audio files for train and test splits."""

    train_df = load_train_labels()
    train_audio_paths = list_audio_files("train")
    test_audio_paths = list_audio_files("test")
    return DatasetSplits(
        train_df=train_df,
        train_audio_paths=train_audio_paths,
        test_audio_paths=test_audio_paths,
    )


