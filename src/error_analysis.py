"""
Error and bias analysis utilities.

This module helps identify where model predictions diverge most from
human scores, and supports structured analysis of potential biases
related to score bands, response length, and ASR issues.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .evaluation import score_band


@dataclass
class LargeErrorCase:
    filename: str
    true_score: float
    pred_score: float
    error: float
    band_true: str


def identify_large_errors(
    df: pd.DataFrame,
    error_threshold: float = 1.0,
) -> pd.DataFrame:
    """Return rows where |prediction - truth| >= threshold.

    Parameters
    ----------
    df:
        DataFrame with at least ``filename``, ``y_true``, and ``y_pred``.
    error_threshold:
        Absolute error cut-off for inclusion.
    """

    required = {"filename", "y_true", "y_pred"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    df = df.copy()
    df["error"] = df["y_pred"] - df["y_true"]
    df["abs_error"] = df["error"].abs()
    df["band_true"] = df["y_true"].apply(score_band)
    return df[df["abs_error"] >= error_threshold].sort_values(
        "abs_error", ascending=False
    )


def join_with_transcripts(
    large_error_df: pd.DataFrame, transcripts_df: pd.DataFrame
) -> pd.DataFrame:
    """Attach transcripts to large-error cases for qualitative review."""

    return large_error_df.merge(
        transcripts_df[["filename", "transcript"]],
        on="filename",
        how="left",
    )


