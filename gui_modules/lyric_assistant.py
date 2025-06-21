"""
Lyric Assistant Module for CodedSwitch

Provides AI-powered lyric generation, analysis, and enhancement tools.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
from datetime import datetime
import json
import os

class LyricAssistant:
    """AI-powered lyric generation and analysis assistant."""
    
    def __init__(self, parent, ai_interface):
        """Initialize the Lyric Assistant."""
        self.parent = parent
        self.ai = ai_interface
        self.lyric_history = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the Lyric Assistant user interface."""
        # Create main window
        self.window = tk.Toplevel(self.parent.root)
        self.window.title("🎤 Lyric Assistant")
        self.window.geometry("900x700")
        
        # Main container
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        self._create_input_section(main_frame)
        
        # Analysis section
        self._create_analysis_section(main_frame)
        
        # Generation section
        self._create_generation_section(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, 
                 relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, pady=(5, 0))
    
    def _create_input_section(self, parent):
        """Create the lyric input section."""
        frame = ttk.LabelFrame(parent, text="📝 Lyrics", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Lyrics editor
        self.lyric_editor = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, width=80, height=10,
            font=('Arial', 10)
        )
        self.lyric_editor.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Load/save buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="Load Lyrics", 
                  command=self._load_lyrics).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Save Lyrics", 
                  command=self._save_lyrics).pack(side=tk.LEFT)
    
    def _create_analysis_section(self, parent):
        """Create the lyric analysis section."""
        frame = ttk.LabelFrame(parent, text="🔍 Analysis", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Analysis options
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(options_frame, text="Analyze Rhyme Scheme",
                  command=self._analyze_rhyme_scheme).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(options_frame, text="Check Flow",
                  command=self._check_flow).pack(side=tk.LEFT, padx=5)
        ttk.Button(options_frame, text="Themes & Content",
                  command=self._analyze_themes).pack(side=tk.LEFT)
        
        # Analysis results
        self.analysis_results = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, width=80, height=10,
            font=('Consolas', 9), state='disabled'
        )
        self.analysis_results.pack(fill=tk.BOTH, expand=True)
    
    def _create_generation_section(self, parent):
        """Create the lyric generation section."""
        frame = ttk.LabelFrame(parent, text="✨ Generate", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Style selection
        style_frame = ttk.Frame(frame)
        style_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(style_frame, text="Style:").pack(side=tk.LEFT, padx=(0, 5))
        self.style_var = tk.StringVar(value="Rap")
        style_combo = ttk.Combobox(
            style_frame, textvariable=self.style_var,
            values=["Rap", "R&B", "Pop", "Rock", "Country", "Jazz", "Custom"],
            state='readonly', width=15
        )
        style_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Generation prompt
        prompt_frame = ttk.Frame(frame)
        prompt_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(prompt_frame, text="Prompt:").pack(side=tk.LEFT, padx=(0, 5))
        self.prompt_entry = ttk.Entry(prompt_frame)
        self.prompt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.prompt_entry.insert(0, "Write a verse about...")
        
        # Generate button
        ttk.Button(frame, text="Generate Lyrics", 
                  command=self._generate_lyrics).pack(pady=(5, 0))
    
    def _load_lyrics(self):
        """Load lyrics from a file."""
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.lyric_editor.delete('1.0', tk.END)
                    self.lyric_editor.insert('1.0', f.read())
                self.status_var.set(f"Loaded lyrics from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def _save_lyrics(self):
        """Save lyrics to a file."""
        lyrics = self.lyric_editor.get('1.0', tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "No lyrics to save.")
            return
            
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(lyrics)
                self.status_var.set(f"Saved lyrics to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def _analyze_lyrics(self, analysis_type):
        """Analyze lyrics with the specified analysis type."""
        lyrics = self.lyric_editor.get('1.0', tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Please enter some lyrics to analyze.")
            return
        
        self.status_var.set(f"Analyzing {analysis_type.lower()}...")
        
        def analyze_worker():
            try:
                analysis = self._get_lyric_analysis(lyrics, analysis_type)
                self.parent.root.after(0, self._display_analysis, analysis_type, analysis)
                self.parent.root.after(0, lambda: self.status_var.set("Analysis complete"))
            except Exception as e:
                self.parent.root.after(0, lambda: messagebox.showerror(
                    "Analysis Error", f"Failed to analyze lyrics: {str(e)}"))
                self.parent.root.after(0, lambda: self.status_var.set("Analysis failed"))
        
        threading.Thread(target=analyze_worker, daemon=True).start()
    
    def _analyze_rhyme_scheme(self):
        """Analyze the rhyme scheme of the lyrics."""
        self._analyze_lyrics("Rhyme Scheme")
    
    def _check_flow(self):
        """Check the flow and rhythm of the lyrics."""
        self._analyze_lyrics("Flow")
    
    def _analyze_themes(self):
        """Analyze themes and content of the lyrics."""
        self._analyze_lyrics("Themes")
    
    def _get_lyric_analysis(self, lyrics, analysis_type):
        """Get AI analysis of lyrics based on the specified type."""
        prompts = {
            "Rhyme Scheme": "Analyze the rhyme scheme of these lyrics. Identify the rhyme pattern, highlight any complex multisyllabic rhymes, and suggest improvements for better flow.",
            "Flow": "Analyze the flow and rhythm of these lyrics. Check syllable count per line, identify any awkward phrasing, and suggest improvements for better musicality.",
            "Themes": "Analyze the themes and content of these lyrics. Identify main themes, emotional tone, and provide suggestions for enhancing the message and impact."
        }
        
        prompt = f"{prompts.get(analysis_type, 'Analyze these lyrics:')}\n\n{lyrics}"
        
        try:
            response = self.ai.chat_response(prompt)
            return f"=== {analysis_type} Analysis ===\n\n{response}"
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _display_analysis(self, analysis_type, analysis):
        """Display the analysis results."""
        self.analysis_results.config(state='normal')
        self.analysis_results.delete('1.0', tk.END)
        self.analysis_results.insert('1.0', analysis)
        self.analysis_results.config(state='disabled')
        
        # Add to history
        self._add_to_history(analysis_type, analysis)
    
    def _generate_lyrics(self):
        """Generate lyrics based on the current prompt and style."""
        prompt = self.prompt_entry.get().strip()
        style = self.style_var.get()
        
        if not prompt or prompt == "Write a verse about...":
            messagebox.showwarning("No Prompt", "Please enter a prompt for generation.")
            return
        
        self.status_var.set(f"Generating {style.lower()} lyrics...")
        
        def generate_worker():
            try:
                generated = self._generate_with_ai(prompt, style)
                self.parent.root.after(0, self._display_generated_lyrics, generated)
                self.parent.root.after(0, lambda: self.status_var.set("Generation complete"))
            except Exception as e:
                self.parent.root.after(0, lambda: messagebox.showerror(
                    "Generation Error", f"Failed to generate lyrics: {str(e)}"))
                self.parent.root.after(0, lambda: self.status_var.set("Generation failed"))
        
        threading.Thread(target=generate_worker, daemon=True).start()
    
    def _generate_with_ai(self, prompt, style):
        """Generate lyrics using the AI interface."""
        generation_prompt = (
            f"Write {style} lyrics about: {prompt}\n\n"
            "Guidelines:\n"
            "- Match the style and tone of the specified genre\n"
            "- Use creative and original metaphors\n"
            "- Maintain consistent rhyme scheme and flow\n"
            "- Keep it between 8-16 lines"
        )
        
        try:
            return self.ai.chat_response(generation_prompt)
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    def _display_generated_lyrics(self, lyrics):
        """Display the generated lyrics in the editor."""
        self.lyric_editor.delete('1.0', tk.END)
        self.lyric_editor.insert('1.0', lyrics)
        
        # Add to history
        self._add_to_history("Generated Lyrics", lyrics)
    
    def _add_to_history(self, action, content):
        """Add an action to the history log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.lyric_history.append({
            'timestamp': timestamp,
            'action': action,
            'content': content[:100] + '...' if len(content) > 100 else content
        })
        
        # Update status
        self.status_var.set(f"{action} completed at {timestamp}")

    def show(self):
        """Show the Lyric Assistant window."""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
