"""
Configuration for the grammar scoring project.

This module centralizes paths, model settings, and random seeds to ensure
reproducibility and easy review by assessment scientists.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Paths:
    """File-system layout for the project.

    We keep a clear separation between:
    - SHL-provided data (audio + labels)
    - Derived artifacts (ASR transcripts, features, models, submissions)
    """

    # Base folders
    project_root: Path = PROJECT_ROOT
    data_dir: Path = PROJECT_ROOT / "data"
    src_dir: Path = PROJECT_ROOT / "src"

    # SHL data (copied or symlinked into data/)
    train_audio_dir: Path = PROJECT_ROOT / "data" / "train_audio"
    test_audio_dir: Path = PROJECT_ROOT / "data" / "test_audio"
    train_csv: Path = PROJECT_ROOT / "data" / "train.csv"

    # Derived artifacts
    asr_cache_dir: Path = PROJECT_ROOT / "data" / "asr_cache"
    features_dir: Path = PROJECT_ROOT / "data" / "features"
    models_dir: Path = PROJECT_ROOT / "data" / "models"
    logs_dir: Path = PROJECT_ROOT / "data" / "logs"

    submissions_dir: Path = PROJECT_ROOT / "submission"


@dataclass(frozen=True)
class ASRConfig:
    """Configuration for the ASR (Whisper) step.

    We fix model name and decoding parameters so that transcripts are
    reproducible and their provenance is well documented.
    """

    # Use the tiny Whisper model by default so ASR is fast enough on CPU.
    # You can switch to \"small\" or larger once everything works.
    model_name: Literal["tiny", "base", "small", "medium", "large"] = "tiny"
    language: str = "en"
    beam_size: int = 5
    temperature: float = 0.0
    fp16: bool = False  # safer default for CPU-only environments


@dataclass(frozen=True)
class TrainingConfig:
    """Configuration for model training and evaluation."""

    random_seed: int = 42
    n_splits_cv: int = 5
    target_column: str = "label"


paths = Paths()
asr_config = ASRConfig()
training_config = TrainingConfig()


def ensure_directories() -> None:
    """Create required directories if they do not exist.

    This is safe to call at the beginning of scripts and notebooks.
    """

    for p in [
        paths.asr_cache_dir,
        paths.features_dir,
        paths.models_dir,
        paths.logs_dir,
        paths.submissions_dir,
    ]:
        p.mkdir(parents=True, exist_ok=True)


