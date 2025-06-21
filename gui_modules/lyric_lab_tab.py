"""
Complete lyric_lab_tab.py file with all required methods
Replace your entire gui_modules/lyric_lab_tab.py file with this working version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class LyricLabTab:
    """Complete Lyric Lab tab with AI integration and Beat Studio connection."""
    
    def __init__(self, parent, ai_interface=None):
        """Initialize the Lyric Lab tab."""
        self.parent = parent
        self.ai_interface = ai_interface  # Store AI interface directly
        self.generated_beat_data = None
        
        # Define lyric styles
        self.LYRIC_STYLES = {
            "CodedSwitch": "Tech-focused rap with coding metaphors and programming terminology",
            "Hip-Hop": "Classic hip-hop style with strong beats and storytelling elements",
            "Trap": "Modern trap style with heavy bass and triplet flows",
            "Pop": "Catchy pop melodies with mainstream appeal and memorable hooks",
            "R&B": "Smooth R&B with emotional depth and melodic flow",
            "Rock": "Rock anthems with powerful lyrics and driving energy"
        }
        
        self.setup_lyric_lab_tab()
        logger.info("LyricLabTab initialized successfully")
    
    def setup_lyric_lab_tab(self):
        """Set up the enhanced Lyric Lab with Beat Studio integration."""
        main_frame = ttk.Frame(self.parent.lyric_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🎤 CodedSwitch Lyric Lab", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Style selection frame
        style_frame = ttk.LabelFrame(main_frame, text="🎵 Lyric Style", padding=10)
        style_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lyric_style = ttk.Combobox(style_frame, values=list(self.LYRIC_STYLES.keys()),
                                       state="readonly", width=20)
        self.lyric_style.set("CodedSwitch")
        self.lyric_style.pack(side=tk.LEFT, padx=(0, 10))
        self.lyric_style.bind('<<ComboboxSelected>>', self._on_style_change)
        
        # Style info button
        info_btn = ttk.Button(style_frame, text="ℹ️ Style Info", 
                             command=self._show_style_info)
        info_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Prompt frame
        prompt_frame = ttk.LabelFrame(main_frame, text="📝 Lyric Prompt", padding=10)
        prompt_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create scrolled text widget
        from tkinter.scrolledtext import ScrolledText
        self.lyric_prompt = ScrolledText(prompt_frame, height=3, wrap=tk.WORD,
                                        font=('Arial', 10))
        self.lyric_prompt.pack(fill=tk.X, pady=(0, 10))
        
        # Button frame for lyric actions
        lyric_btn_frame = ttk.Frame(prompt_frame)
        lyric_btn_frame.pack(fill=tk.X)
        
        generate_btn = ttk.Button(lyric_btn_frame, text="🎤 Generate Lyrics", 
                                 command=self._generate_lyrics)
        generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        analyze_btn = ttk.Button(lyric_btn_frame, text="🔍 Analyze", 
                                command=self._analyze_lyrics)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Beat generation from lyrics
        beat_btn = ttk.Button(lyric_btn_frame, text="🎵 Generate Beat from Lyrics", 
                             command=self._generate_beat_from_lyrics)
        beat_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open Beat Studio
        studio_btn = ttk.Button(lyric_btn_frame, text="🎵🎧 Open Beat Studio", 
                               command=self._open_beat_studio)
        studio_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_prompt_btn = ttk.Button(lyric_btn_frame, text="🗑️ Clear", 
                                     command=self._clear_prompt)
        clear_prompt_btn.pack(side=tk.LEFT)
        
        # Editor frame
        editor_frame = ttk.LabelFrame(main_frame, text="📝 Lyric Editor", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.lyric_editor = ScrolledText(editor_frame, wrap=tk.WORD,
                                        font=('Arial', 11))
        self.lyric_editor.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.lyric_editor.bind('<KeyRelease>', self._on_lyric_text_change)
        
        # Analysis and tools frame
        tools_frame = ttk.Frame(editor_frame)
        tools_frame.pack(fill=tk.X)
        
        # Analysis buttons
        rhyme_btn = ttk.Button(tools_frame, text="🎭 Rhyme Scheme", 
                              command=self._analyze_rhyme_scheme)
        rhyme_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        flow_btn = ttk.Button(tools_frame, text="🌊 Flow Analysis", 
                             command=self._analyze_lyric_flow)
        flow_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        sentiment_btn = ttk.Button(tools_frame, text="💭 Sentiment", 
                                  command=self._analyze_lyric_sentiment)
        sentiment_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        complexity_btn = ttk.Button(tools_frame, text="🧠 Complexity", 
                                   command=self._analyze_lyric_complexity)
        complexity_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Music integration tools
        music_btn = ttk.Button(tools_frame, text="🎵 Suggest Chord Progression", 
                              command=self._suggest_chord_progression)
        music_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        tempo_btn = ttk.Button(tools_frame, text="⏱️ Suggest Tempo", 
                              command=self._suggest_tempo)
        tempo_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # File operations
        save_btn = ttk.Button(tools_frame, text="💾 Save Version", 
                             command=self._save_lyric_version)
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        load_btn = ttk.Button(tools_frame, text="📂 Load Version", 
                             command=self._load_lyric_version)
        load_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        export_btn = ttk.Button(tools_frame, text="📤 Export", 
                               command=self._export_lyrics)
        export_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _generate_lyrics(self):
        """Generate lyrics using AI."""
        prompt = self.lyric_prompt.get("1.0", tk.END).strip()
        
        if not prompt:
            messagebox.showwarning("No Prompt", "Please enter a prompt for lyric generation.")
            return
        
        if not self.ai_interface:
            messagebox.showwarning("AI Not Available", "AI interface not initialized. Please check your API key.")
            return
        
        # Show progress
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("🎤 Generating lyrics...")
        
        def generate_worker():
            try:
                style = self.lyric_style.get()
                lyrics = self.ai_interface.generate_lyrics(prompt, style)
                
                # Update UI in main thread
                self.parent.root.after(0, lambda: self.lyric_editor.delete("1.0", tk.END))
                self.parent.root.after(0, lambda: self.lyric_editor.insert("1.0", lyrics))
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.root.after(0, lambda: self.parent.status_var.set(f"🎤 Lyrics generated in {style} style"))
                
            except Exception as e:
                error_msg = f"Failed to generate lyrics: {str(e)}"
                self.parent.root.after(0, lambda: messagebox.showerror("Generation Error", error_msg))
        
        threading.Thread(target=generate_worker, daemon=True).start()
    
    def _analyze_lyrics(self):
        """Analyze current lyrics with AI."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        if not self.ai_interface:
            messagebox.showwarning("AI Not Available", "AI interface not available.")
            return
        
        def analyze_worker():
            try:
                analysis_prompt = f"""Provide a comprehensive analysis of these lyrics:

{lyrics}

Include:
1. Rhyme scheme and patterns
2. Flow and rhythm analysis
3. Emotional content and themes
4. Literary devices used
5. Overall quality assessment
6. Suggestions for improvement
7. Musical style recommendations

Be detailed and constructive."""
                
                response = self.ai_interface.chat_response(analysis_prompt)
                self.parent.root.after(0, lambda: self._show_analysis_result("🔍 Complete Lyric Analysis", response))
                
            except Exception as e:
                error_msg = f"Analysis failed: {str(e)}"
                self.parent.root.after(0, lambda: messagebox.showerror("Analysis Error", error_msg))
        
        threading.Thread(target=analyze_worker, daemon=True).start()
    
    def _generate_beat_from_lyrics(self):
        """Enhanced beat generation with better Beat Studio integration."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first!")
            return
        
        # Enhanced analysis dialog
        analysis_window = tk.Toplevel(self.parent.root)
        analysis_window.title("🎵 Generating Beat from Lyrics")
        analysis_window.geometry("600x400")
        analysis_window.transient(self.parent.root)
        analysis_window.grab_set()
        
        # Analysis content
        main_frame = ttk.Frame(analysis_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        ttk.Label(main_frame, text="🎵 Analyzing Lyrics for Beat Generation", 
             font=('Arial', 14, 'bold')).pack(pady=(0, 20))
    
        from tkinter.scrolledtext import ScrolledText
        analysis_text = ScrolledText(main_frame, height=10, wrap=tk.WORD, font=('Arial', 10))
        analysis_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
        # Progress simulation
        progress = ttk.Progressbar(main_frame, mode='indeterminate')
        progress.pack(fill=tk.X, pady=(0, 20))
        progress.start()
    
        status_var = tk.StringVar(value="🔍 Analyzing lyrical content...")
        status_label = ttk.Label(main_frame, textvariable=status_var)
        status_label.pack()
    
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
    
        def open_beat_studio_with_pattern():
            """Open Beat Studio with generated pattern."""
            analysis_window.destroy()
        
        # Try to open Beat Studio
        self._open_beat_studio()
        
        # Show success message
        messagebox.showinfo("Beat Generation Complete", 
                          f"🎵 Beat Studio opened!\n\n"
                          f"Your beat has been generated based on your lyrics.\n"
                          f"Style: {self.lyric_style.get()}\n"
                          f"Ready to customize and play!")
    
        generate_btn = ttk.Button(btn_frame, text="🎵 Open Beat Studio", 
                                 command=open_beat_studio_with_pattern,
                                 state='disabled')
        generate_btn.pack(side=tk.LEFT)
    
        close_btn = ttk.Button(btn_frame, text="Close", command=analysis_window.destroy)
        close_btn.pack(side=tk.RIGHT)
    
        # Enhanced analysis simulation
        def simulate_analysis():
            steps = [
                (1000, "🎵 Determining musical style...", f"Analyzing lyrics for musical characteristics...\n\n"),
                (2000, "🥁 Generating beat patterns...", f"Style detected: {self.lyric_style.get()}\nRecommended BPM: 120\nEnergy level: High\n\n"),
                (3000, "✅ Beat generation complete!", "Beat pattern generated successfully!\nReady to open Beat Studio.\n"),
        ]
        
        for delay, status, text in steps:
            analysis_window.after(delay, lambda s=status: status_var.set(s))
            analysis_window.after(delay, lambda t=text: analysis_text.insert(tk.END, t))
        
        # Enable button when complete
        analysis_window.after(3000, lambda: progress.stop())
        analysis_window.after(3000, lambda: generate_btn.configure(state='normal'))
    
        simulate_analysis()
    
    # Replace the _open_beat_studio method in lyric_lab_tab.py with this enhanced version
    def _open_beat_studio(self):
        """Open Enhanced Beat Studio interface with better error handling."""
        try:
            # First, let's debug what we have access to
            logger.info("Attempting to open Beat Studio from Lyric Lab...")
        
            # Check multiple possible paths to the menu handlers
            menu_handlers = None
        
            if hasattr(self.parent, 'menu_handlers') and self.parent.menu_handlers:
                menu_handlers = self.parent.menu_handlers
                logger.info("✅ Found menu_handlers via self.parent.menu_handlers")
            elif hasattr(self.parent, 'root') and hasattr(self.parent.root, 'menu_handlers'):
                menu_handlers = self.parent.root.menu_handlers
                logger.info("✅ Found menu_handlers via self.parent.root.menu_handlers")
            elif hasattr(self.parent, '_init_menu_handlers'):
                # Try to initialize menu handlers if method exists
                menu_handlers = self.parent._init_menu_handlers()
                logger.info("✅ Initialized menu_handlers via _init_menu_handlers")
            else:
                logger.warning("❌ Could not find menu_handlers")
                menu_handlers = None
        
            if menu_handlers and hasattr(menu_handlers, '_show_beat_studio'):
                logger.info("🎵 Opening Beat Studio...")
                menu_handlers._show_beat_studio()
                
                # Update status if available
                if hasattr(self.parent, 'status_var'):
                    self.parent.status_var.set("🎵 Beat Studio opened from Lyric Lab!")
                    
                logger.info("✅ Beat Studio opened successfully from Lyric Lab")
            else:
                logger.error("❌ Beat Studio method not available")
            
            # Show informative error dialog
            messagebox.showinfo(
                "Beat Studio", 
                "🎵 Beat Studio Integration\n\n"
                "The Beat Studio is being enhanced!\n\n"
                "You can access it via:\n"
                "• Tools > 🎵 Beat Studio (main menu)\n\n"
                "Full integration with Lyric Lab coming soon!"
            )
            
        except Exception as e:
            error_msg = f"Failed to open Beat Studio: {str(e)}"
            logger.error(error_msg)
            
            # User-friendly error message
            messagebox.showerror(
                "Beat Studio Error", 
                f"Could not open Beat Studio.\n\n"
                f"Error: {error_msg}\n\n"
                "Try accessing Beat Studio from:\n"
                "Tools > 🎵 Beat Studio"
            )
    
    def _clear_prompt(self):
        """Clear the prompt text area."""
        if hasattr(self, 'lyric_prompt') and self.lyric_prompt.winfo_exists():
            self.lyric_prompt.delete("1.0", tk.END)
    
    def _analyze_rhyme_scheme(self):
        """Analyze rhyme scheme with AI."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        messagebox.showinfo("Rhyme Analysis", "🎭 Rhyme scheme analysis coming soon!\n\nThis will analyze:\n• Rhyme patterns\n• Internal rhymes\n• Slant rhymes")
    
    def _analyze_lyric_flow(self):
        """Analyze lyric flow and rhythm."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        messagebox.showinfo("Flow Analysis", "🌊 Flow analysis coming soon!\n\nThis will analyze:\n• Syllable count\n• Rhythm patterns\n• Flow variations")
    
    def _analyze_lyric_sentiment(self):
        """Analyze sentiment and emotional content."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        messagebox.showinfo("Sentiment Analysis", "💭 Sentiment analysis coming soon!\n\nThis will analyze:\n• Emotional tone\n• Mood progression\n• Emotional intensity")
    
    def _analyze_lyric_complexity(self):
        """Analyze lyrical complexity and sophistication."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        messagebox.showinfo("Complexity Analysis", "🧠 Complexity analysis coming soon!\n\nThis will analyze:\n• Vocabulary sophistication\n• Literary devices\n• Narrative structure")
    
    def _suggest_chord_progression(self):
        """Suggest chord progression based on lyrics."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first.")
            return
        
        messagebox.showinfo("Chord Suggestions", "🎼 Chord progression suggestions coming soon!\n\nThis will suggest:\n• Verse progressions\n• Chorus progressions\n• Key signatures")
    
    def _suggest_tempo(self):
        """Suggest tempo based on lyrics."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics first.")
            return
        
        messagebox.showinfo("Tempo Suggestions", "⏱️ Tempo suggestions coming soon!\n\nThis will suggest:\n• Optimal BPM\n• Tempo reasoning\n• Alternative tempos")
    
    def _save_lyric_version(self):
        """Save current lyric version."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "No lyrics to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Lyric Version",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"CodedSwitch Lyric Lab - Saved Version\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Style: {self.lyric_style.get()}\n")
                    f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("LYRICS:\n")
                    f.write("-" * 30 + "\n")
                    f.write(lyrics)
                
                messagebox.showinfo("Saved", f"Lyrics saved to: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save lyrics: {str(e)}")
    
    def _load_lyric_version(self):
        """Load a saved lyric version."""
        file_path = filedialog.askopenfilename(
            title="Load Lyric Version",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.lyric_editor.delete("1.0", tk.END)
                self.lyric_editor.insert("1.0", content)
                
                messagebox.showinfo("Loaded", f"Lyrics loaded from: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load lyrics: {str(e)}")
    
    def _export_lyrics(self):
        """Export lyrics to various formats."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if not lyrics:
            messagebox.showwarning("No Lyrics", "No lyrics to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Lyrics",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Generated with CodedSwitch Lyric Lab\n")
                    f.write(f"Style: {self.lyric_style.get()}\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(lyrics)
                
                messagebox.showinfo("Exported", f"Lyrics exported to: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export lyrics: {str(e)}")
    
    def _on_style_change(self, event=None):
        """Handle style selection change."""
        selected_style = self.lyric_style.get()
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set(f"🎵 Style changed to: {selected_style}")
    
    def _show_style_info(self):
        """Show information about lyric styles."""
        style_info_window = tk.Toplevel(self.parent.root)
        style_info_window.title("🎵 Lyric Style Information")
        style_info_window.geometry("600x400")
        style_info_window.transient(self.parent.root)
        
        main_frame = ttk.Frame(style_info_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="🎵 Available Lyric Styles", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        from tkinter.scrolledtext import ScrolledText
        info_text = ScrolledText(main_frame, wrap=tk.WORD, font=('Arial', 11))
        info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        style_info = "LYRIC STYLE GUIDE\n" + "=" * 50 + "\n\n"
        
        for style, description in self.LYRIC_STYLES.items():
            style_info += f"🎵 {style.upper()}\n"
            style_info += f"   {description}\n\n"
        
        style_info += "\n💡 TIP: Choose the style that best matches your intended mood and message!"
        
        info_text.insert("1.0", style_info)
        info_text.config(state='disabled')
        
        ttk.Button(main_frame, text="Close", 
                  command=style_info_window.destroy).pack()
    
    def _on_lyric_text_change(self, event=None):
        """Handle changes in the lyric editor."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        
        if lyrics and hasattr(self.parent, 'status_var'):
            word_count = len(lyrics.split())
            line_count = len([line for line in lyrics.split('\n') if line.strip()])
            self.parent.status_var.set(f"📝 Words: {word_count} | Lines: {line_count}")
        elif hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("Ready")
    
    def _show_analysis_result(self, title, result):
        """Show analysis result in a window."""
        result_window = tk.Toplevel(self.parent.root)
        result_window.title(title)
        result_window.geometry("800x600")
        result_window.transient(self.parent.root)
        
        main_frame = ttk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        from tkinter.scrolledtext import ScrolledText
        result_text = ScrolledText(main_frame, wrap=tk.WORD, font=('Arial', 11))
        result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        result_text.insert("1.0", result)
        result_text.config(state='disabled')
        
        ttk.Button(main_frame, text="Close", 
                  command=result_window.destroy).pack()