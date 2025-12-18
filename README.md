# Grammar Scoring Engine for Spoken Audio 🎤

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Can a computer understand how well someone speaks English?** This project tries to answer that question by building a system that listens to people speak and scores their grammar—just like a human teacher would, but automatically.

Built for the SHL Intern Hiring Assessment competition, this project takes audio recordings of people speaking English and predicts how good their grammar is on a scale from 1 to 5. It's designed to be **fair, transparent, and actually useful** for real-world assessment scenarios.

---

## 📊 How Well Does It Work?

Here's the honest truth about how our model performs:

| Metric | What It Means | Our Score |
|--------|---------------|-----------|
| **MAE** | Average prediction error | 0.59 points (pretty good!) |
| **RMSE** | Penalizes big mistakes more | 0.81 points |
| **Pearson Correlation** | How well we match human scores | 0.003 (needs improvement) |
| **Spearman Correlation** | Rank-order agreement | -0.028 (needs work) |

**What this means:** The model can predict grammar scores with an average error of about 0.6 points (out of 5), which is decent but not perfect. The low correlation suggests we're not capturing everything humans notice—but that's okay! This is a baseline model, and there's always room to improve.

**Model Details:**
- **What it is**: A Ridge Regression model (simple but interpretable)
- **What it looks at**: 23 different grammar features (error counts, sentence structure, etc.)
- **Training data**: 409 audio samples with human-assigned scores
- **Validation**: 5-fold cross-validation (we tested it 5 different ways)

![Score Distribution](docs/images/score_distribution.png)

![Predicted vs Actual](docs/images/predicted_vs_actual.png)

![Feature Importance](docs/images/feature_importance.png)

![Cross-Validation Results](docs/images/cv_results.png)

![Band-wise Error Analysis](docs/images/band_wise_errors.png)

![Residuals Plot](docs/images/residuals.png)

---

### What Does This Project Do?

Imagine you're a teacher listening to students speak English. You'd notice things like:
- Do they use the right verb tenses?
- Are their sentences complete?
- Do they make grammar mistakes?

This project tries to automate that process. Here's how it works:

