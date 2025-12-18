"""
Extract grammar features from text.

This is where we turn text into numbers that a machine learning model
can understand. We look for things like:
- How many grammar errors are there?
- Are the sentences complete?
- How complex is the sentence structure?

All features are designed to be interpretable—you should be able to
understand what each one means without a PhD in linguistics.

We deliberately avoid "black box" features (like deep learning embeddings)
at this stage, so the model stays transparent and explainable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np
import pandas as pd


try:  # optional import; we handle absence gracefully in code paths
    import language_tool_python  # type: ignore[import]
except Exception:  # pragma: no cover - environment dependent
    language_tool_python = None  # type: ignore[assignment]

try:  # spaCy is also optional at import time
    import spacy  # type: ignore[import]
except Exception:  # pragma: no cover
    spacy = None  # type: ignore[assignment]


@dataclass
class FeatureExtractorConfig:
    """Configuration for grammar feature extraction."""

    language_tool_lang: str = "en-US"
    spacy_model: str = "en_core_web_sm"


class GrammarFeatureExtractor:
    """Extract interpretable grammar features from cleaned transcripts."""

    def __init__(self, cfg: FeatureExtractorConfig | None = None) -> None:
        self.cfg = cfg or FeatureExtractorConfig()
        self._tool = None
        self._nlp = None

    def _ensure_language_tool(self):
        if language_tool_python is None:
            raise ImportError(
                "language_tool_python is required for grammar error features."
            )
        if self._tool is None:
            self._tool = language_tool_python.LanguageTool(self.cfg.language_tool_lang)

    def _ensure_spacy(self):
        if spacy is None:
            raise ImportError("spaCy is required for syntactic features.")
        if self._nlp is None:
            self._nlp = spacy.load(self.cfg.spacy_model, disable=["ner"])

    def _grammar_error_features(self, text: str) -> dict:
        self._ensure_language_tool()
        assert self._tool is not None

        matches = self._tool.check(text)
        num_tokens = len(text.split())
        counts = {
            "num_grammar_errors": 0,
            "num_verb_tense_errors": 0,
            "num_agreement_errors": 0,
            "num_article_errors": 0,
            "num_preposition_errors": 0,
            "num_word_order_errors": 0,
        }

        for m in matches:
            counts["num_grammar_errors"] += 1
            # language_tool_python uses snake_case attributes
            rule_id = (getattr(m, 'rule_id', None) or getattr(m, 'ruleId', None) or "").lower()
            msg = (getattr(m, 'message', None) or "").lower()

            if "verb" in msg or "tense" in msg:
                counts["num_verb_tense_errors"] += 1
            if "agreement" in msg or "subject-verb" in msg:
                counts["num_agreement_errors"] += 1
            if "article" in msg or "determiner" in msg:
                counts["num_article_errors"] += 1
            if "preposition" in msg:
                counts["num_preposition_errors"] += 1
            if "word order" in msg:
                counts["num_word_order_errors"] += 1

        # Normalised per 100 tokens
        denom = max(num_tokens, 1)
        features = counts.copy()
        for key in list(counts.keys()):
            features[f"{key}_per_100_tokens"] = 100.0 * counts[key] / denom
        features["num_tokens"] = num_tokens
        return features

    def _syntactic_features(self, text: str) -> dict:
        self._ensure_spacy()
        assert self._nlp is not None

        doc = self._nlp(text)
        num_sentences = max(len(list(doc.sents)), 1)
        num_tokens = len(doc)

        num_clauses = 0
        num_subordinate_clauses = 0
        num_coord_conj = 0
        num_verbs = 0
        num_fragments = 0
        num_subject_pronouns = 0

        for sent in doc.sents:
            has_verb = any(tok.pos_ in {"VERB", "AUX"} for tok in sent)
            if not has_verb:
                num_fragments += 1

        for tok in doc:
            if tok.dep_ in {"ROOT", "ccomp", "xcomp", "advcl", "relcl", "acl"}:
                num_clauses += 1
            if tok.dep_ in {"ccomp", "xcomp", "advcl", "relcl", "acl"}:
                num_subordinate_clauses += 1
            if tok.pos_ == "CCONJ":
                num_coord_conj += 1
            if tok.pos_ in {"VERB", "AUX"}:
                num_verbs += 1
            if tok.pos_ == "PRON" and tok.dep_ in {"nsubj", "nsubjpass"}:
                num_subject_pronouns += 1

        features = {
            "num_sentences": num_sentences,
            "avg_sentence_length_tokens": num_tokens / num_sentences if num_sentences else 0.0,
            "num_clauses": num_clauses,
            "num_subordinate_clauses": num_subordinate_clauses,
            "num_coord_conj": num_coord_conj,
            "clause_to_sentence_ratio": num_clauses / num_sentences if num_sentences else 0.0,
            "subordinate_clause_ratio": (
                num_subordinate_clauses / num_clauses if num_clauses else 0.0
            ),
            "verb_token_ratio": num_verbs / num_tokens if num_tokens else 0.0,
            "fragment_ratio": num_fragments / num_sentences if num_sentences else 0.0,
            "pronoun_subject_ratio": num_subject_pronouns / num_clauses if num_clauses else 0.0,
        }
        return features

    def transform(self, texts: Iterable[str]) -> pd.DataFrame:
        """Extract features for a sequence of cleaned transcripts."""

        records: List[dict] = []
        for text in texts:
            if not isinstance(text, str):
                text = "" if text is None else str(text)
            grammar_feats = self._grammar_error_features(text)
            syntactic_feats = self._syntactic_features(text)
            rec = {**grammar_feats, **syntactic_feats}
            records.append(rec)
        return pd.DataFrame.from_records(records)


