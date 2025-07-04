"""
beat_studio_integration.py - Professional Beat Studio Integration for CodedSwitch
This module integrates the advanced beat generation features into your existing GUI
"""

import os
import sys
import logging
logger = logging.getLogger(__name__)  # early logger setup
import numpy as np
import pygame
import threading
import tempfile
from scipy.io import wavfile
from scipy import signal
import json
from typing import Dict, Optional, Tuple, List, Any
from dataclasses import dataclass
import tkinter as tk
import beat_advisor

# ---------------------------------------------------------------------------
# SafeDoubleVar – Defensive wrapper around tk.DoubleVar
# ---------------------------------------------------------------------------
class _SafeDoubleVar(tk.DoubleVar):
    """A drop-in replacement for ``tk.DoubleVar`` that verifies the value
    passed to ``set()`` is numeric (or castable to float).  If an invalid
    value is detected it is **not** applied and we log the incident instead
    of letting Tkinter raise a cryptic ``_tkinter.TclError: expected
    floating-point number but got ...`` error.  This helps track down the
    root cause of mysterious *getdouble()* crashes without killing the GUI.
    """

    def set(self, value):  # type: ignore[override]
        try:
            # Accept ints, floats and anything that can cleanly cast to float
            if not isinstance(value, (int, float)):
                value = float(value)
            super().set(float(value))
        except Exception:
            import traceback, sys
            tb = ''.join(traceback.format_stack(limit=10))
            msg = (
                f"Attempted to set DoubleVar '{getattr(self, '_name', 'unknown')}' "
                f"with non-numeric value: {value!r} ({type(value).__name__})\n{tb}"
            )
            # Send to logger *and* stderr so it shows in console even if logging isn't configured
            logger.error(msg)
            print(msg, file=sys.stderr)


# Monkey-patch globally so every subsequent ``tk.DoubleVar`` usage picks up the
# safe version without invasive refactors.
tk.DoubleVar = _SafeDoubleVar  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Patch low-level ``_tkinter.getdouble`` so it gracefully handles tuple/list
# ---------------------------------------------------------------------------
try:
    import _tkinter  # type: ignore
    _orig_getdouble = getattr(_tkinter, "getdouble", None)

    if _orig_getdouble is not None:
        def _safe_getdouble(val):  # type: ignore[override]
            """Return the first element if a tuple/list is passed to getdouble()."""
            if isinstance(val, (tuple, list)) and val:
                val = val[0]
            return _orig_getdouble(val)

        _tkinter.getdouble = _safe_getdouble  # type: ignore[attr-defined]
        logger.debug("_tkinter.getdouble patched with tuple-safe version")
    else:
        logger.debug("_tkinter.getdouble not present; skipping patch")
except Exception as _patch_err:  # pragma: no cover
    logger.debug("Could not patch _tkinter.getdouble: %s", _patch_err)

from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from datetime import datetime


# Default availability flag (updated after import attempt below)
BEAT_STUDIO_AVAILABLE = False

# Try to import the beat studio modules
try:
    from beat_studio import (
        BeatStudioEngine, PresetManager, EffectsProcessor,
        create_beat_from_lyrics, AudioConstants, Scale,
        DrumSynthesizer, Synthesizer, MelodyGenerator, Sequencer,
        Pattern, Note
    )
    BEAT_STUDIO_AVAILABLE = True
    logger.info("✅ Beat Studio modules loaded successfully!")
except Exception as e:
    # Second attempt: try the stand-alone professional module
    try:
        import beat_studio_professional as beat_studio
        BeatStudioEngine = beat_studio.BeatStudioEngine
        PresetManager = beat_studio.PresetManager
        EffectsProcessor = beat_studio.EffectsProcessor
        create_beat_from_lyrics = beat_studio.create_beat_from_lyrics
        AudioConstants = beat_studio.AudioConstants
        Scale = beat_studio.Scale
        DrumSynthesizer = beat_studio.DrumSynthesizer
        Synthesizer = beat_studio.Synthesizer
        MelodyGenerator = beat_studio.MelodyGenerator
        Sequencer = beat_studio.Sequencer
        Pattern = beat_studio.Pattern
        Note = beat_studio.Note
        BEAT_STUDIO_AVAILABLE = True
        logger.info("✅ beat_studio_professional loaded as fallback!")
    except ImportError:
        logger.warning(f"⚠️ Beat Studio modules not available: {e}")
        BEAT_STUDIO_AVAILABLE = False
    
    # Create minimal fallback classes to satisfy type references
    if not BEAT_STUDIO_AVAILABLE:
        @dataclass
        class Note:
            pitch: int = 60
            velocity: float = 1.0
            duration: float = 1.0
            start_time: float = 0.0

        @dataclass
        class Pattern:
            notes: list = None
            length: float = 0.0
            channel: str = "default"

        class BeatStudioEngine:
            pass

        class PresetManager:
            def __init__(self):
                self.presets = {}

        class EffectsProcessor:
            def apply_effects(self, audio, settings=None):
                return audio

        class AudioConstants:
            SAMPLE_RATE = 44100
            CHANNELS = 2
            BUFFER_SIZE = 512

# ============================================================================
# BEAT STUDIO INTEGRATION CLASS
# ============================================================================

