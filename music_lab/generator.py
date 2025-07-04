from __future__ import annotations
"""music_lab.generator

Light wrapper around Facebook/Meta MusicGen + BasicPitch that hides heavy
dependencies from the rest of CodedSwitch.  If PyTorch / audiocraft / torch
aren't available (e.g. in a lightweight environment), importing this module is
still safe: attempting to instantiate `MusicGenerator` will raise
``DependencyError`` which the GUI can catch and disable generation features.
"""

from typing import Optional, Tuple, Union, Dict, Any
import importlib
import io

__all__ = [
    "DependencyError",
    "MusicGenerator",
]


class DependencyError(RuntimeError):
    """Raised when MusicGen's heavyweight dependencies are missing."""


def _lazy_import(pkg: str):
    """Import *pkg* lazily, raising ``DependencyError`` on failure."""
    try:
        return importlib.import_module(pkg)
    except ModuleNotFoundError as exc:
        raise DependencyError(
            f"The optional dependency '{pkg}' is required for Music Lab generation. "
            "Install the extra packages listed in requirements_music.txt to enable this feature."
        ) from exc


class MusicGenerator:
    """Facade around the MusicGen model and BasicPitch MIDI conversion."""

    _model_cache: Dict[str, Any] = {}

    def __init__(self, model_name: str = "facebook/musicgen-small", device: str = "cpu"):
        """Load the MusicGen *model_name* on *device*.

        Heavy imports (torch, audiocraft) happen lazily; they are cached so that
        multiple instances share the same underlying model object.
        """
        self.model_name = model_name
        self.device = device

        if model_name in self._model_cache:
            self._model = self._model_cache[model_name]
            return

        # Lazy imports – will raise DependencyError if missing
        self._torch = _lazy_import("torch")
        audiocraft = _lazy_import("audiocraft")
        from audiocraft.models import MusicGen  # type: ignore
        from audiocraft.data.audio import audio_write  # type: ignore

        self._audio_write = audio_write  # store ref for later

        # Load the model (this can take several seconds on first run)
        self._model = MusicGen.get_pretrained(model_name, device=device)
        self._model.set_generation_params(duration=30)  # default 30-sec clips

        self._model_cache[model_name] = self._model

        # BasicPitch for WAV→MIDI (optional)
        try:
            import basic_pitch  # noqa: F401 unused import – just check availability
            self._basic_pitch_available = True
        except ModuleNotFoundError:
            self._basic_pitch_available = False

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def generate(self, prompt: str, bpm: int = 120, duration: int = 30, **blueprint) -> Dict[str, Union[bytes, str]]:
        """Generate an audio clip (and optional MIDI) from *prompt*.

        Returns a dict with at least the key ``"wav"`` (16-bit PCM WAV bytes).
        If *basic_pitch* is installed, also includes a ``"midi"`` key with the
        rendered MIDI file bytes.
        """
        self._model.set_generation_params(duration=duration)
        with self._torch.no_grad():
            wav = self._model.generate([prompt])[0].cpu()

        # Convert to WAV bytes
        wav_bytes = io.BytesIO()
        self._audio_write("dummy", wav, wav.shape[-1] / 32000, format="wav", path=wav_bytes)
        wav_bytes.seek(0)

        result = {"wav": wav_bytes.read()}

        if self._basic_pitch_available:
            midi_bytes = self._convert_to_midi(wav, sample_rate=32000)
            if midi_bytes:
                result["midi"] = midi_bytes

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _convert_to_midi(self, wav_tensor, sample_rate: int = 32000) -> Optional[bytes]:
        """Use BasicPitch to convert *wav_tensor* to MIDI bytes."""
        try:
            import numpy as np
            from basic_pitch import ICASSP_2022_MODEL_PATH, load_model, predict
            from basic_pitch.midi import save_midi
        except ModuleNotFoundError:
            return None

        model = load_model(ICASSP_2022_MODEL_PATH)
        audio_np = wav_tensor.squeeze().cpu().numpy()
        model_output, _ = predict(model, audio_np, sample_rate)

        # Write to in-memory buffer
        buf = io.BytesIO()
        save_midi(model_output, buf, instrument=0)
        buf.seek(0)
        return buf.read()
