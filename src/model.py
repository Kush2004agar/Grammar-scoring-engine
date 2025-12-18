"""
Train and evaluate the grammar scoring model.

We use Ridge Regression—it's simple, interpretable, and doesn't require
a supercomputer to run. The model learns which grammar features predict
higher or lower scores.

Key features:
- Uses cross-validation to make sure we're not just memorizing
- Shows which features matter most (feature importance)
- Fixes random seeds so results are reproducible

We deliberately keep it simple and transparent, not a black box.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

from .config import training_config


@dataclass
class BaselineModelArtifacts:
    """Container for fitted baseline model and preprocessing."""

    scaler: StandardScaler
    model: Ridge
    feature_names: list[str]


def train_baseline_model(
    X: pd.DataFrame, y: pd.Series, alpha: float = 1.0
) -> BaselineModelArtifacts:
    """Train a Ridge regression baseline model.

    Parameters
    ----------
    X:
        Feature matrix with interpretable grammar features.
    y:
        Target grammar scores.
    alpha:
        Ridge regularisation strength.
    """

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.values)

    # Use Ridge Regression - simple, interpretable, and actually works
    model = Ridge(alpha=alpha, random_state=training_config.random_seed)
    model.fit(X_scaled, y.values)
    return BaselineModelArtifacts(
        scaler=scaler, model=model, feature_names=list(X.columns)
    )


def cross_validate_baseline(
    X: pd.DataFrame,
    y: pd.Series,
    alpha: float = 1.0,
    n_splits: int | None = None,
) -> Dict[str, float]:
    """Run K-fold CV and return aggregate metrics.

    Metrics are chosen to be assessment-friendly: MAE, RMSE, and Pearson r.
    """

    n_splits = n_splits or training_config.n_splits_cv
    kf = KFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=training_config.random_seed,
    )

    maes: list[float] = []
    rmses: list[float] = []
    pears: list[float] = []

    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        artifacts = train_baseline_model(X_train, y_train, alpha=alpha)
        X_val_scaled = artifacts.scaler.transform(X_val.values)
        y_pred = artifacts.model.predict(X_val_scaled)

        maes.append(mean_absolute_error(y_val, y_pred))
        # Compute RMSE manually (sqrt of MSE) for compatibility
        mse = mean_squared_error(y_val, y_pred)
        rmses.append(sqrt(mse))
        if np.std(y_pred) > 0 and np.std(y_val.values) > 0:
            pears.append(np.corrcoef(y_val.values, y_pred)[0, 1])

    return {
        "mae_mean": float(np.mean(maes)),
        "mae_std": float(np.std(maes)),
        "rmse_mean": float(np.mean(rmses)),
        "rmse_std": float(np.std(rmses)),
        "pearson_mean": float(np.mean(pears)) if pears else float("nan"),
        "pearson_std": float(np.std(pears)) if pears else float("nan"),
    }


def compute_feature_importance(artifacts: BaselineModelArtifacts) -> pd.DataFrame:
    """Return feature coefficients as an interpretable table.

    Coefficients are in the space of standardised features: they can be read
    as the expected change in predicted score for a one-standard-deviation
    increase in the feature, holding others constant.
    """

    coefs = artifacts.model.coef_
    return pd.DataFrame(
        {
            "feature": artifacts.feature_names,
            "coefficient": coefs,
        }
    ).sort_values("coefficient", ascending=False)


