from __future__ import annotations
"""music_lab.controller

Threaded orchestration between the GUI and the underlying `MusicGenerator`.
Separating concerns keeps `music_lab.generator` free of Tkinter-specific calls
while allowing responsive GUI behaviour.
"""

import threading
import traceback
from pathlib import Path
import io

# Optional MIDI handling
try:
    import mido
except ModuleNotFoundError:
    mido = None  # type: ignore
from typing import Callable, Optional, Dict, Any

from . import is_available, MusicGenerator, DependencyError

__all__ = [
    "MusicLabController",
]

Callback = Callable[[str, Dict[str, Any]], None]


class MusicSession:
    def __init__(self):
        self.lyrics = ""
        self.beat_midi = None  # Should be bytes or a MIDI object
        self.prompt = ""
        self.generated_audio = None  # Path to generated WAV
        self.generated_midi = None  # Path or bytes


class MusicLabController:
    """High-level helper used by the Music Lab tab.

    Parameters
    ----------
    prompt_builder : Callable[[Dict[str, Any]], str]
        Function that creates the *text prompt* for MusicGen from a BeatAdvisor
        blueprint and/or lyric metrics.
    on_result : Callable[[str, Dict[str, Any]], None]
        Callback invoked with two positional arguments *(event, payload)* where
        *event* is one of ``"progress"``, ``"done"``, or ``"error"``.
    model_name : str, optional
        Which MusicGen checkpoint to load.  Defaults to the small model which
        is ~1.5 GB and CPU-friendly.
    device : str, optional
        "cpu" or e.g. "cuda".
    """

    def __init__(
        self,
        prompt_builder: Callable[[Dict[str, Any]], str],
        on_result: Callback,
        *,
        model_name: str = "facebook/musicgen-large",
        device: str = "cpu",
    ):
        self._prompt_builder = prompt_builder
        self._on_result = on_result
        self._model_name = model_name
        self._device = device
        self._worker: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()

        if not is_available():
            raise DependencyError(
                "MusicLabController cannot be created because heavy dependencies"
                " are missing. Use music_lab.is_available() before instantiation."
            )

        self._generator = MusicGenerator(model_name, device)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def generate_async(self, blueprint: Dict[str, Any]):
        """Begin generation in a background thread."""
        if self._worker and self._worker.is_alive():
            raise RuntimeError("Music generation already in progress")

        prompt = self._prompt_builder(blueprint)

        self._worker = threading.Thread(
            target=self._worker_fn, args=(prompt, blueprint), daemon=True
        )
        self._stop_flag.clear()
        self._worker.start()

    def stop(self):
        """Attempt to stop generation (best-effort)."""
        self._stop_flag.set()

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------

    def _merge_midi_tracks(self, drum_midi_bytes: bytes, melody_midi_bytes: bytes) -> bytes:
        """Merge *drum* and *melody* MIDI bytes into a single multitrack MIDI file.

        If *mido* is unavailable this returns the melody bytes unchanged.
        """
        if not mido:
            return melody_midi_bytes
        try:
            drum_mid = mido.MidiFile(file=io.BytesIO(drum_midi_bytes))
            melody_mid = mido.MidiFile(file=io.BytesIO(melody_midi_bytes))

            # Create new MIDI with combined tracks
            merged_mid = mido.MidiFile()
            for track in drum_mid.tracks:
                merged_mid.tracks.append(track.copy())
            for track in melody_mid.tracks:
                merged_mid.tracks.append(track.copy())

            buf = io.BytesIO()
            merged_mid.save(file=buf)
            buf.seek(0)
            return buf.read()
        except Exception:
            return melody_midi_bytes

    def _worker_fn(self, prompt: str, blueprint: Dict[str, Any]):
        try:
            self._on_result("progress", {"msg": "Generating…"})
            clip = self._generator.generate(prompt, bpm=blueprint.get("bpm", 120))

            # If full track requested, attempt to merge existing drum MIDI
            if blueprint.get("full_track") and blueprint.get("drum_midi") and "midi" in clip:
                clip["midi"] = self._merge_midi_tracks(blueprint["drum_midi"], clip["midi"])
            if self._stop_flag.is_set():
                return

            # Save to temp WAV for immediate playback
            wav_bytes: bytes = clip["wav"]
            temp_path = Path.cwd() / "music_lab_preview.wav"
            with temp_path.open("wb") as f:
                f.write(wav_bytes)

            self._on_result("done", {"wav_path": temp_path, **clip})
        except Exception as exc:  # pylint: disable=broad-except
            traceback.print_exc()
            self._on_result("error", {"error": str(exc)})
