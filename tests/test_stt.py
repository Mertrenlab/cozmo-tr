"""Tests for bounded push-to-talk transcription."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cozmo_tr.stt import NativeVoskBackend, SttUnavailable, VoskTranscriber, _extract_text


class FakeSpeechBackend:
    """Record capture settings and return a deterministic transcript."""

    def __init__(self) -> None:
        self.request: tuple[Path, int, int] | None = None

    def transcribe(self, model: Path, rate: int, samples: int) -> str:
        self.request = (model, rate, samples)
        return " ileri git "


class FakeAudio:
    """Expose PCM bytes like a NumPy recording."""

    def tobytes(self) -> bytes:
        return b"pcm"


class FakeSoundDevice:
    """Provide the sounddevice methods used by NativeVoskBackend."""

    def rec(self, _frames: int, **_options: object) -> FakeAudio:
        return FakeAudio()

    def wait(self) -> None:
        return None


class FakeRecognizer:
    """Return one stable Vosk JSON payload."""

    def AcceptWaveform(self, _data: bytes) -> bool:  # noqa: N802
        return True

    def FinalResult(self) -> str:  # noqa: N802
        return '{"text": "ileri git"}'


class FakeVosk:
    """Provide Vosk constructors without loading a real model."""

    def Model(self, _path: str) -> object:  # noqa: N802
        return object()

    def KaldiRecognizer(self, _model: object, _rate: int) -> FakeRecognizer:  # noqa: N802
        return FakeRecognizer()


class VoskTranscriberTests(unittest.TestCase):
    """Require a valid model and finite recording window."""

    def test_transcribes_one_bounded_window(self) -> None:
        backend = FakeSpeechBackend()
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory)
            (model / "final.mdl").touch()
            text = VoskTranscriber(model, backend).transcribe_once(2.0)
        self.assertEqual(text, "ileri git")
        self.assertEqual(backend.request, (model, 16_000, 32_000))

    def test_rejects_missing_model(self) -> None:
        with self.assertRaises(SttUnavailable):
            VoskTranscriber(Path("/missing"), FakeSpeechBackend())

    def test_rejects_invalid_duration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory)
            (model / "final.mdl").touch()
            transcriber = VoskTranscriber(model, FakeSpeechBackend())
            for seconds in (0.0, 11.0):
                with self.subTest(seconds=seconds), self.assertRaises(SttUnavailable):
                    transcriber.transcribe_once(seconds)

    def test_native_backend_extracts_text(self) -> None:
        modules = [FakeSoundDevice(), FakeVosk()]
        with patch("cozmo_tr.stt.import_module", side_effect=modules):
            text = NativeVoskBackend().transcribe(Path("model"), 16_000, 16_000)
        self.assertEqual(text, "ileri git")

    def test_rejects_invalid_backend_json_shapes(self) -> None:
        for payload in ("[]", '{"not_text": 1}'):
            with self.subTest(payload=payload), self.assertRaises(SttUnavailable):
                _extract_text(payload)


if __name__ == "__main__":
    unittest.main()
