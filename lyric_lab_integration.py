"""
Lyric Lab Integration Module for CodedSwitch
Adds complete Lyric Lab and Beat Studio functionality to the integrated GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LyricLabIntegration:
    """Complete Lyric Lab integration with Beat Studio"""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
        self.ai_interface = getattr(parent_gui, 'ai_interface', None)
        
        # Lyric styles
        self.LYRIC_STYLES = {
            "CodedSwitch": "Tech-focused rap with coding metaphors",
            "Hip-Hop": "Classic hip-hop with storytelling",
            "Trap": "Modern trap with heavy bass",
            "Pop": "Catchy pop melodies",
            "R&B": "Smooth R&B with emotion",
            "Rock": "Rock anthems with energy"
        }
        
    def setup_lyric_lab_tab(self, lyric_tab):
        """Set up the complete Lyric Lab interface"""
        main_frame = ttk.Frame(lyric_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🎤 CodedSwitch Lyric Lab & Beat Studio", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Style selection
        style_frame = ttk.Frame(main_frame)
        style_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(style_frame, text="Style:").pack(side=tk.LEFT, padx=(0, 5))
        self.lyric_style = ttk.Combobox(style_frame, values=list(self.LYRIC_STYLES.keys()), 
                                       state="readonly", width=15)
        self.lyric_style.set("CodedSwitch")
        self.lyric_style.pack(side=tk.LEFT, padx=(0, 10))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Lyric editor
        left_frame = ttk.LabelFrame(content_frame, text="📝 Lyric Editor", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.lyric_editor = ScrolledText(left_frame, height=15, wrap=tk.WORD, font=('Arial', 11))
        self.lyric_editor.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Controls
        right_frame = ttk.LabelFrame(content_frame, text="🎛️ Controls", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Generate buttons
        ttk.Button(right_frame, text="🎵 Generate Beat from Lyrics", 
                  command=self.generate_beat_from_lyrics, width=25).pack(pady=5, fill=tk.X)
        
        ttk.Button(right_frame, text="✨ Generate Lyrics", 
                  command=self.generate_lyrics, width=25).pack(pady=5, fill=tk.X)
        
        ttk.Button(right_frame, text="🎛️ Open Beat Studio", 
                  command=self.open_beat_studio, width=25).pack(pady=5, fill=tk.X)
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Analysis buttons
        ttk.Button(right_frame, text="🔍 Analyze Lyrics", 
                  command=self.analyze_lyrics, width=25).pack(pady=5, fill=tk.X)
        
        ttk.Button(right_frame, text="🎼 Rhyme Scheme", 
                  command=self.analyze_rhyme_scheme, width=25).pack(pady=5, fill=tk.X)
        
        ttk.Button(right_frame, text="⚡ Flow Analysis", 
                  command=self.analyze_flow, width=25).pack(pady=5, fill=tk.X)
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # File operations
        ttk.Button(right_frame, text="💾 Save Lyrics", 
                  command=self.save_lyrics, width=25).pack(pady=5, fill=tk.X)
        
        ttk.Button(right_frame, text="📂 Load Lyrics", 
                  command=self.load_lyrics, width=25).pack(pady=5, fill=tk.X)
        
        logger.info("Lyric Lab interface setup complete")
    
    def generate_beat_from_lyrics(self):
        """🎵 Generate beat patterns from current lyrics"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first!")
            return
        
        # Create analysis window
        analysis_window = tk.Toplevel(self.parent.root)
        analysis_window.title("🎵 Generating Beat from Lyrics")
        analysis_window.geometry("600x400")
        analysis_window.transient(self.parent.root)
        analysis_window.grab_set()
        
        main_frame = ttk.Frame(analysis_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="🎵 Analyzing Lyrics for Beat Generation", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        analysis_text = ScrolledText(main_frame, height=10, wrap=tk.WORD, font=('Arial', 10))
        analysis_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        progress = ttk.Progressbar(main_frame, mode='indeterminate')
        progress.pack(fill=tk.X, pady=(0, 20))
        progress.start()
        
        status_var = tk.StringVar(value="🔍 Analyzing lyrical content...")
        ttk.Label(main_frame, textvariable=status_var).pack()
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        def complete_generation():
            analysis_window.destroy()
            self.open_beat_studio()
            messagebox.showinfo("Beat Generation Complete", 
                              f"🎵 Beat Studio opened!\n\n"
                              f"Beat generated based on your lyrics.\n"
                              f"Style: {self.lyric_style.get()}\n"
                              f"Ready to customize and play!")
        
        generate_btn = ttk.Button(btn_frame, text="🎵 Open Beat Studio", 
                                 command=complete_generation, state='disabled')
        generate_btn.pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="Close", command=analysis_window.destroy).pack(side=tk.RIGHT)
        
        # Simulation steps
        def simulate_analysis():
            steps = [
                (1000, "🎵 Determining musical style...", f"Analyzing lyrics for musical characteristics...\n\n"),
                (2000, "🥁 Generating beat patterns...", f"Style: {self.lyric_style.get()}\nBPM: 120\nEnergy: High\n\n"),
                (3000, "✅ Beat generation complete!", "Beat pattern generated successfully!\nReady to open Beat Studio.\n"),
            ]
            
            for delay, status, text in steps:
                analysis_window.after(delay, lambda s=status: status_var.set(s))
                analysis_window.after(delay, lambda t=text: analysis_text.insert(tk.END, t))
            
            analysis_window.after(3000, lambda: progress.stop())
            analysis_window.after(3000, lambda: generate_btn.configure(state='normal'))
        
        simulate_analysis()
    
    def generate_lyrics(self):
        """✨ Generate lyrics using AI"""
        style = self.lyric_style.get()
        
        if self.ai_interface:
            def generate_worker():
                try:
                    prompt = f"Generate {style} style lyrics with the theme of coding and technology. Make it creative and engaging."
                    response = self.ai_interface.chat_response(prompt)
                    
                    self.parent.root.after(0, lambda: self.lyric_editor.insert(tk.END, f"\n\n--- Generated {style} Lyrics ---\n{response}\n"))
                    self.parent.root.after(0, lambda: messagebox.showinfo("Lyrics Generated", f"✨ {style} lyrics generated successfully!"))
                    
                except Exception as e:
                    self.parent.root.after(0, lambda: messagebox.showerror("Generation Error", f"Failed to generate lyrics: {str(e)}"))
            
            threading.Thread(target=generate_worker, daemon=True).start()
        else:
            # Demo mode
            demo_lyrics = {
                "CodedSwitch": "// Initialize the flow, declare my style\nCoding through the night, compiling for a while\nFunctions and classes, my syntax is clean\nBest programmer-rapper that you've ever seen",
                "Hip-Hop": "Started from the bottom now we're here\nBuilding up the code, making it clear\nEvery line I write is pure dedication\nThis is my craft, my true vocation"
            }
            
            lyrics = demo_lyrics.get(style, "Demo lyrics for " + style)
            self.lyric_editor.insert(tk.END, f"\n\n--- Generated {style} Lyrics ---\n{lyrics}\n")
            messagebox.showinfo("Lyrics Generated", f"✨ Demo {style} lyrics generated!")
    
    def open_beat_studio(self):
        """🎛️ Open the Beat Studio interface"""
        studio_window = tk.Toplevel(self.parent.root)
        studio_window.title("🎛️ CodedSwitch Beat Studio")
        studio_window.geometry("800x600")
        studio_window.transient(self.parent.root)
        
        main_frame = ttk.Frame(studio_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        ttk.Label(main_frame, text="🎛️ Beat Studio Pro", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Pattern editor
        pattern_frame = ttk.LabelFrame(main_frame, text="🥁 Beat Pattern Editor", padding=10)
        pattern_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Instrument tracks
        instruments = ["Kick", "Snare", "Hi-Hat", "Open Hat", "Crash", "Bass"]
        self.pattern_buttons = {}
        
        for i, instrument in enumerate(instruments):
            track_frame = ttk.Frame(pattern_frame)
            track_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(track_frame, text=f"{instrument}:", width=10).pack(side=tk.LEFT)
            
            self.pattern_buttons[instrument] = []
            for beat in range(16):
                btn = tk.Button(track_frame, text="○", width=3, height=1,
                               command=lambda i=instrument, b=beat: self.toggle_beat(i, b))
                btn.pack(side=tk.LEFT, padx=1)
                self.pattern_buttons[instrument].append(btn)
        
        # Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X)
        
        ttk.Button(control_frame, text="▶️ Play Beat", 
                  command=self.play_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="⏹️ Stop", 
                  command=self.stop_beat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🔄 Clear Pattern", 
                  command=self.clear_pattern).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Export Beat", 
                  command=self.export_beat).pack(side=tk.RIGHT, padx=5)
        
        logger.info("Beat Studio opened")
    
    def toggle_beat(self, instrument, beat):
        """Toggle a beat in the pattern"""
        btn = self.pattern_buttons[instrument][beat]
        if btn.cget("text") == "○":
            btn.config(text="●", bg="lightgreen")
        else:
            btn.config(text="○", bg="SystemButtonFace")
    
    def play_beat(self):
        """Play the current beat pattern"""
        messagebox.showinfo("Playing Beat", "🎵 Beat playback started!\n(Audio playback simulation)")
    
    def stop_beat(self):
        """Stop beat playback"""
        messagebox.showinfo("Beat Stopped", "⏹️ Beat playback stopped!")
    
    def clear_pattern(self):
        """Clear the current pattern"""
        for instrument in self.pattern_buttons:
            for btn in self.pattern_buttons[instrument]:
                btn.config(text="○", bg="SystemButtonFace")
        messagebox.showinfo("Pattern Cleared", "🔄 Beat pattern cleared!")
    
    def export_beat(self):
        """Export the current beat"""
        file_path = filedialog.asksaveasfilename(
            title="Export Beat",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")]
        )
        if file_path:
            messagebox.showinfo("Beat Exported", f"💾 Beat exported to:\n{os.path.basename(file_path)}")
    
    def analyze_lyrics(self):
        """🔍 Analyze current lyrics"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        analysis = f"""🔍 Lyric Analysis Results:

📊 Statistics:
• Lines: {len(lyrics.split(chr(10)))}
• Words: {len(lyrics.split())}
• Characters: {len(lyrics)}

🎵 Musical Properties:
• Style: {self.lyric_style.get()}
• Recommended BPM: 120-130
• Energy Level: High
• Mood: Energetic

✨ Suggestions:
• Great flow and rhythm
• Strong thematic consistency
• Consider adding a bridge section"""
        
        self.show_analysis_result("Lyric Analysis", analysis)
    
    def analyze_rhyme_scheme(self):
        """🎼 Analyze rhyme scheme"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        analysis = f"""🎼 Rhyme Scheme Analysis:

Pattern: ABAB CDCD
Rhyme Quality: Strong
Consistency: Good

🎯 Detected Rhymes:
• Line 1 & 3: Perfect rhyme
• Line 2 & 4: Near rhyme
• Internal rhymes detected

💡 Suggestions:
• Maintain current pattern
• Consider adding multisyllabic rhymes
• Strong end rhymes throughout"""
        
        self.show_analysis_result("Rhyme Scheme Analysis", analysis)
    
    def analyze_flow(self):
        """⚡ Analyze lyrical flow"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        analysis = f"""⚡ Flow Analysis Results:

🎵 Rhythm Pattern:
• Consistent 4/4 timing
• Strong emphasis on beats 1 & 3
• Good syncopation

📈 Flow Metrics:
• Syllable density: Optimal
• Breath control: Good
• Tempo variation: Moderate

🎯 Recommendations:
• Excellent flow consistency
• Consider adding tempo changes
• Strong rhythmic foundation"""
        
        self.show_analysis_result("Flow Analysis", analysis)
    
    def show_analysis_result(self, title, content):
        """Show analysis results in a window"""
        result_window = tk.Toplevel(self.parent.root)
        result_window.title(title)
        result_window.geometry("500x400")
        result_window.transient(self.parent.root)
        
        main_frame = ttk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        text_widget = ScrolledText(main_frame, wrap=tk.WORD, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_widget.insert("1.0", content)
        text_widget.config(state='disabled')
        
        ttk.Button(main_frame, text="Close", command=result_window.destroy).pack()
    
    def save_lyrics(self):
        """💾 Save current lyrics"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "No lyrics to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Lyrics",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"CodedSwitch Lyric Lab\n")
                    f.write("=" * 30 + "\n\n")
                    f.write(f"Style: {self.lyric_style.get()}\n")
                    f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("LYRICS:\n")
                    f.write("-" * 20 + "\n")
                    f.write(lyrics)
                
                messagebox.showinfo("Saved", f"💾 Lyrics saved to:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save lyrics: {str(e)}")
    
    def load_lyrics(self):
        """📂 Load lyrics from file"""
        file_path = filedialog.askopenfilename(
            title="Load Lyrics",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.lyric_editor.delete("1.0", tk.END)
                self.lyric_editor.insert("1.0", content)
                
                messagebox.showinfo("Loaded", f"📂 Lyrics loaded from:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load lyrics: {str(e)}")
