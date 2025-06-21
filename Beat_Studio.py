"""
beat_studio_integration.py - Professional Beat Studio Integration for CodedSwitch
This module integrates the advanced beat generation features into your existing GUI
"""

import os
import sys
import logging
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
from tkinter import ttk, messagebox
import ttkbootstrap as ttk

# Set up logging
logger = logging.getLogger(__name__)

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
except ImportError as e:
    logger.warning(f"⚠️ Beat Studio modules not available: {e}")
    BEAT_STUDIO_AVAILABLE = False
    
    # Create minimal fallback classes
    class BeatStudioEngine:
        pass
    
    class PresetManager:
        def __init__(self):
            self.presets = {}
    
    class AudioConstants:
        SAMPLE_RATE = 44100
        CHANNELS = 2
        BUFFER_SIZE = 512

# ============================================================================
# BEAT STUDIO INTEGRATION CLASS
# ============================================================================

class BeatStudioIntegration:
    """Integrates professional beat generation into CodedSwitch GUI."""
    
    def __init__(self):
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
        """Set up the complete Beat Studio interface."""
        main_frame = ttk.Frame(parent, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
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
            'openhat': [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1]
        }
        
        self.pattern_buttons = {}
        
        # Create pattern rows
        instruments = [
            ("🥁 Kick", "kick", "#FF5722"),
            ("🥁 Snare", "snare", "#2196F3"),
            ("🎩 Hi-Hat", "hihat", "#4CAF50"),
            ("🎩 Open Hat", "openhat", "#FFC107")
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
    
    def _generate_beat(self):
        """Generate beat based on current settings."""
        lyrics = self.beat_lyrics_text.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics to generate a beat!")
            return
        
        # Disable controls during generation
        self.generate_btn.config(state=tk.DISABLED, text="🎵 Generating...")
        self.progress_var.set(0)
        self.status_label.config(text="🎵 Generating your beat...")
        
        # Generate in background thread
        thread = threading.Thread(target=self._generate_beat_thread, args=(lyrics,))
        thread.daemon = True
        thread.start()
    
    def _generate_beat_thread(self, lyrics: str):
        """Background thread for beat generation."""
        try:
            # Update progress
            self._update_progress(20, "Analyzing lyrics...")
            
            # Set up parameters
            self.engine.sequencer.tempo = self.bpm_var.get()
            
            # Apply custom patterns
            drum_pattern = Pattern(
                notes=self._convert_pattern_to_notes('drums'),
                length=4.0,
                channel='drums'
            )
            self.engine.sequencer.add_pattern('drums', drum_pattern)
            
            self._update_progress(40, "Generating beat...")
            
            # Generate the beat
            audio_data = self.engine.generate_beat_from_lyrics(lyrics, duration=16.0)
            
            self._update_progress(60, "Applying effects...")
            
            # Apply effects
            if self.reverb_var.get():
                audio_data = self.effects_processor.reverb(audio_data, 0.3)
            
            if self.compression_var.get():
                audio_data = self.effects_processor.compressor(audio_data)
            
            # Apply master volume
            audio_data *= self.volume_var.get()
            
            self._update_progress(80, "Finalizing...")
            
            # Save to temp file
            temp_file = tempfile.mktemp(suffix='.wav')
            self.engine.save_audio(audio_data, temp_file)
            self.current_audio_file = temp_file
            self.current_beat = audio_data
            
            self._update_progress(100, "✅ Beat generated successfully!")
            
            # Enable playback controls
            self.play_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            logger.error(f"Beat generation failed: {e}")
            self.status_label.config(text=f"❌ Generation failed: {str(e)}")
        finally:
            self.generate_btn.config(state=tk.NORMAL, text="🎵 Generate Beat")
    
    def _convert_pattern_to_notes(self, channel: str) -> List[Note]:
        """Convert UI pattern to Note objects."""
        notes = []
        
        # Map UI patterns to drum sounds
        drum_mapping = {
            'kick': 36,  # MIDI kick drum
            'snare': 38,  # MIDI snare
            'hihat': 42,  # MIDI closed hi-hat
            'openhat': 46  # MIDI open hi-hat
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
    
    def _update_progress(self, value: float, message: str):
        """Update progress bar and status."""
        self.progress_var.set(value)
        self.status_label.config(text=message)
        # Force UI update
        if hasattr(self, 'parent_gui') and hasattr(self.parent_gui, 'root'):
            self.parent_gui.root.update_idletasks()
    
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
        if not self.current_beat is not None:
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
        if not self.current_beat is not None:
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

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Create singleton instance
beat_studio_integration = BeatStudioIntegration()

# Export the integration instance and availability flag
__all__ = ['beat_studio_integration', 'BEAT_STUDIO_AVAILABLE']