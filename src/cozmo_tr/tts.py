"""Generate and validate Turkish audio for Cozmo's speaker.

Responsible for: macOS synthesis and 22.05 kHz PCM WAV validation.
Not responsible for: sending audio to the robot or microphone capture.
"""

import shutil
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path

COZMO_SAMPLE_RATE = 22_050
COZMO_CHANNELS = 1
COZMO_SAMPLE_WIDTH = 2
MACOS_VOICE = "Yelda"


class TtsUnavailable(RuntimeError):
    """Report a missing synthesizer, conversion failure, or invalid WAV."""


@dataclass(frozen=True, slots=True)
class WavSpec:
    """Expose the WAV properties Cozmo requires."""

    sample_rate: int
    channels: int
    sample_width: int


def validate_cozmo_wav(path: Path) -> WavSpec:
    """Return WAV metadata or raise when it is not Cozmo-compatible."""
    try:
        with wave.open(str(path), "rb") as audio:
            spec = WavSpec(
                audio.getframerate(),
                audio.getnchannels(),
                audio.getsampwidth(),
            )
    except (OSError, EOFError, wave.Error) as error:
        raise TtsUnavailable(f"WAV okunamadı: {path}") from error
    if spec != WavSpec(COZMO_SAMPLE_RATE, COZMO_CHANNELS, COZMO_SAMPLE_WIDTH):
        raise TtsUnavailable(f"Cozmo WAV biçimi bekleniyordu, bulunan: {spec}")
    return spec


class MacSayTts:
    """Create Turkish Cozmo WAV files with built-in macOS tools."""

    def synthesize(self, text: str, output: Path) -> WavSpec:
        """Write Turkish PCM WAV; raise TtsUnavailable on tool failure."""
        say, converter = self._tools()
        clean_text = text.strip()
        if not clean_text:
            raise TtsUnavailable("Konuşma metni boş olamaz")
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._run_pipeline(say, converter, clean_text, output)
        except (OSError, subprocess.CalledProcessError) as error:
            raise TtsUnavailable("macOS Türkçe ses üretilemedi") from error
        return validate_cozmo_wav(output)

    @staticmethod
    def _tools() -> tuple[str, str]:
        say = shutil.which("say")
        converter = shutil.which("afconvert")
        if say is None or converter is None:
            raise TtsUnavailable("macOS say veya afconvert bulunamadı")
        return say, converter

    @staticmethod
    def _run_pipeline(say: str, converter: str, text: str, output: Path) -> None:
        with tempfile.TemporaryDirectory(prefix="cozmo-tr-") as directory:
            intermediate = Path(directory) / "speech.aiff"
            subprocess.run(
                [say, "-v", MACOS_VOICE, "-o", intermediate, text],
                check=True,
            )
            subprocess.run(
                [
                    converter,
                    "-f",
                    "WAVE",
                    "-d",
                    "LEI16@22050",
                    "-c",
                    "1",
                    intermediate,
                    output,
                ],
                check=True,
            )
