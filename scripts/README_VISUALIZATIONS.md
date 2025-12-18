# Generating Visualizations - Java Requirement

## Issue

The visualization script requires **Java** to be installed and in your PATH because it needs to extract grammar features using `language_tool_python`.

## Solution

### Option 1: Add Java to PATH (Recommended)

1. **Find your Java installation:**
   - Common locations:
     - `C:\Program Files\Java\jre-XX\bin`
     - `C:\Program Files\Eclipse Adoptium\jdk-XX\bin`
     - `C:\Program Files\Java\jdk-XX\bin`

2. **Add to PATH temporarily (for this session):**
   ```powershell
   $env:Path += ";C:\Program Files\Java\jre-XX\bin"
   java -version  # Verify it works
   ```

3. **Or add permanently:**
   - Open System Properties → Environment Variables
   - Add Java bin directory to PATH
   - Restart terminal

### Option 2: Use Pre-computed Features

If you've already run `train_baseline.py`, the features were computed. However, they're not saved by default.

**Workaround:** Re-run training with Java available, then the visualization script will work.

### Option 3: Skip Feature Extraction (Limited)

If you just want to see the model structure without predictions, you can modify the script to skip feature extraction, but this won't generate the prediction plots.

---

## Quick Fix

If Java is installed but not in PATH, find it and add temporarily:

```powershell
# Find Java
Get-ChildItem "C:\Program Files\Java" -Recurse -Filter "java.exe" | Select-Object FullName

# Add to PATH (replace with actual path)
$env:Path += ";C:\Program Files\Java\jre-21\bin"

# Verify
java -version

# Now run visualization script
python scripts\generate_visualizations.py
```

---

## Alternative: Generate Visualizations After Training

Since you've already trained the model, the easiest approach is:

1. **Ensure Java is in PATH** (see above)
2. **Run the visualization script:**
   ```powershell
   python scripts\generate_visualizations.py
   ```

The script will:
- Load your trained model
- Extract features (requires Java)
- Generate all 7 visualizations
- Save them to `docs/images/`

---

## What Gets Generated

1. `score_distribution.png` - Distribution of grammar scores
2. `predicted_vs_actual.png` - Scatter plot with correlation
3. `residuals.png` - Residuals analysis
4. `feature_importance.png` - Top 15 features
5. `band_wise_errors.png` - Error by score band
6. `cv_results.png` - Cross-validation metrics

All saved to `docs/images/` for inclusion in README.

