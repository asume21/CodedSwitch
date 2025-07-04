"""Wrapper around Meta MusicGen for fast instrumental generation.

The module is optional; if *audiocraft* or compatible GPU is missing we raise a
clean RuntimeError so the GUI can fall back gracefully.
"""
from __future__ import annotations

import hashlib
import os
from typing import Optional
import tempfile

try:
    import torch  # type: ignore
    from audiocraft.models import MusicGen  # type: ignore
    from audiocraft.data.audio import audio_write  # type: ignore
except ImportError as _e:  # pragma: no cover
    torch = None  # type: ignore
    MusicGen = None  # type: ignore
    audio_write = None  # type: ignore
    _IMPORT_ERR: Optional[Exception] = _e  # preserve
else:
    _IMPORT_ERR = None

_CACHE_DIR = os.path.join(tempfile.gettempdir(), "beatstudio_musicgen_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)


class MusicGenBackend:
    """Lazy-loads the MusicGen model the first time it is needed."""

    def __init__(self, model_name: str = "facebook/musicgen-large"):
        if _IMPORT_ERR is not None:
            raise RuntimeError(
                "audiocraft is not installed.  Install with `pip install 'audiocraft@git+https://github.com/facebookresearch/audiocraft'`"
            ) from _IMPORT_ERR
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = MusicGen.get_pretrained(model_name).to(self.device)
        # Disable progress bars for headless runs
        self.model.set_generation_params(duration=30)

    def _prompt_hash(self, prompt: str, duration: int) -> str:
        return hashlib.sha1(f"{prompt}|{duration}".encode()).hexdigest()[:16]

    def generate(self, prompt: str, duration: int = 30) -> str:
        """Generate instrumental and return path to temporary wav file (44.1 kHz 2ch)."""
        cache_key = self._prompt_hash(prompt, duration)
        out_path = os.path.join(_CACHE_DIR, f"{cache_key}.wav")
        if os.path.exists(out_path):
            return out_path
        wav = self.model.generate(
            [prompt],
            progress=True,
            duration=duration,
            top_k=250,
            top_p=0.0,
            temperature=1.0,
        )[0].cpu()
        audio_write(out_path, wav, self.model.sample_rate, strategy="loudness")
        return out_path


# Singleton for convenient re-use
_backend: Optional[MusicGenBackend] = None

def generate_instrumental(lyrics: str, prompt: str, duration: int = 30) -> str:
    """Generate an instrumental via MusicGen and return wav path."""
    global _backend
    if _backend is None:
        _backend = MusicGenBackend()
    return _backend.generate(prompt, duration)
