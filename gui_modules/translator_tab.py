"""
Translator Tab Functionality for CodedSwitch Application - Fixed Version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText as TtkScrolledText
import logging
import threading

logger = logging.getLogger(__name__)

# Safe imports
try:
    from .constants import PROGRAMMING_LANGUAGES
    from .utils import ErrorHandler, InputValidator
except ImportError:
    try:
        from constants import PROGRAMMING_LANGUAGES
        from utils import ErrorHandler, InputValidator
    except ImportError:
        # Fallback
        PROGRAMMING_LANGUAGES = ["Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "TypeScript"]
        
        class ErrorHandler:
            @staticmethod
            def handle_error(operation_name: str):
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            logger.error(f"Error in {operation_name}: {e}")
                            messagebox.showerror(f"{operation_name} Error", f"An error occurred: {e}")
                            return None
                    return wrapper
                return decorator
        
        class InputValidator:
            @staticmethod
            def validate_code(code: str, max_length: int = 50000) -> tuple:
                if not code or not code.strip():
                    return False, "Code cannot be empty"
                if len(code) > max_length:
                    return False, f"Code exceeds maximum length of {max_length} characters"
                return True, "Valid"

class TranslatorTab:
    """Handles all translator tab functionality."""
    
    def __init__(self, parent, ai_interface):
        self.parent = parent
        self.ai = ai_interface
        self.setup_translator_tab()
    
    def setup_translator_tab(self):
        """Set up the translator tab with enhanced UI."""
        
        # Main frame
        main_frame = ttk.Frame(self.parent.translator_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Language selection frame
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Source language
        ttk.Label(lang_frame, text="From:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.parent.source_lang = ttk.Combobox(lang_frame, values=PROGRAMMING_LANGUAGES, 
                                              state="readonly", width=15)
        self.parent.source_lang.set("Python")
        self.parent.source_lang.pack(side=tk.LEFT, padx=(5, 10))
        self.parent.source_lang.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # Swap button
        swap_btn = ttk.Button(lang_frame, text="⇄", width=3, 
                             command=self._swap_languages,
                             bootstyle="info-outline")
        swap_btn.pack(side=tk.LEFT, padx=5)
        
        # Target language
        ttk.Label(lang_frame, text="To:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
        self.parent.target_lang = ttk.Combobox(lang_frame, values=PROGRAMMING_LANGUAGES, 
                                              state="readonly", width=15)
        self.parent.target_lang.set("JavaScript")
        self.parent.target_lang.pack(side=tk.LEFT, padx=(5, 10))
        self.parent.target_lang.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # Model selection
        ttk.Label(lang_frame, text="Model:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(20, 0))
        self.parent.model_var = tk.StringVar(value="gemini-1.5-flash")
        model_combo = ttk.Combobox(lang_frame, textvariable=self.parent.model_var,
                                  values=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"],
                                  state="readonly", width=20)
        model_combo.pack(side=tk.LEFT, padx=(5, 0))
        model_combo.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # Code input/output frame
        code_frame = ttk.Frame(main_frame)
        code_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source code frame
        source_frame = ttk.LabelFrame(code_frame, text="📝 Source Code", padding=10)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.parent.source_code = TtkScrolledText(source_frame, height=20, wrap=tk.WORD,
                                                 font=('Consolas', 11))
        self.parent.source_code.pack(fill=tk.BOTH, expand=True)
        self.parent.source_code.bind('<KeyRelease>', self._on_source_code_change)
        
        # Buttons frame
        btn_frame = ttk.Frame(code_frame)
        btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Translate button
        self.translate_btn = ttk.Button(btn_frame, text="🔄 Translate", 
                                  command=self._translate_code,
                                  bootstyle="success", width=15)
        self.translate_btn.pack(pady=10)
        
        # Clear button
        clear_btn = ttk.Button(btn_frame, text="🗑️ Clear", 
                              command=self._clear_all,
                              bootstyle="danger-outline", width=15)
        clear_btn.pack(pady=5)
        
        # Load file button
        load_btn = ttk.Button(btn_frame, text="📂 Load File", 
                             command=self._load_file,
                             bootstyle="info-outline", width=15)
        load_btn.pack(pady=5)
        
        # Save file button
        save_btn = ttk.Button(btn_frame, text="💾 Save Result", 
                             command=self._save_result,
                             bootstyle="info-outline", width=15)
        save_btn.pack(pady=5)
        
        # Target code frame
        target_frame = ttk.LabelFrame(code_frame, text="✨ Translated Code", padding=10)
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.parent.target_code = TtkScrolledText(target_frame, height=20, wrap=tk.WORD,
                                                 font=('Consolas', 11))
        self.parent.target_code.pack(fill=tk.BOTH, expand=True)
    
    ErrorHandler.handle_error("Language Change")
    def _on_language_change(self, event=None):
        """Handle language selection change."""
        source = self.parent.source_lang.get()
        target = self.parent.target_lang.get()
        logger.info(f"Language changed: {source} -> {target}")
        
        if hasattr(self.parent, 'config_manager'):
            self.parent.config_manager.set('last_source_lang', source)
            self.parent.config_manager.set('last_target_lang', target)
            self.parent.config_manager.save_config()
    
    @ErrorHandler.handle_error("Model Change")
    def on_model_change(self, event=None):
        """Handle model selection change."""
        model = self.parent.model_var.get()
        logger.info(f"Model changed to: {model}")
        
        if hasattr(self.ai, 'use_gemini_model'):
            self.ai.use_gemini_model(model)
        
        if hasattr(self.parent, 'config_manager'):
            self.parent.config_manager.set('gemini_model', model)
            self.parent.config_manager.save_config()
    
    def _swap_languages(self):
        """Swap source and target languages."""
        source = self.parent.source_lang.get()
        target = self.parent.target_lang.get()
        
        self.parent.source_lang.set(target)
        self.parent.target_lang.set(source)
        
        self._on_language_change()
    
    @ErrorHandler.handle_error("Source Code Change")
    def _on_source_code_change(self, event=None):
        """Handle source code text changes."""
        # Auto-save functionality could go here
        pass
    
    @ErrorHandler.handle_error("Translate Code")
    def _translate_code(self):
        """Translate code using the AI interface."""
        if not self.parent.ai_interface:
            messagebox.showwarning("AI Not Available", 
                                 "AI interface not initialized. Please check your API key.")
            return
        
        source_code = self.parent.source_code.get("1.0", tk.END).strip()
        if not source_code:
            messagebox.showwarning("No Code", "Please enter source code to translate.")
            return
        
        # Validate code
        is_valid, error_msg = InputValidator.validate_code(source_code)
        if not is_valid:
            messagebox.showwarning("Invalid Code", error_msg)
            return
        
        source_lang = self.parent.source_lang.get()
        target_lang = self.parent.target_lang.get()
        
        if source_lang == target_lang:
            messagebox.showwarning("Same Language", 
                                 "Source and target languages cannot be the same.")
            return
        
        # Update status
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set(f"🔄 Translating {source_lang} to {target_lang}...")
        
        # Disable button during translation
        self.translate_btn.config(state='disabled')
        
        def translate_worker():
            try:
                # Use the AI interface to translate
                response = self.parent.ai_interface.translate_code(
                    source_code=source_code,
                    target_language=target_lang
                )
                
                # Update UI on main thread
                self.parent.root.after(0, lambda: self._display_translation_result(response))
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.root.after(0, lambda: self.parent.status_var.set("✅ Translation complete!"))
                
            except Exception as e:
                error_msg = f"Translation failed: {str(e)}"
                self.parent.root.after(0, lambda: messagebox.showerror("Translation Error", error_msg))
                logger.error(error_msg, exc_info=True)
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.root.after(0, lambda: self.parent.status_var.set("❌ Translation failed"))
            finally:
                # Re-enable button
                self.parent.root.after(0, lambda: self.translate_btn.config(state='normal'))
        
        # Run translation in background thread
        thread = threading.Thread(target=translate_worker)
        thread.daemon = True
        thread.start()
    
    def _display_translation_result(self, result):
        """Display the translation result."""
        self.parent.target_code.delete("1.0", tk.END)
        self.parent.target_code.insert("1.0", result)
        
        logger.info("Code translation completed successfully")
    
    def _clear_all(self):
        """Clear both source and target code areas."""
        self.parent.source_code.delete("1.0", tk.END)
        self.parent.target_code.delete("1.0", tk.END)
        
        if hasattr(self.parent, 'status_var'):
            self.parent.status_var.set("🗑️ Code areas cleared")
    
    @ErrorHandler.handle_error("File Loading")
    def _load_file(self):
        """Load code from a file."""
        file_path = filedialog.askopenfilename(
            title="Load Code File",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("Java files", "*.java"),
                ("C++ files", "*.cpp *.cc *.cxx"),
                ("C# files", "*.cs"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.parent.source_code.delete("1.0", tk.END)
                self.parent.source_code.insert("1.0", content)
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.status_var.set(f"📂 Loaded: {file_path}")
                
                logger.info(f"Loaded file: {file_path}")
                
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to load file: {str(e)}")
    
    @ErrorHandler.handle_error("File Saving")
    def _save_result(self):
        """Save the translated code to a file."""
        translated_code = self.parent.target_code.get("1.0", tk.END).strip()
        
        if not translated_code:
            messagebox.showwarning("No Content", "No translated code to save.")
            return
        
        target_lang = self.parent.target_lang.get().lower()
        
        # Determine file extension
        ext_map = {
            "python": ".py",
            "javascript": ".js", 
            "java": ".java",
            "c++": ".cpp",
            "c#": ".cs",
            "php": ".php",
            "ruby": ".rb",
            "go": ".go",
            "rust": ".rs",
            "typescript": ".ts"
        }
        
        default_ext = ext_map.get(target_lang, ".txt")
        
        file_path = filedialog.asksaveasfilename(
            title="Save Translated Code",
            defaultextension=default_ext,
            filetypes=[
                (f"{target_lang.title()} files", f"*{default_ext}"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(translated_code)
                
                if hasattr(self.parent, 'status_var'):
                    self.parent.status_var.set(f"💾 Saved: {file_path}")
                
                logger.info(f"Saved translated code to: {file_path}")
                messagebox.showinfo("File Saved", f"Code saved to: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")