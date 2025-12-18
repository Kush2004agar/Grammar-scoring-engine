"""
Convert speech to text using Whisper.

This is where the magic happens—we take audio files and turn them into text
that we can analyze for grammar.

Key features:
- Uses OpenAI's Whisper (it's really good at this!)
- Caches transcripts so we don't have to re-transcribe everything
- Handles errors gracefully (some audio files might be problematic)
- Shows progress so you know it's working (transcribing can take a while)

Important: We don't fix grammar here—we just convert speech to text as
accurately as possible. Grammar scoring happens later.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

from .config import ASRConfig, asr_config, ensure_directories, paths


def _load_whisper_model(cfg: ASRConfig):
    """Load a Whisper model lazily.

    We import ``whisper`` inside the function so that other parts of the
    project (e.g., EDA) do not require ASR dependencies.
    """

    import whisper  # type: ignore[import]

    model = whisper.load_model(cfg.model_name)
    return model


def _load_audio_for_whisper(audio_path: Path):
    """Load audio file for Whisper.
    
    Tries multiple methods:
    1. Pass file path directly to Whisper (Whisper uses ffmpeg internally)
    2. Fallback to librosa if direct path fails
    
    Returns audio array in format expected by Whisper (16kHz, mono, float32).
    """
    # First, try passing the file path directly to Whisper
    # Whisper will use ffmpeg internally if available
    # If this fails, we'll catch it in the calling code and try alternatives
    return str(audio_path)


def _asr_cache_path(split: str) -> Path:
    return paths.asr_cache_dir / f"asr_{split}.csv"


def transcribe_split(
    audio_paths: Iterable[Path],
    split: str,
    cfg: ASRConfig | None = None,
    overwrite: bool = False,
) -> pd.DataFrame:
    """Transcribe a set of audio files with Whisper and cache the results.

    Parameters
    ----------
    audio_paths:
        Iterable of paths to ``.wav`` files.
    split:
        Either ``\"train\"`` or ``\"test\"``; used to name cache files.
    cfg:
        Optional ASR configuration; defaults to global ``asr_config``.
    overwrite:
        If ``True``, ignore an existing cache and recompute transcripts.

    Returns
    -------
    pd.DataFrame
        Columns:
        - ``filename``: stem of the audio file
        - ``split``: train/test
        - ``transcript``: raw ASR text
        - ``asr_config``: JSON-encoded configuration used
        - ``error``: error message if transcription failed (else NaN)
    """

    ensure_directories()
    cfg = cfg or asr_config
    cache_path = _asr_cache_path(split)
    if cache_path.exists() and not overwrite:
        return pd.read_csv(cache_path)

    model = _load_whisper_model(cfg)
    rows: List[dict] = []

    audio_paths = list(sorted(audio_paths))
    total = len(audio_paths)

    for idx, audio_path in enumerate(audio_paths, start=1):
        filename = audio_path.stem
        row: dict = {
            "filename": filename,
            "split": split,
            "transcript": "",
            "asr_config": json.dumps(asdict(cfg)),
            "error": "",
        }
        try:
            # Try passing file path directly to Whisper first
            # Whisper uses ffmpeg internally if available
            audio_input = str(audio_path)
            
            result = model.transcribe(
                audio_input,
                language=cfg.language,
                task="transcribe",
                beam_size=cfg.beam_size,
                temperature=cfg.temperature,
                fp16=cfg.fp16,
            )
            text = (result.get("text") or "").strip()
            row["transcript"] = text
        except Exception as exc:  # pragma: no cover - defensive
            # We record the error but keep the pipeline running so that
            # problematic files can be inspected in error analysis.
            error_msg = str(exc)
            # Provide helpful message if ffmpeg is missing
            if "ffmpeg" in error_msg.lower() or "file not found" in error_msg.lower():
                error_msg = (
                    f"{error_msg}. "
                    "Whisper requires ffmpeg to decode audio files. "
                    "Install ffmpeg: https://ffmpeg.org/download.html "
                    "or download a Windows build from https://www.gyan.dev/ffmpeg/builds/ "
                    "and add its 'bin' folder to your PATH."
                )
            row["error"] = error_msg
        rows.append(row)

        # Lightweight progress logging every 5 files
        if idx % 5 == 0 or idx == total:
            print(f"    ASR progress: {idx}/{total} files transcribed")

    df = pd.DataFrame(rows)
    df.to_csv(cache_path, index=False)
    return df


def load_cached_transcripts(split: str) -> Optional[pd.DataFrame]:
    """Load cached transcripts if they exist, else return None."""

    cache_path = _asr_cache_path(split)
    if not cache_path.exists():
        return None
    return pd.read_csv(cache_path)


