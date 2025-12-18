"""
Extract and save model results to markdown files for documentation.

Run with: python scripts/extract_results.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import joblib
import numpy as np
import pandas as pd

from src.config import paths
from src.data_loader import load_train_labels
from src.asr import load_cached_transcripts
from src.text_cleaning import clean_transcript
from src.feature_engineering import GrammarFeatureExtractor
from src.model import cross_validate_baseline, compute_feature_importance
from src.evaluation import basic_metrics

# Create output directory
output_dir = project_root / "docs" / "results"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Extracting Model Results")
print("=" * 60)

# Load model
model_path = paths.models_dir / "final_baseline_model.joblib"
if not model_path.exists():
    print(f"ERROR: Model not found at {model_path}")
    sys.exit(1)

artifacts = joblib.load(model_path)
print(f"Loaded model with {len(artifacts.feature_names)} features")

# Load data and generate predictions
train_df = load_train_labels()

# Try to load cached features first (faster and doesn't require Java)
features_cache = paths.features_dir / "train_features.csv"
if features_cache.exists():
    print("Loading cached features...")
    feat_df = pd.read_csv(features_cache)
    X = feat_df.drop(columns=["filename"] if "filename" in feat_df.columns else [])
    print(f"Loaded {X.shape[0]} samples with {X.shape[1]} features from cache")
else:
    print("Cached features not found. Extracting features (requires Java)...")
    asr_df = load_cached_transcripts("train")
    if asr_df is None:
        print("ERROR: ASR cache not found. Please run ASR first!")
        sys.exit(1)

    cleaned_texts = []
    for text in asr_df["transcript"].fillna(""):
        cleaned, _ = clean_transcript(text)
        cleaned_texts.append(cleaned)

    try:
        extractor = GrammarFeatureExtractor()
        X = extractor.transform(cleaned_texts)
        # Save features for future use
        feat_df = pd.DataFrame(X)
        feat_df.insert(0, "filename", asr_df["filename"].values)
        features_cache.parent.mkdir(parents=True, exist_ok=True)
        feat_df.to_csv(features_cache, index=False)
        print(f"Saved features to cache: {features_cache}")
    except Exception as e:
        if "java" in str(e).lower():
            print("\nERROR: Java not found in PATH!")
            print("Please ensure Java is installed and in PATH.")
            print("See scripts/README_VISUALIZATIONS.md for details.")
            sys.exit(1)
        else:
            raise

# Align y with X
y = train_df["label"].values
if len(y) != X.shape[0]:
    asr_df = load_cached_transcripts("train")
    merged = train_df.merge(asr_df[["filename"]], left_on="filename", right_on="filename", how="inner")
    y = merged["label"].values
    if len(y) != X.shape[0]:
        min_len = min(X.shape[0], len(y))
        X = X.iloc[:min_len] if hasattr(X, 'iloc') else X[:min_len]
        y = y[:min_len]

X_scaled = artifacts.scaler.transform(X.values)
y_pred = artifacts.model.predict(X_scaled)

# Get metrics
metrics = basic_metrics(y, y_pred)

# Convert to pandas for cross_validate_baseline
if isinstance(y, np.ndarray):
    y_series = pd.Series(y)
else:
    y_series = y
if isinstance(X, np.ndarray):
    X_df = pd.DataFrame(X, columns=artifacts.feature_names)
else:
    X_df = X
cv_results = cross_validate_baseline(X_df, y_series, alpha=1.0)

# 1. Save CV Results
print("\n[1/3] Saving CV results...")
cv_md = f"""# Cross-Validation Results

## 5-Fold Cross-Validation Performance

| Metric | Mean | Std |
|--------|------|-----|
| MAE | {cv_results['mae_mean']:.4f} | {cv_results['mae_std']:.4f} |
| RMSE | {cv_results['rmse_mean']:.4f} | {cv_results['rmse_std']:.4f} |
| Pearson Correlation | {cv_results['pearson_mean']:.4f} | {cv_results['pearson_std']:.4f} |

