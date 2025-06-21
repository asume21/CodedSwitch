"""
Standalone Beat Studio Launcher
Launch this to open the professional Beat Studio interface directly.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
import sys

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Try to import Beat Studio integration
try:
    from beat_studio_integration import beat_studio_integration, BEAT_STUDIO_AVAILABLE
    print("✅ Beat Studio integration loaded successfully!")
except ImportError as e:
    print(f"⚠️ Beat Studio integration not available: {e}")
    BEAT_STUDIO_AVAILABLE = False
    beat_studio_integration = None

class BeatStudioLauncher:
    """Standalone Beat Studio application."""
    
    def __init__(self):
        # Initialize with bootstrap theme
        self.style = ttk.Style(theme="darkly")
        self.root = self.style.master
        self.root.title("🎵 Professional Beat Studio")
        self.root.geometry("1000x700")
        
        # Initialize variables
        self.current_beat = None
        
        # Create the interface
        self._create_interface()
        
        # Show status
        if BEAT_STUDIO_AVAILABLE and beat_studio_integration and beat_studio_integration.is_available():
            self.status_label.config(text="✅ Beat Studio Ready", foreground='green')
        else:
            self.status_label.config(text="⚠️ Demo Mode - Beat Studio Professional module not available", foreground='orange')
    
    def _create_interface(self):
        """Create the main Beat Studio interface."""
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🎵 Professional Beat Studio", 
                 font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(header_frame, text="Initializing...", 
                                     font=('Arial', 10))
        self.status_label.pack(side=tk.RIGHT)
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Lyrics Input Tab
        lyrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(lyrics_frame, text="📝 Lyrics Input")
        self._setup_lyrics_tab(lyrics_frame)
        
        # Beat Generation Tab
        generation_frame = ttk.Frame(self.notebook)
        self.notebook.add(generation_frame, text="🎛️ Beat Generation")
        self._setup_generation_tab(generation_frame)
        
        # Effects Tab
        effects_frame = ttk.Frame(self.notebook)
        self.notebook.add(effects_frame, text="🎚️ Effects & Mixing")
        self._setup_effects_tab(effects_frame)
        
        # Export Tab
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="💾 Export")
        self._setup_export_tab(export_frame)
        
        # Control buttons at bottom
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(control_frame, text="🎵 Generate Beat from Lyrics", 
                  command=self._generate_beat,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="▶️ Play", 
                  command=self._play_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="⏹️ Stop", 
                  command=self._stop_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Save Beat", 
                  command=self._save_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="❌ Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def _setup_lyrics_tab(self, parent):
        """Setup the lyrics input tab."""
        
        # Instructions
        instructions = ttk.Label(parent, 
                               text="Enter your lyrics below and the Beat Studio will analyze them to create a matching beat:",
                               font=('Arial', 11))
        instructions.pack(anchor=tk.W, padx=10, pady=10)
        
        # Lyrics input area
        lyrics_label = ttk.Label(parent, text="Your Lyrics:", font=('Arial', 12, 'bold'))
        lyrics_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Text area with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.lyrics_text = tk.Text(text_frame, height=15, wrap=tk.WORD, 
                                  font=('Consolas', 11))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.lyrics_text.yview)
        self.lyrics_text.configure(yscrollcommand=scrollbar.set)
        
        self.lyrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sample lyrics
        sample_lyrics = """Verse 1:
Started from the bottom now we here
Grinding every day, vision crystal clear
Code flows like water, beats drop like thunder
Building something great, world's about to wonder

