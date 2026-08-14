"""Capture one bounded microphone window and transcribe Turkish with Vosk.

Responsible for: push-to-talk recording and transcript extraction.
Not responsible for: wake words, command parsing, persistence, or robot I/O.
"""

import json
from importlib import import_module
from pathlib import Path
from typing import Protocol, cast

SAMPLE_RATE = 16_000
MAX_RECORD_SECONDS = 10.0


class SttUnavailable(RuntimeError):
    """Report missing models, invalid capture windows, or backend failures."""


class SpeechBackend(Protocol):
    """Turn a bounded microphone window into text."""

    def transcribe(self, model: Path, rate: int, samples: int) -> str:
        """Record and decode one audio window."""
        ...


class _AudioBuffer(Protocol):
    def tobytes(self) -> bytes:
        """Return signed 16-bit PCM bytes."""
        ...


class _SoundDevice(Protocol):
    def rec(self, frames: int, *, samplerate: int, channels: int, dtype: str) -> _AudioBuffer:
        """Start a blocking-compatible recording."""
        ...

    def wait(self) -> None:
        """Wait until the current recording is complete."""
        ...


class _Recognizer(Protocol):
    def AcceptWaveform(self, data: bytes) -> bool:  # noqa: N802
        """Consume PCM bytes."""
        ...

    def FinalResult(self) -> str:  # noqa: N802
        """Return a JSON transcription result."""
        ...


class _VoskModule(Protocol):
    def Model(self, path: str) -> object:  # noqa: N802
        """Load a Vosk model directory."""
        ...

    def KaldiRecognizer(self, model: object, rate: int) -> _Recognizer:  # noqa: N802
        """Create a recognizer for one sample rate."""
        ...


class NativeVoskBackend:
    """Use optional sounddevice and Vosk packages at runtime."""

    def transcribe(self, model: Path, rate: int, samples: int) -> str:
        """Record mono int16 audio and decode its final Turkish text."""
        sound = cast(_SoundDevice, import_module("sounddevice"))
        vosk = cast(_VoskModule, import_module("vosk"))
        recording = sound.rec(samples, samplerate=rate, channels=1, dtype="int16")
        sound.wait()
        recognizer = vosk.KaldiRecognizer(vosk.Model(str(model)), rate)
        recognizer.AcceptWaveform(recording.tobytes())
        return _extract_text(recognizer.FinalResult())


class VoskTranscriber:
    """Validate configuration and expose one bounded push-to-talk call."""

    def __init__(self, model: Path, backend: SpeechBackend | None = None) -> None:
        """Bind an existing Vosk model and optional test backend."""
        if not _model_ready(model):
            raise SttUnavailable(f"Türkçe Vosk modeli bulunamadı: {model}")
        self._model = model
        self._backend = backend or NativeVoskBackend()

    def transcribe_once(self, seconds: float = 4.0) -> str:
        """Record a finite window and return its trimmed transcript."""
        if seconds <= 0 or seconds > MAX_RECORD_SECONDS:
            raise SttUnavailable("Kayıt süresi 0 ile 10 saniye arasında olmalı")
        samples = int(seconds * SAMPLE_RATE)
        return self._backend.transcribe(self._model, SAMPLE_RATE, samples).strip()


def _model_ready(model: Path) -> bool:
    return (model / "final.mdl").is_file() or (model / "am" / "final.mdl").is_file()


def _extract_text(result: str) -> str:
    payload: object = json.loads(result)
    if not isinstance(payload, dict):
        raise SttUnavailable("Vosk geçersiz sonuç döndürdü")
    text = payload.get("text")
    if not isinstance(text, str):
        raise SttUnavailable("Vosk sonucunda metin yok")
    return text.strip()
