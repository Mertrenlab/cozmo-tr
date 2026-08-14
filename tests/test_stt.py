"""Tests for bounded push-to-talk transcription."""

import tempfile
import unittest
from pathlib import Path

from cozmo_tr.stt import SttUnavailable, VoskTranscriber


class FakeSpeechBackend:
    """Record capture settings and return a deterministic transcript."""

    def __init__(self) -> None:
        self.request: tuple[Path, int, int] | None = None

    def transcribe(self, model: Path, rate: int, samples: int) -> str:
        self.request = (model, rate, samples)
        return " ileri git "


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


if __name__ == "__main__":
    unittest.main()
