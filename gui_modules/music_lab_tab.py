from __future__ import annotations
"""gui_modules.music_lab_tab

Initial Music Lab Tab integrating the new `music_lab` package into the GUI.  In
this first iteration it:

• Checks for heavy dependencies with `music_lab.is_available()`.
• If unavailable, shows a helpful message and install hint.
• If available, shows a stub interface with a *Generate* button and a piano-roll
  viewer powered by `music_lab.PianoRoll` and generation handled by
  `music_lab.controller.MusicLabController`.

The goal is to integrate gracefully without breaking the existing app.  Full
feature wiring (BeatAdvisor blueprint, lyric imports, playback controls, etc.)
will arrive in subsequent commits.
"""

from typing import Optional, Dict, Any
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # noqa: F403
import os
import threading
import traceback
import time

from music_lab import is_available
from allegro_integration import generate_midi_from_prompt  # Import the new backend
from lyric_to_music_prompt import get_music_prompt_from_lyrics
from music_lab.musicgen_backend import generate_musicgen_audio, play_audio, export_audio
from music_lab.controller import MusicSession

if is_available():
    from music_lab import controller as ml_controller
    from music_lab import piano_roll as ml_piano_roll
else:
    ml_controller = None  # type: ignore
    ml_piano_roll = None  # type: ignore