class BeatStudioIntegration:
    DRUM_SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "assets", "hq_drums")  # kick.wav, snare.wav, hihat.wav, openhat.wav
    USE_FLUIDSYNTH = False  # toggled via UI
    _sample_cache: Dict[str, pygame.mixer.Sound] = {}

    """Integrates professional beat generation into CodedSwitch GUI."""
    
    def __init__(self):
        global BEAT_STUDIO_AVAILABLE
        self.engine = None
        self.preset_manager = None
        self.effects_processor = None
        self.current_beat = None
        self.current_audio_file = None
        self.is_playing = False
        
        # Initialize components if available
        if BEAT_STUDIO_AVAILABLE:
            try:
                self.engine = BeatStudioEngine()
                self.preset_manager = PresetManager()
                self.effects_processor = EffectsProcessor()
                logger.info("🎵 Beat Studio components initialized successfully!")
                # Pre-load HQ drum samples, but do not fail if audio device is unavailable
                try:
                    self._load_drum_samples()
                except Exception as sample_err:
                    logger.warning(f"Could not load HQ drum samples (continuing without them): {sample_err}")
            except Exception as e:
                logger.error(f"Failed to initialize Beat Studio components: {e}")
                BEAT_STUDIO_AVAILABLE = False
    
    def is_available(self) -> bool:
        """Check if Beat Studio is available and initialized."""
        return BEAT_STUDIO_AVAILABLE and self.engine is not None
    
    def add_beat_studio_tab(self, notebook: ttk.Notebook, parent_gui) -> Optional[ttk.Frame]:
        """Add Beat Studio tab to the main notebook."""
        if not self.is_available():
            logger.warning("Beat Studio not available - tab not added")
            return None
        
        # Create the Beat Studio tab
        beat_tab = ttk.Frame(notebook)
        notebook.add(beat_tab, text="  🎵 Beat Studio  ")
        
        # Set up the Beat Studio interface
        self._setup_beat_studio_tab(beat_tab, parent_gui)
        
        logger.info("🎵 Beat Studio tab added successfully!")
        return beat_tab
    
    def _setup_beat_studio_tab(self, parent: ttk.Frame, parent_gui):
        """Set up the complete Beat Studio interface.

    The UI for Beat Studio is quite tall; on smaller screens the bottom
    playback buttons can get clipped by the application status-bar.
    Wrapping the entire tab in a scroll-able canvas keeps the layout the
    same while letting users scroll to anything that would otherwise be
    hidden.
    """

            # ------------------------------------------------------------------
        # Scrollable container
            # ------------------------------------------------------------------
        # Create an outer frame that will hold the Canvas + scrollbar.
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        # Canvas for scrolling and the vertical scrollbar.
        canvas = tk.Canvas(container, highlightthickness=0)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        # Geometry management
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

            # ------------------------------------------------------------------
        # Interior "main_frame" that will host the actual Beat-Studio widgets
        # ------------------------------------------------------------------
        main_frame = ttk.Frame(canvas, padding=10)
        # Add the frame to the canvas window so it becomes scrollable.
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        # Make the embedded frame match the full canvas width so unused space disappears
        def _on_canvas_config(event):
            """Keep the inner frame width in sync with the canvas."""
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_config)

        # Whenever the size of main_frame changes, update the scrollregion.
        def _on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main_frame.bind("<Configure>", _on_frame_config)

        # Enable mouse-wheel scrolling (Windows & Linux). Mac uses different delta.
        def _on_mousewheel(event):
            # event.delta is negative when scrolling down on Windows
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ------------------------------------------------------------------
        # Build the regular Beat-Studio UI inside main_frame
        # ------------------------------------------------------------------

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            header_frame,
            text="🎵 Professional Beat Studio - AI-Powered Beat Generation",
            font=("Segoe UI", 14, "bold")
        ).pack(side=tk.LEFT)

        # Store references
        self.parent_gui = parent_gui

        # Create main sections
        self._create_lyrics_section(main_frame)
        self._create_generation_controls(main_frame)
        self._create_pattern_editor(main_frame)
        self._create_playback_controls(main_frame)
    
    def _create_lyrics_section(self, parent):
        """Create lyrics input section."""
        lyrics_frame = ttk.LabelFrame(parent, text="📝 Lyrics for Beat Generation", padding=10)
        lyrics_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Top controls
        controls_frame = ttk.Frame(lyrics_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="📋 Import from Lyric Lab",
            command=self._import_from_lyric_lab,
            bootstyle="info"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="🎯 Analyze Mood",
            command=self._analyze_lyrics_mood,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=5)
        
        # Lyrics text area
        from ttkbootstrap.scrolled import ScrolledText
        self.beat_lyrics_text = ScrolledText(
            lyrics_frame,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.beat_lyrics_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_generation_controls(self, parent):
        """Create beat generation controls."""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Beat Generation Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: Presets
        preset_frame = ttk.Frame(control_frame)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(preset_frame, text="Preset:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.preset_var = tk.StringVar(value="Custom")
        preset_values = ["Custom"] + list(self.preset_manager.presets.keys()) if self.preset_manager else ["Custom"]
        preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=preset_values,
            state="readonly",
            width=20
        )
        preset_combo.pack(side=tk.LEFT, padx=(0, 20))
        preset_combo.bind("<<ComboboxSelected>>", self._on_preset_change)
        
        # BPM Control
        ttk.Label(preset_frame, text="BPM:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.bpm_var = tk.IntVar(value=120)
        bpm_scale = ttk.Scale(
            preset_frame,
            from_=60,
            to=200,
            variable=self.bpm_var,
            length=150,
            orient=tk.HORIZONTAL
        )
        bpm_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        self.bpm_label = ttk.Label(preset_frame, text="120")
        self.bpm_label.pack(side=tk.LEFT, padx=(0, 20))
        bpm_scale.configure(command=lambda v: self.bpm_label.config(text=str(int(float(v)))))
        
        # Energy Level
        ttk.Label(preset_frame, text="Energy:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.energy_var = tk.IntVar(value=7)
        energy_scale = ttk.Scale(
            preset_frame,
            from_=1,
            to=10,
            variable=self.energy_var,
            length=100,
            orient=tk.HORIZONTAL
        )
        energy_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        self.energy_label = ttk.Label(preset_frame, text="7")
        self.energy_label.pack(side=tk.LEFT)
        energy_scale.configure(command=lambda v: self.energy_label.config(text=str(int(float(v)))))
        
        # Row 2: Style controls
        style_frame = ttk.Frame(control_frame)
        style_frame.pack(fill=tk.X)
        
        ttk.Label(style_frame, text="Pattern:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.pattern_var = tk.StringVar(value="trap")
        pattern_combo = ttk.Combobox(
            style_frame,
            textvariable=self.pattern_var,
            values=["basic", "trap", "hiphop", "drill", "experimental"],
            state="readonly",
            width=15
        )
        pattern_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(style_frame, text="Scale:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.scale_var = tk.StringVar(value="MINOR")
        scale_combo = ttk.Combobox(
            style_frame,
            textvariable=self.scale_var,
            values=["MAJOR", "MINOR", "PENTATONIC", "BLUES"],
            state="readonly",
            width=15
        )
        scale_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Generate button
        self.generate_btn = ttk.Button(
            style_frame,
            text="🎵 Generate Beat",
            command=self._generate_beat,
            bootstyle="success",
            width=20
        )
        self.generate_btn.pack(side=tk.RIGHT)

        # Instrumental generation button (MusicGen)
        self.instrumental_btn = ttk.Button(
            style_frame,
            text="🌟 Instrumental (Pro)",
            command=self._generate_instrumental,
            bootstyle="info",
            width=24
        )
        self.instrumental_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # Full Song generation button
        self.full_song_btn = ttk.Button(
            style_frame,
            text="🎶 Full Song (3 min)",
            command=self._generate_full_song,
            bootstyle="warning",
            width=22
        )
        # Place it just to the right of the Instrumental button
        self.full_song_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def _create_pattern_editor(self, parent):
        """Create visual pattern editor."""
        pattern_frame = ttk.LabelFrame(parent, text="🎹 Pattern Editor", padding=10)
        pattern_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Pattern grid header
        header_frame = ttk.Frame(pattern_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="", width=10).pack(side=tk.LEFT)  # Spacer for instrument names
        for i in range(1, 17):
            ttk.Label(
                header_frame,
                text=str(i),
                width=3,
                font=("Courier", 8, "bold" if i % 4 == 1 else "normal")
            ).pack(side=tk.LEFT)
        
        # Initialize patterns
        self.patterns = {
            'kick': [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
            'snare': [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            'hihat': [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            'openhat': [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
            'clap': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            'bass808': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            'perc': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        }
        
        self.pattern_buttons = {}
        
        # Create pattern rows
        instruments = [
            ("🥁 Kick", "kick", "#FF5722"),
            ("🥁 Snare", "snare", "#2196F3"),
            ("🎩 Hi-Hat", "hihat", "#4CAF50"),
            ("🎩 Open Hat", "openhat", "#FFC107"),
            ("👏 Clap", "clap", "#E91E63"),
            ("🔊 808 Bass", "bass808", "#9C27B0"),
            ("🥁 Perc Loop", "perc", "#009688")
        ]
        
        for inst_name, inst_key, color in instruments:
            row_frame = ttk.Frame(pattern_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=inst_name, width=10).pack(side=tk.LEFT)
            
            self.pattern_buttons[inst_key] = []
            for i in range(16):
                btn = tk.Button(
                    row_frame,
                    text="●" if self.patterns[inst_key][i] else "○",
                    width=2,
                    height=1,
                    font=("Arial", 8),
                    bg=color if self.patterns[inst_key][i] else "gray80",
                    fg="white",
                    relief=tk.FLAT,
                    command=lambda k=inst_key, idx=i: self._toggle_pattern(k, idx, color)
                )
                btn.pack(side=tk.LEFT, padx=1)
                self.pattern_buttons[inst_key].append(btn)

        # Melody roll (12×16)
        self.melody_grid = [[0 for _ in range(16)] for _ in range(12)]
        self.melody_buttons = []
        note_names = ["C5","B4","A#4","A4","G#4","G4","F#4","F4","E4","D#4","D4","C#4"]
        melody_frame = ttk.LabelFrame(pattern_frame, text="🎶 Melody Roll", padding=5)
        melody_frame.pack(fill=tk.X, pady=(10, 5))
        for r, note_name in enumerate(note_names):
            m_row = ttk.Frame(melody_frame)
            m_row.pack(fill=tk.X, pady=1)
            ttk.Label(m_row, text=note_name, width=4).pack(side=tk.LEFT)
            self.melody_buttons.append([])
            for c in range(16):
                btn = tk.Button(
                    m_row,
                    text="●" if self.melody_grid[r][c] else "○",
                    width=2,
                    height=1,
                    font=("Arial", 8),
                    bg="#673AB7" if self.melody_grid[r][c] else "gray80",
                    fg="white",
                    relief=tk.FLAT,
                    command=lambda row=r, col=c: self._toggle_melody(row, col)
                )
                btn.pack(side=tk.LEFT, padx=1)
                self.melody_buttons[r].append(btn)

        # Drum source selector
        source_frame = ttk.Frame(parent)
        source_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(source_frame, text="Drum Source:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.drum_source_var = tk.StringVar(value="Synth")
        ttk.Combobox(source_frame,
                     textvariable=self.drum_source_var,
                     values=["Synth", "HQ Samples"],
                     state="readonly",
                     width=12).pack(side=tk.LEFT)
    
    def _create_playback_controls(self, parent):
        """Create playback and export controls."""
        playback_frame = ttk.LabelFrame(parent, text="🎧 Playback & Export", padding=10)
        playback_frame.pack(fill=tk.X)
        
        # Status label
        self.status_label = ttk.Label(
            playback_frame,
            text="Ready to generate beats!",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            playback_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(playback_frame)
        button_frame.pack()
        
        self.play_btn = ttk.Button(
            button_frame,
            text="▶️ Play",
            command=self._play_beat,
            bootstyle="primary",
            state=tk.DISABLED,
            width=12
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self._stop_beat,
            state=tk.DISABLED,
            width=12
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Save WAV",
            command=self._save_beat,
            bootstyle="info",
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📤 Export Project",
            command=self._export_project,
            bootstyle="warning",
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Effects controls
        effects_frame = ttk.Frame(playback_frame)
        effects_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(effects_frame, text="Effects:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.reverb_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(effects_frame, text="Reverb", variable=self.reverb_var).pack(side=tk.LEFT, padx=5)
        
        self.compression_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(effects_frame, text="Compression", variable=self.compression_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(effects_frame, text="Master Volume:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        self.volume_var = tk.DoubleVar(value=0.8)
        volume_scale = ttk.Scale(
            effects_frame,
            from_=0.0,
            to=1.0,
            variable=self.volume_var,
            length=100,
            orient=tk.HORIZONTAL
        )
        volume_scale.pack(side=tk.LEFT)
    
    # ============================================================================
    # FUNCTIONALITY METHODS
    # ============================================================================
    
    def _import_from_lyric_lab(self):
        """Import lyrics from the Lyric Lab tab."""
        try:
            if hasattr(self.parent_gui, 'lyric_editor'):
                lyrics = self.parent_gui.lyric_editor.get("1.0", tk.END).strip()
                if lyrics:
                    self.beat_lyrics_text.delete("1.0", tk.END)
                    self.beat_lyrics_text.insert("1.0", lyrics)
                    self.status_label.config(text="✅ Lyrics imported from Lyric Lab!")
                else:
                    messagebox.showwarning("No Lyrics", "No lyrics found in Lyric Lab!")
            else:
                messagebox.showinfo("Import", "Switch to Lyric Lab tab and create some lyrics first!")
        except Exception as e:
            logger.error(f"Failed to import lyrics: {e}")
            messagebox.showerror("Import Error", f"Failed to import lyrics: {str(e)}")
    
    def _analyze_lyrics_mood(self):
        """Analyze lyrics mood and adjust settings."""
        lyrics = self.beat_lyrics_text.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            # Use the engine's mood analysis
            params = self.engine.analyze_lyrics_mood(lyrics)
            
            # Update UI with suggested parameters
            self.bpm_var.set(params['tempo'])
            self.scale_var.set(params['scale'].name)
            self.pattern_var.set(params['drum_pattern'])
            
            self.status_label.config(text=f"🎯 Mood analyzed! Suggested: {params['tempo']} BPM, {params['scale'].name} scale")
            
        except Exception as e:
            logger.error(f"Mood analysis failed: {e}")
            self.status_label.config(text="❌ Mood analysis failed")
    
    def _on_preset_change(self, event=None):
        """Handle preset selection change."""
        preset_name = self.preset_var.get()
        if preset_name != "Custom" and preset_name in self.preset_manager.presets:
            preset = self.preset_manager.presets[preset_name]
            
            # Apply preset settings
            if 'tempo' in preset:
                self.bpm_var.set(preset['tempo'])
            if 'drum_pattern' in preset:
                self.pattern_var.set(preset['drum_pattern'])
            if 'scale' in preset:
                self.scale_var.set(preset['scale'].upper())
            
            self.status_label.config(text=f"✅ Loaded preset: {preset_name}")
    
    def _toggle_pattern(self, instrument: str, index: int, color: str):
        """Toggle a beat in the pattern."""
        self.patterns[instrument][index] = 1 - self.patterns[instrument][index]
        btn = self.pattern_buttons[instrument][index]
        is_active = self.patterns[instrument][index]

        btn.config(
            text="●" if is_active else "○",
            bg=color if is_active else "gray80"
        )

        # Play preview sound when activating a step
        try:
            if is_active and self.engine and hasattr(self.engine, 'preview_drum'):
                if self.drum_source_var.get() == "HQ Samples" and instrument in self._sample_cache:
                    self._sample_cache[instrument].play()
                else:
                    self.engine.preview_drum(instrument)
        except Exception as e:
            logger.debug(f"Preview error: {e}")

    def _convert_pattern_to_notes(self, channel: str) -> List[Note]:
        """Convert UI pattern to Note objects."""
        notes = []
        
        # Map UI patterns to drum sounds
        drum_mapping = {
            'kick': 36,  # MIDI kick drum
            'snare': 38,  # MIDI snare
            'hihat': 42,  # MIDI closed hi-hat
            'openhat': 46,  # MIDI open hi-hat
            'clap': 39,  # MIDI hand clap
            'bass808': 35,  # Acoustic bass drum (808 sub)
            'perc': 75  # Generic percussion sample
        }
        
        for instrument, pattern in self.patterns.items():
            if instrument in drum_mapping:
                for i, active in enumerate(pattern):
                    if active:
                        notes.append(Note(
                            pitch=drum_mapping[instrument],
                            velocity=0.8,
                            duration=0.1,
                            start_time=i * 0.25  # 16th notes
                        ))
        
        return notes

    def _toggle_melody(self, row: int, col: int):
        """Toggle a note in the melody roll grid."""
        try:
            self.melody_grid[row][col] = 1 - self.melody_grid[row][col]
            btn = self.melody_buttons[row][col]
            active = self.melody_grid[row][col]
            btn.config(text="●" if active else "○", bg="#673AB7" if active else "gray80")
        except Exception as e:
            logger.debug(f"Melody toggle error: {e}")

    def _convert_melody_to_notes(self) -> List[Note]:
        """Convert the melody roll grid into Note objects for synthesis."""
        notes: List[Note] = []
        base_pitch = 72  # MIDI C5 for top row
        for row_idx, row in enumerate(self.melody_grid):
            for col_idx, active in enumerate(row):
                if active:
                    pitch = base_pitch - row_idx
                    start_time = col_idx * 0.25  # 16th-note grid
                    notes.append(Note(pitch, 0.9, 0.25, start_time))
        return notes

    def _update_progress(self, value: float, message: str):
        """Thread-safe progress bar + status update."""
        def _apply():
            try:
                self.progress_var.set(value)
                self.status_label.config(text=message)
            except Exception as e:
                logger.debug(f"Progress update error: {e}")
        # Run on main thread via Tk's event loop
        root = getattr(self.parent_gui, 'root', None) if hasattr(self, 'parent_gui') else None
        if root and callable(getattr(root, 'after', None)):
            root.after(0, _apply)
        else:
            # Fallback (non-GUI context) – just call directly
            _apply()
    
    def _play_beat(self):
        """Play the generated beat."""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            messagebox.showwarning("No Beat", "Generate a beat first!")
            return
        
        try:
            self.engine.play_audio(self.current_beat)
            self.play_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="🎵 Playing beat...")
            self.is_playing = True
            
            # Re-enable play button after playback
            def on_playback_complete():
                self.play_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.status_label.config(text="✅ Playback complete")
                self.is_playing = False
            
            # Check playback status in background
            thread = threading.Thread(target=self._monitor_playback, args=(on_playback_complete,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Playback error: {e}")
            messagebox.showerror("Playback Error", f"Failed to play beat: {str(e)}")
    
    def _monitor_playback(self, callback):
        """Monitor playback status."""
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
        callback()
    
    def _stop_beat(self):
        """Stop beat playback."""
        try:
            self.engine.stop_playback()
            self.play_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="⏹️ Stopped")
            self.is_playing = False
        except Exception as e:
            logger.error(f"Stop error: {e}")
    
    def _save_beat(self):
        """Save the beat as WAV file."""
        if self.current_beat is None:
            messagebox.showwarning("No Beat", "Generate a beat first!")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            title="Save Beat As"
        )
        
        if filename:
            try:
                self.engine.save_audio(self.current_beat, filename)
                messagebox.showinfo("Success", f"Beat saved to {filename}")
                self.status_label.config(text=f"💾 Saved: {os.path.basename(filename)}")
            except Exception as e:
                logger.error(f"Save error: {e}")
                messagebox.showerror("Save Error", f"Failed to save beat: {str(e)}")
    
    def _export_project(self):
        """Export complete beat project."""
        if self.current_beat is None:
            messagebox.showwarning("No Beat", "Generate a beat first!")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Beat Project"
        )
        
        if filename:
            try:
                project_data = {
                    "lyrics": self.beat_lyrics_text.get("1.0", tk.END).strip(),
                    "settings": {
                        "bpm": self.bpm_var.get(),
                        "pattern": self.pattern_var.get(),
                        "scale": self.scale_var.get(),
                        "energy": self.energy_var.get(),
                        "preset": self.preset_var.get()
                    },
                    "patterns": self.patterns,
                    "effects": {
                        "reverb": self.reverb_var.get(),
                        "compression": self.compression_var.get(),
                        "volume": self.volume_var.get()
                    },
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "2.1"
                    }
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Project exported to {filename}")
                self.status_label.config(text=f"📤 Exported: {os.path.basename(filename)}")
                
            except Exception as e:
                logger.error(f"Export error: {e}")
                messagebox.showerror("Export Error", f"Failed to export project: {str(e)}")
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    def create_beat_from_lyrics(self, lyrics: str, preset_name: Optional[str] = None) -> Optional[np.ndarray]:
        """Create a beat from lyrics - public API method."""
        if not self.is_available():
            logger.warning("Beat Studio not available")
            return None
        
        try:
            # Apply preset if specified
            if preset_name and preset_name in self.preset_manager.presets:
                preset = self.preset_manager.presets[preset_name]
                # Apply preset parameters
                tempo = preset.get('tempo', 120)
                pattern = preset.get('drum_pattern', 'basic')
            else:
                tempo = 120
                pattern = 'basic'
            
            # Generate beat
            self.engine.sequencer.tempo = tempo
            audio_data = self.engine.generate_beat_from_lyrics(lyrics, duration=16.0)
            
            # Apply default effects
            audio_data = self.effects_processor.reverb(audio_data, 0.3)
            audio_data = self.effects_processor.compressor(audio_data)
            
            self.current_beat = audio_data
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to create beat: {e}")
            return None
    
    def play_current_beat(self) -> bool:
        """Play the current beat."""
        if self.current_beat is not None:
            try:
                self.engine.play_audio(self.current_beat)
                return True
            except Exception as e:
                logger.error(f"Playback error: {e}")
                return False
        return False
    
    def stop_beat(self):
        """Stop beat playback."""
        try:
            self.engine.stop_playback()
        except Exception as e:
            logger.error(f"Stop error: {e}")
    
    def save_beat(self, filename: str) -> bool:
        """Save the current beat to file."""
        if self.current_beat is not None:
            try:
                self.engine.save_audio(self.current_beat, filename)
                return True
            except Exception as e:
                logger.error(f"Save error: {e}")
                return False
        return False


# ----------------------------------------------------------------------------
# Stand-alone wrapper for Generate Beat button
# ----------------------------------------------------------------------------

def _generate_beat(self):
    """Handle Generate Beat button click – starts background generation."""
    lyrics = self.beat_lyrics_text.get("1.0", tk.END).strip()
    if not lyrics:
        messagebox.showwarning("No Lyrics", "Enter some lyrics to generate a beat!")
        return

    # Disable controls while generating
    self.generate_btn.config(state=tk.DISABLED, text="🎵 Generating...")
    self.progress_var.set(0)
    self.status_label.config(text="🎵 Generating your beat...")

    # Run generation in background thread
    thread = threading.Thread(target=self._generate_beat_thread, args=(lyrics,))
    thread.daemon = True
    thread.start()

# ----------------------------------------------------------------------------
# Stand-alone background thread for beat generation (module level)
# ----------------------------------------------------------------------------

def _generate_beat_thread(self, lyrics: str):
    """Background thread that carries out beat generation end-to-end."""
    try:
        self._update_progress(20, "Analyzing lyrics…")
        # Tempo
        self.engine.sequencer.tempo = self.bpm_var.get()

        # Apply pattern from UI
        drum_pattern = Pattern(
            notes=self._convert_pattern_to_notes('drums'),
            length=4.0,
            channel='drums'
        )
        self.engine.sequencer.add_pattern('drums', drum_pattern)

        self._update_progress(40, "Generating beat…")
        audio_data = self.engine.generate_beat_from_lyrics(lyrics, duration=16.0)

        self._update_progress(60, "Applying effects…")
        if getattr(self, 'reverb_var', None) and self.reverb_var.get():
            audio_data = self.effects_processor.reverb(audio_data, 0.3)
        if getattr(self, 'compression_var', None) and self.compression_var.get():
            audio_data = self.effects_processor.compressor(audio_data)
        audio_data *= getattr(self, 'volume_var', tk.DoubleVar(value=1.0)).get()

        self._update_progress(80, "Finalising…")
        tmp = tempfile.mktemp(suffix='.wav')
        self.engine.save_audio(audio_data, tmp)
        self.current_audio_file = tmp
        self.current_beat = audio_data

        self._update_progress(100, "✅ Beat generated successfully!")
        self.play_btn.config(state=tk.NORMAL)
    except Exception as e:
        logger.error(f"Beat generation failed: {e}")
        self.status_label.config(text=f"❌ Generation failed: {str(e)}")
    finally:
        self.generate_btn.config(state=tk.NORMAL, text="🎵 Generate Beat")

# ----------------------------------------------------------------------------
# Stand-alone wrapper for Full Song button
# ----------------------------------------------------------------------------

def _generate_full_song(self):
    """Handle Full Song button click – starts background generation."""
    lyrics = self.beat_lyrics_text.get("1.0", tk.END).strip()
    if not lyrics:
        messagebox.showwarning("No Lyrics", "Enter lyrics to generate a full song!")
        return

    # Disable controls while generating
    self.full_song_btn.config(state=tk.DISABLED, text="🎶 Generating...")
    self.progress_var.set(0)
    self.status_label.config(text="🎶 Generating full song...")

    thread = threading.Thread(target=self._generate_full_song_thread, args=(lyrics,))
    thread.daemon = True
    thread.start()

# ----------------------------------------------------------------------------
# Stand-alone background thread for full song generation
# ----------------------------------------------------------------------------

def _generate_full_song_thread(self, lyrics: str):
    """Background thread that generates a complete 3-minute song."""
    try:
        self._update_progress(20, "Analyzing lyrics…")
        # Tempo
        self.engine.sequencer.tempo = self.bpm_var.get()

        # Apply pattern from UI (optional but keeps user drums)
        drum_pattern = Pattern(
            notes=self._convert_pattern_to_notes('drums'),
            length=4.0,
            channel='drums'
        )
        self.engine.sequencer.add_pattern('drums', drum_pattern)

        self._update_progress(40, "Generating full song… (this may take a while)")
        audio_data = self.engine.generate_full_song_from_lyrics(lyrics, length_seconds=180.0)

        self._update_progress(70, "Applying effects…")
        if getattr(self, 'reverb_var', None) and self.reverb_var.get():
            audio_data = self.effects_processor.reverb(audio_data, 0.3)
        if getattr(self, 'compression_var', None) and self.compression_var.get():
            audio_data = self.effects_processor.compressor(audio_data)
        audio_data *= getattr(self, 'volume_var', tk.DoubleVar(value=1.0)).get()

        self._update_progress(90, "Finalising…")
        tmp = tempfile.mktemp(suffix='.wav')
        self.engine.save_audio(audio_data, tmp)
        self.current_audio_file = tmp
        self.current_beat = audio_data  # reuse for playback

        self._update_progress(100, "✅ Full song generated!")
        self.play_btn.config(state=tk.NORMAL)
    except Exception as e:
        logger.error(f"Full song generation failed: {e}")
        self.status_label.config(text=f"❌ Song generation failed: {str(e)}")
    finally:
        self.full_song_btn.config(state=tk.NORMAL, text="🎶 Full Song (3 min)")

# ----------------------------------------------------------------------------
# Stand-alone wrapper for Instrumental (MusicGen) button
# ----------------------------------------------------------------------------

def _generate_instrumental(self):
    """Handle Instrumental (Pro) button click – starts MusicGen generation."""
    lyrics = self.beat_lyrics_text.get("1.0", tk.END).strip()
    if not lyrics:
        messagebox.showwarning("No Lyrics", "Enter some lyrics to generate an instrumental!")
        return

    # Disable controls while generating
    self.instrumental_btn.config(state=tk.DISABLED, text="🌟 Generating…")
    self.progress_var.set(0)
    self.status_label.config(text="🌟 Generating instrumental…")

    thread = threading.Thread(target=self._generate_instrumental_thread, args=(lyrics,))
    thread.daemon = True
    thread.start()

# ----------------------------------------------------------------------------
# Stand-alone background thread for MusicGen instrumental generation
# ----------------------------------------------------------------------------

def _generate_instrumental_thread(self, lyrics: str):
    try:
        self._update_progress(10, "Analyzing lyrics…")
        from lyric_analyzer import LyricAnalyzer  # local heuristic analyser
        analysis = LyricAnalyzer().analyze(lyrics)

        prompt = (
            f"Instrumental, no vocals. Style: {analysis['drum_pattern']} beat. "
            f"Mood: {'positive' if analysis['sentiment']>=0 else 'sad'}. "
            f"Tempo: {analysis['tempo']} BPM."
        )

        self._update_progress(30, "Running MusicGen…")
        from musicgen_backend import generate_instrumental
        wav_path = generate_instrumental(lyrics, prompt, duration=30)

        self._update_progress(70, "Loading audio…")
        import numpy as np
        from scipy.io import wavfile
        sr, audio_data = wavfile.read(wav_path)
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32) / np.iinfo(audio_data.dtype).max

        # Apply master volume
        audio_data *= getattr(self, 'volume_var', tk.DoubleVar(value=1.0)).get()

        self.current_audio_file = wav_path
        self.current_beat = audio_data

        self._update_progress(100, "✅ Instrumental generated!")
        self.play_btn.config(state=tk.NORMAL)
    except Exception as e:
        logger.error(f"Instrumental generation failed: {e}")
        self.status_label.config(text=f"❌ Instrumental generation failed: {str(e)}")
    finally:
        self.instrumental_btn.config(state=tk.NORMAL, text="🌟 Instrumental (Pro)")
        self.generate_btn.config(state=tk.NORMAL)
        self.full_song_btn.config(state=tk.NORMAL)

# ----------------------------------------------------------------------------
# Stand-alone helper to save the beat
# ----------------------------------------------------------------------------

def _save_beat(self):
    """Prompt user to save current beat as WAV."""
    if self.current_beat is None:
        messagebox.showwarning("No Beat", "Generate a beat first!")
        return

    from tkinter import filedialog
    filename = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        title="Save Beat As"
    )
    if filename:
        try:
            self.engine.save_audio(self.current_beat, filename)
            messagebox.showinfo("Success", f"Beat saved to {filename}")
            self.status_label.config(text=f"💾 Saved: {os.path.basename(filename)}")
        except Exception as e:
            logger.error(f"Save error: {e}")
            messagebox.showerror("Save Error", str(e))

# ----------------------------------------------------------------------------
# Stand-alone helper to export the full project (lyrics + settings + wav path)
# ----------------------------------------------------------------------------

def _export_project(self):
    """Export the current project (lyrics, settings, and beat file) to JSON."""
    if self.current_audio_file is None or not os.path.exists(self.current_audio_file):
        messagebox.showwarning("No Beat", "Generate a beat first!")
        return

    from tkinter import filedialog
    filename = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        title="Export Beat Project"
    )
    if not filename:
        return

    try:
        project = {
            "lyrics": self.beat_lyrics_text.get("1.0", tk.END).strip() if hasattr(self, 'beat_lyrics_text') else "",
            "bpm": getattr(self, 'bpm_var', tk.IntVar(value=120)).get(),
            "volume": getattr(self, 'volume_var', tk.DoubleVar(value=1.0)).get(),
            "reverb": getattr(self, 'reverb_var', tk.BooleanVar(value=False)).get() if hasattr(self, 'reverb_var') else False,
            "compression": getattr(self, 'compression_var', tk.BooleanVar(value=False)).get() if hasattr(self, 'compression_var') else False,
            "audio_file": self.current_audio_file
        }
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(project, fp, indent=2)
        messagebox.showinfo("Success", f"Project exported to {filename}")
        self.status_label.config(text=f"📤 Exported project: {os.path.basename(filename)}")
    except Exception as e:
        logger.error(f"Export error: {e}")
        messagebox.showerror("Export Error", str(e))

# ----------------------------------------------------------------------------
# Stand-alone wrapper for Stop Beat button
# ----------------------------------------------------------------------------

def _stop_beat(self):
    """Handle Stop button click – stops playback."""
    try:
        self.engine.stop_playback()
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="⏹️ Stopped")
        self.is_playing = False
    except Exception as e:
        logger.error(f"Stop error: {e}")

# ----------------------------------------------------------------------------
# Stand-alone wrapper for Suggest Beat button
# ----------------------------------------------------------------------------

def _suggest_beat(self):
    """Analyze lyrics with BeatAdvisor and apply suggestions to the UI."""
    lyrics = self.beat_lyrics_text.get("1.0", tk.END).strip()
    if not lyrics:
        messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
        return
    try:
        suggestion = beat_advisor.suggest_beat(lyrics)
        # Update controls
        self.bpm_var.set(suggestion.get('recommended_bpm', self.bpm_var.get()))
        if isinstance(suggestion.get('drum_pattern'), str):
            self.pattern_var.set(suggestion['drum_pattern'])
        # Instrument preset handling
        instr = suggestion.get('instrument_preset')
        if instr and instr in self.preset_manager.presets:
            self.preset_var.set(instr)
        else:
            self.preset_var.set('Custom')
        # Show advice info
        self.status_label.config(text=(
            f"💡 Suggested {suggestion.get('recommended_bpm')} BPM, "
            f"pattern: {suggestion.get('drum_pattern')}, "
            f"preset: {instr}"
        ))
    except Exception as e:
        logger.error(f"Suggestion failed: {e}")
        self.status_label.config(text="❌ Suggestion failed")

# ----------------------------------------------------------------------------
# Internal helper methods for drum samples
# ----------------------------------------------------------------------------
def _load_drum_samples(self):
    """Load HQ drum samples into cache if files exist."""
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error as e:
            # Audio device might be unavailable (e.g. headless VM). Continue without samples.
            logger.warning(f"Pygame mixer init failed – HQ drum samples disabled: {e}")
            return
    mapping = {
        'kick': 'kick.wav',
        'snare': 'snare.wav',
        'hihat': 'hihat.wav',
        'openhat': 'openhat.wav',
        'clap': 'clap.wav',
        'bass808': '808.wav',
        'perc': 'perc_loop.wav',
    }
    for inst, fname in mapping.items():
        path = os.path.join(self.DRUM_SAMPLE_DIR, fname)
        if os.path.exists(path):
            try:
                self._sample_cache[inst] = pygame.mixer.Sound(path)
            except Exception as e:
                logger.debug(f"Could not load sample {path}: {e}")

# ============================================================================
# ATTACH STANDALONE FUNCTIONS TO CLASS (hot-fix for misplaced indentation)
# ============================================================================

# List of helper functions that were defined at module level but intended to be
# instance methods.  This wiring makes them accessible via the class while we
# refactor the file.
_missing_methods = [
    '_update_progress',
    '_play_beat',
    '_generate_beat_thread',
    '_generate_full_song_thread',
    '_generate_full_song',
    '_generate_beat',
    '_stop_beat',
    '_convert_pattern_to_notes',
    '_toggle_pattern',
    '_create_generation_controls',
    '_create_playback_controls',
    '_create_lyrics_section',
    '_create_pattern_editor',
    '_import_from_lyric_lab',
    '_analyze_lyrics_mood',
    '_on_preset_change',
    '_stop_beat',
    'is_available',
    'add_beat_studio_tab',
    '_setup_beat_studio_tab',
    'play_current_beat',
    'save_beat',
    '_export_project',
    '_monitor_playback',
    'create_beat_from_lyrics',
    '_save_beat',
    '_load_drum_samples'
 ]
# Register newly added helper methods
_missing_methods += ['_toggle_melody', '_convert_melody_to_notes', '_generate_instrumental', '_generate_instrumental_thread']

for _m in _missing_methods:
    if _m in globals() and not hasattr(BeatStudioIntegration, _m):
        setattr(BeatStudioIntegration, _m, globals()[_m])

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Create singleton instance
beat_studio_integration = BeatStudioIntegration()

# -----------------------------------------------------------
# Optionally enhance with advanced features (melody/chords,
# side-chain compression, DAW export, etc.)
# -----------------------------------------------------------
try:
    from beat_studio_advanced import enhance_beat_studio_integration  # type: ignore
    beat_studio_integration = enhance_beat_studio_integration(beat_studio_integration)
    logger.info("✨ Beat Studio advanced features activated!")
except ImportError:
    logger.debug("beat_studio_advanced module not found – using base feature set")
except Exception as _adv_err:
    logger.warning(f"Advanced Beat Studio enhancement failed: {_adv_err}")

# Export the integration instance and availability flag
__all__ = ['beat_studio_integration', 'BEAT_STUDIO_AVAILABLE']