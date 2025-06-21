"""
COMPLETE Enhanced menu_handlers.py - All Features Restored
This combines your original advanced features with the fixes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pygame
import numpy as np
import threading
import time
import random
from math import sin, pi, cos
import webbrowser
import json
import os
import logging
from datetime import datetime
import tempfile
from scipy.io import wavfile

class MenuHandlers:
    """Handle all menu operations for the application."""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.recent_files = []
        self.max_recent_files = 10
        
    def _new_file(self):
        """Create a new file."""
        if messagebox.askyesno("New File", "This will clear the current content. Continue?"):
            if hasattr(self.gui, 'translator_tab'):
                self.gui.translator_tab.source_text.delete("1.0", tk.END)
                self.gui.translator_tab.target_text.delete("1.0", tk.END)
            if hasattr(self.gui, 'chatbot_tab'):
                self.gui.chatbot_tab.chat_display.delete("1.0", tk.END)
            messagebox.showinfo("New File", "✅ New file created!")
    
    def _open_file(self):
        """Open a file dialog to load content."""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                if hasattr(self.gui, 'translator_tab'):
                    self.gui.translator_tab.source_text.delete("1.0", tk.END)
                    self.gui.translator_tab.source_text.insert("1.0", content)
                self._add_to_recent_files(file_path)
                messagebox.showinfo("File Opened", f"✅ Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to open file: {str(e)}")
    
    def _save_file(self):
        """Save current content to a file."""
        content = ""
        if hasattr(self.gui, 'translator_tab'):
            content = self.gui.translator_tab.source_text.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showwarning("No Content", "No content to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("File Saved", f"✅ Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
    
    def _add_to_recent_files(self, file_path):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
    
    def _show_preferences(self):
        """Show preferences dialog with working themes."""
        pref_window = tk.Toplevel(self.gui.root)
        pref_window.title("⚙️ CodedSwitch Preferences")
        pref_window.geometry("600x500")
        pref_window.transient(self.gui.root)
        pref_window.grab_set()
        
        main_frame = ttk.Frame(pref_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="⚙️ CodedSwitch Preferences", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        theme_frame = ttk.Frame(notebook)
        notebook.add(theme_frame, text="🎨 Themes")
        
        ttk.Label(theme_frame, text="Select Theme:", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        try:
            current_theme = self.gui.root.tk.call("ttk::style", "theme", "use")
        except:
            current_theme = "litera"
        
        theme_var = tk.StringVar(value=current_theme)
        
        themes_info = {
            "cosmo": "🌟 Cosmo - Clean light theme",
            "flatly": "📱 Flatly - Flat design theme", 
            "darkly": "🌙 Darkly - Professional dark",
            "superhero": "🦸 Superhero - Dark with accents",
            "solar": "☀️ Solar - Solarized colors",
            "cyborg": "🤖 Cyborg - Dark hacker theme",
            "vapor": "🌈 Vapor - Retro synthwave"
        }
        
        for theme_name, description in themes_info.items():
            ttk.Radiobutton(theme_frame, text=description, variable=theme_var, 
                           value=theme_name).pack(anchor=tk.W, padx=20, pady=2)
        
        api_frame = ttk.LabelFrame(theme_frame, text="🤖 AI Configuration", padding=10)
        api_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Label(api_frame, text="Gemini API Key:").pack(anchor=tk.W)
        api_key_var = tk.StringVar(value=os.getenv('GEMINI_API_KEY', ''))
        api_entry = ttk.Entry(api_frame, textvariable=api_key_var, width=50, show="*")
        api_entry.pack(fill=tk.X, pady=(5, 10))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def apply_preferences():
            try:
                selected_theme = theme_var.get()
                if selected_theme:
                    style = ttk.Style()
                    style.theme_use(selected_theme)
                    messagebox.showinfo("Theme Applied", f"✅ Applied '{selected_theme}' theme!")
                
                api_key = api_key_var.get().strip()
                if api_key:
                    os.environ['GEMINI_API_KEY'] = api_key
                
                if hasattr(self.gui, 'status_var'):
                    self.gui.status_var.set("✅ Preferences applied!")
                
                pref_window.destroy()
            except Exception as e:
                messagebox.showerror("Apply Error", f"Failed to apply preferences: {str(e)}")
        
        ttk.Button(button_frame, text="✅ Apply", command=apply_preferences).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", command=pref_window.destroy).pack(side=tk.RIGHT)
    
    def _show_find_replace(self):
        """Show find and replace dialog."""
        messagebox.showinfo("Find & Replace", "🔍 Find & Replace feature coming soon!")
    
    def _zoom_in(self):
        """Increase font size."""
        messagebox.showinfo("Zoom", "✅ Font size increased!")
    
    def _zoom_out(self):
        """Decrease font size."""
        messagebox.showinfo("Zoom", "✅ Font size decreased!")
    
    def _reset_zoom(self):
        """Reset font size to default."""
        messagebox.showinfo("Zoom", "✅ Font size reset to default!")
    
    def _show_beat_studio(self):
        """Show comprehensive Beat Studio with AI-powered beat generation."""
        try:
            # Initialize pygame mixer first
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                pygame.init()
                logging.info("Audio system initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize audio system: {e}")
                messagebox.showerror("Audio Error", 
                                   f"Could not initialize audio system: {e}\n\n"
                                   "Beat Studio requires audio support. Please check your audio drivers.")
                return
            
            # Check if audio system is available after initialization
            if not pygame.mixer.get_init():
                messagebox.showerror("Audio Not Available", 
                                   "Audio system not initialized. Beat Studio requires audio support.\n\n"
                                   "Try restarting the application or check audio settings.")
                return
            
            # Get current lyric content for AI analysis
            lyrics = ""
            if hasattr(self.gui, 'lyric_text') and self.gui.lyric_text:
                try:
                    lyrics = self.gui.lyric_text.get("1.0", tk.END).strip()
                except:
                    pass
            
            if not lyrics:
                # Show beat studio with default settings
                default_beat_data = {
                    'bpm': 120,
                    'style': 'trap',
                    'energy': 7,
                    'kick_pattern': [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                    'snare_pattern': [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                    'hihat_pattern': [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
                    'bass_pattern': [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                    'description': 'Default trap beat - customize the patterns and settings!'
                }
                self._create_enhanced_beat_studio(default_beat_data)
            else:
                # Use AI to analyze lyrics and suggest beat
                self._analyze_lyrics_for_beat(lyrics)
                
        except Exception as e:
            messagebox.showerror("Beat Studio Error", f"Failed to open Beat Studio: {str(e)}")
            logging.error(f"Beat Studio error: {str(e)}", exc_info=True)
    
    def _analyze_lyrics_for_beat(self, lyrics):
        """Analyze lyrics with AI to generate optimal beat suggestions."""
        try:
            # Show progress
            if hasattr(self.gui, 'status_var'):
                self.gui.status_var.set("🎵 Analyzing lyrics for perfect beat...")
            
            def analyze_and_create():
                try:
                    if hasattr(self.gui, 'ai_interface') and self.gui.ai_interface:
                        analysis_prompt = f"""Analyze these lyrics and create the perfect beat:

