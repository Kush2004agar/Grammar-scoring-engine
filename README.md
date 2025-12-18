# Grammar Scoring Engine 🎤

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

So I built this thing that tries to score how good someone's English grammar is, just by listening to them talk. Wild, right?

It's for the SHL Intern Hiring Assessment competition. Basically, you give it audio of people speaking English, and it spits out a score from 1 to 5. Like a teacher grading your grammar, except... it's a computer. And it's not always right, but hey, neither are humans sometimes.

The whole point was to make something that's actually fair and you can understand how it works—not just some black box that says "trust me, I'm AI."

---

## So... How Good Is It Really?

Let me be straight with you. The results are... mixed.

| Metric | What It Means | What We Got |
|--------|---------------|-------------|
| **MAE** | Average how wrong we are | 0.59 points off (not terrible!) |
| **RMSE** | Big mistakes hurt more | 0.81 points |
| **Pearson** | Do we agree with humans? | 0.003 (basically no correlation, oops) |
| **Spearman** | Rank-order agreement | -0.028 (also not great) |

Yeah, the correlation is basically zero. That's... not ideal. But the MAE is decent—we're usually within 0.6 points, which isn't the worst thing in the world. The model definitely needs work, but it's a start.

**What we built:**
- Ridge Regression (simple but you can actually understand it)
- 23 different grammar features (error counts, sentence stuff, etc.)
- Trained on 409 examples (not a ton, but it's what we had)
- Tested 5 different ways to make sure we're not just lucky

![Score Distribution](docs/images/score_distribution.png)

![Predicted vs Actual](docs/images/predicted_vs_actual.png)

*Yeah, that scatter plot is pretty messy. The model's trying, but it's not quite there yet.*

![Feature Importance](docs/images/feature_importance.png)

![Cross-Validation Results](docs/images/cv_results.png)

![Band-wise Error Analysis](docs/images/band_wise_errors.png)

![Residuals Plot](docs/images/residuals.png)

---

## What Even Is This?

Okay so here's the deal. You know how when you're learning a language, teachers listen to you speak and grade your grammar? This is trying to automate that.

The process is pretty straightforward:
1. **Listen** 👂 - Turn audio into text using Whisper (OpenAI's speech-to-text thing)
2. **Clean** 🧹 - Get rid of "um"s and "uh"s and stutters (but NOT grammar mistakes—we want to score what they actually said)
3. **Analyze** 🔍 - Count grammar errors, look at sentence structure, all that jazz
4. **Score** 📊 - Predict a score from 1 (oof) to 5 (nice)
5. **Explain** 💡 - Show what mattered (so it's not a complete mystery)

Why does this matter? Well, imagine language learning apps that actually give useful feedback. Or job interviews where the system helps screen candidates. But only if it's actually fair and doesn't screw people over because of their accent or whatever.

---

## What Are We Actually Measuring?

**What we score:**
- Grammar mistakes (wrong tenses, messed up subject-verb agreement, that kind of thing)
- Sentence structure (complete sentences vs. fragments)
- Basic English grammar rules

**What we DON'T score:**
- How smart you are (grammar ≠ intelligence)
- Whether you'd be good at your job (that's a whole other thing)
- Your accent or how you sound (we're looking at grammar, not pronunciation)
- Whether you use British vs. American English (both are fine!)

**How it should be used:**
- As ONE piece of info, not the only thing
- For screening people who need English skills
- Alongside other stuff (interviews, writing samples, etc.)

**The catch:**
- The system might be biased against certain accents (speech-to-text isn't perfect)
- It's not a replacement for human judgment
- We gotta be careful about fairness

---

## How I Built This (The Journey)

I split this into 10 phases because... well, it seemed organized at the time. Here's what happened:

**Phase 1: Figure Out What We're Doing** 📝
First, I had to actually define what "grammar" means here. And what it doesn't mean. And what could go wrong ethically. That part was important.

**Phase 2: Look at the Data** 📊
I loaded up the training data and just... looked at it. What do the scores look like? Are there patterns? What does a low score sound like vs. a high score?

**Phase 3: Speech to Text** 🎤→📝
Used Whisper to transcribe everything. This took forever. Also, Whisper makes mistakes sometimes, especially with accents. That's a problem we'll come back to.

**Phase 4: Clean It Up** 🧹
Removed "um"s, "uh"s, stutters. But I was careful NOT to fix grammar mistakes—if someone says "he go" instead of "he goes", I keep it as "he go" because that's what they actually said.

**Phase 5: Extract Features** 🔍
Turned text into numbers. How many grammar errors? Are sentences complete? How complex is the structure? Stuff like that.

**Phase 6: Train a Model** 🤖
Used Ridge Regression because it's simple and you can actually understand what it's doing. Not some deep learning black box.

**Phase 7: See How Bad It Is** 📈
Spoiler: it's not perfect. But we measured it properly and figured out where it fails.

**Phase 8: Analyze the Failures** 🔬
Looked at cases where we were way off. Is it an ASR problem? A grammar problem? What's going on?

**Phase 9: Try to Make It Better** 🚀
Added one improvement (could use better text embeddings maybe?). Compared it to baseline. Is it worth the added complexity? Sometimes yes, sometimes no.

**Phase 10: Generate Predictions** ✅
Trained final model, generated predictions for test set, created submission file. Done.

Each phase has a notebook if you want to see the gory details.

---

## What Features Actually Matter?

The model looks at 23 different things. Here's what it thinks is important:

**Things that predict HIGHER scores:**
- More tokens (longer responses = higher scores, usually)
- More subordinate clauses (complex sentences)
- Agreement errors per 100 tokens (weirdly, this predicts higher scores? Maybe because longer responses have more room for errors?)

**Things that predict LOWER scores:**
- Total grammar errors (duh)
- Verb tense errors (also duh)
- Number of subordinate clauses (wait, this contradicts the thing above? That's... interesting)

So yeah, grammar scoring is complicated. Some features matter in weird ways. That's why we gotta be careful and not over-interpret stuff.

Check out [docs/results/](docs/results/) if you want the full breakdown.

---

## Where It Messes Up

I spent some time looking at where the model fails. Here's what I found:

**Big disagreements** (we're off by 1+ points):
- Sometimes we under-score people with high scores because ASR dropped function words or messed up sentence boundaries
- Sometimes we over-score people with low scores because ASR "fixed" their grammar mistakes (which is... not what we want)

**Disfluency vs. grammar:**
- Some people are disfluent (lots of "um"s, stutters) but grammatically sound—we might under-score them
- Some people are fluent but make lots of grammar errors—we might over-score them

**Regression to the mean:**
- Extreme scores (very low or very high) tend to get pulled toward the middle. The model is conservative.

So the takeaway is: always have humans review edge cases. This thing isn't perfect.

---

## The Problems (Let's Be Honest)

Look, this system has issues. I'm not gonna sugarcoat it.

**The data problem:**
- Only 409 examples. That's... not a lot. The model is less confident at the extremes.
- We don't know people's backgrounds, so we can't directly check for fairness.

**The accent bias problem:**
This is the big one. If Whisper (the speech-to-text) makes mistakes transcribing someone's accent, our grammar score will be wrong. And it's not the speaker's fault—it's the transcription software's fault. But they're the one who gets the bad score.

Someone with a non-native accent might get a lower score not because their grammar is bad, but because Whisper misunderstood them. That's... not great.

We try to be aware of this, but it's a fundamental limitation. Always have humans review borderline cases.

**The "scope creep" problem:**
It's tempting to make the model score "how good the text sounds" instead of just grammar. I tried to stick to grammar only, but it's a slippery slope.

**The "don't over-rely on this" problem:**
This should NEVER be the only thing used to make important decisions. Think of it like spell-check—helpful, but not infallible.

If someone gets a very low or very high score, have a human double-check. Always.

**How to use this ethically:**
1. Always have human oversight
2. Be transparent about limitations
3. Watch for bias patterns
4. Allow appeals
5. Use multiple assessment methods

---

## Getting Started

Want to try it? Here's how:

1. **Get the code**
   ```bash
   git clone https://github.com/Kush2004agar/Grammar-scoring-engine.git
   cd Grammar-scoring-engine
   ```

2. **Install stuff**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
   *Note: You'll need Java for grammar checking and FFmpeg for audio. There are guides in the repo if you get stuck.*

3. **Add your data**
   - Put audio files in `data/train_audio/` and `data/test_audio/`
   - Put labels in `data/train.csv`
   - Should be from the SHL competition (we can't use external datasets)

4. **Train it**
   ```bash
   python train_baseline.py
   ```
   *This takes a while—it has to transcribe all the audio first.*

5. **Generate predictions**
   ```bash
   python submission/generate_submission.py
   ```

More details in the notebooks if you want to dig deeper.

---

## Project Structure

```
grammar-scoring/
├── src/                    # The actual code
│   ├── asr.py             # Speech to text
│   ├── text_cleaning.py   # Clean up spoken language
│   ├── feature_engineering.py  # Extract grammar features
│   ├── model.py           # The model itself
│   └── evaluation.py       # How well did we do?
├── notebooks/             # Jupyter notebooks (the journey)
├── scripts/               # Helper scripts
├── docs/                  # Documentation
│   ├── images/           # Pretty pictures
│   └── results/          # Results tables
├── submission/            # Generate competition submissions
├── train_baseline.py      # Main training script
└── requirements.txt       # What you need to install
```

---

## The Tech Stack

**Python stuff:**
- Python 3.8+ (obviously)
- Whisper (OpenAI) - turns speech into text
- spaCy - analyzes sentence structure
- LanguageTool - finds grammar mistakes
- scikit-learn - the machine learning part
- pandas, numpy - data wrangling

**External tools:**
- FFmpeg - processes audio (Whisper needs this)
- Java - LanguageTool runs on Java

*Don't worry if this sounds complicated—there are installation guides to help you out.*

---

## License

MIT License. Do whatever you want with it. See [LICENSE](LICENSE) for the legal stuff.

---

## Thanks

Shoutout to:
- **OpenAI** - Whisper is amazing
- **LanguageTool** - Open source grammar checking
- **SHL** - For the competition dataset
- **The open-source community** - For all the Python libraries that make this possible

---

## Questions? Found a Bug?

Open an issue on GitHub! I'm happy to help (or at least try to).

---

## The Bottom Line

This is an attempt to automate grammar scoring in a fair, transparent way. It's not perfect (no automated system is), but I tried to be honest about the limitations and build it in a way that's explainable.

**Remember**: This is a tool to help humans, not replace them. Use it responsibly. 🚀
