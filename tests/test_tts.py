"""Tests for macOS Turkish speech and Cozmo WAV validation."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from cozmo_tr.tts import MacSayTts, TtsUnavailable, validate_cozmo_wav


MAC_TTS_AVAILABLE = (
    sys.platform == "darwin"
    and shutil.which("say") is not None
    and shutil.which("afconvert") is not None
)


class WavValidationTests(unittest.TestCase):
    """Verify the system TTS creates robot-compatible PCM."""

    @unittest.skipUnless(MAC_TTS_AVAILABLE, "macOS system TTS required")
    def test_synthesizes_cozmo_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "merhaba.wav"
            MacSayTts().synthesize("Merhaba, ben Cozmo", output)
            spec = validate_cozmo_wav(output)
        self.assertEqual(spec.sample_rate, 22_050)
        self.assertEqual(spec.channels, 1)
        self.assertEqual(spec.sample_width, 2)

    def test_rejects_non_wav_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bad.wav"
            output.write_text("not audio", encoding="utf-8")
            with self.assertRaises(TtsUnavailable):
                validate_cozmo_wav(output)


if __name__ == "__main__":
    unittest.main()