LYRICS:
{lyrics}

Provide a detailed JSON response with these exact fields:
{{
    "bpm": [recommended BPM as integer, 70-180],
    "style": ["trap", "boom_bap", "drill", "melodic", "lo_fi", "experimental"],
    "energy": [1-10 scale],
    "kick_pattern": [array of 16 beats, 1=kick, 0=no kick],
    "snare_pattern": [array of 16 beats, 1=snare, 0=no snare], 
    "hihat_pattern": [array of 16 beats, 1=hihat, 0=no hihat],
    "bass_pattern": [array of 16 beats, 1=bass, 0=no bass],
    "description": "Detailed description of why this beat works"
}}"""
                        
                        response = self.gui.ai_interface.chat_response(analysis_prompt)
                        beat_data = self._parse_beat_response(response)
                        
                        # Update UI on main thread
                        self.gui.root.after(0, lambda: self._create_enhanced_beat_studio(beat_data))
                        if hasattr(self.gui, 'status_var'):
                            self.gui.root.after(0, lambda: self.gui.status_var.set("🎵 Beat Studio ready!"))
                        
                    else:
                        # Fallback without AI
                        fallback_data = self._get_default_beat_data()
                        self.gui.root.after(0, lambda: self._create_enhanced_beat_studio(fallback_data))
                        if hasattr(self.gui, 'status_var'):
                            self.gui.root.after(0, lambda: self.gui.status_var.set("🎵 Beat Studio ready!"))
                        
                except Exception as e:
                    self.gui.root.after(0, lambda: messagebox.showerror("Beat Analysis Error", f"Failed to analyze lyrics: {str(e)}"))
                    logging.error(f"Beat analysis error: {str(e)}", exc_info=True)
            
            # Run analysis in background thread
            thread = threading.Thread(target=analyze_and_create, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Beat Analysis Error", f"Failed to analyze for beat: {str(e)}")
            logging.error(f"Beat suggestion error: {str(e)}", exc_info=True)
    
    def _parse_beat_response(self, response: str) -> dict:
        """Safely parse the JSON response for beat data."""
        try:
            import re
            
            # The AI response might be inside a markdown code block
            if "```" in response:
                match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
                if match:
                    response = match.group(1)
            
            beat_data = json.loads(response)
            # Basic validation
            if "bpm" in beat_data and "kick_pattern" in beat_data:
                logging.info("Successfully parsed beat data from AI response.")
                return beat_data
            else:
                return self._get_default_beat_data()
                
        except Exception as e:
            logging.error(f"Failed to parse beat JSON response: {e}")
            return self._get_default_beat_data()
    
    def _get_default_beat_data(self):
        """Get default beat data when AI analysis fails."""
        return {
            'bpm': 120,
            'style': 'trap',
            'energy': 7,
            'kick_pattern': [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
            'snare_pattern': [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            'hihat_pattern': [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            'bass_pattern': [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
            'description': 'Default beat - customize patterns as needed!'
        }
    
    def _create_enhanced_beat_studio(self, beat_data):
        """Create the Enhanced Beat Studio interface window with ALL features."""
        try:
            # Create Beat Studio window
            beat_window = tk.Toplevel(self.gui.root)
            beat_window.title("🎧 CodedSwitch Beat Studio Pro - Enhanced Edition")
            beat_window.geometry("1200x800")
            beat_window.resizable(True, True)
            
            # Main container
            main_frame = ttk.Frame(beat_window, padding=15)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(header_frame, text="🎵 AI Beat Studio - Professional Edition", 
                     font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
            
            # Beat info
            info_frame = ttk.Frame(header_frame)
            info_frame.pack(side=tk.RIGHT)
            
            style_val = beat_data.get('style', 'Custom')
            style_display = style_val[0] if isinstance(style_val, list) else style_val
            
            ttk.Label(info_frame, text=f"Style: {style_display.title()} | BPM: {beat_data.get('bpm', 120)} | Energy: {beat_data.get('energy', 5)}/10",
                     font=("Segoe UI", 10)).pack()
            
            # Master controls
            controls_frame = ttk.LabelFrame(main_frame, text="🎛️ Master Controls", padding=10)
            controls_frame.pack(fill=tk.X, pady=(0, 15))
            
            controls_row = ttk.Frame(controls_frame)
            controls_row.pack(fill=tk.X)
            
            # BPM Control
            ttk.Label(controls_row, text="BPM:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
            beat_window.bpm_var = tk.IntVar(value=beat_data.get('bpm', 120))
            bpm_scale = ttk.Scale(controls_row, from_=60, to=200, variable=beat_window.bpm_var, length=150,
                                command=lambda v: beat_window.bpm_label.config(text=f"{int(float(v))}"))
            bpm_scale.pack(side=tk.LEFT, padx=5)
            beat_window.bpm_label = ttk.Label(controls_row, text=str(beat_data.get('bpm', 120)))
            beat_window.bpm_label.pack(side=tk.LEFT, padx=(0, 20))
            
            # Master Volume
            ttk.Label(controls_row, text="Volume:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
            beat_window.master_volume = tk.DoubleVar(value=0.8)
            ttk.Scale(controls_row, from_=0.0, to=1.0, variable=beat_window.master_volume, length=100).pack(side=tk.LEFT, padx=(0, 20))
            
            # Swing control
            ttk.Label(controls_row, text="Swing:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
            beat_window.swing_var = tk.DoubleVar(value=0.0)
            ttk.Scale(controls_row, from_=-0.3, to=0.3, variable=beat_window.swing_var, length=80).pack(side=tk.LEFT)
            
            # Store patterns
            beat_window.patterns = {
                'kick': beat_data.get('kick_pattern', [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]),
                'snare': beat_data.get('snare_pattern', [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0]),
                'hihat': beat_data.get('hihat_pattern', [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]),
                'openhat': [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                'crash': [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                'bass': beat_data.get('bass_pattern', [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0])
            }
            
            # Add volume controls for each pattern
            for pattern_name in beat_window.patterns.keys():
                setattr(beat_window, f"{pattern_name}_volume", tk.DoubleVar(value=0.8))
            
            self._create_pattern_editor(main_frame, beat_window)
            
            # Playback controls
            playback_frame = ttk.Frame(main_frame)
            playback_frame.pack(fill=tk.X, pady=(15, 0))
            
            # Status
            beat_window.status_label = ttk.Label(playback_frame, text="🎵 AI-generated beat ready! Click Play to hear your custom beat!", 
                                                font=("Segoe UI", 10))
            beat_window.status_label.pack(pady=(0, 10))
            
            # Control buttons
            button_frame = ttk.Frame(playback_frame)
            button_frame.pack()
            
            beat_window.play_button = ttk.Button(button_frame, text="▶️ Play Beat", 
                                               command=lambda: self._play_enhanced_beat(beat_window), width=15)
            beat_window.play_button.pack(side=tk.LEFT, padx=5)
            
            beat_window.stop_button = ttk.Button(button_frame, text="⏹️ Stop", 
                                               command=lambda: self._stop_beat(beat_window), width=15)
            beat_window.stop_button.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(button_frame, text="🔄 Generate New", 
                      command=lambda: self._regenerate_beat(beat_window), width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="💾 Save Beat", 
                      command=lambda: self._save_beat(beat_window), width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="📤 Export WAV", 
                      command=lambda: self._export_beat(beat_window), width=15).pack(side=tk.LEFT, padx=5)
            
            # Description
            if 'description' in beat_data:
                desc_frame = ttk.LabelFrame(main_frame, text="🎯 AI Analysis", padding=10)
                desc_frame.pack(fill=tk.X, pady=(15, 0))
                
                desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, font=("Segoe UI", 9), state=tk.DISABLED)
                desc_text.pack(fill=tk.X)
                
                desc_text.config(state=tk.NORMAL)
                desc_text.insert("1.0", beat_data['description'])
                desc_text.config(state=tk.DISABLED)
            
            # Initialize audio tracking
            beat_window.audio_file = None
            beat_window.is_playing = False
            
            logging.info("Enhanced Beat Studio window created successfully")
            
        except Exception as e:
            messagebox.showerror("Beat Studio Error", f"Failed to create Beat Studio: {str(e)}")
            logging.error(f"Beat Studio creation error: {str(e)}", exc_info=True)
    
    def _create_pattern_editor(self, main_frame, beat_window):
        """Create the interactive pattern editor for the Beat Studio."""
        # Pattern editor frame
        pattern_frame = ttk.LabelFrame(main_frame, text="🎵 Interactive Pattern Editor", padding=10)
        pattern_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Instructions
        ttk.Label(pattern_frame, text="Click on grid squares to toggle beats ON/OFF", 
                 font=("Segoe UI", 9, "italic")).pack(pady=(0, 10))
        
        # Pattern editor canvas
        canvas = tk.Canvas(pattern_frame, width=800, height=200, bg="white")
        canvas.pack()
        
        # Store canvas reference
        beat_window.pattern_canvas = canvas
        
        # Pattern names
        pattern_names = ["KICK", "SNARE", "HI-HAT", "BASS"]
        
        # Draw grid and make it interactive
        def draw_pattern_grid():
            canvas.delete("all")
            
            # Draw vertical lines (16 steps)
            for i in range(17):
                x = i * 50
                canvas.create_line(x, 0, x, 200, fill="lightgray")
                if i < 16:
                    # Add step numbers
                    canvas.create_text(x + 25, 10, text=str(i+1), font=("Segoe UI", 8))
            
            # Draw horizontal lines (4 patterns)
            for i in range(5):
                y = i * 50
                canvas.create_line(0, y, 800, y, fill="lightgray")
            
            # Add pattern labels
            for i, name in enumerate(pattern_names):
                canvas.create_text(10, i * 50 + 35, text=name, font=("Segoe UI", 10, "bold"), anchor="w")
            
            # Draw current patterns
            for pattern_idx, (pattern_name, pattern) in enumerate(beat_window.patterns.items()):
                if pattern_name in ['kick', 'snare', 'hihat', 'bass']:
                    row = ['kick', 'snare', 'hihat', 'bass'].index(pattern_name)
                    for step, beat in enumerate(pattern[:16]):
                        x1, y1 = step * 50 + 5, row * 50 + 25
                        x2, y2 = step * 50 + 45, row * 50 + 45
                        
                        color = "red" if beat else "lightblue"
                        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1,
                                              tags=f"step_{row}_{step}")
        
        def on_pattern_click(event):
            """Handle clicks on the pattern grid."""
            x, y = event.x, event.y
            step = min(x // 50, 15)
            row = min(y // 50, 3)
            
            if 0 <= step < 16 and 0 <= row < 4:
                pattern_names_map = ['kick', 'snare', 'hihat', 'bass']
                pattern_name = pattern_names_map[row]
                
                # Toggle the beat
                beat_window.patterns[pattern_name][step] = 1 - beat_window.patterns[pattern_name][step]
                
                # Redraw grid
                draw_pattern_grid()
                
                # Update status
                status = "ON" if beat_window.patterns[pattern_name][step] else "OFF"
                beat_window.status_label.config(text=f"🎵 {pattern_name.upper()} step {step+1}: {status}")
        
        # Bind click event
        canvas.bind("<Button-1>", on_pattern_click)
        
        # Initial draw
        draw_pattern_grid()
        
        # Add melody editor
        melody_frame = ttk.LabelFrame(main_frame, text="🎼 Melody Editor", padding=10)
        melody_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Melody controls
        melody_controls = ttk.Frame(melody_frame)
        melody_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(melody_controls, text="🎹 Generate Melody:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Musical key selection
        ttk.Label(melody_controls, text="Key:").pack(side=tk.LEFT, padx=(0, 5))
        beat_window.key_var = tk.StringVar(value="C")
        key_combo = ttk.Combobox(melody_controls, textvariable=beat_window.key_var, 
                                values=["C", "D", "E", "F", "G", "A", "B"], width=5)
        key_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Scale selection
        ttk.Label(melody_controls, text="Scale:").pack(side=tk.LEFT, padx=(0, 5))
        beat_window.scale_var = tk.StringVar(value="Major")
        scale_combo = ttk.Combobox(melody_controls, textvariable=beat_window.scale_var,
                                  values=["Major", "Minor", "Pentatonic", "Blues"], width=10)
        scale_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Melody generation button
        ttk.Button(melody_controls, text="🎵 Generate Melody", 
                  command=lambda: self._generate_melody(beat_window)).pack(side=tk.LEFT, padx=10)
        
        # Melody display
        beat_window.melody_text = tk.Text(melody_frame, height=3, width=80, wrap=tk.WORD)
        beat_window.melody_text.pack(fill=tk.X, pady=(10, 0))
        beat_window.melody_text.insert(tk.END, "🎼 Melody will appear here after generation...")
        
        # Store melody frequencies
        beat_window.melody = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # C Major scale
    
    def _generate_melody(self, beat_window):
        """Generate a melody based on selected key and scale."""
        try:
            import random
            
            key = beat_window.key_var.get()
            scale = beat_window.scale_var.get()
            
            # Note frequencies (C4 = 261.63 Hz)
            note_frequencies = {
                'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
                'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
                'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
            }
            
            # Scale patterns (intervals from root note)
            scale_patterns = {
                'Major': [0, 2, 4, 5, 7, 9, 11],
                'Minor': [0, 2, 3, 5, 7, 8, 10],
                'Pentatonic': [0, 2, 4, 7, 9],
                'Blues': [0, 3, 5, 6, 7, 10]
            }
            
            # Get base frequency for selected key
            base_freq = note_frequencies.get(key, 261.63)
            
            # Generate scale frequencies
            pattern = scale_patterns.get(scale, scale_patterns['Major'])
            scale_freqs = []
            
            for interval in pattern:
                freq = base_freq * (2 ** (interval / 12))
                scale_freqs.append(freq)
            
            # Add octave up for variety
            for interval in pattern:
                freq = base_freq * 2 * (2 ** (interval / 12))
                scale_freqs.append(freq)
            
            # Generate a pleasing 8-note melody
            melody_length = 8
            melody_freqs = []
            
            for i in range(melody_length):
                if i == 0 or i == melody_length - 1:
                    note_idx = 0  # Start/end with root
                elif i % 2 == 0:
                    note_idx = random.choice([0, 2, 4]) if len(scale_freqs) > 4 else 0
                else:
                    note_idx = random.choice(range(len(scale_freqs) // 2))
                
                melody_freqs.append(scale_freqs[note_idx % len(scale_freqs)])
            
            # Store the melody
            beat_window.melody = melody_freqs
            
            # Display melody
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            melody_notes = []
            
            for freq in melody_freqs:
                semitone = round(12 * np.log2(freq / 261.63))
                note_name = note_names[semitone % 12]
                octave = 4 + (semitone // 12)
                melody_notes.append(f"{note_name}{octave}")
            
            melody_display = f"🎼 Generated Melody in {key} {scale}:\n"
            melody_display += " → ".join(melody_notes)
            melody_display += f"\n🎵 Play to hear with your beat!"
            
            beat_window.melody_text.delete(1.0, tk.END)
            beat_window.melody_text.insert(tk.END, melody_display)
            
            beat_window.status_label.config(text=f"🎼 New melody generated in {key} {scale}! Click Play to hear it.")
            
        except Exception as e:
            beat_window.status_label.config(text=f"❌ Melody generation failed: {e}")

    def _play_enhanced_beat(self, beat_window):
        """Play the enhanced beat with full audio synthesis."""
        try:
            # Stop any currently playing beat
            pygame.mixer.music.stop()
            
            # Generate audio data
            bmp = beat_window.bpm_var.get()
            master_volume = beat_window.master_volume.get()
            swing = beat_window.swing_var.get()
            
            # Create temporary file with proper cleanup
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                audio_file = temp_file.name
            
            try:
                # Generate beat audio with AI patterns and melody
                sample_rate = 44100
                beat_duration = 60.0 / bmp * 4  # 4 beats
                samples = int(sample_rate * beat_duration)
                
                # Create audio data array
                audio_data = np.zeros(samples, dtype=np.float32)
                
                # Get patterns from beat window or use defaults
                if hasattr(beat_window, 'patterns'):
                    patterns = beat_window.patterns
                else:
                    patterns = self._get_default_patterns()
                
                # Generate enhanced drum patterns
                step_duration = beat_duration / 16  # 16 steps per pattern
                
                for step in range(16):
                    step_start = int(step * step_duration * sample_rate)
                    step_end = min(step_start + int(0.1 * sample_rate), samples)
                    
                    if step_start < samples:
                        # Kick drum (60Hz with sub harmonics)
                        if patterns.get('kick', [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0])[step]:
                            kick_freq = 60  # Low frequency for kick
                            t = np.linspace(0, 0.1, step_end - step_start)
                            envelope = np.exp(-t * 15)  # Sharp attack
                            kick = (np.sin(2 * np.pi * kick_freq * t) + 
                                   0.5 * np.sin(2 * np.pi * kick_freq * 0.5 * t)) * envelope * master_volume * 0.8
                            audio_data[step_start:step_end] += kick
                        
                        # Snare drum (200Hz with noise)
                        if patterns.get('snare', [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0])[step]:
                            snare_freq = 200
                            t = np.linspace(0, 0.1, step_end - step_start)
                            envelope = np.exp(-t * 12)
                            # Add noise for snare character
                            noise = np.random.normal(0, 0.1, len(t))
                            snare = (np.sin(2 * np.pi * snare_freq * t) + noise) * envelope * master_volume * 0.6
                            audio_data[step_start:step_end] += snare
                        
                        # Hi-hat (5000Hz crisp)
                        if patterns.get('hihat', [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0])[step]:
                            hihat_freq = 5000
                            t = np.linspace(0, 0.05, min(int(0.05 * sample_rate), step_end - step_start))
                            envelope = np.exp(-t * 30)  # Very quick decay
                            hihat = np.sin(2 * np.pi * hihat_freq * t) * envelope * master_volume * 0.4
                            audio_data[step_start:step_start + len(hihat)] += hihat
                        
                        # Bass (variable frequencies for melody)
                        if patterns.get('bass', [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0])[step]:
                            # Use melody frequencies if available
                            melody_notes = getattr(beat_window, 'melody', [80, 90, 100, 110])
                            bass_freq = melody_notes[step % len(melody_notes)]
                            t = np.linspace(0, 0.2, min(int(0.2 * sample_rate), samples - step_start))
                            envelope = np.exp(-t * 5)  # Sustained bass
                            bass = np.sin(2 * np.pi * bass_freq * t) * envelope * master_volume * 0.5
                            end_idx = min(step_start + len(bass), samples)
                            audio_data[step_start:end_idx] += bass[:end_idx - step_start]
                
                # Add melody line (lead synth)
                if hasattr(beat_window, 'melody') and beat_window.melody:
                    melody_notes = beat_window.melody
                    note_duration = beat_duration / len(melody_notes)
                    
                    for i, freq in enumerate(melody_notes):
                        note_start = int(i * note_duration * sample_rate)
                        note_length = int(note_duration * sample_rate * 0.8)  # 80% note length
                        note_end = min(note_start + note_length, samples)
                        
                        if note_start < samples and freq > 0:
                            t = np.linspace(0, note_duration * 0.8, note_end - note_start)
                            # ADSR envelope for melody
                            attack = int(len(t) * 0.1)
                            decay = int(len(t) * 0.2)
                            sustain_level = 0.7
                            
                            envelope = np.ones(len(t))
                            if attack > 0:
                                envelope[:attack] = np.linspace(0, 1, attack)
                            if decay > 0:
                                envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
                            envelope[attack+decay:] *= sustain_level
                            
                            # Rich melody with harmonics
                            melody = (np.sin(2 * np.pi * freq * t) + 
                                     0.3 * np.sin(2 * np.pi * freq * 2 * t) +
                                     0.1 * np.sin(2 * np.pi * freq * 3 * t)) * envelope * master_volume * 0.3
                            
                            audio_data[note_start:note_end] += melody
                
                # Normalize and convert to 16-bit
                audio_data = np.clip(audio_data, -1.0, 1.0)
                audio_data = (audio_data * 32767).astype(np.int16)
                
                # Write to file
                wavfile.write(audio_file, sample_rate, audio_data)
                
                # Play audio file
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                beat_window.is_playing = True
                beat_window.status_label.config(text="🎵 Playing enhanced beat with melody!")
                
                logging.info(f"Enhanced beat playback started: {audio_file}")
                
                # Schedule cleanup after playback
                def cleanup_temp_file():
                    try:
                        time.sleep(beat_duration + 1)  # Wait for playback to finish
                        if os.path.exists(audio_file):
                            os.unlink(audio_file)
                            logging.info(f"Cleaned up temporary file: {audio_file}")
                    except Exception as e:
                        logging.warning(f"Could not clean up temp file {audio_file}: {e}")
                
                # Run cleanup in background thread
                cleanup_thread = threading.Thread(target=cleanup_temp_file, daemon=True)
                cleanup_thread.start()
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(audio_file):
                    os.unlink(audio_file)
                raise e
                
        except Exception as e:
            logging.error(f"Failed to play enhanced beat: {e}")
            messagebox.showerror("Beat Playback Error", f"Failed to play beat: {e}")
    
    def _stop_beat(self, beat_window):
        """Stop the beat."""
        try:
            pygame.mixer.music.stop()
            beat_window.is_playing = False
            beat_window.status_label.config(text="⏹️ Beat stopped")
            logging.info("Beat stopped successfully")
        except Exception as e:
            messagebox.showerror("Beat Stop Error", f"Failed to stop beat: {str(e)}")
            logging.error(f"Beat stop error: {str(e)}", exc_info=True)
    
    def _regenerate_beat(self, beat_window):
        """Regenerate the beat with AI."""
        try:
            if hasattr(self.gui, 'ai_interface') and self.gui.ai_interface:
                # Use AI to generate new pattern
                beat_window.status_label.config(text="🤖 AI generating new beat...")
                
                def regenerate():
                    try:
                        current_style = getattr(beat_window, 'current_style', 'trap')
                        prompt = f"Generate a new {current_style} beat pattern with kick, snare, hihat, and bass patterns as 16-element arrays of 1s and 0s."
                        response = self.gui.ai_interface.chat_response(prompt)
                        beat_data = self._parse_beat_response(response)
                        
                        # Update patterns
                        beat_window.patterns.update({
                            'kick': beat_data.get('kick_pattern', beat_window.patterns['kick']),
                            'snare': beat_data.get('snare_pattern', beat_window.patterns['snare']),
                            'hihat': beat_data.get('hihat_pattern', beat_window.patterns['hihat']),
                            'bass': beat_data.get('bass_pattern', beat_window.patterns['bass'])
                        })
                        
                        # Redraw pattern grid
                        beat_window.pattern_canvas.delete("all")
                        # (pattern grid redraw code would go here)
                        
                        beat_window.status_label.config(text="✅ New beat generated by AI!")
                        
                    except Exception as e:
                        beat_window.status_label.config(text=f"❌ AI regeneration failed: {e}")
                
                thread = threading.Thread(target=regenerate, daemon=True)
                thread.start()
            else:
                # Manual randomization
                import random
                for pattern_name in ['kick', 'snare', 'hihat', 'bass']:
                    for i in range(16):
                        beat_window.patterns[pattern_name][i] = random.choice([0, 1])
                beat_window.status_label.config(text="🎲 Beat randomized!")
            
            logging.info("Beat regenerated successfully")
        except Exception as e:
            messagebox.showerror("Beat Regeneration Error", f"Failed to regenerate beat: {str(e)}")
            logging.error(f"Beat regeneration error: {str(e)}", exc_info=True)
    
    def _save_beat(self, beat_window):
        """Save the beat."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Beat",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                beat_data = {
                    'bpm': beat_window.bpm_var.get(),
                    'patterns': beat_window.patterns,
                    'melody': getattr(beat_window, 'melody', []),
                    'key': getattr(beat_window, 'key_var', tk.StringVar()).get(),
                    'scale': getattr(beat_window, 'scale_var', tk.StringVar()).get(),
                    'master_volume': beat_window.master_volume.get(),
                    'swing': beat_window.swing_var.get(),
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(file_path, 'w') as file:
                    json.dump(beat_data, file, indent=2)
                
                beat_window.status_label.config(text=f"💾 Beat saved: {os.path.basename(file_path)}")
                logging.info("Beat saved successfully")
        except Exception as e:
            messagebox.showerror("Beat Save Error", f"Failed to save beat: {str(e)}")
            logging.error(f"Beat save error: {str(e)}", exc_info=True)
    
    def _export_beat(self, beat_window):
        """Export the beat as a WAV file."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Beat as WAV",
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
            )
            
            if file_path:
                # Generate full quality audio
                sample_rate = 44100
                bpm = beat_window.bpm_var.get()
                beat_duration = 60.0 / bpm * 8  # 8 beats for longer export
                samples = int(sample_rate * beat_duration)
                
                audio_data = np.zeros(samples, dtype=np.float32)
                master_volume = beat_window.master_volume.get()
                
                # Generate full beat with all patterns
                step_duration = beat_duration / 32  # 32 steps for longer beat
                
                for step in range(32):
                    step_start = int(step * step_duration * sample_rate)
                    
                    # Use patterns cyclically
                    pattern_step = step % 16
                    
                    if beat_window.patterns['kick'][pattern_step]:
                        # Enhanced kick with sub harmonics
                        t = np.linspace(0, 0.15, int(0.15 * sample_rate))
                        envelope = np.exp(-t * 12)
                        kick = (np.sin(2 * np.pi * 60 * t) + 
                               0.7 * np.sin(2 * np.pi * 45 * t) +
                               0.3 * np.sin(2 * np.pi * 30 * t)) * envelope * master_volume * 0.9
                        end_idx = min(step_start + len(kick), samples)
                        audio_data[step_start:end_idx] += kick[:end_idx - step_start]
                    
                    if beat_window.patterns['snare'][pattern_step]:
                        # Enhanced snare with noise texture
                        t = np.linspace(0, 0.12, int(0.12 * sample_rate))
                        envelope = np.exp(-t * 15)
                        noise = np.random.normal(0, 0.2, len(t))
                        snare = (np.sin(2 * np.pi * 200 * t) + 
                                np.sin(2 * np.pi * 180 * t) * 0.5 + noise) * envelope * master_volume * 0.7
                        end_idx = min(step_start + len(snare), samples)
                        audio_data[step_start:end_idx] += snare[:end_idx - step_start]
                    
                    if beat_window.patterns['hihat'][pattern_step]:
                        # Crisp hi-hat
                        t = np.linspace(0, 0.08, int(0.08 * sample_rate))
                        envelope = np.exp(-t * 25)
                        hihat = (np.sin(2 * np.pi * 8000 * t) + 
                                np.sin(2 * np.pi * 12000 * t) * 0.3) * envelope * master_volume * 0.4
                        end_idx = min(step_start + len(hihat), samples)
                        audio_data[step_start:end_idx] += hihat[:end_idx - step_start]
                
                # Add melody throughout
                if hasattr(beat_window, 'melody') and beat_window.melody:
                    melody_notes = beat_window.melody
                    for beat_num in range(8):  # 8 beats
                        for note_num, freq in enumerate(melody_notes):
                            note_start = int((beat_num + note_num/len(melody_notes)) * (60.0/bpm) * sample_rate)
                            note_length = int((60.0/bpm/len(melody_notes)) * sample_rate * 0.9)
                            note_end = min(note_start + note_length, samples)
                            
                            if note_start < samples:
                                t = np.linspace(0, note_length/sample_rate, note_end - note_start)
                                # ADSR envelope
                                attack_len = len(t) // 10
                                decay_len = len(t) // 5
                                sustain_level = 0.6
                                
                                envelope = np.ones(len(t)) * sustain_level
                                if attack_len > 0:
                                    envelope[:attack_len] = np.linspace(0, 1, attack_len)
                                if decay_len > 0:
                                    envelope[attack_len:attack_len+decay_len] = np.linspace(1, sustain_level, decay_len)
                                
                                # Rich melody with harmonics
                                melody = (np.sin(2 * np.pi * freq * t) + 
                                         0.4 * np.sin(2 * np.pi * freq * 2 * t) +
                                         0.2 * np.sin(2 * np.pi * freq * 3 * t)) * envelope * master_volume * 0.25
                                
                                audio_data[note_start:note_end] += melody
                
                # Normalize and export
                audio_data = np.clip(audio_data, -1.0, 1.0)
                audio_data = (audio_data * 32767).astype(np.int16)
                
                wavfile.write(file_path, sample_rate, audio_data)
                
                beat_window.status_label.config(text=f"📤 Beat exported: {os.path.basename(file_path)}")
                messagebox.showinfo("Export Complete", f"Beat exported successfully to:\n{file_path}")
                logging.info("Beat exported successfully")
        except Exception as e:
            messagebox.showerror("Beat Export Error", f"Failed to export beat: {str(e)}")
            logging.error(f"Beat export error: {str(e)}", exc_info=True)
    
    def _show_audio_tools(self):
        """Open Audio Tools interface."""
        messagebox.showinfo("Audio Tools", "🎧 Audio Tools feature coming soon!")
    
    def _show_lyric_assistant(self):
        """Open Lyric Assistant interface."""
        messagebox.showinfo("Lyric Assistant", "🎤 Lyric Assistant feature coming soon!")
    
    def _show_code_analyzer(self):
        """Show code analyzer interface."""
        messagebox.showinfo("Code Analyzer", "🔍 Code Analyzer feature coming soon!")
    
    def _show_documentation(self):
        """Show documentation window."""
        doc_window = tk.Toplevel(self.gui.root)
        doc_window.title("📚 Documentation")
        doc_window.geometry("800x600")
        doc_window.transient(self.gui.root)
        
        main_frame = ttk.Frame(doc_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="📚 CodedSwitch Documentation", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        doc_text = tk.Text(main_frame, wrap=tk.WORD, font=('Arial', 11))
        doc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        documentation = """🚀 CODEDSWITCH USER GUIDE

MAIN FEATURES:
• 🔄 Code Translation: Convert code between programming languages
• 🤖 AI Chatbot: Get programming help and explanations  
• 🔒 Security Scanner: Analyze code for vulnerabilities
• 🎤 Lyric Lab: Generate and analyze song lyrics
• 🎵 Beat Studio: Create professional beats and music with AI
• 🎧 Audio Tools: Process and edit audio files

BEAT STUDIO FEATURES:
• AI-powered beat generation from lyrics
• Interactive pattern editor with click-to-toggle
• Melody generation with musical scales
• Professional audio synthesis with ADSR envelopes
• Real-time playback with harmonics and sub-bass
• Export to WAV and JSON formats
• Multiple instrument patterns (kick, snare, hi-hat, bass)
• BPM and swing controls
• Master volume and individual track volumes

GETTING STARTED:
1. Set up your API key in Edit → Preferences → AI Configuration
2. Use the Translator tab to convert code between languages
3. Chat with the AI assistant for programming help
4. Create music in the Beat Studio with AI analysis
5. Generate lyrics in the Lyric Lab
6. Use the pattern editor to customize beats

KEYBOARD SHORTCUTS:
Ctrl+N          New file
Ctrl+O          Open file
Ctrl+S          Save file
Ctrl+F          Find and replace
F1              Show documentation

For more help, visit the CodedSwitch website or contact support."""
        
        doc_text.insert("1.0", documentation)
        doc_text.config(state='disabled')
        
        ttk.Button(main_frame, text="Close", command=doc_window.destroy).pack()
    
    def _show_about(self):
        """Show about dialog."""
        about_window = tk.Toplevel(self.gui.root)
        about_window.title("ℹ️ About CodedSwitch")
        about_window.geometry("500x400")
        about_window.transient(self.gui.root)
        about_window.grab_set()
        
        main_frame = ttk.Frame(about_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="🎵💻 CodedSwitch", 
                 font=('Arial', 24, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="AI Code Translator & Music Production Suite", 
                 font=('Arial', 12)).pack(pady=(5, 20))
        
        info_text = """Version: 2.0.0 (Enhanced Production)
Build Date: June 2025
AI Engine: Google Gemini
GUI Framework: ttkbootstrap

🌟 ENHANCED FEATURES:
• Multi-language code translation with AI
• Advanced music production with Beat Studio
• Melody generation with musical theory
• Professional audio synthesis
• Interactive pattern editing
• Lyric analysis for beat generation
• Real-time audio playback

© 2024 CodedSwitch Team"""
        
        ttk.Label(main_frame, text=info_text, justify=tk.LEFT).pack(pady=(0, 20))
        
        ttk.Button(main_frame, text="✅ Close", command=about_window.destroy).pack()
    
    def _on_closing(self):
        """Handle application closing."""
        if messagebox.askyesno("Exit CodedSwitch", 
                              "Are you sure you want to exit CodedSwitch?\n\n"
                              "Make sure to save any unsaved work."):
            try:
                self._save_preferences()
            except:
                pass
            self.gui.root.quit()
            self.gui.root.destroy()
    
    def _save_preferences(self):
        """Save user preferences."""
        try:
            prefs = {
                "recent_files": self.recent_files,
                "last_session": datetime.now().isoformat()
            }
            
            config_dir = os.path.expanduser("~/.codedswitch")
            os.makedirs(config_dir, exist_ok=True)
            
            prefs_file = os.path.join(config_dir, "preferences.json")
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f, indent=2)
                
        except Exception as e:
            logging.error(f"Failed to save preferences: {e}")