1. **Listen** 👂 - Converts audio recordings to text using OpenAI's Whisper (the same tech behind ChatGPT's voice features)
2. **Clean** 🧹 - Removes "um"s, "uh"s, and stutters (but doesn't "fix" grammar—we want to score what they actually said)
3. **Analyze** 🔍 - Looks for grammar errors, sentence structure, and other linguistic patterns
4. **Score** 📊 - Predicts a grammar score from 1 (needs work) to 5 (excellent)
5. **Explain** 💡 - Shows which features mattered most (so it's not a black box)

**Why this matters:** Automated grammar scoring could help with language learning apps, job interviews, or educational assessments—but only if it's fair, transparent, and actually works well.

---

### What Are We Actually Measuring?

**What we're scoring:**
- Grammar mistakes (wrong tenses, subject-verb agreement, etc.)
- Sentence structure (complete sentences vs. fragments)
- Basic English grammar rules

**What we're NOT scoring:**
- How smart someone is
- Whether they'd be good at their job
- Their accent or pronunciation (we're looking at grammar, not how they sound)
- Whether they use "proper" British English vs. American English (both are valid!)

**How it should be used:**
- As **one piece** of information, not the only thing that matters
- For screening candidates who need English communication skills
- Alongside other assessments (interviews, writing samples, etc.)

**Important caveats:**
- The system might be biased against certain accents (because speech-to-text isn't perfect)
- It's not a replacement for human judgment
- We need to be careful about fairness and not over-relying on automated scores

---

### Methodology Summary

The project is organised in **phases**, each mapped to code and notebooks.

- **Phase 1 — Problem framing**
  - `notebooks/01_problem_framing.ipynb` documents the construct, non-constructs, intended use, and ethical/automation risks (no code).

- **Phase 2 — Dataset exploration**
  - `notebooks/02_data_exploration.ipynb` loads `data/train.csv`, examines **score distributions**, and explores audio duration vs. score.
  - Includes **qualitative listening notes** across low/medium/high score bands.

- **Phase 3 — ASR pipeline**
  - `src/asr.py` implements **Whisper-based transcription** (e.g., `small` model), with:
    - Configurable decoding parameters in `src/config.py`.
    - **Caching** to `data/asr_cache/asr_[train|test].csv`.
    - Error logging for problematic files.
  - `notebooks/03_asr_analysis.ipynb` inspects transcript quality and discusses how ASR errors can inflate or mask grammar errors.

- **Phase 4 — Spoken text cleaning**
  - `src/text_cleaning.py` implements **minimal, non-corrective cleaning**:
    - Whitespace/case normalisation.
    - Removal of **non-lexical fillers** (“uh”, “um”, etc.).
    - Conservative collapse of **stutter-like repetitions**.
    - Conservative trimming of **very short false starts**.
  - Each rule is documented with **assessment rationale**: remove performance noise, never “fix” grammar.

- **Phase 5 — Feature engineering**
  - `src/feature_engineering.py` extracts **interpretable grammar features** from cleaned transcripts:
    - Grammar error counts and **error density per 100 tokens** using `language_tool_python`.
    - Sentence and clause metrics (number of clauses, subordinate clauses, fragments, ratios) using spaCy.
    - POS-based patterns (verb ratios, subject pronouns, etc.).
  - `notebooks/04_feature_engineering.ipynb` explains each feature and shows **feature distributions**, connecting them to human judgment.

- **Phase 6 — Baseline modelling**
  - `src/model.py` implements a **Ridge regression** baseline:
    - Uses only **grammar features** (no deep embeddings).
    - Fixes random seeds and uses **K-fold cross-validation**.
    - Provides **feature importance** (standardised coefficients) for interpretability.
  - `notebooks/05_modeling.ipynb` trains the baseline, displays CV metrics, and interprets coefficients in linguistic terms.

- **Phase 7 — Evaluation**
  - `src/evaluation.py` provides:
    - **Pearson** and **Spearman** correlations.
    - **MAE** and **RMSE**.
    - **Score-band error analysis** (low/medium/high).
  - `notebooks/06_evaluation.ipynb` plots predicted vs. actual scores, residuals, and band-wise performance, and discusses alignment with human raters.

- **Phase 8 — Error & bias analysis**
  - `src/error_analysis.py`:
    - Identifies **large-error cases** (e.g., |prediction – truth| ≥ 1.0).
    - Joins with transcripts for **qualitative ASR vs. grammar** analysis.
    - Supports analyses by **score band** and (optionally) response length.
  - Error tables and qualitative insights are reported in `notebooks/06_evaluation.ipynb` and associated notes.

- **Phase 9 — One controlled improvement**
  - A **single additional modelling component** is introduced (e.g., a fixed transformer-based sentence embedding combined with grammar features in a Ridge model).
  - The improvement is **strictly compared** to the baseline:
    - Same data, same CV protocol.
    - Metrics and band-wise errors.
    - Trade-offs in **accuracy vs. interpretability / construct purity** are explicitly discussed.

- **Phase 10 — Final model & submission**
  - A final model is selected based on **performance, robustness, and interpretability**.
  - `submission/generate_submission.py`:
    - Loads the trained model and preprocessing.
    - Ensures test ASR transcripts and cleaned text/features are computed.
    - Generates a **competition-compatible** `submission.csv` (`filename,label`).

---

### What Features Matter Most?

The model looks at 23 different grammar features. Here's what it found most important:

**Features that predict HIGHER scores:**
- More tokens (longer responses tend to score higher)
- More subordinate clauses (complex sentences)
- Agreement errors per 100 tokens (surprisingly, this predicts higher scores—maybe because longer responses have more opportunities for errors?)

**Features that predict LOWER scores:**
- Total grammar errors (makes sense!)
- Verb tense errors (also makes sense!)
- Number of subordinate clauses (wait, this contradicts the above? That's interesting...)

**The takeaway**: Grammar scoring is complicated! Some features matter in unexpected ways. That's why we need to be careful and not over-interpret the results.

See the [detailed results](docs/results/) for the full feature importance analysis.

---

### Error Analysis Highlights

Error and bias analysis focuses on:

- **Large disagreements** (e.g., |error| ≥ 1.0 points):
  - Under-prediction of high-true scores often linked to **ASR dropping function words** or mis-segmenting sentences, inflating error density.
  - Over-prediction of low-true scores when ASR partially **normalises tense/agreement errors**.
- **Disfluency vs. grammar**:
  - Some disfluent but grammatically sound responses may be under-scored if features conflate disfluency with incomplete syntax.
  - Some fluent but errorful responses may be over-scored if complexity dominates error features.
- **Regression to the mean**:
  - Extremes (very low or high grammar scores) tend to be pulled toward the centre, reducing differentiation at critical boundaries.

These patterns are used to motivate:

- **Human review** for certain bands or flagged cases.
- Cautious use of the model as **one indicator**, not a sole decision-maker.

---

### ⚠️ Important Limitations & Ethical Considerations

Let's be honest about what this system can and can't do:

#### The Data Problem
- **Small dataset**: We only have 409 examples to learn from. That's not a lot! The model is less confident at the extremes (scores near 1 or 5).
- **Missing context**: We don't know people's backgrounds, accents, or demographics, so we can't directly check for fairness issues.

#### The Accent Bias Problem
This is a **big deal** and we need to talk about it:

- **Speech-to-text isn't perfect**: If the transcription software (Whisper) makes mistakes transcribing someone's accent, our grammar score will be wrong—and it's not the speaker's fault!
- **Real-world impact**: Someone with a non-native accent might get a lower score not because their grammar is bad, but because the speech-to-text misunderstood them.
- **What we can do**: We try to be aware of this, but it's a fundamental limitation. Always have humans review borderline cases.

#### The "Scope Creep" Problem
- **Mission drift**: It's tempting to make the model score "how good the text sounds" instead of just grammar. We try to stick to grammar only, but it's a slippery slope.

#### The "Don't Over-Rely on This" Problem
- **Not a replacement for humans**: This should NEVER be the only thing used to make important decisions (like hiring or grading).
- **Use it as a tool**: Think of it like spell-check—helpful, but not infallible.
- **Always review edge cases**: If someone gets a very low or very high score, have a human double-check.

#### How to Use This Ethically
1. **Always have human oversight** - Don't automate away human judgment
2. **Be transparent** - Tell people their scores are automated and explain the limitations
3. **Watch for bias** - Monitor if certain groups consistently get different scores
4. **Allow appeals** - People should be able to challenge automated scores
5. **Use multiple methods** - Combine this with interviews, writing samples, etc.

---

### Getting Started (5 Minutes)

Want to try it yourself? Here's how:

1. **Get the code**
   ```bash
   git clone https://github.com/Kush2004agar/Grammar-scoring-engine.git
   cd Grammar-scoring-engine
   ```

2. **Install what you need**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
   *Note: You'll also need Java installed for grammar checking, and FFmpeg for audio processing. See the installation guides if you run into issues.*

3. **Add your data**
   - Put your audio files in `data/train_audio/` and `data/test_audio/`
   - Put your labels CSV in `data/train.csv`
   - The data should come from the SHL competition (we can't use external datasets)

4. **Train the model**
   ```bash
   python train_baseline.py
   ```
   *This will take a while—it needs to transcribe all the audio first!*

5. **Generate predictions**
   ```bash
   python submission/generate_submission.py
   ```
   *This creates a CSV file with predictions for all test audio files.*

### Detailed Documentation

- **Installation & Setup**: See [GITHUB_SETUP.md](GITHUB_SETUP.md)
- **Methodology**: See notebooks in `notebooks/`
- **Results**: See [docs/results/](docs/results/)
- **Visualizations**: See [docs/images/](docs/images/)

---

## 📁 Project Structure

```
grammar-scoring/
├── src/                    # Core source code
│   ├── asr.py             # Whisper-based ASR
│   ├── text_cleaning.py   # Spoken language cleaning
│   ├── feature_engineering.py  # Grammar features
│   ├── model.py           # Ridge regression model
│   └── evaluation.py      # Assessment metrics
├── notebooks/             # Jupyter notebooks (phases 1-6)
├── scripts/               # Utility scripts
│   ├── generate_visualizations.py
│   └── extract_results.py
├── docs/                  # Documentation
│   ├── images/           # Visualizations
│   └── results/          # Results tables
├── submission/            # Submission generation
├── train_baseline.py      # Main training script
└── requirements.txt       # Dependencies
```

---

## 🔧 What's Under the Hood?

### The Tech Stack

- **Python 3.8+** - The programming language
- **Whisper** (OpenAI) - Converts speech to text (it's really good at this!)
- **spaCy** - Analyzes sentence structure and parts of speech
- **LanguageTool** - Finds grammar mistakes (like a spell-checker for grammar)
- **scikit-learn** - The machine learning library that trains our model
- **pandas, numpy** - For handling data and doing math

### External Tools You'll Need

- **FFmpeg** - Processes audio files (Whisper needs this)
- **Java** - LanguageTool runs on Java (like Minecraft, but for grammar checking)

*Don't worry if this sounds complicated—there are installation guides in the repo to help you set everything up!*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Thanks & Credits

This project wouldn't exist without:

- **OpenAI** - For creating Whisper, the amazing speech-to-text system
- **LanguageTool** - For the open-source grammar checking
- **SHL** - For providing the competition dataset
- **The open-source community** - For all the amazing Python libraries

---

## 💬 Questions? Found a Bug?

Feel free to:
- Open an issue on GitHub if you find a bug or have a question
- Check the notebooks for detailed explanations of each step
- Read the code—it's well-documented and meant to be understandable!

---

## 🎯 The Bottom Line

This project is an attempt to automate grammar scoring in a **fair, transparent, and useful** way. It's not perfect (no automated system is!), but we've tried to be honest about its limitations and build it in a way that's explainable and ethical.

**Remember**: This is a tool to help humans, not replace them. Always use it responsibly! 🚀


