"""
Evaluate how well the model performs.

We use metrics that make sense for assessment:
- Correlation: Does the model agree with human scores?
- MAE/RMSE: How far off are the predictions on average?
- Band analysis: Is the model too harsh or too lenient for certain score ranges?

The goal is to understand not just "is it good?" but "where does it fail?"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt


@dataclass
class EvaluationResults:
    pearson: float
    spearman: float
    mae: float
    rmse: float


def basic_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> EvaluationResults:
    """Compute core assessment metrics."""

    from scipy.stats import pearsonr, spearmanr  # type: ignore[import]

    pearson, _ = pearsonr(y_true, y_pred)
    spearman, _ = spearmanr(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    # Compute RMSE manually (sqrt of MSE) for compatibility
    mse = mean_squared_error(y_true, y_pred)
    rmse = sqrt(mse)
    return EvaluationResults(
        pearson=float(pearson),
        spearman=float(spearman),
        mae=float(mae),
        rmse=float(rmse),
    )


def score_band(x: float) -> str:
    """Bucket scores into low/medium/high for analysis."""

    if x <= 2.5:
        return "low"
    if x < 4.0:
        return "medium"
    return "high"


def band_error_analysis(
    y_true: np.ndarray, y_pred: np.ndarray
) -> pd.DataFrame:
    """Summarise error statistics by score band."""

    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
    df["band_true"] = df["y_true"].apply(score_band)
    df["error"] = df["y_pred"] - df["y_true"]
    grouped = df.groupby("band_true")
    summary = grouped.agg(
        n=("y_true", "size"),
        mean_true=("y_true", "mean"),
        mean_pred=("y_pred", "mean"),
        mean_error=("error", "mean"),
        mae=("error", lambda e: float(np.mean(np.abs(e)))),
        rmse=("error", lambda e: float(np.sqrt(np.mean(e**2)))),
    ).reset_index()
    return summary