## Interpretation

- **MAE (Mean Absolute Error)**: On average, predictions are off by {cv_results['mae_mean']:.3f} points
- **RMSE (Root Mean Squared Error)**: {cv_results['rmse_mean']:.3f} points (penalizes large errors more)
- **Pearson Correlation**: {cv_results['pearson_mean']:.3f} indicates {'strong' if cv_results['pearson_mean'] > 0.7 else 'moderate' if cv_results['pearson_mean'] > 0.5 else 'weak'} linear relationship with human scores
"""

with open(output_dir / "cv_results.md", "w", encoding="utf-8") as f:
    f.write(cv_md)
print(f"    Saved: {output_dir / 'cv_results.md'}")

# 2. Save Feature Importance
print("\n[2/3] Saving feature importance...")
feature_importance = compute_feature_importance(artifacts)

feature_md = """# Feature Importance

## Top Features by Coefficient

Features are standardized, so coefficients represent the expected change in predicted score for a one-standard-deviation increase in the feature, holding others constant.

| Rank | Feature | Coefficient | Interpretation |
|------|---------|-------------|---------------|
"""

for idx, row in feature_importance.head(20).iterrows():
    coef = row['coefficient']
    direction = "Higher" if coef > 0 else "Lower"
    feature_md += f"| {idx+1} | {row['feature']} | {coef:.4f} | {direction} values -> {'higher' if coef > 0 else 'lower'} predicted score |\n"

feature_md += f"""

## Summary

- **Total features**: {len(feature_importance)}
- **Positive coefficients**: {(feature_importance['coefficient'] > 0).sum()} (associated with higher scores)
- **Negative coefficients**: {(feature_importance['coefficient'] < 0).sum()} (associated with lower scores)
- **Most important feature**: {feature_importance.iloc[0]['feature']} (coefficient: {feature_importance.iloc[0]['coefficient']:.4f})
"""

with open(output_dir / "feature_importance.md", "w", encoding="utf-8") as f:
    f.write(feature_md)
print(f"    Saved: {output_dir / 'feature_importance.md'}")

# 3. Save Final Model Performance
print("\n[3/3] Saving final model performance...")
performance_md = f"""# Final Model Performance

## Overall Metrics (Full Training Set)

| Metric | Value |
|--------|-------|
| MAE | {metrics.mae:.4f} |
| RMSE | {metrics.rmse:.4f} |
| Pearson Correlation | {metrics.pearson:.4f} |
| Spearman Correlation | {metrics.spearman:.4f} |

## Model Details

- **Model Type**: Ridge Regression
- **Regularization (alpha)**: 1.0
- **Number of Features**: {len(artifacts.feature_names)}
- **Training Samples**: {len(y)}

## Performance Interpretation

- The model achieves a Pearson correlation of {metrics.pearson:.3f} with human-assigned grammar scores
- Mean absolute error of {metrics.mae:.3f} points suggests {'good' if metrics.mae < 0.5 else 'moderate' if metrics.mae < 0.7 else 'room for improvement'} alignment with human judgment
- Spearman correlation of {metrics.spearman:.3f} indicates {'strong' if metrics.spearman > 0.7 else 'moderate' if metrics.spearman > 0.5 else 'weak'} rank-order agreement
"""

with open(output_dir / "final_model_performance.md", "w", encoding="utf-8") as f:
    f.write(performance_md)
print(f"    Saved: {output_dir / 'final_model_performance.md'}")

print("\n" + "=" * 60)
print("Results Extraction Complete!")
print("=" * 60)
print(f"\nAll results saved to: {output_dir}")
print("\nNext steps:")
print("1. Review results in docs/results/")
print("2. Copy key metrics to README.md")
print("3. Add feature importance table to README.md")
print("=" * 60)

