import subprocess
import tempfile
import os
from core.config import settings


class TextToSpeech:
    def synthesize(self, text: str) -> bytes:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                out_path = f.name

            clean_text = self._clean_text(text)

            result = subprocess.run(
                [
                    "piper",
                    "--model",
                    settings.PIPER_MODEL,
                    "--output_file",
                    out_path
                ],
                input=clean_text.encode(),
                capture_output=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Piper failed: {result.stderr.decode(errors='ignore')}"
                )

            with open(out_path, "rb") as f:
                audio_bytes = f.read()

            if os.path.exists(out_path):
                os.unlink(out_path)

            return audio_bytes

        except FileNotFoundError:
            print("Piper not found, using espeak fallback...")
            return self._fallback_tts(text)

        except Exception as e:
            print(f"Piper TTS failed: {e}")
            return self._fallback_tts(text)

    def _clean_text(self, text: str) -> str:
        import re

        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'#+\s', '', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

        return text[:500]

    def _fallback_tts(self, text: str) -> bytes:
        """
        Headless CI-safe fallback using espeak.
        Generates a WAV file directly without requiring
        an audio device or pyttsx3.
        """
        try:
            clean_text = self._clean_text(text)

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as f:
                out_path = f.name

            result = subprocess.run(
                [
                    "espeak",
                    "-w",
                    out_path,
                    clean_text
                ],
                capture_output=True,
                timeout=30
            )

            if result.returncode != 0:
                print(
                    f"espeak failed: "
                    f"{result.stderr.decode(errors='ignore')}"
                )
                return b""

            if not os.path.exists(out_path):
                print("espeak did not create WAV file")
                return b""

            with open(out_path, "rb") as f:
                audio_bytes = f.read()

            if os.path.exists(out_path):
                os.unlink(out_path)

            return audio_bytes

        except Exception as e:
            print(f"Fallback TTS failed: {e}")
            return b""


tts = TextToSpeech()