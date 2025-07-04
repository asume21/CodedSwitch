# Advanced_Beat_Studio_UI_Components 

"""
beat_studio_ui_advanced.py - Advanced UI components for Beat Studio
Provides enhanced interface elements for professional beat production
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
import numpy as np
import threading
from typing import Dict, List, Callable, Optional
import json
from datetime import datetime

# ============================================================================
# ADVANCED PATTERN EDITOR
# ============================================================================

class AdvancedPatternEditor(ttk.Frame):
    """Professional pattern editor with velocity, swing, and more."""
    
    def __init__(self, parent, on_pattern_change: Callable = None):
        super().__init__(parent)
        self.on_pattern_change = on_pattern_change
        self.current_pattern_length = 16
        self.current_page = 0  # For patterns longer than 16 steps
        
        # Pattern data structure with velocity
        self.patterns = {
            'kick': {'hits': [0]*64, 'velocities': [0.8]*64},
            'snare': {'hits': [0]*64, 'velocities': [0.8]*64},
            'hihat': {'hits': [0]*64, 'velocities': [0.6]*64},
            'openhat': {'hits': [0]*64, 'velocities': [0.6]*64},
            'clap': {'hits': [0]*64, 'velocities': [0.8]*64},
            'bass808': {'hits': [0]*64, 'velocities': [0.8]*64},
            'perc': {'hits': [0]*64, 'velocities': [0.7]*64}
        }
        
        self.selected_instrument = 'kick'
        self.velocity_mode = False
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the advanced pattern editor UI."""
        # Top controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Pattern length
        ttk.Label(control_frame, text="Length:").pack(side=tk.LEFT, padx=(0, 5))
        self.length_var = tk.IntVar(value=16)
        length_combo = ttk.Combobox(
            control_frame,
            textvariable=self.length_var,
            values=[16, 32, 64],
            width=5,
            state="readonly"
        )
        length_combo.pack(side=tk.LEFT, padx=(0, 20))
        length_combo.bind("<<ComboboxSelected>>", self._on_length_change)
        
        # Page navigation
        ttk.Button(
            control_frame,
            text="◀",
            command=self._prev_page,
            width=3
        ).pack(side=tk.LEFT)
        
        self.page_label = ttk.Label(control_frame, text="Page 1/1")
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="▶",
            command=self._next_page,
            width=3
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Mode buttons
        ttk.Button(
            control_frame,
            text="🎹 Velocity Mode",
            command=self._toggle_velocity_mode,
            bootstyle="info"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="🎲 Randomize",
            command=self._randomize_pattern,
            bootstyle="warning"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="🗑️ Clear",
            command=self._clear_pattern,
            bootstyle="danger"
        ).pack(side=tk.LEFT)
        
        # Pattern grid
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_pattern_grid()
    
    def _create_pattern_grid(self):
        """Create the visual pattern grid."""
        # Clear existing grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Step numbers
        header_frame = ttk.Frame(self.grid_frame)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="", width=10).pack(side=tk.LEFT)
        
        start_step = self.current_page * 16
        for i in range(16):
            step_num = start_step + i + 1
            weight = "bold" if (i % 4) == 0 else "normal"
            ttk.Label(
                header_frame,
                text=str(step_num),
                width=3,
                font=("Courier", 8, weight)
            ).pack(side=tk.LEFT)
        
        # Instrument rows
        instruments = [
            ("🥁 Kick", "kick", "#FF5722"),
            ("🥁 Snare", "snare", "#2196F3"),
            ("🎩 Hi-Hat", "hihat", "#4CAF50"),
            ("🎩 Open Hat", "openhat", "#FFC107"),
            ("👏 Clap", "clap", "#E91E63"),
            ("🔊 808 Bass", "bass808", "#9C27B0"),
            ("🥁 Perc Loop", "perc", "#009688")
        ]
        
        self.pattern_buttons = {}
        
        for inst_name, inst_key, color in instruments:
            row_frame = ttk.Frame(self.grid_frame)
            row_frame.pack(fill=tk.X, pady=1)
            
            # Instrument label with selection
            inst_btn = tk.Button(
                row_frame,
                text=inst_name,
                width=10,
                relief=tk.RAISED if inst_key == self.selected_instrument else tk.FLAT,
                command=lambda k=inst_key: self._select_instrument(k)
            )
            inst_btn.pack(side=tk.LEFT)
            
            # Pattern buttons
            self.pattern_buttons[inst_key] = []
            
            for i in range(16):
                step_idx = start_step + i
                
                if self.velocity_mode and inst_key == self.selected_instrument:
                    # Velocity slider
                    vel_var = tk.DoubleVar(value=self.patterns[inst_key]['velocities'][step_idx])
                    vel_scale = ttk.Scale(
                        row_frame,
                        from_=0.0,
                        to=1.0,
                        variable=vel_var,
                        length=20,
                        orient=tk.VERTICAL,
                        command=lambda v, k=inst_key, idx=step_idx: self._update_velocity(k, idx, float(v))
                    )
                    vel_scale.pack(side=tk.LEFT, padx=1)
                else:
                    # Hit button
                    is_hit = self.patterns[inst_key]['hits'][step_idx]
                    velocity = self.patterns[inst_key]['velocities'][step_idx]
                    
                    btn = tk.Button(
                        row_frame,
                        text="●" if is_hit else "○",
                        width=2,
                        height=1,
                        font=("Arial", 8),
                        bg=self._velocity_to_color(color, velocity) if is_hit else "gray80",
                        fg="white",
                        relief=tk.FLAT,
                        command=lambda k=inst_key, idx=step_idx, c=color: self._toggle_hit(k, idx, c)
                    )
                    btn.pack(side=tk.LEFT, padx=1)
                    self.pattern_buttons[inst_key].append(btn)
    
    def _velocity_to_color(self, base_color: str, velocity: float) -> str:
        """Convert velocity to color shade."""
        # Simple brightness adjustment based on velocity
        if velocity > 0.8:
            return base_color
        elif velocity > 0.5:
            return base_color + "CC"  # Slightly transparent
        else:
            return base_color + "88"  # More transparent
    
    def _toggle_hit(self, instrument: str, step: int, color: str):
        """Toggle a hit in the pattern."""
        self.patterns[instrument]['hits'][step] = 1 - self.patterns[instrument]['hits'][step]
        self._update_grid()
        
        if self.on_pattern_change:
            self.on_pattern_change(self.get_current_pattern())
    
    def _update_velocity(self, instrument: str, step: int, velocity: float):
        """Update velocity for a step."""
        self.patterns[instrument]['velocities'][step] = velocity
        
        if self.on_pattern_change:
            self.on_pattern_change(self.get_current_pattern())
    
    def _select_instrument(self, instrument: str):
        """Select an instrument for editing."""
        self.selected_instrument = instrument
        self._create_pattern_grid()
    
    def _toggle_velocity_mode(self):
        """Toggle velocity editing mode."""
        self.velocity_mode = not self.velocity_mode
        self._create_pattern_grid()
    
    def _randomize_pattern(self):
        """Randomize the current instrument's pattern."""
        instrument = self.selected_instrument
        length = self.length_var.get()
        
        # Random hits with musical probability
        for i in range(length):
            # Higher probability on downbeats
            prob = 0.7 if i % 4 == 0 else 0.3
            self.patterns[instrument]['hits'][i] = 1 if np.random.random() < prob else 0
            
            # Random velocities
            if self.patterns[instrument]['hits'][i]:
                self.patterns[instrument]['velocities'][i] = np.random.uniform(0.5, 1.0)
        
        self._update_grid()
        if self.on_pattern_change:
            self.on_pattern_change(self.get_current_pattern())
    
    def _clear_pattern(self):
        """Clear the current instrument's pattern."""
        instrument = self.selected_instrument
        self.patterns[instrument]['hits'] = [0] * 64
        self.patterns[instrument]['velocities'] = [0.8] * 64
        
        self._update_grid()
        if self.on_pattern_change:
            self.on_pattern_change(self.get_current_pattern())
    
    def _on_length_change(self, event=None):
        """Handle pattern length change."""
        self.current_pattern_length = self.length_var.get()
        self._update_page_label()
        self._create_pattern_grid()
    
    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_page_label()
            self._create_pattern_grid()
    
    def _next_page(self):
        """Go to next page."""
        max_pages = self.current_pattern_length // 16
        if self.current_page < max_pages - 1:
            self.current_page += 1
            self._update_page_label()
            self._create_pattern_grid()
    
    def _update_page_label(self):
        """Update page navigation label."""
        max_pages = self.current_pattern_length // 16
        self.page_label.config(text=f"Page {self.current_page + 1}/{max_pages}")
    
    def _update_grid(self):
        """Update the visual grid."""
        self._create_pattern_grid()
    
    def get_current_pattern(self) -> Dict:
        """Get the current pattern data."""
        length = self.current_pattern_length
        pattern = {}
        
        for instrument in self.patterns:
            pattern[instrument] = {
                'hits': self.patterns[instrument]['hits'][:length],
                'velocities': self.patterns[instrument]['velocities'][:length]
            }
        
        return pattern

