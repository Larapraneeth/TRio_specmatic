import subprocess
import tempfile
import os
import io
import wave
import struct
from core.config import settings


class TextToSpeech:
    def synthesize(self, text: str) -> bytes:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                out_path = f.name

            clean_text = self._clean_text(text)

            result = subprocess.run(
                ["piper", "--model", settings.PIPER_MODEL, "--output_file", out_path],
                input=clean_text.encode(),
                capture_output=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"Piper failed: {result.stderr.decode(errors='ignore')}")

            with open(out_path, "rb") as f:
                audio_bytes = f.read()
            if os.path.exists(out_path):
                os.unlink(out_path)

            return audio_bytes if audio_bytes else self._fallback_tts(text)

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
        Headless-safe fallback. Tries espeak (writes a WAV directly, no audio
        device needed). If espeak is unavailable, returns a valid minimal silent
        WAV so the endpoint always responds with well-formed audio/wav instead of
        failing. Guarantees deterministic behaviour across environments.
        """
        try:
            clean_text = self._clean_text(text)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                out_path = f.name

            result = subprocess.run(
                ["espeak", "-w", out_path, clean_text],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and os.path.exists(out_path):
                with open(out_path, "rb") as f:
                    audio_bytes = f.read()
                if os.path.exists(out_path):
                    os.unlink(out_path)
                if audio_bytes:
                    return audio_bytes
        except Exception as e:
            print(f"espeak fallback failed: {e}")

        return self._silent_wav()

    def _silent_wav(self, duration_seconds: float = 0.2, sample_rate: int = 22050) -> bytes:
        """Generate a valid silent WAV file in memory."""
        n_frames = int(duration_seconds * sample_rate)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(struct.pack("<" + "h" * n_frames, *([0] * n_frames)))
        return buf.getvalue()


tts = TextToSpeech()