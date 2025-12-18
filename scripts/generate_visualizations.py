"""
Script to generate all visualizations for GitHub presentation.

This script generates key visualizations from the trained model and saves them
to docs/images/ for inclusion in the README and documentation.

Run with: python scripts/generate_visualizations.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt

from src.config import paths
from src.data_loader import load_train_labels
from src.asr import load_cached_transcripts
from src.text_cleaning import clean_transcript
from src.feature_engineering import GrammarFeatureExtractor
from src.model import cross_validate_baseline, compute_feature_importance
from src.evaluation import basic_metrics, score_band
from scipy.stats import pearsonr, spearmanr

# Create output directory
output_dir = project_root / "docs" / "images"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Generating Visualizations for GitHub Presentation")
print("=" * 60)

# 1. Score Distribution Histogram
print("\n[1/7] Generating score distribution histogram...")
train_df = load_train_labels()
plt.figure(figsize=(8, 5))
plt.hist(train_df['label'], bins=20, edgecolor='black', alpha=0.7, color='steelblue')
plt.xlabel('Grammar Score', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.title('Distribution of Grammar Scores in Training Data', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "score_distribution.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    Saved: {output_dir / 'score_distribution.png'}")

# 2. Load model and generate predictions for visualization
print("\n[2/7] Loading model and generating predictions...")
model_path = paths.models_dir / "final_baseline_model.joblib"
if not model_path.exists():
    print(f"    ERROR: Model not found at {model_path}")
    print("    Please run train_baseline.py first!")
    sys.exit(1)

artifacts = joblib.load(model_path)

# Try to load cached features first (faster and doesn't require Java)
features_cache = paths.features_dir / "train_features.csv"
if features_cache.exists():
    print("    Loading cached features...")
    feat_df = pd.read_csv(features_cache)
    X = feat_df.drop(columns=["filename"] if "filename" in feat_df.columns else [])
    print(f"    Loaded {X.shape[0]} samples with {X.shape[1]} features from cache")
else:
    print("    Cached features not found. Extracting features (requires Java)...")
    # Load transcripts and prepare features
    asr_df = load_cached_transcripts("train")
    if asr_df is None:
        print("    ERROR: ASR cache not found. Please run ASR first!")
        sys.exit(1)

    # Clean transcripts
    cleaned_texts = []
    for text in asr_df["transcript"].fillna(""):
        cleaned, _ = clean_transcript(text)
        cleaned_texts.append(cleaned)

    # Extract features
    try:
        extractor = GrammarFeatureExtractor()
        X = extractor.transform(cleaned_texts)
        # Save features for future use
        feat_df = pd.DataFrame(X)
        feat_df.insert(0, "filename", asr_df["filename"].values)
        features_cache.parent.mkdir(parents=True, exist_ok=True)
        feat_df.to_csv(features_cache, index=False)
        print(f"    Saved features to cache: {features_cache}")
    except Exception as e:
        if "java" in str(e).lower():
            print(f"\n    ERROR: Java not found in PATH!")
            print(f"    To fix this:")
            print(f"    1. Install Java (JRE) from: https://adoptium.net/")
            print(f"    2. Add Java bin directory to PATH")
            print(f"    3. Restart terminal and verify with: java -version")
            print(f"\n    Or add Java to PATH temporarily:")
            print(f'       $env:Path += ";C:\\path\\to\\java\\bin"')
            print(f"\n    See scripts/README_VISUALIZATIONS.md for details.")
            sys.exit(1)
        else:
            raise

# Align y with X (in case of any mismatches)
y = train_df["label"].values
if len(y) != X.shape[0]:
    # Merge on filename to align
    asr_df = load_cached_transcripts("train")
    merged = train_df.merge(asr_df[["filename"]], left_on="filename", right_on="filename", how="inner")
    y = merged["label"].values
    if len(y) != X.shape[0]:
        print(f"    WARNING: Mismatch between features ({X.shape[0]}) and labels ({len(y)})")
        min_len = min(X.shape[0], len(y))
        X = X.iloc[:min_len] if hasattr(X, 'iloc') else X[:min_len]
        y = y[:min_len]

# Get predictions
X_scaled = artifacts.scaler.transform(X.values)
y_pred = artifacts.model.predict(X_scaled)

# 3. Predicted vs Actual Scatter Plot
print("\n[3/7] Generating predicted vs actual scatter plot...")
metrics = basic_metrics(y, y_pred)
plt.figure(figsize=(8, 8))
plt.scatter(y, y_pred, alpha=0.5, s=50, color='steelblue', edgecolors='black', linewidth=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Perfect Prediction')
plt.xlabel('Actual Grammar Score', fontsize=12)
plt.ylabel('Predicted Grammar Score', fontsize=12)
plt.title(f'Predicted vs Actual Grammar Scores\nPearson r = {metrics.pearson:.3f}, MAE = {metrics.mae:.3f}', 
          fontsize=14, fontweight='bold')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "predicted_vs_actual.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    Saved: {output_dir / 'predicted_vs_actual.png'}")
print(f"    Metrics: Pearson={metrics.pearson:.3f}, MAE={metrics.mae:.3f}, RMSE={metrics.rmse:.3f}")

# 4. Residuals Plot
print("\n[4/7] Generating residuals plot...")
residuals = y_pred - y
plt.figure(figsize=(8, 6))
plt.scatter(y, residuals, alpha=0.5, s=50, color='coral', edgecolors='black', linewidth=0.5)
plt.axhline(y=0, color='r', linestyle='--', lw=2)
plt.xlabel('Actual Grammar Score', fontsize=12)
plt.ylabel('Residuals (Predicted - Actual)', fontsize=12)
plt.title('Residuals Plot', fontsize=14, fontweight='bold')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "residuals.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    Saved: {output_dir / 'residuals.png'}")

# 5. Feature Importance Bar Chart
print("\n[5/7] Generating feature importance chart...")
feature_importance = compute_feature_importance(artifacts)
top_features = feature_importance.head(15)

plt.figure(figsize=(10, 8))
colors = ['steelblue' if x > 0 else 'coral' for x in top_features['coefficient']]
plt.barh(range(len(top_features)), top_features['coefficient'], color=colors, alpha=0.7, edgecolor='black')
plt.yticks(range(len(top_features)), top_features['feature'])
plt.xlabel('Coefficient (Standardized)', fontsize=12)
plt.title('Top 15 Feature Importance (Ridge Regression Coefficients)', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
plt.tight_layout()
plt.savefig(output_dir / "feature_importance.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    Saved: {output_dir / 'feature_importance.png'}")

# 6. Band-wise Error Analysis
print("\n[6/7] Generating band-wise error analysis...")
train_df_with_pred = train_df.copy()
train_df_with_pred['predicted'] = y_pred
train_df_with_pred['error'] = train_df_with_pred['predicted'] - train_df_with_pred['label']
train_df_with_pred['band'] = train_df_with_pred['label'].apply(score_band)

band_order = ['low', 'medium', 'high']
band_data = [train_df_with_pred[train_df_with_pred['band'] == band]['error'].values 
             for band in band_order]

plt.figure(figsize=(10, 6))
bp = plt.boxplot(band_data, tick_labels=band_order, patch_artist=True, 
                 boxprops=dict(facecolor='steelblue', alpha=0.7),
                 medianprops=dict(color='red', linewidth=2))
plt.ylabel('Prediction Error (Predicted - Actual)', fontsize=12)
plt.xlabel('Score Band', fontsize=12)
plt.title('Error Distribution by Score Band', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
plt.tight_layout()
plt.savefig(output_dir / "band_wise_errors.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    Saved: {output_dir / 'band_wise_errors.png'}")

# 7. Cross-Validation Results (if available, create a summary)
print("\n[7/7] Running cross-validation for visualization...")
# Convert y to pandas Series if it's a numpy array (cross_validate_baseline expects Series)
if isinstance(y, np.ndarray):
    y_series = pd.Series(y)
else:
    y_series = y
# Convert X to DataFrame if it's not already
if isinstance(X, np.ndarray):
    X_df = pd.DataFrame(X, columns=artifacts.feature_names)
else:
    X_df = X
cv_results = cross_validate_baseline(X_df, y_series, alpha=1.0)

# Create CV results visualization
fig, ax = plt.subplots(figsize=(10, 6))
metrics_names = ['MAE', 'RMSE', 'Pearson']
means = [cv_results['mae_mean'], cv_results['rmse_mean'], cv_results['pearson_mean']]
stds = [cv_results['mae_std'], cv_results['rmse_std'], cv_results['pearson_std']]

x_pos = np.arange(len(metrics_names))
bars = ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, 
              color=['steelblue', 'coral', 'lightgreen'], edgecolor='black')
ax.set_xlabel('Metric', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('5-Fold Cross-Validation Results (Mean ± Std)', fontsize=14, fontweight='bold')
ax.set_xticks(x_pos)
ax.set_xticklabels(metrics_names)
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (mean, std) in enumerate(zip(means, stds)):
    ax.text(i, mean + std + 0.01, f'{mean:.3f}±{std:.3f}', 
            ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / "cv_results.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    Saved: {output_dir / 'cv_results.png'}")
print(f"    CV Results: MAE={cv_results['mae_mean']:.3f}±{cv_results['mae_std']:.3f}, "
      f"RMSE={cv_results['rmse_mean']:.3f}±{cv_results['rmse_std']:.3f}, "
      f"Pearson={cv_results['pearson_mean']:.3f}±{cv_results['pearson_std']:.3f}")

print("\n" + "=" * 60)
print("Visualization Generation Complete!")
print("=" * 60)
print(f"\nAll visualizations saved to: {output_dir}")
print("\nNext steps:")
print("1. Review images in docs/images/")
print("2. Embed images in README.md")
print("3. Add results numbers to README.md")
print("=" * 60)

