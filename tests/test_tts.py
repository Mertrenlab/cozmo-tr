"""Tests for macOS Turkish speech and Cozmo WAV validation."""

import shutil
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

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

    def test_rejects_wrong_wav_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "wrong.wav"
            with wave.open(str(output), "wb") as audio:
                audio.setnchannels(2)
                audio.setsampwidth(2)
                audio.setframerate(44_100)
                audio.writeframes(b"\0" * 16)
            with self.assertRaises(TtsUnavailable):
                validate_cozmo_wav(output)

    def test_rejects_empty_text(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaises(TtsUnavailable),
        ):
            MacSayTts().synthesize(" ", Path(directory) / "empty.wav")

    def test_reports_missing_system_tools(self) -> None:
        with (
            patch("cozmo_tr.tts.shutil.which", return_value=None),
            self.assertRaises(TtsUnavailable),
        ):
            MacSayTts().synthesize("Merhaba", Path("unused.wav"))


if __name__ == "__main__":
    unittest.main()
