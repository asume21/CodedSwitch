"""
Script to add Beat Studio button and functionality to the Lyric Lab tab
"""

def add_beat_studio_functionality():
    """Add Beat Studio button and methods to the integrated GUI."""
    
    # Read the current integrated_gui.py
    with open('integrated_gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the location in the _setup_lyric_lab_tab method where we can add the Beat Studio button
    # Look for the existing button section in the Lyric Lab
    
    # Add Beat Studio methods to the class
    beat_studio_methods = '''
    def _open_beat_studio(self):
        """Open the professional Beat Studio interface."""
        if not hasattr(self, 'beat_studio_window') or not self.beat_studio_window.winfo_exists():
            self._create_beat_studio_window()
        else:
            self.beat_studio_window.lift()
            self.beat_studio_window.focus()
    
    def _create_beat_studio_window(self):
        """Create the professional Beat Studio window."""
        self.beat_studio_window = tk.Toplevel(self.root)
        self.beat_studio_window.title("🎵 Professional Beat Studio")
        self.beat_studio_window.geometry("1000x700")
        self.beat_studio_window.configure(bg='#1a1a1a')
        
        # Make it modal
        self.beat_studio_window.transient(self.root)
        self.beat_studio_window.grab_set()
        
        # Main container with modern styling
        main_frame = ttk.Frame(self.beat_studio_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🎵 Professional Beat Studio", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Status label
        self.beat_status_label = ttk.Label(header_frame, text="Ready", 
                                          foreground='green')
        self.beat_status_label.pack(side=tk.RIGHT)
        
        # Create notebook for different sections
        studio_notebook = ttk.Notebook(main_frame)
        studio_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Lyrics Input Tab
        lyrics_frame = ttk.Frame(studio_notebook)
        studio_notebook.add(lyrics_frame, text="📝 Lyrics Input")
        self._setup_lyrics_input_tab(lyrics_frame)
        
        # Beat Generation Tab
        generation_frame = ttk.Frame(studio_notebook)
        studio_notebook.add(generation_frame, text="🎛️ Beat Generation")
        self._setup_beat_generation_tab(generation_frame)
        
        # Effects & Mixing Tab
        effects_frame = ttk.Frame(studio_notebook)
        studio_notebook.add(effects_frame, text="🎚️ Effects & Mixing")
        self._setup_effects_tab(effects_frame)
        
        # Export Tab
        export_frame = ttk.Frame(studio_notebook)
        studio_notebook.add(export_frame, text="💾 Export")
        self._setup_export_tab(export_frame)
        
        # Control buttons at bottom
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(control_frame, text="🎵 Generate Beat", 
                  command=self._generate_beat_from_studio,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="▶️ Play", 
                  command=self._play_studio_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="⏹️ Stop", 
                  command=self._stop_studio_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Save", 
                  command=self._save_studio_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="❌ Close", 
                  command=self.beat_studio_window.destroy).pack(side=tk.RIGHT)
    
    def _setup_lyrics_input_tab(self, parent):
        """Setup the lyrics input tab in Beat Studio."""
        # Lyrics input area
        lyrics_label = ttk.Label(parent, text="Enter your lyrics:", font=('Arial', 12, 'bold'))
        lyrics_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.studio_lyrics_text = tk.Text(parent, height=15, wrap=tk.WORD, 
                                         font=('Consolas', 11))
        self.studio_lyrics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Quick actions
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="📋 Paste from Lyric Lab", 
                  command=self._paste_from_lyric_lab).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(actions_frame, text="🔄 Clear", 
                  command=lambda: self.studio_lyrics_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="🎯 Analyze Mood", 
                  command=self._analyze_lyrics_mood).pack(side=tk.LEFT, padx=5)
    
    def _setup_beat_generation_tab(self, parent):
        """Setup the beat generation tab."""
        # Preset selection
        preset_frame = ttk.LabelFrame(parent, text="🎛️ Beat Presets", padding=10)
        preset_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.studio_preset_var = tk.StringVar(value="trap_modern")
        presets = ["trap_modern", "boom_bap_classic", "drill_aggressive", "melodic_chill", "experimental"]
        
        for i, preset in enumerate(presets):
            ttk.Radiobutton(preset_frame, text=preset.replace('_', ' ').title(), 
                           variable=self.studio_preset_var, value=preset).grid(row=0, column=i, padx=5)
        
        # Manual controls
        controls_frame = ttk.LabelFrame(parent, text="🎚️ Manual Controls", padding=10)
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # BPM control
        ttk.Label(controls_frame, text="BPM:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.studio_bpm_var = tk.IntVar(value=140)
        bpm_scale = ttk.Scale(controls_frame, from_=60, to=200, variable=self.studio_bpm_var, 
                             orient=tk.HORIZONTAL, length=200)
        bpm_scale.grid(row=0, column=1, padx=10, pady=5)
        self.studio_bpm_label = ttk.Label(controls_frame, text="140")
        self.studio_bpm_label.grid(row=0, column=2, pady=5)
        
        # Update BPM label
        def update_bpm_label(*args):
            self.studio_bpm_label.config(text=str(self.studio_bpm_var.get()))
        self.studio_bpm_var.trace('w', update_bpm_label)
        
        # Scale selection
        ttk.Label(controls_frame, text="Scale:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.studio_scale_var = tk.StringVar(value="minor")
        scale_combo = ttk.Combobox(controls_frame, textvariable=self.studio_scale_var,
                                  values=["major", "minor", "pentatonic", "blues", "chromatic"])
        scale_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Energy level
        ttk.Label(controls_frame, text="Energy:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.studio_energy_var = tk.IntVar(value=7)
        energy_scale = ttk.Scale(controls_frame, from_=1, to=10, variable=self.studio_energy_var,
                                orient=tk.HORIZONTAL, length=200)
        energy_scale.grid(row=2, column=1, padx=10, pady=5)
        self.studio_energy_label = ttk.Label(controls_frame, text="7")
        self.studio_energy_label.grid(row=2, column=2, pady=5)
        
        # Update energy label
        def update_energy_label(*args):
            self.studio_energy_label.config(text=str(self.studio_energy_var.get()))
        self.studio_energy_var.trace('w', update_energy_label)
    
    def _setup_effects_tab(self, parent):
        """Setup the effects and mixing tab."""
        # Effects controls
        effects_frame = ttk.LabelFrame(parent, text="🎚️ Audio Effects", padding=10)
        effects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Reverb
        ttk.Label(effects_frame, text="Reverb:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.studio_reverb_var = tk.DoubleVar(value=0.3)
        reverb_scale = ttk.Scale(effects_frame, from_=0.0, to=1.0, variable=self.studio_reverb_var,
                                orient=tk.HORIZONTAL, length=200)
        reverb_scale.grid(row=0, column=1, padx=10, pady=5)
        
        # Compression
        ttk.Label(effects_frame, text="Compression:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.studio_compression_var = tk.DoubleVar(value=0.5)
        comp_scale = ttk.Scale(effects_frame, from_=0.0, to=1.0, variable=self.studio_compression_var,
                              orient=tk.HORIZONTAL, length=200)
        comp_scale.grid(row=1, column=1, padx=10, pady=5)
        
        # EQ controls
        eq_frame = ttk.LabelFrame(effects_frame, text="🎛️ 3-Band EQ", padding=5)
        eq_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        # Bass
        ttk.Label(eq_frame, text="Bass:").grid(row=0, column=0, pady=2)
        self.studio_bass_var = tk.DoubleVar(value=0.0)
        ttk.Scale(eq_frame, from_=-12, to=12, variable=self.studio_bass_var,
                 orient=tk.HORIZONTAL, length=150).grid(row=0, column=1, padx=5)
        
        # Mid
        ttk.Label(eq_frame, text="Mid:").grid(row=1, column=0, pady=2)
        self.studio_mid_var = tk.DoubleVar(value=0.0)
        ttk.Scale(eq_frame, from_=-12, to=12, variable=self.studio_mid_var,
                 orient=tk.HORIZONTAL, length=150).grid(row=1, column=1, padx=5)
        
        # Treble
        ttk.Label(eq_frame, text="Treble:").grid(row=2, column=0, pady=2)
        self.studio_treble_var = tk.DoubleVar(value=0.0)
        ttk.Scale(eq_frame, from_=-12, to=12, variable=self.studio_treble_var,
                 orient=tk.HORIZONTAL, length=150).grid(row=2, column=1, padx=5)
    
    def _setup_export_tab(self, parent):
        """Setup the export tab."""
        export_frame = ttk.LabelFrame(parent, text="💾 Export Options", padding=10)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Format selection
        ttk.Label(export_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.studio_format_var = tk.StringVar(value="WAV")
        format_combo = ttk.Combobox(export_frame, textvariable=self.studio_format_var,
                                   values=["WAV", "MP3", "FLAC"])
        format_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Quality selection
        ttk.Label(export_frame, text="Quality:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.studio_quality_var = tk.StringVar(value="High")
        quality_combo = ttk.Combobox(export_frame, textvariable=self.studio_quality_var,
                                    values=["Low", "Medium", "High", "Studio"])
        quality_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Export buttons
        button_frame = ttk.Frame(export_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="💾 Export Audio", 
                  command=self._export_studio_audio).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📁 Export Project", 
                  command=self._export_studio_project).pack(side=tk.LEFT, padx=5)
    
    def _paste_from_lyric_lab(self):
        """Paste lyrics from the main Lyric Lab tab."""
        try:
            lyrics = self.lyric_text.get(1.0, tk.END).strip()
            if lyrics:
                self.studio_lyrics_text.delete(1.0, tk.END)
                self.studio_lyrics_text.insert(1.0, lyrics)
                self.beat_status_label.config(text="Lyrics pasted from Lyric Lab", foreground='blue')
            else:
                messagebox.showwarning("No Lyrics", "No lyrics found in Lyric Lab to paste.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste lyrics: {e}")
    
    def _analyze_lyrics_mood(self):
        """Analyze the mood of the entered lyrics."""
        lyrics = self.studio_lyrics_text.get(1.0, tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first.")
            return
        
        # Simple mood analysis (you can enhance this with AI)
        mood_keywords = {
            'aggressive': ['fight', 'battle', 'war', 'rage', 'anger', 'destroy'],
            'sad': ['cry', 'tears', 'pain', 'hurt', 'lonely', 'broken'],
            'happy': ['joy', 'smile', 'love', 'celebration', 'party', 'good'],
            'chill': ['relax', 'calm', 'peace', 'smooth', 'easy', 'flow']
        }
        
        lyrics_lower = lyrics.lower()
        mood_scores = {}
        
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in lyrics_lower)
            mood_scores[mood] = score
        
        detected_mood = max(mood_scores, key=mood_scores.get) if any(mood_scores.values()) else 'neutral'
        
        # Update UI based on mood
        mood_settings = {
            'aggressive': {'bpm': 160, 'energy': 9, 'preset': 'drill_aggressive'},
            'sad': {'bpm': 80, 'energy': 3, 'preset': 'melodic_chill'},
            'happy': {'bpm': 120, 'energy': 7, 'preset': 'trap_modern'},
            'chill': {'bpm': 90, 'energy': 5, 'preset': 'boom_bap_classic'},
            'neutral': {'bpm': 140, 'energy': 6, 'preset': 'trap_modern'}
        }
        
        settings = mood_settings.get(detected_mood, mood_settings['neutral'])
        
        # Apply settings
        if hasattr(self, 'studio_bpm_var'):
            self.studio_bpm_var.set(settings['bpm'])
        if hasattr(self, 'studio_energy_var'):
            self.studio_energy_var.set(settings['energy'])
        if hasattr(self, 'studio_preset_var'):
            self.studio_preset_var.set(settings['preset'])
        
        self.beat_status_label.config(text=f"Mood detected: {detected_mood.title()}", foreground='green')
        messagebox.showinfo("Mood Analysis", f"Detected mood: {detected_mood.title()}\\nSettings adjusted automatically!")
    
    def _generate_beat_from_studio(self):
        """Generate beat using the Beat Studio engine."""
        lyrics = self.studio_lyrics_text.get(1.0, tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first.")
            return
        
        try:
            self.beat_status_label.config(text="Generating beat...", foreground='orange')
            self.beat_studio_window.update()
            
            # Check if Beat Studio is available
            if hasattr(self, 'beat_studio_integration') and beat_studio_integration and beat_studio_integration.is_available():
                preset = self.studio_preset_var.get() if hasattr(self, 'studio_preset_var') else None
                beat_data = beat_studio_integration.create_beat_from_lyrics(lyrics, preset_name=preset)
                
                if beat_data:
                    self.current_studio_beat = beat_data
                    self.beat_status_label.config(text="Beat generated successfully!", foreground='green')
                    messagebox.showinfo("Success", "Beat generated successfully! Use the Play button to listen.")
                else:
                    self.beat_status_label.config(text="Failed to generate beat", foreground='red')
                    messagebox.showerror("Error", "Failed to generate beat. Check the console for details.")
            else:
                # Fallback demo mode
                self.beat_status_label.config(text="Demo mode - Beat simulated", foreground='blue')
                messagebox.showinfo("Demo Mode", "Beat Studio is in demo mode. Beat generation simulated successfully!")
                
        except Exception as e:
            self.beat_status_label.config(text="Error generating beat", foreground='red')
            messagebox.showerror("Error", f"Failed to generate beat: {e}")
    
    def _play_studio_beat(self):
        """Play the generated beat."""
        if hasattr(self, 'current_studio_beat') and self.current_studio_beat:
            try:
                if beat_studio_integration and beat_studio_integration.is_available():
                    if beat_studio_integration.play_current_beat():
                        self.beat_status_label.config(text="Playing beat...", foreground='green')
                    else:
                        messagebox.showerror("Error", "Failed to play beat.")
                else:
                    messagebox.showinfo("Demo Mode", "🎵 Beat is playing! (Demo mode)")
                    self.beat_status_label.config(text="Playing (demo)", foreground='blue')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to play beat: {e}")
        else:
            messagebox.showwarning("No Beat", "Please generate a beat first.")
    
    def _stop_studio_beat(self):
        """Stop the playing beat."""
        try:
            if beat_studio_integration and beat_studio_integration.is_available():
                beat_studio_integration.stop_beat()
            self.beat_status_label.config(text="Stopped", foreground='gray')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop beat: {e}")
    
    def _save_studio_beat(self):
        """Save the generated beat to file."""
        if hasattr(self, 'current_studio_beat') and self.current_studio_beat:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    if beat_studio_integration and beat_studio_integration.is_available():
                        if beat_studio_integration.save_beat(file_path):
                            messagebox.showinfo("Success", f"Beat saved to {file_path}")
                            self.beat_status_label.config(text="Beat saved", foreground='green')
                        else:
                            messagebox.showerror("Error", "Failed to save beat.")
                    else:
                        # Demo mode - create a placeholder file
                        with open(file_path, 'w') as f:
                            f.write("Demo beat file - Beat Studio integration required for actual audio")
                        messagebox.showinfo("Demo Mode", f"Demo beat file saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save beat: {e}")
        else:
            messagebox.showwarning("No Beat", "Please generate a beat first.")
    
    def _export_studio_audio(self):
        """Export the beat as audio file."""
        self._save_studio_beat()  # Reuse the save functionality
    
    def _export_studio_project(self):
        """Export the entire project including lyrics and settings."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                project_data = {
                    'lyrics': self.studio_lyrics_text.get(1.0, tk.END).strip(),
                    'preset': self.studio_preset_var.get() if hasattr(self, 'studio_preset_var') else 'trap_modern',
                    'bpm': self.studio_bpm_var.get() if hasattr(self, 'studio_bpm_var') else 140,
                    'scale': self.studio_scale_var.get() if hasattr(self, 'studio_scale_var') else 'minor',
                    'energy': self.studio_energy_var.get() if hasattr(self, 'studio_energy_var') else 7,
                    'effects': {
                        'reverb': self.studio_reverb_var.get() if hasattr(self, 'studio_reverb_var') else 0.3,
                        'compression': self.studio_compression_var.get() if hasattr(self, 'studio_compression_var') else 0.5,
                        'bass': self.studio_bass_var.get() if hasattr(self, 'studio_bass_var') else 0.0,
                        'mid': self.studio_mid_var.get() if hasattr(self, 'studio_mid_var') else 0.0,
                        'treble': self.studio_treble_var.get() if hasattr(self, 'studio_treble_var') else 0.0
                    },
                    'format': self.studio_format_var.get() if hasattr(self, 'studio_format_var') else 'WAV',
                    'quality': self.studio_quality_var.get() if hasattr(self, 'studio_quality_var') else 'High'
                }
                
                import json
                with open(file_path, 'w') as f:
                    json.dump(project_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Project exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export project: {e}")'''
    
    # Find where to insert the Beat Studio button in the Lyric Lab tab
    # Look for the existing button section
    button_search = "# Enhanced action buttons with better organization"
    
    if button_search in content:
        # Add the Beat Studio button to the existing button section
        beat_studio_button = '''
        # Beat Studio button
        beat_studio_btn = ttk.Button(
            action_frame, 
            text="🎵 Open Beat Studio", 
            command=self._open_beat_studio,
            style='Accent.TButton'
        )
        beat_studio_btn.pack(side=tk.LEFT, padx=5)'''
        
        # Insert the button code
        content = content.replace(
            button_search,
            button_search + beat_studio_button
        )
    
    # Add the methods to the class (find a good insertion point)
    class_end_marker = "    def run(self):"
    
    if class_end_marker in content:
        content = content.replace(
            class_end_marker,
            beat_studio_methods + "\n\n    " + class_end_marker
        )
    
    # Write back to file
    with open('integrated_gui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Beat Studio functionality added to integrated_gui.py")

if __name__ == "__main__":
    add_beat_studio_functionality()
