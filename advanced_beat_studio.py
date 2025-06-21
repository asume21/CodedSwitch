"""
Advanced Beat Studio for CodedSwitch
Professional-grade music production environment with AI integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
import numpy as np
import threading
import time
import logging
from datetime import datetime
import json
import math

logger = logging.getLogger(__name__)

class AdvancedBeatStudio:
    """Professional Beat Studio with advanced editing capabilities."""
    
    def __init__(self, parent, ai_interface=None):
        self.parent = parent
        self.ai = ai_interface
        
        # Audio engine initialization
        self.sample_rate = 44100
        self.buffer_size = 512
        self.bpm = 120
        self.swing = 0.0
        self.master_volume = 0.8
        
        # Track data
        self.tracks = {
            'kick': {'pattern': [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0], 'volume': 0.8, 'pitch': 60, 'effects': {}},
            'snare': {'pattern': [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0], 'volume': 0.7, 'pitch': 200, 'effects': {}},
            'hihat': {'pattern': [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0], 'volume': 0.5, 'pitch': 5000, 'effects': {}},
            'openhat': {'pattern': [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1], 'volume': 0.6, 'pitch': 4000, 'effects': {}},
            'bass': {'pattern': [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0], 'volume': 0.7, 'pitch': 80, 'effects': {}},
            'lead': {'pattern': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'volume': 0.6, 'pitch': 440, 'effects': {}},
            'pad': {'pattern': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'volume': 0.4, 'pitch': 220, 'effects': {}},
            'fx': {'pattern': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'volume': 0.5, 'pitch': 1000, 'effects': {}}
        }
        
        # Melody system
        self.melody_tracks = {
            'melody1': {'notes': [], 'volume': 0.7, 'instrument': 'sine'},
            'melody2': {'notes': [], 'volume': 0.5, 'instrument': 'square'},
            'bass_melody': {'notes': [], 'volume': 0.8, 'instrument': 'sawtooth'}
        }
        
        # Music theory
        self.scales = {
            'Major': [0, 2, 4, 5, 7, 9, 11],
            'Minor': [0, 2, 3, 5, 7, 8, 10],
            'Dorian': [0, 2, 3, 5, 7, 9, 10],
            'Pentatonic': [0, 2, 4, 7, 9],
            'Blues': [0, 3, 5, 6, 7, 10],
            'Harmonic Minor': [0, 2, 3, 5, 7, 8, 11],
            'Phrygian': [0, 1, 3, 5, 7, 8, 10]
        }
        
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Playback state
        self.is_playing = False
        self.current_step = 0
        self.loop_enabled = True
        self.recording = False
        
        # Audio synthesis
        self.oscillators = {}
        self.effects_chain = {}
        
        # Initialize audio (with fallback)
        self._init_audio_engine()
        
        # Create UI
        self.create_studio_interface()
    
    def _init_audio_engine(self):
        """Initialize audio engine with graceful fallback."""
        try:
            import pygame
            pygame.mixer.pre_init(frequency=self.sample_rate, size=-16, channels=2, buffer=self.buffer_size)
            pygame.mixer.init()
            self.audio_available = True
            logger.info("Audio engine initialized successfully")
        except ImportError:
            self.audio_available = False
            logger.warning("Audio engine not available - pygame not installed")
        except Exception as e:
            self.audio_available = False
            logger.error(f"Audio engine initialization failed: {e}")
    
    def create_studio_interface(self):
        """Create the main Beat Studio interface."""
        self.window = tk.Toplevel()
        self.window.title("🎵 CodedSwitch Beat Studio Pro")
        self.window.geometry("1400x900")
        self.window.configure(bg='#1a1a1a')
        
        # Main container with dark theme
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_sequencer_tab()
        self._create_melody_editor_tab()
        self._create_mixer_tab()
        self._create_effects_tab()
        self._create_ai_assistant_tab()
        
        # Transport controls at bottom
        self._create_transport_controls(main_frame)
        
        logger.info("Advanced Beat Studio interface created")
    
    def _create_sequencer_tab(self):
        """Create the main sequencer interface."""
        seq_frame = ttk.Frame(self.notebook)
        self.notebook.add(seq_frame, text="🥁 Sequencer")
        
        # Header controls
        header_frame = ttk.Frame(seq_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # BPM and time signature
        ttk.Label(header_frame, text="BPM:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.bpm_var = tk.IntVar(value=self.bpm)
        bpm_spin = ttk.Spinbox(header_frame, from_=60, to=200, textvariable=self.bpm_var, 
                              width=10, command=self._update_bpm)
        bpm_spin.pack(side=tk.LEFT, padx=(5, 20))
        
        # Swing control
        ttk.Label(header_frame, text="Swing:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.swing_var = tk.DoubleVar(value=self.swing)
        swing_scale = ttk.Scale(header_frame, from_=-0.3, to=0.3, variable=self.swing_var,
                               length=100, command=self._update_swing)
        swing_scale.pack(side=tk.LEFT, padx=(5, 20))
        
        # Pattern length
        ttk.Label(header_frame, text="Steps:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.steps_var = tk.IntVar(value=16)
        steps_combo = ttk.Combobox(header_frame, textvariable=self.steps_var, 
                                  values=[8, 16, 32, 64], width=8, state='readonly')
        steps_combo.pack(side=tk.LEFT, padx=(5, 20))
        steps_combo.bind('<<ComboboxSelected>>', self._update_pattern_length)
        
        # AI Generate button
        ai_gen_btn = ttk.Button(header_frame, text="🤖 AI Generate Beat", 
                               command=self._ai_generate_beat, bootstyle="success")
        ai_gen_btn.pack(side=tk.RIGHT, padx=5)
        
        # Pattern editor
        self._create_pattern_editor(seq_frame)
        
        # Pattern management
        self._create_pattern_management(seq_frame)
    
    def _create_pattern_editor(self, parent):
        """Create the advanced pattern editor."""
        editor_frame = ttk.LabelFrame(parent, text="🎛️ Pattern Editor", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create canvas for pattern grid
        canvas_frame = ttk.Frame(editor_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable canvas
        self.pattern_canvas = tk.Canvas(canvas_frame, bg='#2a2a2a', height=400)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.pattern_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.pattern_canvas.yview)
        
        self.pattern_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.pattern_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.pattern_canvas.bind('<Button-1>', self._on_pattern_click)
        self.pattern_canvas.bind('<B1-Motion>', self._on_pattern_drag)
        self.pattern_canvas.bind('<Button-3>', self._on_pattern_right_click)
        
        # Draw initial pattern
        self._draw_pattern_grid()
        
        # Track controls on the right
        self._create_track_controls(editor_frame)
    
    def _create_track_controls(self, parent):
        """Create individual track controls."""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Label(controls_frame, text="Track Controls", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.track_controls = {}
        
        for track_name in self.tracks.keys():
            track_frame = ttk.LabelFrame(controls_frame, text=track_name.title(), padding=5)
            track_frame.pack(fill=tk.X, pady=2)
            
            # Volume control
            vol_frame = ttk.Frame(track_frame)
            vol_frame.pack(fill=tk.X)
            ttk.Label(vol_frame, text="Vol:", width=4).pack(side=tk.LEFT)
            
            vol_var = tk.DoubleVar(value=self.tracks[track_name]['volume'])
            vol_scale = ttk.Scale(vol_frame, from_=0.0, to=1.0, variable=vol_var,
                                 length=80, command=lambda v, t=track_name: self._update_track_volume(t, v))
            vol_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Pitch control  
            pitch_frame = ttk.Frame(track_frame)
            pitch_frame.pack(fill=tk.X)
            ttk.Label(pitch_frame, text="Pitch:", width=4).pack(side=tk.LEFT)
            
            pitch_var = tk.DoubleVar(value=self.tracks[track_name]['pitch'])
            pitch_scale = ttk.Scale(pitch_frame, from_=20, to=2000, variable=pitch_var,
                                   length=80, command=lambda v, t=track_name: self._update_track_pitch(t, v))
            pitch_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Mute/Solo buttons
            btn_frame = ttk.Frame(track_frame)
            btn_frame.pack(fill=tk.X)
            
            mute_var = tk.BooleanVar()
            solo_var = tk.BooleanVar()
            
            ttk.Checkbutton(btn_frame, text="M", variable=mute_var, width=3).pack(side=tk.LEFT)
            ttk.Checkbutton(btn_frame, text="S", variable=solo_var, width=3).pack(side=tk.LEFT)
            
            self.track_controls[track_name] = {
                'volume': vol_var,
                'pitch': pitch_var,
                'mute': mute_var,
                'solo': solo_var
            }
    
    def _create_melody_editor_tab(self):
        """Create advanced melody editor."""
        melody_frame = ttk.Frame(self.notebook)
        self.notebook.add(melody_frame, text="🎹 Melody Editor")
        
        # Melody controls
        controls_frame = ttk.Frame(melody_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Key and scale selection
        ttk.Label(controls_frame, text="Key:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.key_var = tk.StringVar(value="C")
        key_combo = ttk.Combobox(controls_frame, textvariable=self.key_var, 
                                values=self.note_names, width=5, state='readonly')
        key_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(controls_frame, text="Scale:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.scale_var = tk.StringVar(value="Major")
        scale_combo = ttk.Combobox(controls_frame, textvariable=self.scale_var,
                                  values=list(self.scales.keys()), width=15, state='readonly')
        scale_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Melody generation
        ttk.Button(controls_frame, text="🎵 Generate Melody", 
                  command=self._generate_melody, bootstyle="success").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🎲 Random Melody", 
                  command=self._random_melody, bootstyle="info").pack(side=tk.LEFT, padx=5)
        
        # Piano roll editor
        self._create_piano_roll(melody_frame)
        
        # Melody track selector
        track_select_frame = ttk.Frame(melody_frame)
        track_select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(track_select_frame, text="Track:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.melody_track_var = tk.StringVar(value="melody1")
        track_combo = ttk.Combobox(track_select_frame, textvariable=self.melody_track_var,
                                  values=list(self.melody_tracks.keys()), width=15, state='readonly')
        track_combo.pack(side=tk.LEFT, padx=(5, 20))
        track_combo.bind('<<ComboboxSelected>>', self._switch_melody_track)
    
    def _create_piano_roll(self, parent):
        """Create piano roll editor for melodies."""
        piano_frame = ttk.LabelFrame(parent, text="🎹 Piano Roll", padding=10)
        piano_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create piano roll canvas
        self.piano_canvas = tk.Canvas(piano_frame, bg='#1a1a1a', height=300)
        
        # Scrollbars
        h_scroll_piano = ttk.Scrollbar(piano_frame, orient=tk.HORIZONTAL, command=self.piano_canvas.xview)
        v_scroll_piano = ttk.Scrollbar(piano_frame, orient=tk.VERTICAL, command=self.piano_canvas.yview)
        
        self.piano_canvas.configure(xscrollcommand=h_scroll_piano.set, yscrollcommand=v_scroll_piano.set)
        
        self.piano_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll_piano.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll_piano.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind piano roll events
        self.piano_canvas.bind('<Button-1>', self._on_piano_click)
        self.piano_canvas.bind('<B1-Motion>', self._on_piano_drag)
        self.piano_canvas.bind('<Button-3>', self._on_piano_right_click)
        
        # Draw piano roll
        self._draw_piano_roll()
    
    def _create_mixer_tab(self):
        """Create professional mixer interface."""
        mixer_frame = ttk.Frame(self.notebook)
        self.notebook.add(mixer_frame, text="🎚️ Mixer")
        
        # Master section
        master_frame = ttk.LabelFrame(mixer_frame, text="Master", padding=10)
        master_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Master volume
        ttk.Label(master_frame, text="Master Volume").pack()
        self.master_vol_var = tk.DoubleVar(value=self.master_volume)
        master_vol_scale = ttk.Scale(master_frame, from_=0.0, to=1.0, variable=self.master_vol_var,
                                    length=200, orient=tk.VERTICAL, command=self._update_master_volume)
        master_vol_scale.pack(pady=10)
        
        # Individual channel strips
        channels_frame = ttk.Frame(mixer_frame)
        channels_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._create_channel_strips(channels_frame)
    
    def _create_channel_strips(self, parent):
        """Create individual channel mixer strips."""
        for i, (track_name, track_data) in enumerate(self.tracks.items()):
            channel_frame = ttk.LabelFrame(parent, text=track_name.title(), padding=5)
            channel_frame.grid(row=0, column=i, sticky='nsew', padx=2)
            
            # EQ controls
            eq_frame = ttk.LabelFrame(channel_frame, text="EQ", padding=5)
            eq_frame.pack(fill=tk.X, pady=5)
            
            # High, Mid, Low EQ
            for eq_band in ['High', 'Mid', 'Low']:
                ttk.Label(eq_frame, text=eq_band, font=('Arial', 8)).pack()
                eq_var = tk.DoubleVar(value=0.0)
                eq_scale = ttk.Scale(eq_frame, from_=-12, to=12, variable=eq_var,
                                    length=80, orient=tk.VERTICAL)
                eq_scale.pack()
            
            # Send controls
            send_frame = ttk.LabelFrame(channel_frame, text="Sends", padding=5)
            send_frame.pack(fill=tk.X, pady=5)
            
            for send in ['Reverb', 'Delay']:
                ttk.Label(send_frame, text=send, font=('Arial', 8)).pack()
                send_var = tk.DoubleVar(value=0.0)
                send_scale = ttk.Scale(send_frame, from_=0.0, to=1.0, variable=send_var,
                                      length=60, orient=tk.VERTICAL)
                send_scale.pack()
            
            # Channel fader
            ttk.Label(channel_frame, text="Level", font=('Arial', 8)).pack()
            vol_var = tk.DoubleVar(value=track_data['volume'])
            vol_fader = ttk.Scale(channel_frame, from_=0.0, to=1.0, variable=vol_var,
                                 length=150, orient=tk.VERTICAL)
            vol_fader.pack(pady=10)
            
            # Mute/Solo
            btn_frame = ttk.Frame(channel_frame)
            btn_frame.pack()
            
            ttk.Button(btn_frame, text="M", width=3, bootstyle="danger").pack(pady=2)
            ttk.Button(btn_frame, text="S", width=3, bootstyle="warning").pack(pady=2)
        
        # Configure grid weights
        for i in range(len(self.tracks)):
            parent.columnconfigure(i, weight=1)
    
    def _create_effects_tab(self):
        """Create effects processing interface."""
        effects_frame = ttk.Frame(self.notebook)
        self.notebook.add(effects_frame, text="🔊 Effects")
        
        # Effects rack
        rack_frame = ttk.LabelFrame(effects_frame, text="Effects Rack", padding=10)
        rack_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Available effects
        effects_list = ['Reverb', 'Delay', 'Chorus', 'Distortion', 'Filter', 'Compressor', 'EQ']
        
        for i, effect in enumerate(effects_list):
            effect_frame = ttk.LabelFrame(rack_frame, text=effect, padding=5)
            effect_frame.grid(row=i//2, column=i%2, sticky='ew', padx=5, pady=5)
            
            # Effect enable
            enable_var = tk.BooleanVar()
            ttk.Checkbutton(effect_frame, text="Enable", variable=enable_var).pack(anchor=tk.W)
            
            # Effect parameters (simplified)
            for param in ['Amount', 'Time', 'Feedback']:
                param_frame = ttk.Frame(effect_frame)
                param_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(param_frame, text=f"{param}:", width=8).pack(side=tk.LEFT)
                param_var = tk.DoubleVar(value=0.5)
                ttk.Scale(param_frame, from_=0.0, to=1.0, variable=param_var,
                         length=100).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure grid
        rack_frame.columnconfigure(0, weight=1)
        rack_frame.columnconfigure(1, weight=1)
    
    def _create_ai_assistant_tab(self):
        """Create AI assistant for music production."""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🤖 AI Assistant")
        
        # AI controls
        controls_frame = ttk.Frame(ai_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="🎵 AI Music Assistant", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        # Quick actions
        actions_frame = ttk.LabelFrame(controls_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="🎵 Generate Full Beat", 
                  command=self._ai_full_beat, bootstyle="success").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="🎹 Generate Melody", 
                  command=self._ai_melody, bootstyle="info").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="🥁 Generate Drums", 
                  command=self._ai_drums, bootstyle="primary").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="🎸 Generate Bass", 
                  command=self._ai_bass, bootstyle="secondary").pack(side=tk.LEFT, padx=5)
        
        # Style selector
        style_frame = ttk.Frame(controls_frame)
        style_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(style_frame, text="Style:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.music_style_var = tk.StringVar(value="Hip-Hop")
        style_combo = ttk.Combobox(style_frame, textvariable=self.music_style_var,
                                  values=["Hip-Hop", "Electronic", "Rock", "Jazz", "Pop", "Ambient", "Trap", "House"],
                                  width=15, state='readonly')
        style_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Custom prompt
        prompt_frame = ttk.LabelFrame(ai_frame, text="Custom AI Prompt", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        from ttkbootstrap.scrolled import ScrolledText
        self.ai_prompt = ScrolledText(prompt_frame, height=5, wrap=tk.WORD)
        self.ai_prompt.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.ai_prompt.insert("1.0", "Describe the music you want to create...")
        
        ttk.Button(prompt_frame, text="🚀 Generate with AI", 
                  command=self._ai_custom_generation, bootstyle="success").pack()
        
        # AI suggestions display
        suggestions_frame = ttk.LabelFrame(ai_frame, text="AI Suggestions", padding=10)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.ai_suggestions = ScrolledText(suggestions_frame, height=8, wrap=tk.WORD, state='disabled')
        self.ai_suggestions.pack(fill=tk.BOTH, expand=True)
    
    def _create_transport_controls(self, parent):
        """Create transport controls (play, stop, record, etc.)."""
        transport_frame = ttk.Frame(parent)
        transport_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Playback controls
        play_frame = ttk.Frame(transport_frame)
        play_frame.pack(side=tk.LEFT)
        
        self.play_btn = ttk.Button(play_frame, text="▶️", command=self._toggle_playback, 
                                  bootstyle="success", width=4)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(play_frame, text="⏹", command=self._stop_playback, 
                  bootstyle="danger", width=4).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(play_frame, text="⏺", command=self._toggle_recording, 
                  bootstyle="warning", width=4).pack(side=tk.LEFT, padx=2)
        
        # Loop control
        self.loop_var = tk.BooleanVar(value=self.loop_enabled)
        ttk.Checkbutton(play_frame, text="🔄 Loop", variable=self.loop_var).pack(side=tk.LEFT, padx=10)
        
        # Position indicator
        position_frame = ttk.Frame(transport_frame)
        position_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        
        self.position_var = tk.DoubleVar()
        self.position_scale = ttk.Scale(position_frame, from_=0, to=100, variable=self.position_var,
                                       length=300, command=self._seek_position)
        self.position_scale.pack(fill=tk.X)
        
        # File operations
        file_frame = ttk.Frame(transport_frame)
        file_frame.pack(side=tk.RIGHT)
        
        ttk.Button(file_frame, text="💾 Save Project", command=self._save_project, 
                  bootstyle="info-outline").pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="📂 Load Project", command=self._load_project, 
                  bootstyle="info-outline").pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="📤 Export WAV", command=self._export_wav, 
                  bootstyle="primary").pack(side=tk.LEFT, padx=2)
    
    def _draw_pattern_grid(self):
        """Draw the pattern sequencer grid."""
        self.pattern_canvas.delete("all")
        
        steps = self.steps_var.get()
        track_names = list(self.tracks.keys())
        
        # Grid dimensions
        step_width = 40
        track_height = 30
        
        # Draw grid lines and step buttons
        for step in range(steps):
            x = step * step_width + 100  # Offset for track labels
            
            # Step number
            self.pattern_canvas.create_text(x + step_width//2, 15, text=str(step+1), 
                                          fill='white', font=('Arial', 8))
            
            # Vertical grid line
            self.pattern_canvas.create_line(x, 30, x, 30 + len(track_names) * track_height, 
                                          fill='#444', width=1)
            
            for track_idx, track_name in enumerate(track_names):
                y = 30 + track_idx * track_height
                
                # Track label (only for first step)
                if step == 0:
                    self.pattern_canvas.create_text(50, y + track_height//2, text=track_name.title(), 
                                                  fill='white', font=('Arial', 9, 'bold'), anchor='e')
                
                # Step button
                is_active = self.tracks[track_name]['pattern'][step] if step < len(self.tracks[track_name]['pattern']) else 0
                color = '#ff6b6b' if is_active else '#333'
                
                button_id = self.pattern_canvas.create_rectangle(x + 2, y + 2, x + step_width - 2, y + track_height - 2,
                                                               fill=color, outline='#666', width=1,
                                                               tags=f"step_{track_name}_{step}")
                
                # Velocity indicator (brightness)
                if is_active:
                    velocity = is_active if isinstance(is_active, (int, float)) else 1.0
                    alpha = max(0.3, velocity)
                    # Visual indicator of velocity could be added here
        
        # Horizontal grid lines
        for track_idx in range(len(track_names) + 1):
            y = 30 + track_idx * track_height
            self.pattern_canvas.create_line(100, y, 100 + steps * step_width, y, fill='#444', width=1)
        
        # Current step indicator
        if hasattr(self, 'current_step'):
            self._update_step_indicator()
        
        # Update scroll region
        self.pattern_canvas.configure(scrollregion=self.pattern_canvas.bbox("all"))
    
    def _draw_piano_roll(self):
        """Draw the piano roll editor."""
        self.piano_canvas.delete("all")
        
        # Piano roll dimensions
        note_height = 12
        beat_width = 60
        num_beats = 16
        num_octaves = 4
        notes_per_octave = 12
        
        # Draw piano keys and grid
        for octave in range(num_octaves):
            for note in range(notes_per_octave):
                note_num = octave * notes_per_octave + note
                y = note_num * note_height
                
                # Piano key color
                note_name = self.note_names[note]
                is_black_key = '#' in note_name
                key_color = '#2a2a2a' if is_black_key else '#4a4a4a'
                
                # Draw piano key
                self.piano_canvas.create_rectangle(0, y, 80, y + note_height,
                                                 fill=key_color, outline='#666', width=1)
                
                # Note name
                if not is_black_key:
                    octave_num = 4 + octave
                    self.piano_canvas.create_text(40, y + note_height//2, 
                                                text=f"{note_name}{octave_num}",
                                                fill='white', font=('Arial', 8))
        
        # Draw beat grid
        for beat in range(num_beats):
            x = 80 + beat * beat_width
            self.piano_canvas.create_line(x, 0, x, num_octaves * notes_per_octave * note_height,
                                        fill='#444', width=1)
        
        # Draw notes for current melody track
        current_track = self.melody_track_var.get()
        if current_track in self.melody_tracks:
            self._draw_melody_notes(current_track)
        
        # Update scroll region
        self.piano_canvas.configure(scrollregion=self.piano_canvas.bbox("all"))
    
    def _draw_melody_notes(self, track_name):
        """Draw notes for a specific melody track."""
        notes = self.melody_tracks[track_name]['notes']
        
        for note in notes:
            # Note position and size
            x = 80 + note['start'] * 60  # Beat position
            y = note['pitch'] * 12  # Note height
            width = note['length'] * 60  # Note duration
            height = 10
            
            # Draw note
            self.piano_canvas.create_rectangle(x, y, x + width, y + height,
                                             fill='#66d9ff', outline='#4dc3ff', width=2,
                                             tags=f"note_{track_name}_{note['id']}")
    
    # Event handlers
    def _on_pattern_click(self, event):
        """Handle pattern grid clicks."""
        canvas = event.widget
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        
        # Find clicked item
        item = canvas.find_closest(x, y)[0]
        tags = canvas.gettags(item)
        
        for tag in tags:
            if tag.startswith('step_'):
                parts = tag.split('_')
                if len(parts) >= 3:
                    track_name = parts[1]
                    step = int(parts[2])
                    
                    # Toggle step
                    current_value = self.tracks[track_name]['pattern'][step]
                    new_value = 0 if current_value else 1
                    self.tracks[track_name]['pattern'][step] = new_value
                    
                    # Update visual
                    color = '#ff6b6b' if new_value else '#333'
                    canvas.itemconfig(item, fill=color)
                    break
    
    def _on_pattern_drag(self, event):
        """Handle pattern grid dragging."""
        # Similar to click but for painting across multiple steps
        self._on_pattern_click(event)
    
    def _on_pattern_right_click(self, event):
        """Handle right-click for velocity editing."""
        # Show velocity editor popup
        pass
    
    def _on_piano_click(self, event):
        """Handle piano roll clicks."""
        canvas = event.widget
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        
        if x > 80:  # In the note area
            # Calculate note and beat position
            beat = (x - 80) // 60
            note_num = int(y // 12)
            
            # Add note to current melody track
            current_track = self.melody_track_var.get()
            note_id = len(self.melody_tracks[current_track]['notes'])
            
            new_note = {
                'id': note_id,
                'pitch': note_num,
                'start': beat,
                'length': 1,  # Default length
                'velocity': 100
            }
            
            self.melody_tracks[current_track]['notes'].append(new_note)
            self._draw_melody_notes(current_track)
    
    def _on_piano_drag(self, event):
        """Handle piano roll dragging for note length."""
        pass
    
    def _on_piano_right_click(self, event):
        """Handle right-click for note deletion."""
        pass
    
    # Audio generation and synthesis
    def _generate_audio_buffer(self):
        """Generate audio buffer for current patterns."""
        if not self.audio_available:
            return None
        
        try:
            # Calculate buffer parameters
            beats_per_minute = self.bpm
            beats_per_second = beats_per_minute / 60.0
            samples_per_beat = int(self.sample_rate / beats_per_second)
            steps = self.steps_var.get()
            total_samples = samples_per_beat * steps // 4  # Assuming 16th notes
            
            # Create stereo buffer
            buffer = np.zeros((total_samples, 2), dtype=np.float32)
            
            # Generate each track
            for track_name, track_data in self.tracks.items():
                if any(track_data['pattern']):  # If track has active steps
                    track_audio = self._generate_track_audio(track_name, track_data, total_samples)
                    if track_audio is not None:
                        # Mix track into buffer
                        buffer += track_audio * track_data['volume']
            
            # Add melody tracks
            for track_name, track_data in self.melody_tracks.items():
                if track_data['notes']:
                    melody_audio = self._generate_melody_audio(track_name, track_data, total_samples)
                    if melody_audio is not None:
                        buffer += melody_audio * track_data['volume']
            
            # Apply master volume and normalize
            buffer *= self.master_volume
            buffer = np.clip(buffer, -1.0, 1.0)
            
            return buffer
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return None
    
    def _generate_track_audio(self, track_name, track_data, total_samples):
        """Generate audio for a specific drum track."""
        try:
            pattern = track_data['pattern']
            steps = len(pattern)
            samples_per_step = total_samples // steps
            
            # Create track buffer
            track_buffer = np.zeros((total_samples, 2), dtype=np.float32)
            
            for step, active in enumerate(pattern):
                if active:
                    start_sample = step * samples_per_step
                    
                    # Generate drum sound based on track type
                    drum_sound = self._synthesize_drum_sound(track_name, track_data)
                    
                    if drum_sound is not None:
                        # Add to buffer
                        end_sample = min(start_sample + len(drum_sound), total_samples)
                        actual_length = end_sample - start_sample
                        
                        if actual_length > 0:
                            # Convert mono to stereo if needed
                            if len(drum_sound.shape) == 1:
                                drum_stereo = np.column_stack([drum_sound[:actual_length], 
                                                             drum_sound[:actual_length]])
                            else:
                                drum_stereo = drum_sound[:actual_length]
                            
                            track_buffer[start_sample:end_sample] += drum_stereo
            
            return track_buffer
            
        except Exception as e:
            logger.error(f"Track audio generation failed for {track_name}: {e}")
            return None
    
    def _synthesize_drum_sound(self, track_name, track_data):
        """Synthesize drum sounds."""
        try:
            frequency = track_data['pitch']
            duration = 0.1  # Default drum hit duration
            samples = int(self.sample_rate * duration)
            
            t = np.linspace(0, duration, samples)
            
            if track_name == 'kick':
                # Sub bass kick
                envelope = np.exp(-t * 15)
                sound = np.sin(2 * np.pi * frequency * t) * envelope
                # Add click
                sound += 0.3 * np.sin(2 * np.pi * frequency * 4 * t) * np.exp(-t * 50)
                
            elif track_name == 'snare':
                # Snare with noise
                envelope = np.exp(-t * 12)
                tone = np.sin(2 * np.pi * frequency * t) * envelope * 0.7
                noise = np.random.normal(0, 0.1, samples) * envelope
                sound = tone + noise
                
            elif track_name in ['hihat', 'openhat']:
                # Hi-hat (filtered noise)
                envelope = np.exp(-t * (30 if track_name == 'hihat' else 10))
                noise = np.random.normal(0, 0.1, samples)
                # Simple high-pass filter simulation
                sound = noise * envelope
                
            elif track_name == 'bass':
                # Bass line
                envelope = np.exp(-t * 5)
                sound = np.sin(2 * np.pi * frequency * t) * envelope
                # Add some harmonics
                sound += 0.3 * np.sin(2 * np.pi * frequency * 2 * t) * envelope
                
            else:
                # Generic tone
                envelope = np.exp(-t * 8)
                sound = np.sin(2 * np.pi * frequency * t) * envelope
            
            return sound
            
        except Exception as e:
            logger.error(f"Drum synthesis failed for {track_name}: {e}")
            return None
    
    def _generate_melody_audio(self, track_name, track_data, total_samples):
        """Generate audio for melody tracks."""
        try:
            instrument = track_data['instrument']
            notes = track_data['notes']
            
            # Create melody buffer
            melody_buffer = np.zeros((total_samples, 2), dtype=np.float32)
            
            beats_per_minute = self.bpm
            beats_per_second = beats_per_minute / 60.0
            samples_per_beat = int(self.sample_rate / beats_per_second)
            
            for note in notes:
                # Calculate note timing
                start_sample = int(note['start'] * samples_per_beat)
                length_samples = int(note['length'] * samples_per_beat)
                end_sample = min(start_sample + length_samples, total_samples)
                
                if start_sample < total_samples:
                    # Generate note sound
                    note_sound = self._synthesize_note(note, length_samples, instrument)
                    
                    if note_sound is not None:
                        actual_length = min(len(note_sound), end_sample - start_sample)
                        
                        # Convert to stereo
                        if len(note_sound.shape) == 1:
                            note_stereo = np.column_stack([note_sound[:actual_length], 
                                                         note_sound[:actual_length]])
                        else:
                            note_stereo = note_sound[:actual_length]
                        
                        melody_buffer[start_sample:start_sample + actual_length] += note_stereo
            
            return melody_buffer
            
        except Exception as e:
            logger.error(f"Melody audio generation failed for {track_name}: {e}")
            return None
    
    def _synthesize_note(self, note, length_samples, instrument):
        """Synthesize individual notes."""
        try:
            # Convert MIDI note to frequency
            frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
            duration = length_samples / self.sample_rate
            
            t = np.linspace(0, duration, length_samples)
            
            # ADSR envelope
            attack_time = 0.05
            decay_time = 0.1
            sustain_level = 0.7
            release_time = 0.2
            
            envelope = np.ones(length_samples)
            
            # Apply ADSR
            attack_samples = int(attack_time * self.sample_rate)
            decay_samples = int(decay_time * self.sample_rate)
            release_samples = int(release_time * self.sample_rate)
            
            if attack_samples > 0:
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
            
            if decay_samples > 0 and attack_samples + decay_samples < length_samples:
                envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain_level, decay_samples)
            
            if release_samples > 0:
                envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
            
            # Generate waveform based on instrument
            if instrument == 'sine':
                waveform = np.sin(2 * np.pi * frequency * t)
            elif instrument == 'square':
                waveform = np.sign(np.sin(2 * np.pi * frequency * t))
            elif instrument == 'sawtooth':
                waveform = 2 * (t * frequency % 1) - 1
            elif instrument == 'triangle':
                waveform = 2 * np.abs(2 * (t * frequency % 1) - 1) - 1
            else:
                waveform = np.sin(2 * np.pi * frequency * t)
            
            # Apply envelope and velocity
            velocity = note['velocity'] / 127.0
            sound = waveform * envelope * velocity
            
            return sound
            
        except Exception as e:
            logger.error(f"Note synthesis failed: {e}")
            return None
    
    # AI-powered generation methods
    def _ai_generate_beat(self):
        """Generate beat patterns using AI."""
        if not self.ai:
            messagebox.showwarning("AI Not Available", "AI interface not available.")
            return
        
        style = self.music_style_var.get()
        prompt = f"Generate a {style} drum pattern. Provide the pattern as JSON with kick, snare, hihat patterns as arrays of 16 steps (1=hit, 0=silence)."
        
        def generate_worker():
            try:
                response = self.ai.chat_response(prompt)
                # Parse JSON response and update patterns
                self.window.after(0, lambda: self._apply_ai_patterns(response))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("AI Error", f"Failed to generate beat: {e}"))
        
        threading.Thread(target=generate_worker, daemon=True).start()
    
    def _ai_full_beat(self):
        """Generate complete beat arrangement."""
        self._ai_generate_beat()
    
    def _ai_melody(self):
        """Generate melody using AI."""
        if not self.ai:
            messagebox.showwarning("AI Not Available", "AI interface not available.")
            return
        
        key = self.key_var.get()
        scale = self.scale_var.get()
        style = self.music_style_var.get()
        
        prompt = f"Generate a {style} melody in {key} {scale}. Provide note sequence with timing."
        
        def generate_worker():
            try:
                response = self.ai.chat_response(prompt)
                self.window.after(0, lambda: self._apply_ai_melody(response))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("AI Error", f"Failed to generate melody: {e}"))
        
        threading.Thread(target=generate_worker, daemon=True).start()
    
    def _ai_drums(self):
        """Generate drum patterns only."""
        self._ai_generate_beat()
    
    def _ai_bass(self):
        """Generate bass line."""
        self._ai_melody()  # Similar to melody but for bass
    
    def _ai_custom_generation(self):
        """Generate music based on custom prompt."""
        custom_prompt = self.ai_prompt.get("1.0", tk.END).strip()
        if not custom_prompt or custom_prompt == "Describe the music you want to create...":
            messagebox.showwarning("No Prompt", "Please enter a custom prompt.")
            return
        
        if not self.ai:
            messagebox.showwarning("AI Not Available", "AI interface not available.")
            return
        
        def generate_worker():
            try:
                response = self.ai.chat_response(f"Create music based on this description: {custom_prompt}")
                self.window.after(0, lambda: self._display_ai_suggestions(response))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("AI Error", f"Failed to generate: {e}"))
        
        threading.Thread(target=generate_worker, daemon=True).start()
    
    def _apply_ai_patterns(self, response):
        """Apply AI-generated patterns to tracks."""
        try:
            # Try to parse JSON response
            import json
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                pattern_data = json.loads(json_match.group())
                
                # Apply patterns
                for track_name, pattern in pattern_data.items():
                    if track_name in self.tracks and isinstance(pattern, list):
                        self.tracks[track_name]['pattern'] = pattern[:16]  # Ensure 16 steps
                
                # Redraw pattern grid
                self._draw_pattern_grid()
                messagebox.showinfo("AI Success", "Beat patterns generated successfully!")
            else:
                # Fallback: show AI response as suggestions
                self._display_ai_suggestions(response)
                
        except Exception as e:
            logger.error(f"Failed to apply AI patterns: {e}")
            self._display_ai_suggestions(response)
    
    def _apply_ai_melody(self, response):
        """Apply AI-generated melody."""
        # For now, display as suggestions
        self._display_ai_suggestions(response)
    
    def _display_ai_suggestions(self, text):
        """Display AI suggestions in the suggestions area."""
        self.ai_suggestions.config(state='normal')
        self.ai_suggestions.delete("1.0", tk.END)
        self.ai_suggestions.insert("1.0", text)
        self.ai_suggestions.config(state='disabled')
    
    # Playback and control methods
    def _toggle_playback(self):
        """Toggle playback state."""
        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()
    
    def _start_playback(self):
        """Start audio playback."""
        if not self.audio_available:
            messagebox.showinfo("Audio Not Available", 
                               "Audio playback requires pygame. Install with: pip install pygame")
            return
        
        self.is_playing = True
        self.play_btn.configure(text="⏸️")
        
        # Generate and play audio
        threading.Thread(target=self._playback_worker, daemon=True).start()
    
    def _pause_playback(self):
        """Pause playback."""
        self.is_playing = False
        self.play_btn.configure(text="▶️")
    
    def _stop_playback(self):
        """Stop playback."""
        self.is_playing = False
        self.current_step = 0
        self.play_btn.configure(text="▶️")
        self._update_step_indicator()
    
    def _toggle_recording(self):
        """Toggle recording state."""
        self.recording = not self.recording
        # Recording functionality would be implemented here
    
    def _playback_worker(self):
        """Background playback worker."""
        try:
            # Generate audio buffer
            audio_buffer = self._generate_audio_buffer()
            
            if audio_buffer is not None and self.audio_available:
                # Play audio using pygame
                import pygame
                import tempfile
                from scipy.io import wavfile
                
                # Convert to 16-bit integer
                audio_int = (audio_buffer * 32767).astype(np.int16)
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    wavfile.write(temp_file.name, self.sample_rate, audio_int)
                    
                    # Load and play
                    pygame.mixer.music.load(temp_file.name)
                    pygame.mixer.music.play(loops=-1 if self.loop_var.get() else 0)
                    
                    # Update position indicator
                    steps = self.steps_var.get()
                    step_duration = 60.0 / self.bpm / 4  # 16th note duration
                    
                    while self.is_playing and pygame.mixer.music.get_busy():
                        # Update current step
                        self.current_step = (self.current_step + 1) % steps
                        self.window.after(0, self._update_step_indicator)
                        
                        time.sleep(step_duration)
                    
                    # Cleanup
                    import os
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
            
        except Exception as e:
            logger.error(f"Playback failed: {e}")
            self.window.after(0, lambda: messagebox.showerror("Playback Error", f"Playback failed: {e}"))
        finally:
            self.window.after(0, lambda: setattr(self, 'is_playing', False))
            self.window.after(0, lambda: self.play_btn.configure(text="▶️"))
    
    def _update_step_indicator(self):
        """Update visual step indicator."""
        # Highlight current step in pattern grid
        self.pattern_canvas.delete("step_indicator")
        
        if hasattr(self, 'current_step'):
            step_width = 40
            x = self.current_step * step_width + 100
            
            self.pattern_canvas.create_line(x, 30, x, 30 + len(self.tracks) * 30,
                                          fill='yellow', width=3, tags="step_indicator")
    
    # Project management
    def _save_project(self):
        """Save project to file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Beat Studio Project",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                project_data = {
                    'bpm': self.bpm,
                    'swing': self.swing,
                    'tracks': self.tracks,
                    'melody_tracks': self.melody_tracks,
                    'key': self.key_var.get(),
                    'scale': self.scale_var.get(),
                    'steps': self.steps_var.get()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(project_data, f, indent=2)
                
                messagebox.showinfo("Save Complete", f"Project saved to: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save project: {e}")
    
    def _load_project(self):
        """Load project from file."""
        file_path = filedialog.askopenfilename(
            title="Load Beat Studio Project",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    project_data = json.load(f)
                
                # Load project data
                self.bpm = project_data.get('bpm', 120)
                self.swing = project_data.get('swing', 0.0)
                self.tracks = project_data.get('tracks', self.tracks)
                self.melody_tracks = project_data.get('melody_tracks', self.melody_tracks)
                
                # Update UI
                self.bpm_var.set(self.bpm)
                self.swing_var.set(self.swing)
                self.key_var.set(project_data.get('key', 'C'))
                self.scale_var.set(project_data.get('scale', 'Major'))
                self.steps_var.set(project_data.get('steps', 16))
                
                # Redraw interfaces
                self._draw_pattern_grid()
                self._draw_piano_roll()
                
                messagebox.showinfo("Load Complete", f"Project loaded from: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load project: {e}")
    
    def _export_wav(self):
        """Export project as WAV file."""
        file_path = filedialog.asksaveasfilename(
            title="Export as WAV",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Generate full audio
                audio_buffer = self._generate_audio_buffer()
                
                if audio_buffer is not None:
                    from scipy.io import wavfile
                    
                    # Convert to 16-bit integer
                    audio_int = (audio_buffer * 32767).astype(np.int16)
                    
                    # Write WAV file
                    wavfile.write(file_path, self.sample_rate, audio_int)
                    
                    messagebox.showinfo("Export Complete", f"Audio exported to: {file_path}")
                else:
                    messagebox.showerror("Export Error", "Failed to generate audio buffer")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export audio: {e}")
    
    # Utility methods for UI updates
    def _update_bpm(self):
        """Update BPM value."""
        self.bpm = self.bpm_var.get()
    
    def _update_swing(self, value):
        """Update swing value."""
        self.swing = float(value)
    
    def _update_pattern_length(self, event=None):
        """Update pattern length."""
        new_length = self.steps_var.get()
        
        # Resize all patterns
        for track_name in self.tracks:
            current_pattern = self.tracks[track_name]['pattern']
            
            if len(current_pattern) < new_length:
                # Extend pattern with zeros
                self.tracks[track_name]['pattern'].extend([0] * (new_length - len(current_pattern)))
            elif len(current_pattern) > new_length:
                # Truncate pattern
                self.tracks[track_name]['pattern'] = current_pattern[:new_length]
        
        # Redraw grid
        self._draw_pattern_grid()
    
    def _update_track_volume(self, track_name, value):
        """Update individual track volume."""
        self.tracks[track_name]['volume'] = float(value)
    
    def _update_track_pitch(self, track_name, value):
        """Update individual track pitch."""
        self.tracks[track_name]['pitch'] = float(value)
    
    def _update_master_volume(self, value):
        """Update master volume."""
        self.master_volume = float(value)
    
    def _seek_position(self, value):
        """Seek to position in song."""
        # Position seeking functionality
        pass
    
    def _switch_melody_track(self, event=None):
        """Switch active melody track."""
        self._draw_piano_roll()
    
    def _generate_melody(self):
        """Generate melody based on key and scale."""
        key = self.key_var.get()
        scale_name = self.scale_var.get()
        scale_intervals = self.scales[scale_name]
        
        # Generate simple melody
        current_track = self.melody_track_var.get()
        self.melody_tracks[current_track]['notes'] = []
        
        # Create melody notes
        for beat in range(8):  # 8 beat melody
            # Choose note from scale
            scale_degree = np.random.choice(len(scale_intervals))
            note_offset = scale_intervals[scale_degree]
            
            # Convert to MIDI note number (C4 = 60)
            base_note = 60 + self.note_names.index(key)
            note_pitch = base_note + note_offset
            
            note = {
                'id': beat,
                'pitch': note_pitch,
                'start': beat,
                'length': 1,
                'velocity': 80 + np.random.randint(-20, 20)
            }
            
            self.melody_tracks[current_track]['notes'].append(note)
        
        self._draw_piano_roll()
        messagebox.showinfo("Melody Generated", f"Generated melody in {key} {scale_name}")
    
    def _random_melody(self):
        """Generate random melody."""
        # Randomize key and scale first
        self.key_var.set(np.random.choice(self.note_names))
        self.scale_var.set(np.random.choice(list(self.scales.keys())))
        
        # Then generate melody
        self._generate_melody()

def show_advanced_beat_studio(parent, ai_interface=None):
    """Launch the Advanced Beat Studio."""
    try:
        studio = AdvancedBeatStudio(parent, ai_interface)
        return studio
    except Exception as e:
        logger.error(f"Failed to launch Advanced Beat Studio: {e}")
        messagebox.showerror("Beat Studio Error", f"Failed to launch Beat Studio: {e}")
        return None