Chorus:
We're rising up, never backing down
From the underground to the top of town
Beat drops hard when the bass line hits
This is our time, this is our gift"""
        
        self.lyrics_text.insert(1.0, sample_lyrics)
        
        # Quick actions
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="🔄 Clear", 
                  command=lambda: self.lyrics_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(actions_frame, text="📁 Load from File", 
                  command=self._load_lyrics_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="🎯 Analyze Mood", 
                  command=self._analyze_mood).pack(side=tk.LEFT, padx=5)
    
    def _setup_generation_tab(self, parent):
        """Setup the beat generation tab."""
        
        # Preset selection
        preset_frame = ttk.LabelFrame(parent, text="🎛️ Beat Presets", padding=10)
        preset_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.preset_var = tk.StringVar(value="trap_modern")
        presets = [
            ("Trap Modern", "trap_modern"),
            ("Boom Bap Classic", "boom_bap_classic"), 
            ("Drill Aggressive", "drill_aggressive"),
            ("Melodic Chill", "melodic_chill"),
            ("Experimental", "experimental")
        ]
        
        for i, (display_name, value) in enumerate(presets):
            ttk.Radiobutton(preset_frame, text=display_name, 
                           variable=self.preset_var, value=value).grid(row=i//3, column=i%3, padx=10, pady=5, sticky=tk.W)
        
        # Manual controls
        controls_frame = ttk.LabelFrame(parent, text="🎚️ Manual Controls", padding=10)
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # BPM control
        ttk.Label(controls_frame, text="BPM (Beats Per Minute):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bpm_var = tk.IntVar(value=140)
        bpm_scale = ttk.Scale(controls_frame, from_=60, to=200, variable=self.bpm_var, 
                             orient=tk.HORIZONTAL, length=300)
        bpm_scale.grid(row=0, column=1, padx=10, pady=5)
        self.bpm_label = ttk.Label(controls_frame, text="140")
        self.bpm_label.grid(row=0, column=2, pady=5)
        
        # Update BPM label
        def update_bpm_label(*args):
            self.bpm_label.config(text=str(self.bpm_var.get()))
        self.bpm_var.trace('w', update_bpm_label)
        
        # Scale selection
        ttk.Label(controls_frame, text="Musical Scale:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.scale_var = tk.StringVar(value="minor")
        scale_combo = ttk.Combobox(controls_frame, textvariable=self.scale_var,
                                  values=["major", "minor", "pentatonic", "blues", "chromatic"])
        scale_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Energy level
        ttk.Label(controls_frame, text="Energy Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.energy_var = tk.IntVar(value=7)
        energy_scale = ttk.Scale(controls_frame, from_=1, to=10, variable=self.energy_var,
                                orient=tk.HORIZONTAL, length=300)
        energy_scale.grid(row=2, column=1, padx=10, pady=5)
        self.energy_label = ttk.Label(controls_frame, text="7")
        self.energy_label.grid(row=2, column=2, pady=5)
        
        # Update energy label
        def update_energy_label(*args):
            self.energy_label.config(text=str(self.energy_var.get()))
        self.energy_var.trace('w', update_energy_label)
    
    def _setup_effects_tab(self, parent):
        """Setup the effects tab."""
        
        # Effects controls
        effects_frame = ttk.LabelFrame(parent, text="🎚️ Audio Effects", padding=10)
        effects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Reverb
        ttk.Label(effects_frame, text="Reverb:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reverb_var = tk.DoubleVar(value=0.3)
        reverb_scale = ttk.Scale(effects_frame, from_=0.0, to=1.0, variable=self.reverb_var,
                                orient=tk.HORIZONTAL, length=300)
        reverb_scale.grid(row=0, column=1, padx=10, pady=5)
        
        # Compression
        ttk.Label(effects_frame, text="Compression:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.compression_var = tk.DoubleVar(value=0.5)
        comp_scale = ttk.Scale(effects_frame, from_=0.0, to=1.0, variable=self.compression_var,
                              orient=tk.HORIZONTAL, length=300)
        comp_scale.grid(row=1, column=1, padx=10, pady=5)
        
        # EQ controls
        eq_frame = ttk.LabelFrame(effects_frame, text="🎛️ 3-Band Equalizer", padding=10)
        eq_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        # Bass
        ttk.Label(eq_frame, text="Bass:").grid(row=0, column=0, pady=5)
        self.bass_var = tk.DoubleVar(value=0.0)
        ttk.Scale(eq_frame, from_=-12, to=12, variable=self.bass_var,
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, padx=10)
        
        # Mid
        ttk.Label(eq_frame, text="Mid:").grid(row=1, column=0, pady=5)
        self.mid_var = tk.DoubleVar(value=0.0)
        ttk.Scale(eq_frame, from_=-12, to=12, variable=self.mid_var,
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, padx=10)
        
        # Treble
        ttk.Label(eq_frame, text="Treble:").grid(row=2, column=0, pady=5)
        self.treble_var = tk.DoubleVar(value=0.0)
        ttk.Scale(eq_frame, from_=-12, to=12, variable=self.treble_var,
                 orient=tk.HORIZONTAL, length=200).grid(row=2, column=1, padx=10)
    
    def _setup_export_tab(self, parent):
        """Setup the export tab."""
        
        export_frame = ttk.LabelFrame(parent, text="💾 Export Options", padding=10)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Format selection
        ttk.Label(export_frame, text="Audio Format:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="WAV")
        format_combo = ttk.Combobox(export_frame, textvariable=self.format_var,
                                   values=["WAV", "MP3", "FLAC"])
        format_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Quality selection
        ttk.Label(export_frame, text="Quality:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value="High")
        quality_combo = ttk.Combobox(export_frame, textvariable=self.quality_var,
                                    values=["Low", "Medium", "High", "Studio"])
        quality_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Export buttons
        button_frame = ttk.Frame(export_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="💾 Export Audio Only", 
                  command=self._export_audio).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📁 Export Full Project", 
                  command=self._export_project).pack(side=tk.LEFT, padx=5)
    
    def _load_lyrics_file(self):
        """Load lyrics from a text file."""
        file_path = filedialog.askopenfilename(
            title="Load Lyrics File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lyrics = f.read()
                self.lyrics_text.delete(1.0, tk.END)
                self.lyrics_text.insert(1.0, lyrics)
                self.status_label.config(text=f"Lyrics loaded from {os.path.basename(file_path)}", foreground='blue')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def _analyze_mood(self):
        """Analyze the mood of the lyrics and adjust settings."""
        lyrics = self.lyrics_text.get(1.0, tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first.")
            return
        
        # Simple mood analysis
        mood_keywords = {
            'aggressive': ['fight', 'battle', 'war', 'rage', 'anger', 'destroy', 'kill', 'hate'],
            'sad': ['cry', 'tears', 'pain', 'hurt', 'lonely', 'broken', 'lost', 'miss'],
            'happy': ['joy', 'smile', 'love', 'celebration', 'party', 'good', 'amazing', 'great'],
            'chill': ['relax', 'calm', 'peace', 'smooth', 'easy', 'flow', 'cool', 'laid']
        }
        
        lyrics_lower = lyrics.lower()
        mood_scores = {}
        
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in lyrics_lower)
            mood_scores[mood] = score
        
        detected_mood = max(mood_scores, key=mood_scores.get) if any(mood_scores.values()) else 'neutral'
        
        # Update settings based on mood
        mood_settings = {
            'aggressive': {'bpm': 160, 'energy': 9, 'preset': 'drill_aggressive'},
            'sad': {'bpm': 80, 'energy': 3, 'preset': 'melodic_chill'},
            'happy': {'bpm': 120, 'energy': 7, 'preset': 'trap_modern'},
            'chill': {'bpm': 90, 'energy': 5, 'preset': 'boom_bap_classic'},
            'neutral': {'bpm': 140, 'energy': 6, 'preset': 'trap_modern'}
        }
        
        settings = mood_settings.get(detected_mood, mood_settings['neutral'])
        
        # Apply settings
        self.bpm_var.set(settings['bpm'])
        self.energy_var.set(settings['energy'])
        self.preset_var.set(settings['preset'])
        
        self.status_label.config(text=f"Mood detected: {detected_mood.title()} - Settings adjusted", foreground='green')
        messagebox.showinfo("Mood Analysis Complete", 
                           f"Detected mood: {detected_mood.title()}\n"
                           f"BPM set to: {settings['bpm']}\n"
                           f"Energy level: {settings['energy']}\n"
                           f"Preset: {settings['preset'].replace('_', ' ').title()}")
    
    def _generate_beat(self):
        """Generate a beat from the lyrics."""
        lyrics = self.lyrics_text.get(1.0, tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first.")
            return
        
        try:
            self.status_label.config(text="Generating beat...", foreground='orange')
            self.root.update()
            
            # Check if Beat Studio is available
            if BEAT_STUDIO_AVAILABLE and beat_studio_integration and beat_studio_integration.is_available():
                preset = self.preset_var.get()
                beat_data = beat_studio_integration.create_beat_from_lyrics(lyrics, preset_name=preset)
                
                if beat_data:
                    self.current_beat = beat_data
                    self.status_label.config(text="✅ Beat generated successfully!", foreground='green')
                    
                    # Show beat info
                    beat_info = beat_studio_integration.get_beat_info()
                    info_text = f"Beat generated successfully!\n\n"
                    if beat_info:
                        info_text += f"BPM: {beat_info.get('bpm', 'N/A')}\n"
                        info_text += f"Scale: {beat_info.get('scale', 'N/A')}\n"
                        info_text += f"Style: {beat_info.get('style', 'N/A')}\n"
                        info_text += f"Energy: {beat_info.get('energy', 'N/A')}/10\n"
                    info_text += "\nUse the Play button to listen to your beat!"
                    
                    messagebox.showinfo("Beat Generated", info_text)
                else:
                    self.status_label.config(text="❌ Failed to generate beat", foreground='red')
                    messagebox.showerror("Error", "Failed to generate beat. Check the console for details.")
            else:
                # Demo mode
                self.status_label.config(text="🎵 Demo beat generated", foreground='blue')
                messagebox.showinfo("Demo Mode", 
                                   f"Beat generated in demo mode!\n\n"
                                   f"Preset: {self.preset_var.get().replace('_', ' ').title()}\n"
                                   f"BPM: {self.bpm_var.get()}\n"
                                   f"Scale: {self.scale_var.get().title()}\n"
                                   f"Energy: {self.energy_var.get()}/10\n\n"
                                   f"Install the full Beat Studio module for actual audio generation.")
                
        except Exception as e:
            self.status_label.config(text="❌ Error generating beat", foreground='red')
            messagebox.showerror("Error", f"Failed to generate beat: {e}")
    
    def _play_beat(self):
        """Play the generated beat."""
        if BEAT_STUDIO_AVAILABLE and beat_studio_integration and beat_studio_integration.is_available():
            if hasattr(self, 'current_beat') and self.current_beat:
                try:
                    if beat_studio_integration.play_current_beat():
                        self.status_label.config(text="🎵 Playing beat...", foreground='green')
                    else:
                        messagebox.showerror("Error", "Failed to play beat.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to play beat: {e}")
            else:
                messagebox.showwarning("No Beat", "Please generate a beat first.")
        else:
            messagebox.showinfo("Demo Mode", "🎵 Beat is playing! (Demo mode - no actual audio)")
            self.status_label.config(text="🎵 Playing (demo)", foreground='blue')
    
    def _stop_beat(self):
        """Stop the playing beat."""
        try:
            if BEAT_STUDIO_AVAILABLE and beat_studio_integration and beat_studio_integration.is_available():
                beat_studio_integration.stop_beat()
            self.status_label.config(text="⏹️ Stopped", foreground='gray')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop beat: {e}")
    
    def _save_beat(self):
        """Save the generated beat."""
        if BEAT_STUDIO_AVAILABLE and beat_studio_integration and beat_studio_integration.is_available():
            if hasattr(self, 'current_beat') and self.current_beat:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".wav",
                    filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")]
                )
                if file_path:
                    try:
                        if beat_studio_integration.save_beat(file_path):
                            messagebox.showinfo("Success", f"Beat saved to {file_path}")
                            self.status_label.config(text="💾 Beat saved", foreground='green')
                        else:
                            messagebox.showerror("Error", "Failed to save beat.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save beat: {e}")
            else:
                messagebox.showwarning("No Beat", "Please generate a beat first.")
        else:
            # Demo mode
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write("Demo Beat Studio Project\n")
                        f.write("=" * 30 + "\n\n")
                        f.write("Lyrics:\n")
                        f.write(self.lyrics_text.get(1.0, tk.END))
                        f.write(f"\n\nSettings:\n")
                        f.write(f"Preset: {self.preset_var.get()}\n")
                        f.write(f"BPM: {self.bpm_var.get()}\n")
                        f.write(f"Scale: {self.scale_var.get()}\n")
                        f.write(f"Energy: {self.energy_var.get()}\n")
                    messagebox.showinfo("Demo Mode", f"Project info saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save: {e}")
    
    def _export_audio(self):
        """Export audio file."""
        self._save_beat()  # Reuse save functionality
    
    def _export_project(self):
        """Export complete project."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                project_data = {
                    'lyrics': self.lyrics_text.get(1.0, tk.END).strip(),
                    'preset': self.preset_var.get(),
                    'bpm': self.bpm_var.get(),
                    'scale': self.scale_var.get(),
                    'energy': self.energy_var.get(),
                    'effects': {
                        'reverb': self.reverb_var.get(),
                        'compression': self.compression_var.get(),
                        'bass': self.bass_var.get(),
                        'mid': self.mid_var.get(),
                        'treble': self.treble_var.get()
                    },
                    'format': self.format_var.get(),
                    'quality': self.quality_var.get()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(project_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Project exported to {file_path}")
                self.status_label.config(text="📁 Project exported", foreground='green')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export project: {e}")
    
    def run(self):
        """Run the Beat Studio application."""
        print("🎵 Starting Professional Beat Studio...")
        self.root.mainloop()

def main():
    """Launch the Beat Studio."""
    try:
        app = BeatStudioLauncher()
        app.run()
    except Exception as e:
        print(f"Error launching Beat Studio: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
