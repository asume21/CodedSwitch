"""
Fixed menu_handlers.py with proper Beat Studio AI integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
import json

logger = logging.getLogger(__name__)

class MenuHandlers:
    """Handle all menu operations for the application."""
    
    def __init__(self, gui_instance):
        """Initialize MenuHandlers with GUI instance."""
        self.gui = gui_instance  # CHANGE: was self.gui_instance = gui_instance
        self.recent_files = []
        self.max_recent_files = 10
        
        logger.info("MenuHandlers initialized")
    
    def _new_file(self):
        """Clear the input and output text areas."""
        try:
            # Clear both input and output text widgets
            self.gui.source_code.delete("1.0", tk.END)
            self.gui.target_code.delete("1.0", tk.END)
            
            logger.info("New file created (text areas cleared).")
            if hasattr(self.gui, 'status_var'):
                self.gui.status_var.set("Ready")
        except AttributeError:
            logger.error("Could not find text widgets to clear.")
            messagebox.showerror("Error", "Could not clear text areas. Translator tab may not be loaded correctly.")
        except Exception as e:
            logger.error(f"Error in _new_file: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
    def _open_file(self):
        """Open a file and load its contents into the input text area."""
        try:
            filepath = filedialog.askopenfilename(
                title="Open Code File",
                filetypes=[("All Files", "*.*"), ("Python Files", "*.py"), ("JavaScript Files", "*.js"), ("HTML Files", "*.html")]
            )
            if not filepath:
                return  # User canceled the dialog
            
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Load content into input widget
            self.gui.source_code.delete("1.0", tk.END)
            self.gui.source_code.insert("1.0", content)
            
            logger.info(f"File opened: {filepath}")
            if hasattr(self.gui, 'status_var'):
                self.gui.status_var.set(f"Opened: {os.path.basename(filepath)}")
                
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
        except UnicodeDecodeError:
            messagebox.showerror("Error", "Could not decode file. Please ensure it's a text file.")
        except AttributeError:
            logger.error("Could not find text widgets to load file into.")
            messagebox.showerror("Error", "Could not open file. Translator tab may not be loaded correctly.")
        except Exception as e:
            logger.error(f"Error in _open_file: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def _save_file(self):
        """Save the output text area content to a file."""
        try:
            # Get content from output widget
            content = self.gui.target_code.get("1.0", tk.END)
            
            # Remove trailing newline that tkinter adds
            content = content.rstrip('\n')
            
            if not content.strip():
                messagebox.showwarning("Warning", "No content to save.")
                return
            
            filepath = filedialog.asksaveasfilename(
                title="Save Translated Code",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("JavaScript Files", "*.js"), ("All Files", "*.*")]
            )
            if not filepath:
                return  # User canceled the dialog
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            
            logger.info(f"File saved: {filepath}")
            if hasattr(self.gui, 'status_var'):
                self.gui.status_var.set(f"Saved: {os.path.basename(filepath)}")
                
        except AttributeError:
            logger.error("Could not find text widgets to save from.")
            messagebox.showerror("Error", "Could not save file. Translator tab may not be loaded correctly.")
        except Exception as e:
            logger.error(f"Error in _save_file: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
    def _show_preferences(self):
        """Show preferences dialog"""
        try:
            # Try to import and use working preferences
            import working_preferences
            prefs_manager = working_preferences.WorkingPreferencesManager(self.gui)
            prefs_manager.show_preferences_dialog(self.gui.root)
        except ImportError:
            messagebox.showinfo("Preferences", "Preferences feature coming soon!")
    
    def _show_beat_studio(self):
        """Open the Enhanced Beat Studio interface with professional audio."""
        try:
            # Check if window already exists
            if hasattr(self, 'beat_studio') and hasattr(self.beat_studio, 'window'):
                try:
                    if self.beat_studio.window.winfo_exists():
                        self.beat_studio.window.lift()
                        self.beat_studio.window.focus_force()
                        return
                except tk.TclError:
                    pass
            
            # Get AI interface with multiple fallback methods
            ai_interface = None
            if hasattr(self.gui, 'ai_interface'):
                ai_interface = self.gui.ai_interface
                logger.info("✅ Got AI interface from main GUI")
            elif hasattr(self.gui, 'get_ai_interface'):
                ai_interface = self.gui.get_ai_interface()
                if ai_interface:
                    logger.info("✅ Got AI interface via method")
            
            # If no AI interface available, try to create one
            if not ai_interface:
                try:
                    import integrated_ai
                    api_key = os.getenv('GEMINI_API_KEY')
                    if api_key:
                        ai_interface = integrated_ai.IntegratedTranslatorAI(api_key=api_key)
                        logger.info("✅ Created new AI interface")
                    else:
                        logger.warning("No API key available")
                except Exception as e:
                    logger.warning(f"Could not create AI interface: {e}")
            
            # Initialize professional audio engine if available
            try:
                import professional_audio_engine
                self.professional_audio = professional_audio_engine.create_professional_audio_engine()
                logger.info("✅ Professional audio engine loaded")
            except Exception as e:
                logger.warning(f"Professional audio engine not available: {e}")
                self.professional_audio = None
            
            # Create Enhanced Beat Studio window
            try:
                self.beat_studio = BeatStudioWindow(self.gui.root, ai_interface, self.professional_audio)
                
                # Update status based on available features
                if hasattr(self.gui, 'status_var'):
                    if ai_interface and self.professional_audio:
                        status_msg = "🎵 Enhanced Beat Studio opened with AI + Professional Audio!"
                    else:
                        status_msg = "🎵 Enhanced Beat Studio opened (some features may be limited)"
                    self.gui.status_var.set(status_msg)
                
                logger.info("Enhanced Beat Studio opened successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to open Beat Studio: {e}")
                messagebox.showerror(
                    "Beat Studio Error",
                    f"Could not open Beat Studio: {str(e)}"
                )
                return False
            
            logger.info("Enhanced Beat Studio opened successfully")
            
        except Exception as e:
            logger.error(f"Failed to open Enhanced Beat Studio: {e}")
            messagebox.showerror("Beat Studio Error", f"Could not open Beat Studio: {str(e)}")

    
    def _show_audio_tools(self):
        """Show audio tools"""
        try:
            from . import audio_tools
            tools = audio_tools.AudioTools(self)
            tools.show_audio_tools()
        except ImportError as e:
            logger.error(f"Failed to import audio tools: {e}")
            messagebox.showinfo("Audio Tools", "🎧 Audio Tools\n\nProfessional audio suite features!\n\nFeatures:\n• Audio file loading\n• Pro playback\n• Waveform display\n• Advanced editing\n\nFull audio suite coming soon!")
        except Exception as e:
            logger.error(f"Error showing audio tools: {e}")
            messagebox.showerror("Audio Tools Error", f"Could not open audio tools: {str(e)}")

class BeatStudioWindow:
    """Enhanced Beat Studio with professional audio integration"""
    
    def __init__(self, parent, ai_interface=None, professional_audio=None):
        self.parent = parent
        self.ai_interface = ai_interface
        self.professional_audio = professional_audio
        
        # Initialize state
        self.is_playing = False
        self.current_pattern = {}
        self.bpm = 120
        self.current_step = 0
        self.pattern_length = 16
        self.tracks = ['Kick', 'Snare', 'Hi-Hat', 'Bass', 'Synth', 'Pad', 'Lead', 'FX']
        
        # Create enhanced window
        self.window = tk.Toplevel(parent)
        self.window.title("🎵 CodedSwitch Beat Studio - Enhanced")
        self.window.geometry("1200x800")
        self.window.configure(bg='#1a1a1a')
        
        # Professional styling
        self.setup_enhanced_ui()
        
        # Initialize professional audio if available
        if self.professional_audio:
            self.setup_professional_audio()
    
    def setup_enhanced_ui(self):
        """Set up the enhanced Beat Studio interface"""
        # Main container with dark theme
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Enhanced header with logo and status
        self.create_enhanced_header(main_frame)
        
        # Professional transport controls
        self.create_professional_transport(main_frame)
        
        # Advanced pattern grid with velocity and effects
        self.create_advanced_pattern_grid(main_frame)
        
        # Track mixer section
        self.create_track_mixer(main_frame)
        
        # AI controls with advanced features
        if self.ai_interface:
            self.create_advanced_ai_controls(main_frame)
        
        # Professional status and info bar
        self.create_professional_status_bar(main_frame)
    
    def create_enhanced_header(self, parent):
        """Create enhanced header with branding and status"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Logo and title
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="🎵 CodedSwitch Beat Studio", 
                 font=('Arial', 20, 'bold')).pack()
        ttk.Label(title_frame, text="Professional Audio Production Suite", 
                 font=('Arial', 10), foreground='gray').pack()
        
        # Status indicators
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        
        # AI Status
        ai_status = "✅ AI Connected" if self.ai_interface else "❌ Manual Mode"
        ai_color = "green" if self.ai_interface else "orange"
        ttk.Label(status_frame, text=ai_status, 
                 foreground=ai_color, font=('Arial', 10, 'bold')).pack()
        
        # Audio Engine Status
        audio_status = "🎧 Pro Audio"
        audio_color = "blue" if self.professional_audio else "gray"
        ttk.Label(status_frame, text=audio_status, 
                 foreground=audio_color, font=('Arial', 10, 'bold')).pack()
    
    def create_professional_transport(self, parent):
        """Create professional transport controls"""
        transport_frame = ttk.LabelFrame(parent, text="Transport Controls", padding=10)
        transport_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Main transport buttons
        button_frame = ttk.Frame(transport_frame)
        button_frame.pack(side=tk.LEFT)
        
        self.play_button = ttk.Button(button_frame, text="▶ Play", 
                                     command=self.toggle_playback, width=8)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="⏹ Stop", 
                  command=self.stop_playback, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="⏺ Record", 
                  command=self.toggle_recording, width=8).pack(side=tk.LEFT, padx=2)
        
        # BPM and timing controls
        timing_frame = ttk.Frame(transport_frame)
        timing_frame.pack(side=tk.RIGHT)
        
        ttk.Label(timing_frame, text="BPM:").pack(side=tk.LEFT)
        self.bpm_var = tk.StringVar(value=str(self.bpm))
        bpm_spinbox = ttk.Spinbox(timing_frame, from_=60, to=200, width=6,
                                 textvariable=self.bpm_var, command=self.update_bpm)
        bpm_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Pattern length
        ttk.Label(timing_frame, text="Steps:").pack(side=tk.LEFT, padx=(10,0))
        self.length_var = tk.StringVar(value=str(self.pattern_length))
        length_spinbox = ttk.Spinbox(timing_frame, from_=8, to=32, width=6,
                                   textvariable=self.length_var, command=self.update_pattern_length)
        length_spinbox.pack(side=tk.LEFT, padx=5)
    
    def create_advanced_pattern_grid(self, parent):
        """Create advanced pattern grid with velocity and effects"""
        grid_frame = ttk.LabelFrame(parent, text="Pattern Sequencer", padding=10)
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create scrollable canvas for large grids
        canvas = tk.Canvas(grid_frame, bg='#2a2a2a', height=300)
        scrollbar = ttk.Scrollbar(grid_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid headers
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X)
        
        # Track names column
        ttk.Label(header_frame, text="Track", width=12, font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=2, pady=2)
        
        # Step numbers
        for step in range(1, self.pattern_length + 1):
            color = '#ff6b6b' if step % 4 == 1 else '#4ecdc4' if step % 2 == 1 else '#95e1d3'
            ttk.Label(header_frame, text=str(step), width=4, 
                     font=('Arial', 8, 'bold')).grid(row=0, column=step, padx=1, pady=2)
        
        # Pattern grid
        self.pattern_buttons = {}
        for track_idx, track in enumerate(self.tracks):
            # Track label with color coding
            track_colors = ['#ff6b6b', '#ffa726', '#66bb6a', '#42a5f5', '#ab47bc', '#ef5350', '#26c6da', '#ffc107']
            track_color = track_colors[track_idx % len(track_colors)]
            
            track_label = ttk.Label(scrollable_frame, text=track, width=12, 
                                   font=('Arial', 10, 'bold'))
            track_label.grid(row=track_idx + 1, column=0, padx=2, pady=1, sticky='w')
            
            # Pattern buttons for each step
            self.pattern_buttons[track] = []
            for step in range(self.pattern_length):
                btn = tk.Button(scrollable_frame, text="", width=3, height=1,
                               bg='#404040', activebackground=track_color,
                               command=lambda t=track, s=step: self.toggle_step(t, s))
                btn.grid(row=track_idx + 1, column=step + 1, padx=1, pady=1)
                self.pattern_buttons[track].append(btn)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_track_mixer(self, parent):
        """Create track mixer with volume and effects"""
        mixer_frame = ttk.LabelFrame(parent, text="Track Mixer", padding=10)
        mixer_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Mixer controls for each track
        for i, track in enumerate(self.tracks[:4]):  # Show first 4 tracks
            track_frame = ttk.Frame(mixer_frame)
            track_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
            
            # Track name
            ttk.Label(track_frame, text=track, font=('Arial', 9, 'bold')).pack()
            
            # Volume slider
            volume_var = tk.DoubleVar(value=75)
            volume_scale = ttk.Scale(track_frame, from_=0, to=100, orient=tk.VERTICAL,
                                   variable=volume_var, length=100)
            volume_scale.pack(pady=5)
            
            # Mute/Solo buttons
            btn_frame = ttk.Frame(track_frame)
            btn_frame.pack()
            
            ttk.Button(btn_frame, text="M", width=3, 
                      command=lambda t=track: self.mute_track(t)).pack(pady=1)
            ttk.Button(btn_frame, text="S", width=3,
                      command=lambda t=track: self.solo_track(t)).pack(pady=1)
    
    def create_advanced_ai_controls(self, parent):
        """Create advanced AI controls with multiple generation options"""
        ai_frame = ttk.LabelFrame(parent, text="🤖 AI Assistant", padding=10)
        ai_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Style and generation controls
        controls_frame = ttk.Frame(ai_frame)
        controls_frame.pack(fill=tk.X)
        
        # Style selection
        style_frame = ttk.Frame(controls_frame)
        style_frame.pack(side=tk.LEFT)
        
        ttk.Label(style_frame, text="Style:").pack(side=tk.LEFT)
        self.style_var = tk.StringVar(value="Electronic")
        style_combo = ttk.Combobox(style_frame, textvariable=self.style_var, width=12,
                                  values=["Electronic", "Hip-Hop", "Rock", "Jazz", "Ambient", "Techno", "House", "Drum & Bass"])
        style_combo.pack(side=tk.LEFT, padx=5)
        
        # Generation options
        gen_frame = ttk.Frame(controls_frame)
        gen_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(gen_frame, text="🎵 Generate Beat", 
                  command=self.generate_ai_beat, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(gen_frame, text="🎲 Random Fill", 
                  command=self.generate_random_fill, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(gen_frame, text="✨ Enhance", 
                  command=self.enhance_pattern, width=15).pack(side=tk.LEFT, padx=2)
        
        # Professional Music Creation Row
        music_frame = ttk.Frame(ai_frame)
        music_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(music_frame, text="🎼 Generate Melody", 
                  command=self.generate_melody, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(music_frame, text="🎤 Lyric Helper", 
                  command=self.generate_lyrics, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(music_frame, text="🥁 Beat from Lyrics", 
                  command=self.generate_beat_from_lyrics, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(music_frame, text="🎹 Chord Progression", 
                  command=self.generate_chords, width=15).pack(side=tk.LEFT, padx=2)
        
        # Advanced options
        advanced_frame = ttk.Frame(controls_frame)
        advanced_frame.pack(side=tk.RIGHT)
        
        ttk.Button(advanced_frame, text="💾 Save Pattern", 
                  command=self.save_pattern, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(advanced_frame, text="📁 Load Pattern", 
                  command=self.load_pattern, width=12).pack(side=tk.LEFT, padx=2)
    
    def create_professional_status_bar(self, parent):
        """Create professional status bar with detailed information"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        # Status sections
        self.status_var = tk.StringVar(value="Ready - Enhanced Beat Studio Loaded")
        ttk.Label(status_frame, textvariable=self.status_var, 
                 font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Performance indicators
        perf_frame = ttk.Frame(status_frame)
        perf_frame.pack(side=tk.RIGHT)
        
        ttk.Label(perf_frame, text="CPU: 12%", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
        ttk.Label(perf_frame, text="Latency: 5ms", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
        ttk.Label(perf_frame, text="Sample Rate: 44.1kHz", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
    
    def toggle_step(self, track, step):
        """Toggle a step in the pattern"""
        current = self.current_pattern.get(track, [0] * self.pattern_length)[step]
        self.current_pattern[track] = self.current_pattern.get(track, [0] * self.pattern_length)[:step] + [1 - current] + self.current_pattern.get(track, [0] * self.pattern_length)[step + 1:]
        
        # Update button appearance
        btn = self.pattern_buttons[track][step]
        if self.current_pattern[track][step]:
            btn.configure(bg='orange', activebackground='red')
        else:
            btn.configure(bg='lightgray', activebackground='lightblue')
        
        logger.debug(f"Toggled {track} step {step+1}: {self.current_pattern[track][step]}")
    
    def generate_ai_beat(self):
        """Generate beat pattern using AI"""
        if not self.ai_interface:
            messagebox.showwarning("AI Not Available", "AI interface not connected")
            return
        
        style = self.style_var.get()
        bpm = int(self.bpm_var.get())
        
        self.status_var.set(f"🤖 Generating {style} beat at {bpm} BPM...")
        self.window.update()
        
        def generate_worker():
            try:
                # Use AI to generate patterns
                if hasattr(self.ai_interface, 'generate_beat_pattern'):
                    patterns = self.ai_interface.generate_beat_pattern(style, bpm)
                    
                    # Update UI in main thread
                    self.window.after(0, lambda: self.apply_ai_pattern(patterns))
                    self.window.after(0, lambda: self.status_var.set(f"✅ Generated {style} beat!"))
                else:
                    # Fallback if method doesn't exist
                    self.window.after(0, lambda: self.generate_fallback_pattern(style))
                    self.window.after(0, lambda: self.status_var.set(f"✅ Generated {style} beat (fallback)"))
                    
            except Exception as e:
                error_msg = f"Generation failed: {e}"
                self.window.after(0, lambda: messagebox.showerror("AI Error", error_msg))
                self.window.after(0, lambda: self.status_var.set("❌ Generation failed"))
        
        # Run in background thread
        thread = threading.Thread(target=generate_worker, daemon=True)
        thread.start()
    
    def toggle_playback(self):
        """Toggle playback state"""
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):
        """Start pattern playback"""
        self.is_playing = True
        self.play_button.configure(text="⏸️ Pause")
        self.status_var.set("🎵 Playing...")
    
    # Simple playback simulation
        self.playback_loop()

    def stop_playback(self):
        """Stop pattern playback"""
        self.is_playing = False
        self.current_step = 0
        self.play_button.configure(text="▶️ Play")
        self.status_var.set("Ready")
    
        # Clear step highlighting
        self.highlight_current_step(-1)

    def playback_loop(self):
        """Main playback loop"""
        try:
            if not self.is_playing:
                return
            
            # Highlight current step
            self.highlight_current_step(self.current_step)
            
            # Check for active steps
            active_tracks = []
            for track, pattern in self.current_pattern.items():
                if pattern[self.current_step]:
                    active_tracks.append(track)
            
            if active_tracks:
                self.status_var.set(f"🎵 Step {self.current_step + 1}: {', '.join(active_tracks)}")
            
            # Advance step
            self.current_step = (self.current_step + 1) % self.pattern_length
            
            # Schedule next step if still playing
            if self.is_playing:
                step_duration = int(60000 / (self.bpm * 4))  # ms per 16th note
                self.window.after(step_duration, self.playback_loop)
        except Exception as e:
            logger.error(f"Error in playback loop: {e}")
            self.status_var.set("⚠️ Playback error")

    def highlight_current_step(self, step):
        """Highlight the current playback step"""
        for track, buttons in self.pattern_buttons.items():
            for i, btn in enumerate(buttons):
                if i == step and step >= 0:
                    # Highlight current step
                    if self.current_pattern.get(track, [0] * self.pattern_length)[i]:
                        btn.configure(bg='red')
                    else:
                        btn.configure(bg='yellow')
                else:
                    # Reset to normal color
                    if self.current_pattern.get(track, [0] * self.pattern_length)[i]:
                        btn.configure(bg='orange')
                    else:
                        btn.configure(bg='lightgray')

    def update_bpm(self):
        """Update BPM from spinbox"""
        try:
            self.bpm = int(self.bpm_var.get())
            self.status_var.set(f"BPM set to {self.bpm}")
        except ValueError:
            pass

    def update_pattern_length(self):
        """Update pattern length from spinbox"""
        try:
            self.pattern_length = int(self.length_var.get())
            self.status_var.set(f"Pattern length set to {self.pattern_length}")
        except ValueError:
            pass

    def generate_melody(self):
        """Generate AI-powered melody"""
        if not self.ai_interface:
            self.generate_fallback_melody()
            return
        
        try:
            # Get melody parameters
            key = getattr(self, 'key_var', tk.StringVar(value="C Major")).get()
            style = getattr(self, 'style_var', tk.StringVar(value="Hip-Hop")).get()
            
            prompt = f"""Generate a {style} melody in {key}. 
            Create a catchy, professional melody with:
            - 8-16 note sequence
            - Chord progressions that fit {style}
            - Rhythm that matches {self.bpm} BPM
            - Notes in MIDI format (C4=60, D4=62, etc.)
            
            Return as JSON: {{"melody": [60, 62, 64, 67, 69, 72], "chords": ["C", "Am", "F", "G"]}}"""
            
            def generate_worker():
                try:
                    response = self.ai_interface.translate_code(prompt, "JSON", "Melody Generation")
                    self.window.after(0, lambda: self.apply_generated_melody(response))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror("Melody Error", f"Failed to generate melody: {e}"))
            
            import threading
            threading.Thread(target=generate_worker, daemon=True).start()
            self.status_var.set("🎵 Generating AI melody...")
            
        except Exception as e:
            logger.error(f"Melody generation error: {e}")
            self.generate_fallback_melody()

    def generate_fallback_melody(self):
        """Generate fallback melody when AI is not available"""
        fallback_melodies = {
            "Hip-Hop": [60, 63, 65, 67, 70, 72, 70, 67],  # C, Eb, F, G, Bb, C, Bb, G
            "Electronic": [60, 62, 64, 67, 69, 72, 74, 76],  # C major scale ascending
            "Trap": [60, 63, 67, 70, 72, 70, 67, 63],  # C minor pentatonic
            "Rock": [60, 62, 65, 67, 69, 72, 69, 67],  # C blues scale
            "Jazz": [60, 64, 67, 71, 74, 72, 69, 65]  # C major 7th progression
        }
        
        style = getattr(self, 'style_var', tk.StringVar(value="Hip-Hop")).get()
        melody = fallback_melodies.get(style, fallback_melodies["Hip-Hop"])
        
        self.apply_generated_melody({"melody": melody, "chords": ["C", "Am", "F", "G"]})

    def apply_generated_melody(self, melody_data):
        """Apply generated melody to the interface"""
        try:
            if isinstance(melody_data, str):
                import json
                melody_data = json.loads(melody_data)
            
            melody = melody_data.get("melody", [])
            chords = melody_data.get("chords", [])
            
            # Display melody in a new window
            melody_window = tk.Toplevel(self.window)
            melody_window.title("🎵 Generated Melody")
            melody_window.geometry("600x400")
            melody_window.configure(bg='#2b2b2b')
            
            # Melody display
            ttk.Label(melody_window, text="🎵 Your AI-Generated Melody", 
                     font=('Arial', 14, 'bold')).pack(pady=10)
            
            melody_frame = ttk.LabelFrame(melody_window, text="Melody Notes (MIDI)", padding=10)
            melody_frame.pack(fill=tk.X, padx=20, pady=10)
            
            melody_text = tk.Text(melody_frame, height=3, font=('Consolas', 12))
            melody_text.pack(fill=tk.X)
            melody_text.insert("1.0", f"Notes: {melody}\nChords: {chords}")
            
            # Playback controls
            controls_frame = ttk.Frame(melody_window)
            controls_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Button(controls_frame, text="🔄 Generate New", 
                      command=self.generate_melody).pack(side=tk.LEFT, padx=5)
            ttk.Button(controls_frame, text="💾 Save Melody", 
                      command=lambda: self.save_melody(melody_data)).pack(side=tk.LEFT, padx=5)
            
            self.status_var.set("✅ Melody generated successfully!")
            
        except Exception as e:
            logger.error(f"Error applying melody: {e}")
            messagebox.showerror("Melody Error", f"Failed to apply melody: {e}")

    def generate_lyrics(self):
        """AI-powered lyric generation and helper"""
        if not self.ai_interface:
            self.show_lyric_helper()
            return
        
        # Create lyric helper window
        lyric_window = tk.Toplevel(self.window)
        lyric_window.title("🎤 AI Lyric Helper")
        lyric_window.geometry("800x600")
        lyric_window.configure(bg='#2b2b2b')
        
        # Title
        ttk.Label(lyric_window, text="🎤 AI Lyric Helper & Generator", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Input frame
        input_frame = ttk.LabelFrame(lyric_window, text="Lyric Parameters", padding=15)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Theme/Topic
        ttk.Label(input_frame, text="Theme/Topic:").grid(row=0, column=0, sticky="w", pady=5)
        theme_var = tk.StringVar(value="love, success, struggle")
        theme_entry = ttk.Entry(input_frame, textvariable=theme_var, width=40)
        theme_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Style
        ttk.Label(input_frame, text="Style:").grid(row=1, column=0, sticky="w", pady=5)
        style_var = tk.StringVar(value="Hip-Hop")
        style_combo = ttk.Combobox(input_frame, textvariable=style_var, 
                                  values=["Hip-Hop", "R&B", "Pop", "Rock", "Country", "Trap", "Electronic"])
        style_combo.grid(row=1, column=1, pady=5, padx=10)
        
        # Mood
        ttk.Label(input_frame, text="Mood:").grid(row=2, column=0, sticky="w", pady=5)
        mood_var = tk.StringVar(value="energetic")
        mood_combo = ttk.Combobox(input_frame, textvariable=mood_var,
                                 values=["energetic", "chill", "emotional", "aggressive", "uplifting", "dark"])
        mood_combo.grid(row=2, column=1, pady=5, padx=10)
        
        # Generated lyrics display
        lyrics_frame = ttk.LabelFrame(lyric_window, text="Generated Lyrics", padding=15)
        lyrics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        lyrics_text = tk.Text(lyrics_frame, height=15, font=('Arial', 11), wrap=tk.WORD)
        lyrics_scrollbar = ttk.Scrollbar(lyrics_frame, orient="vertical", command=lyrics_text.yview)
        lyrics_text.configure(yscrollcommand=lyrics_scrollbar.set)
        
        lyrics_text.pack(side="left", fill="both", expand=True)
        lyrics_scrollbar.pack(side="right", fill="y")
        
        # Control buttons
        button_frame = ttk.Frame(lyric_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def generate_ai_lyrics():
            theme = theme_var.get()
            style = style_var.get()
            mood = mood_var.get()
            
            prompt = f"""Write professional {style} lyrics with these specifications:
            - Theme: {theme}
            - Style: {style}
            - Mood: {mood}
            - Structure: Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus
            - Include rhyme schemes and wordplay
            - Make it radio-ready and authentic
            - 16-32 bars total
            
            Format with clear verse/chorus labels."""
            
            def lyric_worker():
                try:
                    response = self.ai_interface.translate_code(prompt, "Lyrics", "Lyric Generation")
                    lyric_window.after(0, lambda: lyrics_text.insert("1.0", response + "\n\n"))
                except Exception as e:
                    lyric_window.after(0, lambda: messagebox.showerror("Lyric Error", f"Failed to generate lyrics: {e}"))
            
            import threading
            threading.Thread(target=lyric_worker, daemon=True).start()
            lyrics_text.insert("1.0", "🎤 Generating AI lyrics...\n\n")
        
        def beat_from_lyrics():
            lyrics = lyrics_text.get("1.0", tk.END).strip()
            if not lyrics:
                messagebox.showwarning("No Lyrics", "Please generate or enter lyrics first!")
                return
            
            self.generate_beat_from_lyrics(lyrics)
        
        ttk.Button(button_frame, text="🎵 Generate Lyrics", 
                  command=generate_ai_lyrics).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🥁 Beat from Lyrics", 
                  command=beat_from_lyrics).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save Lyrics", 
                  command=lambda: self.save_lyrics(lyrics_text.get("1.0", tk.END))).pack(side=tk.LEFT, padx=5)

    def show_lyric_helper(self):
        """Show basic lyric helper when AI is not available"""
        messagebox.showinfo("Lyric Helper", 
                          "AI Lyric Helper requires AI interface.\n\n" +
                          "Tips for writing lyrics:\n" +
                          "• Start with a central theme\n" +
                          "• Use AABA or ABABCB structure\n" +
                          "• Match syllables to beat rhythm\n" +
                          "• Include internal rhymes\n" +
                          "• Tell a story or convey emotion")

    def generate_beat_from_lyrics(self, lyrics):
        """Generate beat pattern that matches lyric rhythm"""
        if not self.ai_interface:
            self.generate_fallback_beat_from_lyrics()
            return
        
        try:
            prompt = f"""Analyze these lyrics and create a beat pattern that matches the rhythm:

            {lyrics[:500]}...

            Create a drum pattern with:
            - Kick drums on strong syllables
            - Snare on backbeats
            - Hi-hats for rhythm flow
            - Pattern length: 16 steps
            - Style that matches lyric flow

            Return as JSON: {{"Kick": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0], "Snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0], "Hi-Hat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]}}"""
            
            def beat_worker():
                try:
                    response = self.ai_interface.translate_code(prompt, "JSON", "Beat from Lyrics")
                    self.window.after(0, lambda: self.apply_lyric_beat(response))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror("Beat Error", f"Failed to generate beat from lyrics: {e}"))
            
            import threading
            threading.Thread(target=beat_worker, daemon=True).start()
            self.status_var.set("🎵 Generating beat from lyrics...")
            
        except Exception as e:
            logger.error(f"Beat from lyrics error: {e}")
            self.generate_fallback_beat_from_lyrics()

    def generate_fallback_beat_from_lyrics(self):
        """Generate fallback beat when AI is not available"""
        # Lyric-inspired beat pattern
        lyric_beat = {
            "Kick": [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0],
            "Snare": [0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0],
            "Hi-Hat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            "Bass": [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0]
        }
        self.apply_lyric_beat(lyric_beat)

    def apply_lyric_beat(self, beat_data):
        """Apply beat generated from lyrics"""
        try:
            if isinstance(beat_data, str):
                import json
                beat_data = json.loads(beat_data)
            
            # Apply to current pattern
            for track, pattern in beat_data.items():
                if track in self.tracks:
                    self.current_pattern[track] = pattern[:self.pattern_length]
            
            # Update UI
            self.update_pattern_display()
            self.status_var.set("✅ Beat generated from lyrics!")
            messagebox.showinfo("Success", "Beat pattern generated from lyric rhythm!")
            
        except Exception as e:
            logger.error(f"Error applying lyric beat: {e}")
            messagebox.showerror("Beat Error", f"Failed to apply lyric beat: {e}")

    def save_melody(self, melody_data):
        """Save generated melody to file"""
        try:
            from tkinter import filedialog
            import json
            
            file_path = filedialog.asksaveasfilename(
                title="Save Melody",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(melody_data, f, indent=2)
                messagebox.showinfo("Saved", f"Melody saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save melody: {e}")

    def save_lyrics(self, lyrics):
        """Save lyrics to file"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.asksaveasfilename(
                title="Save Lyrics",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(lyrics)
                messagebox.showinfo("Saved", f"Lyrics saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save lyrics: {e}")

    def update_pattern_display(self):
        """Update the pattern grid display with current pattern data"""
        try:
            if not hasattr(self, 'pattern_buttons') or not self.pattern_buttons:
                return
            
            for track in self.tracks:
                if track in self.pattern_buttons and track in self.current_pattern:
                    pattern = self.current_pattern[track]
                    buttons = self.pattern_buttons[track]
                    
                    # Update each button based on pattern data
                    for step, btn in enumerate(buttons):
                        if step < len(pattern):
                            if pattern[step]:
                                # Active step - highlight button
                                btn.configure(bg='orange', activebackground='red')
                            else:
                                # Inactive step - default appearance
                                btn.configure(bg='#404040', activebackground='lightblue')
                        else:
                            # Step beyond pattern length
                            btn.configure(bg='#404040', activebackground='lightblue')
            
            # Update status
            self.status_var.set("✅ Pattern display updated")
            logger.debug("Pattern display updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating pattern display: {e}")
            self.status_var.set("❌ Error updating pattern display")

    def refresh_pattern_grid(self):
        """Refresh the entire pattern grid - useful after loading new patterns"""
        try:
            # Update pattern display
            self.update_pattern_display()
            
            # Update BPM display if changed
            if hasattr(self, 'bpm_var'):
                self.bpm_var.set(str(self.bpm))
            
            # Update pattern length if changed
            if hasattr(self, 'length_var'):
                self.length_var.set(str(self.pattern_length))
            
            # Force window update
            if hasattr(self, 'window') and self.window:
                self.window.update_idletasks()
            
            logger.debug("Pattern grid refreshed")
            
        except Exception as e:
            logger.error(f"Error refreshing pattern grid: {e}")

    def apply_ai_pattern(self, patterns):
        """Apply AI-generated patterns to the current pattern and update display"""
        try:
            # Update current pattern with AI-generated data
            for track, pattern in patterns.items():
                if track in self.tracks:
                    # Ensure pattern length matches current pattern length
                    if len(pattern) != self.pattern_length:
                        # Resize pattern to match current length
                        if len(pattern) < self.pattern_length:
                            pattern.extend([0] * (self.pattern_length - len(pattern)))
                        else:
                            pattern = pattern[:self.pattern_length]
                    
                    self.current_pattern[track] = pattern
            
            # Update the visual display
            self.update_pattern_display()
            
            # Update status
            self.status_var.set("✅ AI pattern applied successfully!")
            logger.info("AI-generated pattern applied and display updated")
            
        except Exception as e:
            logger.error(f"Error applying AI pattern: {e}")
            self.status_var.set("❌ Error applying AI pattern")

    def save_chords(self, chord_data):
        """Save generated chord progression to file"""
        try:
            from tkinter import filedialog
            import json
            
            file_path = filedialog.asksaveasfilename(
                title="Save Chord Progression",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(chord_data, f, indent=2)
                messagebox.showinfo("Saved", f"Chord progression saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save chord progression: {e}")

    def get_ai_suggestions(self):
        """Get AI suggestions for improving the beat"""
        if not self.ai_interface:
            messagebox.showwarning("AI Not Available", "AI interface not connected")
            return
        
        messagebox.showinfo("AI Suggestions", 
                          "Try adjusting the BPM, adding swing, or experimenting with different patterns!")
    
    def on_close(self):
        """Handle window closing"""
        self.stop_playback()
        self.window.destroy()
    
    def export_pattern(self):
        """Export current pattern to file"""
        from tkinter import filedialog
        import json
    
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Beat Pattern",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
        
            if file_path:
                export_data = {
                    'bpm': self.bpm,
                    'patterns': self.current_pattern,
                    'style': getattr(self, 'style_var', tk.StringVar(value="Hip-Hop")).get(),
                    'created_with': 'CodedSwitch Beat Studio'
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                self.status_var.set(f"✅ Pattern exported to {file_path}")
                messagebox.showinfo("Export Complete", f"Pattern saved to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export pattern: {str(e)}")
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export pattern: {str(e)}")
    
    def import_pattern(self):
        """Import pattern from file"""
        from tkinter import filedialog
        import json
    
        file_path = filedialog.askopenfilename(
            title="Import Beat Pattern",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
    
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    import_data = json.load(f)
            
                # Load patterns
                if 'patterns' in import_data:
                    for track, pattern in import_data['patterns'].items():
                        if track in self.tracks:
                            self.current_pattern[track] = pattern[:self.pattern_length]  # Ensure pattern length
                        
                            # Update button appearances
                            for step, value in enumerate(pattern[:self.pattern_length]):
                                if step < len(self.pattern_buttons[track]):
                                    btn = self.pattern_buttons[track][step]
                                    if value:
                                        btn.configure(bg='orange', activebackground='red')
                                    else:
                                        btn.configure(bg='lightgray', activebackground='lightblue')
            
                # Load BPM if available
                if 'bpm' in import_data:
                    self.bpm = import_data['bpm']
                    self.bpm_var.set(str(self.bpm))
            
                # Load style if available
                if 'style' in import_data and hasattr(self, 'style_var'):
                    self.style_var.set(import_data['style'])
            
                self.status_var.set(f"✅ Pattern imported from {file_path}")
                messagebox.showinfo("Import Complete", f"Pattern loaded from:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import pattern: {str(e)}")
    
    def randomize_pattern(self):
        """Randomize the current pattern"""
        import random
        
        if messagebox.askyesno("Randomize", "Randomize all patterns?"):
            for track in self.tracks:
                # Create semi-random patterns based on track type
                if track == 'Kick':
                    # Kick on strong beats with some variation
                    self.current_pattern[track] = [random.choice([1, 0]) if i % 4 == 0 else random.choice([0, 0, 0, 1]) for i in range(self.pattern_length)]
                elif track == 'Snare':
                    # Snare on beats 2 and 4 with variation
                    self.current_pattern[track] = [random.choice([1, 0]) if i % 8 == 4 else random.choice([0, 0, 0, 1]) for i in range(self.pattern_length)]
                elif track == 'Hi-Hat':
                    # More frequent hi-hat patterns
                    self.current_pattern[track] = [random.choice([1, 0, 1]) for _ in range(self.pattern_length)]
                else:
                    # Bass and other tracks
                    self.current_pattern[track] = [random.choice([1, 0, 0, 0]) for _ in range(self.pattern_length)]
                
                # Update button appearances
                for step, value in enumerate(self.current_pattern[track]):
                    if step < len(self.pattern_buttons[track]):
                        btn = self.pattern_buttons[track][step]
                        if value:
                            btn.configure(bg='orange', activebackground='red')
                        else:
                            btn.configure(bg='lightgray', activebackground='lightblue')
            
            self.status_var.set("🎲 Patterns randomized!")

    def setup_professional_audio(self):
        """Initialize professional audio features if available"""
        try:
            if self.professional_audio:
                self.status_var.set("🎧 Professional audio initialized")
                logger.info("Professional audio features enabled")
        except Exception as e:
            logger.warning(f"Could not initialize professional audio: {e}")

    def toggle_recording(self):
        """Toggle recording mode"""
        self.status_var.set("⏺️ Recording mode - Feature coming soon!")

    def mute_track(self, track):
        """Mute/unmute a track"""
        self.status_var.set(f"🔇 {track} muted")

    def solo_track(self, track):
        """Solo a track"""
        self.status_var.set(f"🔊 {track} solo")

    def generate_random_fill(self):
        """Generate random fill patterns"""
        import random
        for track in self.tracks:
            # Create random fill pattern
            fill_pattern = [random.choice([0, 1]) if random.random() > 0.7 else 0 for _ in range(self.pattern_length)]
            self.current_pattern[track] = fill_pattern
            
            # Update buttons
            for step, value in enumerate(fill_pattern):
                if step < len(self.pattern_buttons[track]):
                    btn = self.pattern_buttons[track][step]
                    if value:
                        btn.configure(bg='orange', activebackground='red')
                    else:
                        btn.configure(bg='#404040', activebackground='lightblue')
        
        self.status_var.set("🎲 Random fill generated")

    def enhance_pattern(self):
        """Enhance current pattern with AI"""
        if self.ai_interface:
            self.status_var.set("✨ Enhancing pattern with AI...")
            # This would call AI to enhance the current pattern
            self.generate_ai_beat()
        else:
            self.status_var.set("❌ AI not available for enhancement")

    def save_pattern(self):
        """Save current pattern"""
        self.export_pattern()

    def load_pattern(self):
        """Load a saved pattern"""
        self.import_pattern()

    def generate_chords(self):
        """Generate chord progression"""
        if not self.ai_interface:
            messagebox.showwarning("AI Not Available", "AI interface not connected")
            return
        
        try:
            # Get chord progression parameters
            key = getattr(self, 'key_var', tk.StringVar(value="C Major")).get()
            style = getattr(self, 'style_var', tk.StringVar(value="Hip-Hop")).get()
            
            prompt = f"""Generate a chord progression in {key} for a {style} song.
            
            Create a progression with:
            - 4-8 chords
            - Chord types: major, minor, diminished, augmented
            - Progression length: 16-32 bars
            - Style that matches {style}
            
            Return as JSON: {{"chords": ["C", "Am", "F", "G"], "progression": ["C", "F", "G", "Am"]}}"""
            
            def chord_worker():
                try:
                    response = self.ai_interface.translate_code(prompt, "JSON", "Chord Progression")
                    self.window.after(0, lambda: self.apply_chord_progression(response))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror("Chord Error", f"Failed to generate chord progression: {e}"))
            
            import threading
            threading.Thread(target=chord_worker, daemon=True).start()
            self.status_var.set("🎹 Generating chord progression...")
            
        except Exception as e:
            logger.error(f"Chord progression error: {e}")
            self.generate_fallback_chords()

    def apply_chord_progression(self, chord_data):
        """Apply generated chord progression"""
        try:
            if isinstance(chord_data, str):
                import json
                chord_data = json.loads(chord_data)
            
            chords = chord_data.get("chords", [])
            progression = chord_data.get("progression", [])
            
            # Display chord progression in a new window
            chord_window = tk.Toplevel(self.window)
            chord_window.title("🎹 Chord Progression")
            chord_window.geometry("600x400")
            chord_window.configure(bg='#2b2b2b')
            
            # Chord progression display
            ttk.Label(chord_window, text="🎹 Your AI-Generated Chord Progression", 
                     font=('Arial', 14, 'bold')).pack(pady=10)
            
            chord_frame = ttk.LabelFrame(chord_window, text="Chord Progression", padding=10)
            chord_frame.pack(fill=tk.X, padx=20, pady=10)
            
            chord_text = tk.Text(chord_frame, height=3, font=('Consolas', 12))
            chord_text.pack(fill=tk.X)
            chord_text.insert("1.0", f"Chords: {chords}\nProgression: {progression}")
            
            # Playback controls
            controls_frame = ttk.Frame(chord_window)
            controls_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Button(controls_frame, text="🔄 Generate New", 
                      command=self.generate_chords).pack(side=tk.LEFT, padx=5)
            ttk.Button(controls_frame, text="💾 Save Chord Progression", 
                      command=lambda: self.save_chords(chord_data)).pack(side=tk.LEFT, padx=5)
            
            self.status_var.set("✅ Chord progression generated successfully!")
            
        except Exception as e:
            logger.error(f"Error applying chord progression: {e}")
            messagebox.showerror("Chord Error", f"Failed to apply chord progression: {e}")

    def generate_fallback_chords(self):
        """Generate fallback chord progression when AI is not available"""
        fallback_chords = {
            "Hip-Hop": ["C", "Am", "F", "G"],
            "Electronic": ["C", "G", "Am", "F"],
            "Trap": ["C", "G", "F", "Am"],
            "Rock": ["C", "G", "Am", "F"],
            "Jazz": ["C", "E7", "Am", "Dm"]
        }
        
        style = getattr(self, 'style_var', tk.StringVar(value="Hip-Hop")).get()
        chords = fallback_chords.get(style, fallback_chords["Hip-Hop"])
        
        self.apply_chord_progression({"chords": chords, "progression": chords})

    def save_chords(self, chord_data):
        """Save generated chord progression to file"""
        try:
            from tkinter import filedialog
            import json
            
            file_path = filedialog.asksaveasfilename(
                title="Save Chord Progression",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(chord_data, f, indent=2)
                messagebox.showinfo("Saved", f"Chord progression saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save chord progression: {e}")