from __future__ import annotations
"""music_lab.piano_roll

Lightweight Tkinter piano-roll widget that can *display* (and minimally edit)
MIDI data.  The widget avoids heavy DAW-style functionality – the goal is to
provide a visual reference for clips produced by `music_lab.generator` and let
users export the edited MIDI.

If the optional *mido* dependency is missing, the widget still loads and works
with an internal note list; only the MIDI import/export helpers raise
``DependencyError``.
"""

from typing import List, Tuple, Optional, Dict, Any
import importlib
import tkinter as tk
from tkinter import ttk
import tempfile
import os
import time
import threading
try:
    import fluidsynth
except ImportError:
    fluidsynth = None

__all__ = [
    "PianoRoll",
    "DependencyError",
]


class DependencyError(RuntimeError):
    """Raised when a required optional dependency is missing."""


# ----------------------------------------------------------------------------
# Utility – lazy import mido so the rest of the app remains light.
# ----------------------------------------------------------------------------

def _lazy_import_mido():
    try:
        return importlib.import_module("mido")
    except ModuleNotFoundError as exc:
        raise DependencyError(
            "The optional dependency 'mido' is required for MIDI import/export. "
            "Install it with `pip install mido python-rtmidi` to enable full piano-roll features."
        ) from exc


# ----------------------------------------------------------------------------
# PianoRoll widget
# ----------------------------------------------------------------------------

class PianoRoll(ttk.Frame):
    """Simple piano-roll widget.

    Notes are stored as tuples *(pitch, start, duration)* where *pitch* is MIDI
    note (0–127), *start* and *duration* are in *beats*.
    """

    def __init__(self, parent, *, beats_per_bar: int = 4, ppqn: int = 480):
        super().__init__(parent)
        self.beats_per_bar = beats_per_bar
        self.ppqn = ppqn

        # Internal representation
        self.notes: List[Tuple[int, float, float]] = []  # (pitch, start, duration) – beats

        # Canvas size/scale
        self._beat_px = 40  # pixels per beat (X-axis)
        self._note_h = 6    # pixels per semitone (Y-axis)

        # Create UI
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Mouse interactions (basic – toggles notes)
        self.canvas.bind("<Button-1>", self._on_click)

        self._draw_background()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def load_midi(self, midi_bytes: bytes):
        """Parse MIDI bytes into the internal note list."""
        mido = _lazy_import_mido()
        import io

        midi = mido.MidiFile(file=io.BytesIO(midi_bytes))

        self.notes.clear()
        time_beats = 0.0
        tempo = 500000  # default 120 bpm
        ticks_per_beat = midi.ticks_per_beat or self.ppqn

        # We only consider note_on/note_off of track 0 for simplicity
        active_notes: Dict[int, float] = {}

        for msg in midi:
            time_beats += msg.time * (tempo / 1_000_000) * (1.0 / 60.0)  # convert seconds to beats
            if msg.type == "set_tempo":
                tempo = msg.tempo
            elif msg.type == "note_on" and msg.velocity > 0:
                active_notes[msg.note] = time_beats
            elif (msg.type == "note_off") or (msg.type == "note_on" and msg.velocity == 0):
                start = active_notes.pop(msg.note, None)
                if start is not None:
                    duration = max(time_beats - start, 0.125)
                    self.notes.append((msg.note, start, duration))

        self._redraw()

    def export_midi(self) -> bytes:
        """Return current notes as MIDI bytes (single-track file)."""
        mido = _lazy_import_mido()
        import io

        midi = mido.MidiFile(ticks_per_beat=self.ppqn)
        track = mido.MidiTrack()
        midi.tracks.append(track)

        tempo = mido.bpm2tempo(120)  # not tracking tempo changes for now
        track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))

        # Sort by start time
        sorted_notes = sorted(self.notes, key=lambda n: n[1])
        last_tick = 0
        for note, start, duration in sorted_notes:
            start_tick = int(start * self.ppqn)
            delta = max(0, start_tick - last_tick)
            track.append(mido.Message("note_on", note=note, velocity=96, time=delta))
            end_tick = start_tick + int(duration * self.ppqn)
            last_tick = start_tick
            # note_off later – store for second pass
            track.append(mido.Message("note_off", note=note, velocity=0, time=max(0, int(duration * self.ppqn))))
            last_tick = end_tick

        buf = io.BytesIO()
        midi.save(file=buf)
        buf.seek(0)
        return buf.read()

    def play_with_fluidsynth(self, soundfont_path=r"D:\Projects\AI_Projects\AI_Code_Translator_Advanced_Final\Soundfonts\GeneralUser-GS.sf2"):
        """Export notes to a temp MIDI file and play with FluidSynth."""
        if fluidsynth is None:
            raise ImportError("pyfluidsynth is not installed. Please install it with 'pip install pyfluidsynth'.")
        midi_bytes = self.export_midi()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as tmp_midi:
            tmp_midi.write(midi_bytes)
            tmp_midi_path = tmp_midi.name
        def _play():
            import mido
            fs = fluidsynth.Synth()
            fs.start()
            sfid = fs.sfload(soundfont_path)
            fs.program_select(0, sfid, 0, 0)
            mid = mido.MidiFile(tmp_midi_path)
            for msg in mid.play():
                if msg.type == 'note_on':
                    fs.noteon(0, msg.note, msg.velocity)
                elif msg.type == 'note_off':
                    fs.noteoff(0, msg.note)
            fs.delete()
            os.remove(tmp_midi_path)
        threading.Thread(target=_play, daemon=True).start()

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_background(self):
        self.canvas.delete("bg")
        # Draw horizontal key lines every octave
        for midi_note in range(128):
            y = (127 - midi_note) * self._note_h
            color = "#333333" if midi_note % 12 in {1, 3, 6, 8, 10} else "#2a2a2a"
            tag = "bg"
            self.canvas.create_rectangle(0, y, 10_000, y + self._note_h, fill=color, width=0, tags=tag)

        # Beat/grid lines
        for beat in range(256):  # arbitrary limit
            x = beat * self._beat_px
            color = "#505050" if beat % self.beats_per_bar == 0 else "#3a3a3a"
            tag = "bg"
            self.canvas.create_line(x, 0, x, 128 * self._note_h, fill=color, tags=tag)

        self.canvas.configure(scrollregion=(0, 0, 256 * self._beat_px, 128 * self._note_h))

    def _redraw(self):
        self.canvas.delete("note")
        for pitch, start, duration in self.notes:
            x0 = start * self._beat_px
            x1 = (start + duration) * self._beat_px
            y0 = (127 - pitch) * self._note_h
            y1 = y0 + self._note_h
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="#1abc9c", outline="", tags="note")

    # ------------------------------------------------------------------
    # Interaction – simple toggle add/remove notes by clicking
    # ------------------------------------------------------------------

    def _on_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        pitch = 127 - int(canvas_y // self._note_h)
        beat = canvas_x / self._beat_px
        beat = round(beat * 4) / 4  # quantize 16th notes

        # Remove existing note at this grid pos, else add
        for idx, (p, s, d) in enumerate(self.notes):
            if p == pitch and abs(s - beat) < 1e-3:
                self.notes.pop(idx)
                self._redraw()
                return

        self.notes.append((pitch, beat, 1.0))
        self._redraw()