# ============================================================================
# MIXER CONSOLE
# ============================================================================

class MixerConsole(ttk.Frame):
    """Professional mixing console UI."""
    
    def __init__(self, parent, num_channels: int = 8, on_change: Callable = None):
        super().__init__(parent)
        self.num_channels = num_channels
        self.on_change = on_change
        self.channels = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create mixer UI."""
        # Main mixer frame
        mixer_frame = ttk.Frame(self)
        mixer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create channel strips
        for i in range(self.num_channels):
            channel = self._create_channel_strip(mixer_frame, i)
            channel.pack(side=tk.LEFT, fill=tk.Y, padx=2)
            self.channels.append(channel)
        
        # Master section
        master_frame = self._create_master_section(mixer_frame)
        master_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 5))
    
    def _create_channel_strip(self, parent, channel_num: int) -> ttk.Frame:
        """Create a single channel strip."""
        strip = ttk.LabelFrame(parent, text=f"CH {channel_num + 1}", padding=5)
        
        # Channel data
        channel_data = {
            'volume': tk.DoubleVar(value=0.8),
            'pan': tk.DoubleVar(value=0.0),
            'mute': tk.BooleanVar(value=False),
            'solo': tk.BooleanVar(value=False),
            'eq_low': tk.DoubleVar(value=0.0),
            'eq_mid': tk.DoubleVar(value=0.0),
            'eq_high': tk.DoubleVar(value=0.0)
        }
        
        # EQ Section
        eq_frame = ttk.LabelFrame(strip, text="EQ", padding=5)
        eq_frame.pack(fill=tk.X, pady=(0, 10))
        
        # High
        ttk.Label(eq_frame, text="H", font=("Arial", 8)).pack()
        high_knob = ttk.Scale(
            eq_frame,
            from_=-12,
            to=12,
            variable=channel_data['eq_high'],
            length=60,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        )
        high_knob.pack()
        
        # Mid
        ttk.Label(eq_frame, text="M", font=("Arial", 8)).pack()
        mid_knob = ttk.Scale(
            eq_frame,
            from_=-12,
            to=12,
            variable=channel_data['eq_mid'],
            length=60,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        )
        mid_knob.pack()
        
        # Low
        ttk.Label(eq_frame, text="L", font=("Arial", 8)).pack()
        low_knob = ttk.Scale(
            eq_frame,
            from_=-12,
            to=12,
            variable=channel_data['eq_low'],
            length=60,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        )
        low_knob.pack()
        
        # Pan
        ttk.Label(strip, text="PAN", font=("Arial", 8)).pack()
        pan_knob = ttk.Scale(
            strip,
            from_=-1.0,
            to=1.0,
            variable=channel_data['pan'],
            length=60,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        )
        pan_knob.pack(pady=5)
        
        # Volume fader
        ttk.Label(strip, text="VOL", font=("Arial", 8)).pack()
        volume_fader = ttk.Scale(
            strip,
            from_=1.0,
            to=0.0,
            variable=channel_data['volume'],
            length=150,
            orient=tk.VERTICAL,
            command=lambda v: self._on_change()
        )
        volume_fader.pack(pady=5)
        
        # Mute/Solo buttons
        button_frame = ttk.Frame(strip)
        button_frame.pack()
        
        mute_btn = ttk.Checkbutton(
            button_frame,
            text="M",
            variable=channel_data['mute'],
            bootstyle="danger",
            command=self._on_change
        )
        mute_btn.pack(side=tk.LEFT, padx=2)
        
        solo_btn = ttk.Checkbutton(
            button_frame,
            text="S",
            variable=channel_data['solo'],
            bootstyle="warning",
            command=self._on_change
        )
        solo_btn.pack(side=tk.LEFT, padx=2)
        
        # Store channel data
        strip.channel_data = channel_data
        
        return strip
    
    def _create_master_section(self, parent) -> ttk.Frame:
        """Create master channel section."""
        master = ttk.LabelFrame(parent, text="MASTER", padding=10)
        
        # Master volume
        self.master_volume = tk.DoubleVar(value=0.8)
        
        ttk.Label(master, text="MASTER", font=("Arial", 10, "bold")).pack()
        
        master_fader = ttk.Scale(
            master,
            from_=1.0,
            to=0.0,
            variable=self.master_volume,
            length=200,
            orient=tk.VERTICAL,
            command=lambda v: self._on_change()
        )
        master_fader.pack(pady=10)
        
        # Master limiter
        self.limiter_on = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            master,
            text="Limiter",
            variable=self.limiter_on,
            command=self._on_change
        ).pack()
        
        return master
    
    def _on_change(self):
        """Handle any mixer change."""
        if self.on_change:
            self.on_change(self.get_mixer_state())
    
    def get_mixer_state(self) -> Dict:
        """Get current mixer state."""
        state = {
            'channels': [],
            'master_volume': self.master_volume.get(),
            'limiter_on': self.limiter_on.get()
        }
        
        for channel in self.channels:
            if hasattr(channel, 'channel_data'):
                ch_state = {
                    key: var.get() 
                    for key, var in channel.channel_data.items()
                }
                state['channels'].append(ch_state)
        
        return state

# ============================================================================
# EFFECTS RACK
# ============================================================================

class EffectsRack(ttk.Frame):
    """Professional effects rack with multiple processors."""
    
    def __init__(self, parent, on_change: Callable = None):
        super().__init__(parent)
        self.on_change = on_change
        self.effects = {}
        
        self._create_ui()
    
    def _create_ui(self):
        """Create effects rack UI."""
        # Title
        ttk.Label(self, text="🎛️ Effects Rack", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Effects container
        effects_container = ttk.Frame(self)
        effects_container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Create effect modules
        self._create_reverb_module(effects_container)
        self._create_delay_module(effects_container)
        self._create_distortion_module(effects_container)
        self._create_compressor_module(effects_container)
    
    def _create_reverb_module(self, parent):
        """Create reverb effect module."""
        reverb_frame = ttk.LabelFrame(parent, text="🌊 Reverb", padding=10)
        reverb_frame.pack(fill=tk.X, pady=5)
        
        self.effects['reverb'] = {
            'enabled': tk.BooleanVar(value=False),
            'room_size': tk.DoubleVar(value=0.5),
            'damping': tk.DoubleVar(value=0.5),
            'mix': tk.DoubleVar(value=0.2)
        }
        
        # Enable checkbox
        ttk.Checkbutton(
            reverb_frame,
            text="Enable",
            variable=self.effects['reverb']['enabled'],
            command=self._on_change
        ).pack(anchor=tk.W)
        
        # Controls
        controls_frame = ttk.Frame(reverb_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Room Size
        ttk.Label(controls_frame, text="Room:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            variable=self.effects['reverb']['room_size'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=0, column=1, padx=5)
        
        # Damping
        ttk.Label(controls_frame, text="Damp:").grid(row=1, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            variable=self.effects['reverb']['damping'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=1, column=1, padx=5)
        
        # Mix
        ttk.Label(controls_frame, text="Mix:").grid(row=2, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            variable=self.effects['reverb']['mix'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=2, column=1, padx=5)
    
    def _create_delay_module(self, parent):
        """Create delay effect module."""
        delay_frame = ttk.LabelFrame(parent, text="⏱️ Delay", padding=10)
        delay_frame.pack(fill=tk.X, pady=5)
        
        self.effects['delay'] = {
            'enabled': tk.BooleanVar(value=False),
            'time': tk.DoubleVar(value=0.25),
            'feedback': tk.DoubleVar(value=0.3),
            'mix': tk.DoubleVar(value=0.2)
        }
        
        # Enable checkbox
        ttk.Checkbutton(
            delay_frame,
            text="Enable",
            variable=self.effects['delay']['enabled'],
            command=self._on_change
        ).pack(anchor=tk.W)
        
        # Controls
        controls_frame = ttk.Frame(delay_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Delay Time
        ttk.Label(controls_frame, text="Time:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.01,
            to=1.0,
            variable=self.effects['delay']['time'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=0, column=1, padx=5)
        
        # Feedback
        ttk.Label(controls_frame, text="Feedback:").grid(row=1, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=0.9,
            variable=self.effects['delay']['feedback'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=1, column=1, padx=5)
        
        # Mix
        ttk.Label(controls_frame, text="Mix:").grid(row=2, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            variable=self.effects['delay']['mix'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=2, column=1, padx=5)
    
    def _create_distortion_module(self, parent):
        """Create distortion effect module."""
        dist_frame = ttk.LabelFrame(parent, text="🔥 Distortion", padding=10)
        dist_frame.pack(fill=tk.X, pady=5)
        
        self.effects['distortion'] = {
            'enabled': tk.BooleanVar(value=False),
            'drive': tk.DoubleVar(value=2.0),
            'tone': tk.DoubleVar(value=0.5),
            'mix': tk.DoubleVar(value=0.5)
        }
        
        # Enable checkbox
        ttk.Checkbutton(
            dist_frame,
            text="Enable",
            variable=self.effects['distortion']['enabled'],
            command=self._on_change
        ).pack(anchor=tk.W)
        
        # Controls
        controls_frame = ttk.Frame(dist_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Drive
        ttk.Label(controls_frame, text="Drive:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=1.0,
            to=10.0,
            variable=self.effects['distortion']['drive'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=0, column=1, padx=5)
        
        # Tone
        ttk.Label(controls_frame, text="Tone:").grid(row=1, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            variable=self.effects['distortion']['tone'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=1, column=1, padx=5)
        
        # Mix
        ttk.Label(controls_frame, text="Mix:").grid(row=2, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            variable=self.effects['distortion']['mix'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=2, column=1, padx=5)
    
    def _create_compressor_module(self, parent):
        """Create compressor effect module."""
        comp_frame = ttk.LabelFrame(parent, text="🎚️ Compressor", padding=10)
        comp_frame.pack(fill=tk.X, pady=5)
        
        self.effects['compressor'] = {
            'enabled': tk.BooleanVar(value=True),
            'threshold': tk.DoubleVar(value=0.7),
            'ratio': tk.DoubleVar(value=4.0),
            'attack': tk.DoubleVar(value=0.005),
            'release': tk.DoubleVar(value=0.1)
        }
        
        # Enable checkbox
        ttk.Checkbutton(
            comp_frame,
            text="Enable",
            variable=self.effects['compressor']['enabled'],
            command=self._on_change
        ).pack(anchor=tk.W)
        
        # Controls
        controls_frame = ttk.Frame(comp_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Threshold
        ttk.Label(controls_frame, text="Threshold:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            variable=self.effects['compressor']['threshold'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=0, column=1, padx=5)
        
        # Ratio
        ttk.Label(controls_frame, text="Ratio:").grid(row=1, column=0, sticky=tk.W)
        ttk.Scale(
            controls_frame,
            from_=1.0,
            to=20.0,
            variable=self.effects['compressor']['ratio'],
            length=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_change()
        ).grid(row=1, column=1, padx=5)
    
    def _on_change(self):
        """Handle effect parameter change."""
        if self.on_change:
            self.on_change(self.get_effects_state())
    
    def get_effects_state(self) -> Dict:
        """Get current effects state."""
        state = {}
        
        for effect_name, effect_params in self.effects.items():
            state[effect_name] = {
                key: var.get()
                for key, var in effect_params.items()
            }
        
        return state

# ============================================================================
# LIVE PERFORMANCE PAD
# ============================================================================

class PerformancePad(ttk.Frame):
    """MPC-style performance pad interface."""
    
    def __init__(self, parent, on_trigger: Callable = None):
        super().__init__(parent)
        self.on_trigger = on_trigger
        self.pads = []
        self.pad_sounds = {}
        
        self._create_ui()
    
    def _create_ui(self):
        """Create performance pad UI."""
        # Title
        ttk.Label(self, text="🎹 Performance Pads", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Pad grid (4x4)
        pad_container = ttk.Frame(self)
        pad_container.pack(padx=10, pady=10)
        
        colors = [
            "#FF5722", "#2196F3", "#4CAF50", "#FFC107",
            "#9C27B0", "#00BCD4", "#FF9800", "#E91E63",
            "#795548", "#607D8B", "#FF5252", "#536DFE",
            "#69F0AE", "#FFD740", "#FF6E40", "#18FFFF"
        ]
        
        for i in range(16):
            row = i // 4
            col = i % 4
            
            pad_btn = tk.Button(
                pad_container,
                text=str(i + 1),
                width=8,
                height=4,
                bg=colors[i],
                fg="white",
                font=("Arial", 12, "bold"),
                relief=tk.RAISED,
                bd=3
            )
            pad_btn.grid(row=row, column=col, padx=2, pady=2)
            
            # Bind events
            pad_btn.bind("<ButtonPress-1>", lambda e, idx=i: self._on_pad_press(idx))
            pad_btn.bind("<ButtonRelease-1>", lambda e, idx=i: self._on_pad_release(idx))
            
            self.pads.append(pad_btn)
        
        # Control panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            control_frame,
            text="🎵 Load Sounds",
            command=self._load_sounds,
            bootstyle="info"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="🎹 Velocity Sensitive",
            command=self._toggle_velocity,
            bootstyle="warning"
        ).pack(side=tk.LEFT, padx=5)
        
        self.velocity_sensitive = tk.BooleanVar(value=True)
    
    def _on_pad_press(self, pad_index: int):
        """Handle pad press."""
        self.pads[pad_index].config(relief=tk.SUNKEN)
        
        # Calculate velocity based on how quickly the pad was pressed
        velocity = 0.8  # Default velocity
        
        if self.on_trigger:
            self.on_trigger(pad_index, velocity, 'press')
    
    def _on_pad_release(self, pad_index: int):
        """Handle pad release."""
        self.pads[pad_index].config(relief=tk.RAISED)
        
        if self.on_trigger:
            self.on_trigger(pad_index, 0, 'release')
    
    def _load_sounds(self):
        """Load sounds for pads."""
        # This would open a dialog to assign sounds to pads
        messagebox.showinfo("Load Sounds", "Sound loading interface would appear here")
    
    def _toggle_velocity(self):
        """Toggle velocity sensitivity."""
        self.velocity_sensitive.set(not self.velocity_sensitive.get())
    
    def assign_sound(self, pad_index: int, sound_name: str):
        """Assign a sound to a pad."""
        if 0 <= pad_index < 16:
            self.pad_sounds[pad_index] = sound_name
            # Update pad label
            self.pads[pad_index].config(text=f"{pad_index + 1}\n{sound_name[:8]}")

# ============================================================================
# BEAT SUGGESTION PANEL
# ============================================================================

class BeatSuggestionPanel(ttk.Frame):
    """AI-powered beat suggestion interface."""
    
    def __init__(self, parent, on_apply_suggestion: Callable = None):
        super().__init__(parent)
        self.on_apply_suggestion = on_apply_suggestion
        self.current_suggestions = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create suggestion panel UI."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="🤖 AI Beat Suggestions",
            font=("Arial", 12, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            header_frame,
            text="🔄 Refresh",
            command=self._refresh_suggestions,
            bootstyle="info",
            width=10
        ).pack(side=tk.RIGHT)
        
        # Suggestions container
        self.suggestions_frame = ttk.Frame(self)
        self.suggestions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initial suggestions
        self._create_suggestion_cards()
    
    def _create_suggestion_cards(self):
        """Create suggestion cards."""
        # Clear existing cards
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        # Sample suggestions
        suggestions = [
            {
                'name': 'Trap Banger',
                'tempo': 140,
                'style': 'Aggressive trap with heavy 808s',
                'energy': 9,
                'color': 'danger'
            },
            {
                'name': 'Lo-Fi Chill',
                'tempo': 75,
                'style': 'Relaxed boom bap with vinyl texture',
                'energy': 3,
                'color': 'info'
            },
            {
                'name': 'Drill Intensity',
                'tempo': 145,
                'style': 'UK drill with sliding 808s',
                'energy': 8,
                'color': 'warning'
            },
            {
                'name': 'Jazz Fusion',
                'tempo': 110,
                'style': 'Complex jazz-influenced hip-hop',
                'energy': 6,
                'color': 'success'
            }
        ]
        
        for i, suggestion in enumerate(suggestions):
            card = self._create_suggestion_card(self.suggestions_frame, suggestion, i)
            card.pack(fill=tk.X, pady=5, padx=10)
            
        self.current_suggestions = suggestions
    
    def _create_suggestion_card(self, parent, suggestion: Dict, index: int) -> ttk.Frame:
        """Create a single suggestion card."""
        card = ttk.LabelFrame(parent, text=suggestion['name'], bootstyle=suggestion['color'])
        
        # Description
        ttk.Label(
            card,
            text=suggestion['style'],
            font=("Arial", 9),
            wraplength=300
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        # Metrics
        metrics_frame = ttk.Frame(card)
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            metrics_frame,
            text=f"BPM: {suggestion['tempo']}",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(
            metrics_frame,
            text=f"Energy: {suggestion['energy']}/10",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT)
        
        # Apply button
        ttk.Button(
            card,
            text="Apply This Style",
            command=lambda idx=index: self._apply_suggestion(idx),
            bootstyle=f"{suggestion['color']}-outline",
            width=20
        ).pack(pady=(0, 10))
        
        return card
    
    def _apply_suggestion(self, index: int):
        """Apply a suggestion."""
        if self.on_apply_suggestion and 0 <= index < len(self.current_suggestions):
            self.on_apply_suggestion(self.current_suggestions[index])
    
    def _refresh_suggestions(self):
        """Refresh suggestions based on current context."""
        # In a real implementation, this would analyze current lyrics/mood
        self._create_suggestion_cards()
    
    def update_suggestions(self, lyrics: str = None, mood: str = None):
        """Update suggestions based on new context."""
        # This would use the ML suggestion engine
        self._refresh_suggestions()

# ============================================================================
# COMPLETE BEAT STUDIO WINDOW
# ============================================================================

class CompleteBeatStudioWindow:
    """Complete professional beat studio interface."""
    
    def __init__(self, parent_gui=None):
        self.parent_gui = parent_gui
        self.window = tk.Toplevel() if parent_gui else tk.Tk()
        self.window.title("🎵 CodedSwitch Beat Studio Pro")
        self.window.geometry("1400x900")
        
        # Initialize components
        self.pattern_editor = None
        self.mixer_console = None
        self.effects_rack = None
        self.performance_pad = None
        self.suggestion_panel = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the complete studio UI."""
        # Menu bar
        self._create_menu_bar()
        
        # Main container with paned windows
        main_paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Pattern editor and performance
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=3)
        
        # Pattern editor
        pattern_frame = ttk.LabelFrame(left_panel, text="🎹 Pattern Sequencer", padding=10)
        pattern_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.pattern_editor = AdvancedPatternEditor(
            pattern_frame,
            on_pattern_change=self._on_pattern_change
        )
        self.pattern_editor.pack(fill=tk.BOTH, expand=True)
        
        # Performance pads
        perf_frame = ttk.LabelFrame(left_panel, text="🎹 Live Performance", padding=10)
        perf_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.performance_pad = PerformancePad(
            perf_frame,
            on_trigger=self._on_pad_trigger
        )
        self.performance_pad.pack()
        
        # Center panel - Mixer
        center_panel = ttk.Frame(main_paned)
        main_paned.add(center_panel, weight=2)
        
        mixer_frame = ttk.LabelFrame(center_panel, text="🎚️ Mixing Console", padding=10)
        mixer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.mixer_console = MixerConsole(
            mixer_frame,
            num_channels=8,
            on_change=self._on_mixer_change
        )
        self.mixer_console.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Effects and suggestions
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=2)
        
        # Effects rack
        effects_frame = ttk.Frame(right_paned)
        right_paned.add(effects_frame, weight=2)
        
        self.effects_rack = EffectsRack(
            effects_frame,
            on_change=self._on_effects_change
        )
        self.effects_rack.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Suggestions panel
        suggestion_frame = ttk.Frame(right_paned)
        right_paned.add(suggestion_frame, weight=1)
        
        self.suggestion_panel = BeatSuggestionPanel(
            suggestion_frame,
            on_apply_suggestion=self._apply_suggestion
        )
        self.suggestion_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom status bar
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """Create studio menu bar."""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project...", accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", accelerator="Ctrl+S")
        file_menu.add_command(label="Export Beat...", accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self.window.destroy)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy Pattern", accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste Pattern", accelerator="Ctrl+V")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Pattern Editor")
        view_menu.add_checkbutton(label="Mixer")
        view_menu.add_checkbutton(label="Effects")
        view_menu.add_checkbutton(label="Performance Pads")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Tap Tempo")
        tools_menu.add_command(label="Metronome")
        tools_menu.add_separator()
        tools_menu.add_command(label="MIDI Settings...")
        tools_menu.add_command(label="Audio Settings...")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Beat Studio Guide")
        help_menu.add_command(label="Keyboard Shortcuts")
        help_menu.add_separator()
        help_menu.add_command(label="About Beat Studio")
    
    def _create_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self.window)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            padding=(10, 5)
        ).pack(side=tk.LEFT)
        
        # CPU meter
        ttk.Label(
            status_frame,
            text="CPU: 12%",
            padding=(10, 5)
        ).pack(side=tk.RIGHT)
        
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y)
        
        # Project info
        ttk.Label(
            status_frame,
            text="Project: Untitled | 140 BPM | 4/4",
            padding=(10, 5)
        ).pack(side=tk.RIGHT)
    
    # Event handlers
    def _on_pattern_change(self, pattern_data):
        """Handle pattern change."""
        self.status_var.set("Pattern updated")
    
    def _on_mixer_change(self, mixer_state):
        """Handle mixer change."""
        self.status_var.set("Mixer adjusted")
    
    def _on_effects_change(self, effects_state):
        """Handle effects change."""
        self.status_var.set("Effects updated")
    
    def _on_pad_trigger(self, pad_index, velocity, action):
        """Handle performance pad trigger."""
        if action == 'press':
            self.status_var.set(f"Pad {pad_index + 1} triggered (vel: {velocity:.2f})")
    
    def _apply_suggestion(self, suggestion):
        """Apply a beat suggestion."""
        self.status_var.set(f"Applied style: {suggestion['name']}")
        # This would update pattern, tempo, etc.

# ============================================================================
# INTEGRATION FUNCTIONS
# ============================================================================

def create_professional_beat_studio(parent_gui=None):
    """Create and return a complete beat studio window."""
    studio = CompleteBeatStudioWindow(parent_gui)
    return studio

def add_advanced_ui_to_integration(beat_studio_integration):
    """Add advanced UI components to existing integration."""
    # This would enhance the existing beat studio integration
    # with all the advanced UI components
    
    # Add references to advanced UI classes
    beat_studio_integration.AdvancedPatternEditor = AdvancedPatternEditor
    beat_studio_integration.MixerConsole = MixerConsole
    beat_studio_integration.EffectsRack = EffectsRack
    beat_studio_integration.PerformancePad = PerformancePad
    beat_studio_integration.BeatSuggestionPanel = BeatSuggestionPanel
    beat_studio_integration.CompleteBeatStudioWindow = CompleteBeatStudioWindow
    
    return beat_studio_integration
    
  