class MusicLabTab(ttk.Frame):
    """Music Lab Tab – minimal viable UI."""

    def __init__(self, parent_gui, *_, **__):
        super().__init__(parent_gui.notebook)
        self.parent_gui = parent_gui
        self.session = MusicSession()  # Shared session for this tab
        if not is_available():
            self._create_missing_dep_ui()
            return
        self._controller: Optional[ml_controller.MusicLabController] = None
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI builders
    # ------------------------------------------------------------------

    def _create_missing_dep_ui(self):
        ttk.Label(
            self,
            text=
                "Music Lab is disabled because required dependencies are missing.\n"
                "Install PyTorch, audiocraft, basic-pitch, mido, and python-rtmidi to enable.\n\n"
                "Example (CUDA 11.8):\n"
                "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118\n"
                "pip install audiocraft basic-pitch mido python-rtmidi",
            justify=tk.LEFT,
            wraplength=600,
        ).pack(padx=20, pady=20)

    def _setup_ui(self):
        # Prompt frame
        prompt_frame = ttk.Frame(self)
        prompt_frame.pack(fill=tk.X, pady=(10, 5), padx=10)

        ttk.Label(prompt_frame, text="Prompt:").pack(side=tk.LEFT)
        self.prompt_var = tk.StringVar(value="A chilled lo-fi beat with jazzy chords")
        ttk.Entry(prompt_frame, textvariable=self.prompt_var, width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Model selection dropdown
        self.model_var = tk.StringVar(value="MusicGen")
        model_dropdown = ttk.Combobox(prompt_frame, textvariable=self.model_var, values=["MusicGen", "Allegro"], width=10, state="readonly")
        model_dropdown.pack(side=tk.LEFT, padx=5)

        self.generate_btn = ttk.Button(prompt_frame, text="🥁 Generate", command=self._on_generate, bootstyle="primary")
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.full_btn = ttk.Button(prompt_frame, text="🎼 Generate Full Track", command=self._on_generate_full, bootstyle="success")
        self.full_btn.pack(side=tk.LEFT, padx=5)

        # Progress label
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(self, textvariable=self.status_var).pack(anchor=tk.W, padx=15)

        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=15, pady=(0, 5))
        self.progress.pack_forget()  # Hide initially

        # Piano roll
        self.piano_roll = ml_piano_roll.PianoRoll(self)
        self.piano_roll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bottom export buttons
        export_frame = ttk.Frame(self)
        export_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        ttk.Button(export_frame, text="💾 Export MIDI", command=self._export_midi).pack(side=tk.LEFT)
        ttk.Button(export_frame, text="▶ Play", command=self._play_wav).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="▶ Play Piano Roll", command=self._play_piano_roll).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="💾 Export WAV", command=self._export_wav).pack(side=tk.LEFT, padx=5)
        self._last_musicgen_wav = None

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_generate_full(self):
        """Generate a complete track conditioned on existing drum MIDI."""
        prompt = self.prompt_var.get().strip()
        if not prompt:
            messagebox.showwarning("Missing Prompt", "Please enter a prompt for generation.")
            return

        if not self.piano_roll.notes:
            messagebox.showinfo("Need Drums", "Generate drums first so the AI can build melody over them.")
            return

        drum_midi = self.piano_roll.export_midi()

        if self._controller is None:
            try:
                self._controller = ml_controller.MusicLabController(
                    prompt_builder=lambda _: prompt,
                    on_result=self._on_controller_event,
                )
            except Exception as exc:  # pylint: disable=broad-except
                messagebox.showerror("Music Lab Error", str(exc))
                return

        self.generate_btn.configure(state=tk.DISABLED)
        self.full_btn.configure(state=tk.DISABLED)
        self.status_var.set("Generating full track… this may take a minute.")
        self._controller.generate_async({"full_track": True, "drum_midi": drum_midi})

    def _on_generate(self):
        prompt = self.prompt_var.get().strip()
        if not prompt:
            messagebox.showwarning("Missing Prompt", "Please enter a prompt for generation.")
            return
        model_choice = self.model_var.get()
        self.session.prompt = prompt  # Store in session
        self.generate_btn.configure(state=tk.DISABLED)
        self.full_btn.configure(state=tk.DISABLED)
        self.status_var.set(f"Generating with {model_choice}…")
        self.progress.pack(fill=tk.X, padx=15, pady=(0, 5))
        self.progress.start(10)
        if model_choice == "MusicGen":
            def run_musicgen():
                try:
                    wav_path = generate_musicgen_audio(prompt, duration=15)
                    self._last_musicgen_wav = wav_path
                    self.session.generated_audio = wav_path  # Store in session
                    self.after(0, lambda: self._on_musicgen_complete(success=True))
                except Exception as exc:
                    traceback.print_exc()
                    self.after(0, lambda: self._on_musicgen_complete(success=False, error=exc))
            self.status_var.set("Generating audio with MusicGen…")
            self.update_idletasks()
            threading.Thread(target=run_musicgen, daemon=True).start()
        elif model_choice == "Allegro":
            try:
                # Use the new lyric-to-music intent pipeline
                music_info = get_music_prompt_from_lyrics(prompt)
                tokens = music_info.get("tokens", [])
                midi_bytes = generate_midi_from_prompt(tokens)
                self.piano_roll.load_midi(midi_bytes)
                mood = music_info.get("mood", "?")
                tempo = music_info.get("tempo", "?")
                key = music_info.get("key", "?")
                self.status_var.set(f"Allegro complete ✔ | Mood: {mood} | Tempo: {tempo} | Key: {key}")
            except Exception as exc:
                messagebox.showerror("Allegro Error", str(exc))
                self.status_var.set(f"Error: {exc}")
            self.progress.stop()
            self.progress.pack_forget()
            self.generate_btn.configure(state=tk.NORMAL)
            self.full_btn.configure(state=tk.NORMAL)

    def _on_controller_event(self, event: str, payload: Dict[str, Any]):
        self.parent_gui.root.after(0, self._handle_controller_event, event, payload)

    def _handle_controller_event(self, event: str, payload: Dict[str, Any]):
        if event == "progress":
            self.status_var.set(payload.get("msg", "Working…"))
        elif event == "done":
            self.status_var.set("Generation complete ✔")
            wav_path = payload.get("wav_path")
            midi_bytes = payload.get("midi")
            if midi_bytes:
                self.piano_roll.load_midi(midi_bytes)
            if wav_path and wav_path.exists():
                # basic playback using default system player
                try:
                    import webbrowser
                    webbrowser.open(wav_path.as_uri())
                except Exception:
                    pass
            self.generate_btn.configure(state=tk.NORMAL)
        elif event == "error":
            self.status_var.set(f"Error: {payload.get('error')}")
            self.generate_btn.configure(state=tk.NORMAL)

    def _on_musicgen_complete(self, success: bool, error: Exception = None):
        self.progress.stop()
        self.progress.pack_forget()
        if success:
            self.status_var.set("MusicGen complete ✔")
        else:
            self.status_var.set(f"MusicGen Error: {error}")
            messagebox.showerror("MusicGen Error", str(error))
        self.generate_btn.configure(state=tk.NORMAL)
        self.full_btn.configure(state=tk.NORMAL)

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def _export_midi(self):
        if not self.piano_roll.notes:
            messagebox.showinfo("No MIDI", "Nothing to export yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".mid", filetypes=[("MIDI File", "*.mid"), ("All", "*.*")]
        )
        if path:
            try:
                data = self.piano_roll.export_midi()
                with open(path, "wb") as f:
                    f.write(data)
                messagebox.showinfo("Exported", f"Saved MIDI to {path}")
            except Exception as exc:  # pylint: disable=broad-except
                messagebox.showerror("Export Error", str(exc))

    def _play_wav(self):
        wav_path = self.session.generated_audio or self._last_musicgen_wav
        if not wav_path or not os.path.exists(wav_path):
            messagebox.showwarning("No audio", "Generate audio first.")
            return
        try:
            self.status_var.set("Playing audio…")
            self.update_idletasks()
            play_audio(wav_path)
            self.status_var.set("Playback finished.")
        except Exception as exc:
            messagebox.showerror("Playback Error", str(exc))
            self.status_var.set(f"Error: {exc}")

    def _export_wav(self):
        wav_path = self.session.generated_audio or self._last_musicgen_wav
        if not wav_path or not os.path.exists(wav_path):
            messagebox.showwarning("No audio", "Generate audio first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".wav", filetypes=[("WAV File", "*.wav"), ("All", "*.*")]
        )
        if path:
            try:
                export_audio(wav_path, path)
                messagebox.showinfo("Exported", f"Saved WAV to {path}")
            except Exception as exc:
                messagebox.showerror("Export Error", str(exc))

    def _play_piano_roll(self):
        if not self.piano_roll.notes:
            messagebox.showinfo("No Notes", "There are no notes in the piano roll to play.")
            return
        try:
            self.status_var.set("Playing piano roll…")
            self.update_idletasks()
            # Calculate total duration in seconds
            midi_bytes = self.piano_roll.export_midi()
            import io, mido
            midi = mido.MidiFile(file=io.BytesIO(midi_bytes))
            tempo = 500000  # default 120 bpm
            total_ticks = 0
            for msg in midi:
                if msg.type == "set_tempo":
                    tempo = msg.tempo
                total_ticks += msg.time
            ticks_per_beat = midi.ticks_per_beat or 480
            total_beats = total_ticks / ticks_per_beat
            total_seconds = total_beats * (tempo / 1_000_000)
            # Set up progress bar
            self.progress.config(mode="determinate", maximum=total_seconds)
            self.progress.pack(fill=tk.X, padx=15, pady=(0, 5))
            self.progress['value'] = 0
            self.progress.update_idletasks()
            # Start playback and update progress
            def update_progress(start_time):
                elapsed = time.time() - start_time
                self.progress['value'] = min(elapsed, total_seconds)
                if elapsed < total_seconds:
                    self.after(50, update_progress, start_time)
                else:
                    self.progress['value'] = 0
                    self.status_var.set("Playback finished.")
            def play_and_update():
                start_time = time.time()
                self.after(0, update_progress, start_time)
                self.piano_roll.play_with_fluidsynth(r"D:\Projects\AI_Projects\AI_Code_Translator_Advanced_Final\Soundfonts\GeneralUser-GS.sf2")
            threading.Thread(target=play_and_update, daemon=True).start()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Playback Error", f"{type(exc).__name__}: {exc}")
            self.status_var.set(f"Error: {exc}")
