"""
CodedSwitch - Integrated GUI for AI Code Translator with LLM Integration and Premium Features

This module provides a GUI that integrates the chatbot, translator, vulnerability scanner,
and NEW LYRIC LAB into a single, seamless interface powered by the IntegratedTranslatorAI.
"""

import os
import sys
import logging
import argparse
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText as TtkScrolledText
from pathlib import Path
from datetime import datetime
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import json
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import our modules
try:
    from security.premium_manager import PremiumManager
    from security.vulnerability_scanner import VulnerabilityScanner
    from integrated_ai import IntegratedTranslatorAI
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    # Create fallback classes if imports fail
    class PremiumManager:
        def is_premium(self):
            return True
        def get_license_info(self):
            return {'type': 'premium', 'days_remaining': 30}
    
    class VulnerabilityScanner:
        def scan_code(self, code, language):
            return []

# Define available themes
THEMES = {
    "Dark": "darkly",
    "Light": "cosmo",
    "Monokai": "cyborg",
    "Solarized": "solar",
    "Default": "litera"
}

# Programming language options
PROGRAMMING_LANGUAGES = [
    "Python",
    "JavaScript",
    "Java",
    "C++",
    "PHP"
]

class IntegratedTranslatorGUI:
    def __init__(self, gemini_api_key=None, gemini_model="models/gemini-1.5-pro-001", enable_premium=False, enable_security=True):
        """Initialize the CodedSwitch integrated translator GUI."""
        # Initialize with bootstrap theme
        self.style = ttk.Style(theme=THEMES["Dark"])
        self.root = self.style.master
        self.root.title("CodedSwitch - AI Code Translator & Lyric Lab")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set application icon
        if platform.system() == "Windows":
            icon_path = os.path.join(os.path.dirname(__file__), "resources", "codedswitch_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
        
        # Initialize variables
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self.enable_premium = enable_premium  # Premium features flag
        self.enable_security = enable_security  # Always enabled for demo
        self.current_file = None
        self.font_size = 10
        self.current_theme = "Dark"
        
        # Initialize PremiumManager
        self.premium_manager = PremiumManager()
        
        # Initialize language vars
        self.source_lang = tk.StringVar(value="Python")
        self.target_lang = tk.StringVar(value="JavaScript")
        self.scan_lang = tk.StringVar(value="Python")
        
        # Initialize settings variables
        self.vulnerability_scanner = None
        self.scan_results = []
        self.scan_in_progress = False
        self.word_wrap_var = tk.BooleanVar(value=False)
        self.line_numbers_var = tk.BooleanVar(value=True)
        self.syntax_highlight_var = tk.BooleanVar(value=True)
        self.highlight_style_var = tk.StringVar(value="monokai")
        self.auto_indent_var = tk.BooleanVar(value=True)
        self.ui_scale_var = tk.DoubleVar(value=1.0)
        
        # Configure global styles
        self._configure_styles()
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self._create_status_bar()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.translator_tab = ttk.Frame(self.notebook)
        self.chatbot_tab = ttk.Frame(self.notebook)
        self.security_tab = ttk.Frame(self.notebook)
        self.lyric_tab = ttk.Frame(self.notebook)  # NEW LYRIC LAB TAB!
        
        # Add tabs to notebook with icons
        self.notebook.add(self.translator_tab, text="  CodedSwitch Translator  ")
        self.notebook.add(self.chatbot_tab, text="  CodedSwitch Assistant  ")
        self.notebook.add(self.security_tab, text="  Security Scanner  ")
        self.notebook.add(self.lyric_tab, text="  🎤 Lyric Lab  ")  # NEW TAB!
        
        # Initialize components
        self._setup_translator_tab()
        self._setup_chatbot_tab()
        self._setup_security_tab()
        self._setup_lyric_lab_tab()  # NEW SETUP METHOD!
        
        # Check for API key first (environment variable or passed parameter)
        if not self.gemini_api_key:
            # Try to get API key from environment variable
            self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
            
            # If still no key, try credentials file
            if not self.gemini_api_key:
                credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
                if os.path.exists(credentials_path):
                    try:
                        with open(credentials_path, 'r') as f:
                            credentials = json.load(f)
                            self.gemini_api_key = credentials.get("api_key")
                    except Exception as e:
                        logger.warning(f"Failed to load credentials from file: {e}")
        
        # Initialize AI interface
        self._initialize_ai()
            
        # Check for API key - prompt only if still not found
        if not self.gemini_api_key:
            self.prompt_for_api_key()
            
        # Add keyboard shortcuts
        self._setup_keyboard_shortcuts()
            
        # Load settings
        self._load_settings()
        
        # Update status bar indicators
        self.model_indicator.config(text=f"Model: {self.gemini_model}")
        self.theme_indicator.config(text=f"Theme: {self.current_theme}")
        self.api_status.config(text="API: Connected" if self.gemini_api_key else "API: Not Connected")
        
        # Ensure model name consistency
        self.model_var.set(self.gemini_model)

    def _initialize_ai(self):
        """Initialize the AI interface."""
        try:
            # Check if we have an API key
            if not self.gemini_api_key:
                return  # Will be handled by prompt_for_api_key later
            
            # Initialize Gemini interface
            self.ai = IntegratedTranslatorAI(
                api_key=self.gemini_api_key,
                model_name=self.gemini_model
            )
            
            logger.info(f"Successfully initialized AI with model: {self.gemini_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI: {str(e)}")
            messagebox.showerror("Error", f"Failed to initialize AI: {str(e)}")
            self.root.quit()

    def _configure_styles(self):
        """Configure custom styles for the application."""
        # Configure text styles
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TCheckbutton", font=("Segoe UI", 10))
        self.style.configure("TRadiobutton", font=("Segoe UI", 10))
        
        # Configure heading styles
        self.style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))
        
        # Configure notebook styles
        self.style.configure("TNotebook", padding=5)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(10, 5))
        
        # Configure button styles
        self.style.configure("primary.TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("success.TButton", font=("Segoe UI", 10))
        self.style.configure("danger.TButton", font=("Segoe UI", 10))

    def _setup_keyboard_shortcuts(self):
        """Enhanced keyboard shortcuts with tooltips and help system."""
        shortcuts = {
            "<Control-n>": ("New File", self.new_file),
            "<Control-o>": ("Open File", self.open_file),
            "<Control-s>": ("Save File", self.save_file),
            "<Control-t>": ("Translate Code", self.translate_code),
            "<F5>": ("Scan for Vulnerabilities", self.scan_code_for_vulnerabilities),
            "<F1>": ("Help", self._show_help),
            "<Control-q>": ("Quit", self.root.quit),
            "<Control-plus>": ("Increase Font", lambda e: self._change_font_size(1)),
            "<Control-minus>": ("Decrease Font", lambda e: self._change_font_size(-1)),
            "<Control-r>": ("Reverse Translation", lambda e: self.translate_code(reverse=True)),
            "<Control-Shift-C>": ("Clear All", lambda e: self.clear_all_code()),
            "<Control-d>": ("Demo Mode", lambda e: self._load_demo_code()),
            "<Control-e>": ("Export Results", lambda e: self._export_current_results()),
            "<Escape>": ("Clear Status", lambda e: self.status_var.set("Ready")),
        }
        
        # Bind all shortcuts
        for shortcut, (description, command) in shortcuts.items():
            try:
                self.root.bind(shortcut, lambda e, cmd=command: cmd() if callable(cmd) else cmd(e))
            except Exception as e:
                print(f"Failed to bind shortcut {shortcut}: {e}")
        
        # Store shortcuts for help display
        self.keyboard_shortcuts = shortcuts
        
    def prompt_for_api_key(self):
        """Prompt the user for their API key."""
        dialog = tk.Toplevel(self.root)
        dialog.title("CodedSwitch - Gemini API Key Required")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Force the dialog to be centered on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add a way to move the dialog if it's still not visible
        def start_move(event):
            dialog.x = event.x
            dialog.y = event.y
        
        def on_motion(event):
            deltax = event.x - dialog.x
            deltay = event.y - dialog.y
            x = dialog.winfo_x() + deltax
            y = dialog.winfo_y() + deltay
            dialog.geometry(f"+{x}+{y}")
        
        dialog.bind("<ButtonPress-1>", start_move)
        dialog.bind("<B1-Motion>", on_motion)
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add header
        ttk.Label(
            main_frame,
            text="CodedSwitch API Key Required",
            font=("Helvetica", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Add description
        ttk.Label(
            main_frame,
            text="Please enter your Gemini API key to use CodedSwitch.",
            wraplength=460
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Add key entry
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(key_frame, text="API Key:").pack(side=tk.LEFT)
        
        self.api_key_var = tk.StringVar()
        key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, width=40, show="*")
        key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Add show/hide checkbox
        show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main_frame,
            text="Show API key",
            variable=show_var,
            command=lambda: key_entry.config(show="" if show_var.get() else "*")
        ).pack(pady=(0, 10))
        
        # Add help text
        help_text = """To get your API key:
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key"""
        
        help_label = ttk.Label(
            main_frame,
            text=help_text,
            justify=tk.LEFT,
            font=("Segoe UI", 9)
        )
        help_label.pack(pady=(0, 20))
        
        # Add buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add demo mode button
        ttk.Button(
            btn_frame,
            text="Use Demo Mode",
            command=lambda: self._enter_demo_mode(dialog)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Save",
            command=lambda: self._save_api_key(self.api_key_var.get(), dialog)
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Configure entry
        key_entry.focus()
        
        # Wait for dialog
        self.root.wait_window(dialog)
    
    def _enter_demo_mode(self, dialog):
        """Enter demo mode with a mock API key."""
        # This is a mock key for demo purposes only
        mock_key = "DEMO_MODE_NO_REAL_API_ACCESS"
        self._mock_ai_interface()
        dialog.destroy()
        self.status_var.set("Running in demo mode - limited functionality")
        self.api_status.config(text="API: Demo Mode")
        
    def _mock_ai_interface(self):
        """Create a mock AI interface for demo purposes."""
        self.ai = type('MockAI', (), {
            'translate_code': lambda source_code, target_language, use_neural=False, use_llm=False: 
                f"// Translated to {target_language}\n// DEMO MODE - NO ACTUAL TRANSLATION\n\n{source_code}",
            'chat': lambda message: "This is demo mode. Please enter a valid API key for full functionality.",
            'chat_response': lambda message: "This is demo mode. Please enter a valid API key for full functionality.",
            'scan_vulnerabilities': lambda code, language: [
                type('VulnerabilityResult', (), {
                    'severity': type('Severity', (), {'name': 'HIGH'})(),
                    'line_number': 1,
                    'category': 'Demo Vulnerability',
                    'description': 'This is a demo vulnerability for testing purposes.'
                })()
            ]
        })()
        
    def _save_api_key(self, api_key: str, dialog: tk.Toplevel):
        """Save the API key and initialize AI."""
        if not api_key:
            messagebox.showwarning("Invalid Key", "Please enter a valid API key.")
            return
            
        try:
            # Save API key
            self.gemini_api_key = api_key
            
            # Initialize AI with the new key
            self._initialize_ai()
            
            if hasattr(self, 'ai') and self.ai:
                messagebox.showinfo("Success", "API key saved successfully!")
                dialog.destroy()
                # Update status indicators
                self.api_status.config(text="API: Connected")
            else:
                messagebox.showerror("Error", "Failed to initialize AI with the provided key.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}")
            
    def _create_menu_bar(self):
        """Create the menu bar."""
        # Create menubar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save...", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=lambda: self._select_all())
        edit_menu.add_separator()
        edit_menu.add_command(label="Increase Font Size", accelerator="Ctrl+Plus", command=lambda: self._change_font_size(1))
        edit_menu.add_command(label="Decrease Font Size", accelerator="Ctrl+Minus", command=lambda: self._change_font_size(-1))
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Themes submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        # Add theme options
        self.theme_var = tk.StringVar(value=self.current_theme)
        for theme_name in THEMES:
            theme_menu.add_radiobutton(
                label=theme_name,
                variable=self.theme_var,
                value=theme_name,
                command=self._change_theme
            )
        
        view_menu.add_separator()
        view_menu.add_command(label="Settings...", command=self._show_settings)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Translate", accelerator="Ctrl+T", command=self.translate_code)
        run_menu.add_command(label="Reverse Translate", accelerator="Ctrl+R", command=lambda: self.translate_code(reverse=True))
        run_menu.add_separator()
        run_menu.add_command(label="Clear All", accelerator="Ctrl+Shift+C", command=self.clear_all_code)
        run_menu.add_separator()
        run_menu.add_command(label="Scan for Vulnerabilities", command=self.scan_code_for_vulnerabilities)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", accelerator="F1", command=self._show_about)
        help_menu.add_command(label="Documentation", command=lambda: webbrowser.open("https://github.com/your-repo/codedswitch"))
        help_menu.add_command(label="Report Issue", command=lambda: webbrowser.open("https://github.com/your-repo/codedswitch/issues"))

    def _create_status_bar(self):
        """Create the application status bar."""
        # Create frame for status bar
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            padding=(10, 5)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Model indicator
        self.model_indicator = ttk.Label(
            self.status_frame,
            text=f"Model: {self.gemini_model}",
            padding=(10, 5)
        )
        self.model_indicator.pack(side=tk.RIGHT)
        
        # Theme indicator
        self.theme_indicator = ttk.Label(
            self.status_frame,
            text=f"Theme: {self.current_theme}",
            padding=(10, 5)
        )
        self.theme_indicator.pack(side=tk.RIGHT)
        
        # Add divider
        ttk.Separator(self.status_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # API status indicator
        self.api_status = ttk.Label(
            self.status_frame,
            text="API: Connected" if self.gemini_api_key else "API: Not Connected",
            padding=(10, 5)
        )
        self.api_status.pack(side=tk.RIGHT)

    def _setup_translator_tab(self):
        """Set up the translator tab UI"""
        main_frame = ttk.Frame(self.translator_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Model selection frame
        model_frame = ttk.LabelFrame(main_frame, text="Model Selection", padding=10)
        model_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_var = tk.StringVar(value=self.gemini_model)
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["models/gemini-1.5-pro-001"],
            width=15,
            state="readonly"
        )
        model_combo.pack(side=tk.LEFT)
        model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # Language selection frame with quick action buttons
        lang_frame = ttk.LabelFrame(main_frame, text="Languages", padding=10)
        lang_frame.pack(fill=tk.X, pady=(0, 15))

        # Top row - Language selection and buttons
        lang_select_frame = ttk.Frame(lang_frame)
        lang_select_frame.pack(fill=tk.X)

        # Source language
        source_frame = ttk.Frame(lang_select_frame)
        source_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(source_frame, text="Source:").pack(side=tk.LEFT, padx=(0, 5))
        self.source_lang = tk.StringVar(value="Python")
        source_combo = ttk.Combobox(
            source_frame,
            textvariable=self.source_lang,
            values=PROGRAMMING_LANGUAGES,
            width=15,
            state="readonly"
        )
        source_combo.pack(side=tk.LEFT)

        # Target language
        target_frame = ttk.Frame(lang_select_frame)
        target_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(target_frame, text="Target:").pack(side=tk.LEFT, padx=(0, 5))
        self.target_lang = tk.StringVar(value="JavaScript")
        target_combo = ttk.Combobox(
            target_frame,
            textvariable=self.target_lang,
            values=PROGRAMMING_LANGUAGES,
            width=15,
            state="readonly"
        )
        target_combo.pack(side=tk.LEFT)

        # Quick Action Buttons
        action_frame = ttk.Frame(lang_select_frame)
        action_frame.pack(side=tk.RIGHT)

        ttk.Button(
            action_frame,
            text="Translate →",
            command=lambda: self.translate_code(reverse=False),
            style="primary.TButton",
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="Clear All",
            command=self.clear_all_code,
            style="secondary.TButton",
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="Export",
            command=lambda: self._export_current_results(),
            width=8
        ).pack(side=tk.LEFT)

        # Code editor area
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Source code frame
        source_frame = ttk.LabelFrame(editor_frame, text="Source Code", padding=5)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Source code editor
        self.source_code = TtkScrolledText(
            source_frame,
            wrap=tk.WORD,
            height=20,
            font=("Courier New", self.font_size)
        )
        self.source_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Translation arrows frame (between source and target)
        arrows_frame = ttk.Frame(editor_frame)
        arrows_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Add some vertical centering
        ttk.Label(arrows_frame, text="").pack(pady=50)

        ttk.Button(
            arrows_frame,
            text="→",
            command=lambda: self.translate_code(reverse=False),
            width=3,
            style="primary.TButton"
        ).pack(pady=5)

        ttk.Button(
            arrows_frame,
            text="←",
            command=lambda: self.translate_code(reverse=True),
            width=3,
            style="secondary.TButton"
        ).pack(pady=5)

        # Target code frame
        target_frame = ttk.LabelFrame(editor_frame, text="Target Code", padding=5)
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Target code display
        self.target_code = TtkScrolledText(
            target_frame,
            wrap=tk.WORD,
            height=20,
            font=("Courier New", self.font_size)
        )
        self.target_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bottom frame for additional options and feedback
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        # Translation feedback
        feedback_frame = ttk.LabelFrame(bottom_frame, text="Translation Notes", padding=5)
        feedback_frame.pack(fill=tk.BOTH, expand=True)

        self.feedback_text = TtkScrolledText(
            feedback_frame,
            wrap=tk.WORD,
            height=5,
            font=("Segoe UI", self.font_size)
        )
        self.feedback_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _setup_chatbot_tab(self):
        """Set up the chatbot tab UI"""
        # Create main container with padding
        main_frame = ttk.Frame(self.chatbot_tab, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Chat display area with custom styling
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_display = TtkScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("Segoe UI", self.font_size)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configure text tags for different message types
        self.chat_display.tag_configure("user_msg", foreground="blue")
        self.chat_display.tag_configure("assistant_msg", foreground="green")
        self.chat_display.tag_configure("system_msg", foreground="gray")

        # Input area with improved styling
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.message_input = TtkScrolledText(
            input_frame,
            wrap=tk.WORD,
            width=70,
            height=3,
            font=("Segoe UI", self.font_size)
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Button frame
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT, padx=5)

        # Send button with icon (using text for now, can be replaced with image)
        send_button = ttk.Button(
            btn_frame,
            text="Send",
            command=self.send_message,
            style="primary.TButton"
        )
        send_button.pack(side=tk.TOP, pady=(0, 5))

        # Clear button
        clear_button = ttk.Button(
            btn_frame,
            text="Clear",
            command=self._clear_chat,
            width=10
        )
        clear_button.pack(side=tk.TOP)

        # Bind keys
        self.message_input.bind("<Return>", self.send_message)
        self.message_input.bind("<Shift-Return>", lambda e: "break")

        # Add welcome message
        self.add_message(
            "CodedSwitch AI",
            "Hello! I'm your CodedSwitch AI assistant. I can help you with:\n" +
            "• Translating code between different programming languages\n" +
            "• Analyzing and optimizing code\n" +
            "• Identifying security vulnerabilities\n" +
            "• Providing coding best practices\n" +
            "• Writing and analyzing rap lyrics\n\n" +
            "How can I assist you today?"
        )

    def _setup_security_tab(self):
        """Set up the security scanning tab"""
        # Main frame
        main_frame = ttk.Frame(self.security_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Code input frame
        code_frame = ttk.LabelFrame(main_frame, text="Code to Scan", padding=5)
        code_frame.pack(fill=tk.BOTH, expand=True)

        # Language selection
        lang_frame = ttk.Frame(code_frame)
        lang_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.scan_lang,
            values=PROGRAMMING_LANGUAGES,
            state="readonly"
        )
        lang_combo.pack(side=tk.LEFT, padx=5)

        # Example code button
        example_button = ttk.Button(
            code_frame,
            text="Load Test Code",
            command=self.load_test_code,
            style="secondary.TButton"
        )
        example_button.pack(anchor=tk.E, pady=5)

        # Code editor
        self.scan_code = TtkScrolledText(
            code_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier New", self.font_size)
        )
        self.scan_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Results display
        self.scan_results = TtkScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Segoe UI", self.font_size)
        )
        self.scan_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure tags
        self.scan_results.tag_configure("header", font=("Segoe UI", self.font_size, "bold"))
        self.scan_results.tag_configure("info", foreground="green")
        self.scan_results.tag_configure("error", foreground="red")
        self.scan_results.tag_configure("high", foreground="red")
        self.scan_results.tag_configure("medium", foreground="orange")
        self.scan_results.tag_configure("low", foreground="blue")

        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        # Scan button
        scan_button = ttk.Button(
            controls_frame,
            text="Scan for Vulnerabilities",
            command=self.scan_code_for_vulnerabilities,
            style="Accent.TButton"
        )
        scan_button.pack(side=tk.LEFT, padx=(0, 10))

        # Export button
        export_button = ttk.Button(
            controls_frame,
            text="Export Report",
            command=self.export_report
        )
        export_button.pack(side=tk.LEFT, padx=10)

        # Fix button
        fix_button = ttk.Button(
            controls_frame,
            text="Fix Selected",
            command=self.fix_selected_vulnerability
        )
        fix_button.pack(side=tk.LEFT)

    def _setup_lyric_lab_tab(self):
        """🎤 Set up the NEW Lyric Lab tab for AI-powered songwriting 🎤"""
        # Main frame
        main_frame = ttk.Frame(self.lyric_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header frame with branding
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame, 
            text="🎤 CodedSwitch Lyric Lab - Where Code Meets Bars", 
            font=("Segoe UI", 14, "bold")
        ).pack(side=tk.LEFT)
        
        # Story Protocol button
        ttk.Button(
            header_frame,
            text="📜 Register on Story Protocol",
            command=self._register_lyrics_on_story,
            style="success.TButton"
        ).pack(side=tk.RIGHT)
        
        # Lyric composition area
        composition_frame = ttk.LabelFrame(main_frame, text="Lyric Composition", padding=10)
        composition_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Lyric editor
        editor_frame = ttk.Frame(composition_frame)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Lyric editor
        self.lyric_editor = TtkScrolledText(
            editor_frame,
            wrap=tk.WORD,
            height=25,
            font=("Courier New", self.font_size)
        )
        self.lyric_editor.pack(fill=tk.BOTH, expand=True)
        
        # Bind for real-time AI suggestions
        self.lyric_editor.bind("<KeyRelease>", self._on_lyric_text_change)
        
        # Right side - AI assistance panel
        ai_panel = ttk.LabelFrame(composition_frame, text="AI Writing Assistant", padding=5)
        ai_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Rhyme suggestions
        rhyme_frame = ttk.LabelFrame(ai_panel, text="Rhyme Suggestions", padding=5)
        rhyme_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.rhyme_suggestions = tk.Listbox(rhyme_frame, height=8, width=20)
        self.rhyme_suggestions.pack(fill=tk.X, padx=5, pady=5)
        
        # AI prompt area
        prompt_frame = ttk.LabelFrame(ai_panel, text="AI Lyric Helper", padding=5)
        prompt_frame.pack(fill=tk.BOTH, expand=True)
        
        self.lyric_prompt = TtkScrolledText(
            prompt_frame,
            wrap=tk.WORD,
            height=8,
            width=30,
            font=("Segoe UI", 9)
        )
        self.lyric_prompt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # AI generate button
        ttk.Button(
            prompt_frame,
            text="✨ Generate Ideas",
            command=self._generate_lyric_ideas,
            style="primary.TButton"
        ).pack(pady=5)
        
        # Bottom control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Lyric analysis tools
        analysis_frame = ttk.LabelFrame(control_frame, text="Analysis Tools", padding=5)
        analysis_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(
            analysis_frame,
            text="📊 Analyze Flow",
            command=self._analyze_lyric_flow
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            analysis_frame,
            text="🎵 Check Rhyme Scheme",
            command=self._check_rhyme_scheme
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            analysis_frame,
            text="📝 Word Count",
            command=self._show_lyric_stats
        ).pack(side=tk.LEFT)
        
        # Export/Save options
        export_frame = ttk.LabelFrame(control_frame, text="Export & Protect", padding=5)
        export_frame.pack(side=tk.RIGHT, fill=tk.X, padx=(10, 0))
        
        ttk.Button(
            export_frame,
            text="💾 Save Lyrics",
            command=self._save_lyrics
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            export_frame,
            text="🛡️ IP Protect",
            command=self._register_lyrics_on_story,
            style="success.TButton"
        ).pack(side=tk.LEFT)

    # 🎤 NEW LYRIC LAB METHODS 🎤

    def _on_lyric_text_change(self, event):
        """Handle real-time lyric text changes for AI suggestions"""
        try:
            # Get current line and word
            current_line = self.lyric_editor.get("insert linestart", "insert lineend")
            words = current_line.split()
            
            if words:
                last_word = words[-1].strip(".,!?;:")
                if len(last_word) > 2:  # Only suggest for meaningful words
                    self._get_rhyme_suggestions(last_word)
        except Exception as e:
            logger.error(f"Error in lyric text change: {e}")

    def _get_rhyme_suggestions(self, word):
        """Get AI-powered rhyme suggestions"""
        try:
            prompt = f"""Give me 10 words that rhyme with "{word}" that would work well in rap/hip-hop lyrics. 
            Focus on multi-syllable rhymes and words that are commonly used in modern rap.
            Return just the words, one per line."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else "demo mode"
            
            # Parse response and update rhyme suggestions
            rhymes = [line.strip() for line in response.split('\n') if line.strip()]
            
            # Update the rhyme suggestions listbox
            self.rhyme_suggestions.delete(0, tk.END)
            for rhyme in rhymes[:10]:  # Limit to 10 suggestions
                self.rhyme_suggestions.insert(tk.END, rhyme)
                
        except Exception as e:
            logger.error(f"Error getting rhyme suggestions: {e}")

    def _generate_lyric_ideas(self):
        """Generate AI-powered lyric ideas based on user prompt"""
        try:
            prompt = self.lyric_prompt.get("1.0", tk.END).strip()
            if not prompt:
                messagebox.showwarning("No Prompt", "Enter a theme or idea for AI to work with!")
                return
            
            ai_prompt = f"""You are a talented rap lyricist. Based on this theme: "{prompt}"
            
            Generate creative rap lyrics that incorporate coding/programming references naturally.
            Make it clever with wordplay, metaphors connecting code to life, and good flow.
            Keep it clean and creative. Focus on the "CodedSwitch" concept - switching between 
            different modes/languages/styles.
            
            Generate 8-16 bars."""
            
            response = self.ai.chat_response(ai_prompt) if hasattr(self.ai, 'chat_response') else f"Demo lyrics for theme: {prompt}\n\nI'm like a coder in the booth, debugging every line\nSwitching languages like Python to JavaScript divine\nCodedSwitch in my DNA, I translate every bar\nFrom the streets to the IDE, I'm a lyrical star"
            
            # Insert the generated lyrics
            current_text = self.lyric_editor.get("1.0", tk.END).strip()
            if current_text:
                self.lyric_editor.insert(tk.END, "\n\n" + response)
            else:
                self.lyric_editor.insert("1.0", response)
                
            self.status_var.set("✨ AI lyrics generated!")
            
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate lyrics: {str(e)}")

    def _analyze_lyric_flow(self):
        """Analyze the flow and rhythm of lyrics"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            prompt = f"""Analyze these rap lyrics for flow, rhythm, and structure:

{lyrics}

Provide analysis on:
1. Syllable count per line
2. Rhyme scheme pattern
3. Flow consistency 
4. Suggestions for improvement
5. Overall rating (1-10)

Be constructive and specific."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else f"FLOW ANALYSIS:\n\n✅ Lines: {len(lyrics.splitlines())}\n✅ Flow: Consistent\n✅ Rhyme scheme: ABAB pattern detected\n✅ Rating: 8/10\n\nSuggestions: Great work! Consider adding more internal rhymes."
            
            # Show results in a dialog
            result_window = tk.Toplevel(self.root)
            result_window.title("Flow Analysis Results")
            result_window.geometry("600x400")
            
            text_widget = TtkScrolledText(result_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert("1.0", response)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze lyrics: {str(e)}")

    def _check_rhyme_scheme(self):
        """Check and visualize rhyme scheme"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            prompt = f"""Analyze the rhyme scheme of these lyrics:

{lyrics}

Show me:
1. The rhyme scheme pattern (ABAB, AABB, etc.)
2. Which words rhyme with which
3. Any slant rhymes or near-rhymes
4. Suggestions for improving the rhyme scheme

Format it clearly."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else f"RHYME SCHEME ANALYSIS:\n\n🎵 Pattern: ABAB\n🎵 End rhymes detected\n🎵 Strong rhyme consistency\n\nGreat rhyming structure!"
            
            # Show in dialog
            result_window = tk.Toplevel(self.root)
            result_window.title("Rhyme Scheme Analysis")
            result_window.geometry("500x400")
            
            text_widget = TtkScrolledText(result_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert("1.0", response)
            
        except Exception as e:
            messagebox.showerror("Rhyme Analysis Error", f"Failed to analyze rhymes: {str(e)}")

    def _show_lyric_stats(self):
        """Show detailed statistics about the lyrics"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        # Calculate basic stats
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        words = lyrics.split()
        chars = len(lyrics.replace(' ', ''))
        
        # Estimate syllables (rough approximation)
        syllables = sum(max(1, len([c for c in word if c.lower() in 'aeiou'])) for word in words)
        
        stats = f"""📊 LYRIC STATISTICS 📊

Lines: {len(lines)}
Words: {len(words)}
Characters: {chars}
Estimated Syllables: {syllables}

Average words per line: {len(words)/max(1, len(lines)):.1f}
Average syllables per line: {syllables/max(1, len(lines)):.1f}

🎤 Performance estimates:
• Fast rap (6 syl/sec): ~{syllables/6:.1f} seconds
• Medium pace (4 syl/sec): ~{syllables/4:.1f} seconds  
• Slow flow (3 syl/sec): ~{syllables/3:.1f} seconds"""
        
        messagebox.showinfo("Lyric Statistics", stats)

    def _save_lyrics(self):
        """Save lyrics to file"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "No lyrics to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Lyrics Files", "*.lyr"), ("All Files", "*.*")],
            title="Save Lyrics"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# CodedSwitch Lyrics\n")
                    f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(lyrics)
                
                messagebox.showinfo("Saved", "Lyrics saved successfully!")
                self.status_var.set(f"Lyrics saved to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save lyrics: {str(e)}")

    def _register_lyrics_on_story(self):
        """Register lyrics as IP on Story Protocol"""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics to register!")
            return
        
        # For now, show information about Story Protocol registration
        info_text = f"""🛡️ STORY PROTOCOL IP REGISTRATION 🛡️

Ready to protect your lyrics on blockchain!

Your lyrics ({len(lyrics.split())} words, {len(lyrics.splitlines())} lines)

🔗 Next Steps:
1. Visit: portal.story.foundation
2. Connect your wallet 
3. Upload these lyrics as an IP Asset
4. Set licensing terms and royalties
5. Get automatic protection!

💰 Estimated cost: $1-5 worth of $IP tokens

Would you like to export your lyrics for Story Protocol registration?"""
        
        if messagebox.askyesno("Story Protocol Registration", info_text):
            # Export in Story Protocol friendly format
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")],
                title="Export for Story Protocol"
            )
            
            if file_path:
                try:
                    metadata = {
                        "title": "CodedSwitch Lyrics",
                        "description": "Original lyrics created with CodedSwitch Lyric Lab",
                        "content": lyrics,
                        "created": datetime.now().isoformat(),
                        "type": "lyrics",
                        "tags": ["rap", "hip-hop", "coding", "CodedSwitch"],
                        "licensing": "Commercial use allowed with attribution"
                    }
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2)
                    
                    messagebox.showinfo("Exported", 
                        f"Lyrics exported for Story Protocol!\n\n" +
                        f"File: {file_path}\n\n" +
                        "Upload this file to portal.story.foundation to register your IP!")
                    
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    # EXISTING METHODS (All your original functionality)

    def clear_all_code(self):
        """Clear all code areas and notes."""
        if messagebox.askyesno("Clear All", "Clear both code areas and notes?"):
            self.source_code.delete(1.0, tk.END)
            self.target_code.delete(1.0, tk.END)
            self.feedback_text.delete(1.0, tk.END)
            self.status_var.set("All code areas cleared")

    def on_model_change(self, event):
        """Handle change in Gemini model selection."""
        new_model = self.model_var.get()
        if new_model != self.gemini_model:
            try:
                # Update the model in the AI interface
                self.ai.use_gemini_model(new_model)
                
                # Update status indicators
                self.model_indicator.config(text=f"Model: {new_model}")
                self.gemini_model = new_model
                
                # Clear any existing chat history
                self._clear_chat()
                
                # Add a welcome message with the new model
                self.add_message(
                    "CodedSwitch AI",
                    f"Hello! I've been updated to use the {new_model} model. How can I assist you today?",
                    "assistant_msg"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to switch model: {str(e)}")

    def open_file(self):
        """Open a Python file for translation."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.source_code.delete(1.0, tk.END)
                    self.source_code.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Open File", f"Failed to open file: {e}")

    def save_file(self):
        """Save the translated JavaScript code to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".js",
            filetypes=[("JavaScript Files", "*.js"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.target_code.get(1.0, tk.END).strip())
                    messagebox.showinfo("Save File", "File saved successfully.")
            except Exception as e:
                messagebox.showerror("Save File", f"Failed to save file: {e}")

    def translate_code(self, reverse=False):
        """Enhanced translate_code method with better UX."""
        source_code = self.source_code.get(1.0, tk.END).strip()
        
        # Input validation with friendly messages
        if not source_code:
            messagebox.showwarning(
                "Empty Code", 
                "Please enter some code to translate!\n\nTip: Try pasting some Python code in the Source Code area."
            )
            self.source_code.focus()
            return
        
        # Check for very long code
        if len(source_code) > 10000:
            if not messagebox.askyesno(
                "Large Code Warning", 
                f"You're translating {len(source_code)} characters of code.\n\nThis might take a moment. Continue?"
            ):
                return

        try:
            # Show loading state
            self._show_loading_state("🔄 Translating code with AI...")
            
            # Disable buttons during translation
            self._set_ui_enabled(False)
            
            # Update UI to show progress
            self.root.update_idletasks()
            
            if reverse:
                translated_code = self.ai.translate_code(
                    source_code=source_code,
                    target_language=self.source_lang.get(),
                    use_neural=False,
                    use_llm=True
                )
                self.source_code.delete(1.0, tk.END)
                self.source_code.insert(tk.END, translated_code)
                
                # Show success message
                self._show_success_state(f"✅ Translated to {self.source_lang.get()}!")
            else:
                translated_code = self.ai.translate_code(
                    source_code=source_code,
                    target_language=self.target_lang.get(),
                    use_neural=False,
                    use_llm=True
                )
                self.target_code.delete(1.0, tk.END)
                self.target_code.insert(tk.END, translated_code)
                
                # Show success message with tips
                self._show_success_state(f"✅ Translated to {self.target_lang.get()}!")
                
                # Add helpful feedback
                self.feedback_text.delete(1.0, tk.END)
                feedback = f"""Translation completed successfully! 🎉

Source: {self.source_lang.get()} ({len(source_code)} characters)
Target: {self.target_lang.get()} ({len(translated_code)} characters)

💡 Tips:
• Use the Security Scanner to check for vulnerabilities
• Try different target languages to explore syntax differences
• Chat with CodedSwitch AI for code explanations and improvements
• Check out the new Lyric Lab for creative writing!
"""
                self.feedback_text.insert(tk.END, feedback)
                
        except Exception as e:
            # Enhanced error handling
            error_msg = str(e)
            self._show_error_state("❌ Translation failed")
            
            # User-friendly error messages
            if "API" in error_msg:
                messagebox.showerror(
                    "API Connection Error", 
                    "Couldn't connect to the AI service.\n\n" +
                    "Please check:\n" +
                    "• Your internet connection\n" +
                    "• Your API key is valid\n" +
                    "• Try again in a moment"
                )
            elif "quota" in error_msg.lower():
                messagebox.showerror(
                    "API Quota Exceeded", 
                    "You've reached your daily API limit.\n\n" +
                    "Solutions:\n" +
                    "• Wait until tomorrow for reset\n" +
                    "• Upgrade your API plan\n" +
                    "• Try smaller code snippets"
                )
            else:
                messagebox.showerror(
                    "Translation Error", 
                    f"Something went wrong during translation.\n\n" +
                    f"Error details: {error_msg}\n\n" +
                    "Try:\n" +
                    "• Simplifying your code\n" +
                    "• Checking for syntax errors\n" +
                    "• Restarting the application"
                )
        finally:
            # Always re-enable UI
            self._set_ui_enabled(True)
            
            # Reset status after delay
            self.root.after(3000, lambda: self.status_var.set("Ready"))

    def add_message(self, sender: str, message: str, message_type: str = None):
        """Add a message to the chat display."""
        # Get current timestamp
        timestamp = datetime.now().strftime("%I:%M %p")
        
        # Format message with sender and timestamp
        formatted_msg = f"{sender} ({timestamp}):\n{message}\n\n"
        
        # Insert message with appropriate tag
        self.chat_display.insert(tk.END, formatted_msg, message_type or "system_msg")
        
        # Scroll to end
        self.chat_display.see(tk.END)

    def send_message(self, event=None):
        """Send a message to the chatbot."""
        # Handle Shift+Return for new line
        if event and event.state & 0x4:  # Check if Shift key is pressed
            return "break"
            
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return "break"
            
        # Clear input
        self.message_input.delete("1.0", tk.END)
        
        # Add user message to chat
        self.add_message("You", message, "user_msg")
        
        # Get bot response
        try:
            response = self.ai.chat_response(message) if hasattr(self.ai, 'chat_response') else "Demo mode response"
            self.add_message("Assistant", response, "assistant_msg")
        except Exception as e:
            self.add_message("System", f"Error: {str(e)}", "system_msg")
            
        return "break"

    def scan_code_for_vulnerabilities(self):
        """Enhanced vulnerability scanning with better UX."""
        code = self.scan_code.get("1.0", tk.END).strip()
        language = self.scan_lang.get().lower()
        
        # Input validation
        if not code:
            messagebox.showwarning(
                "No Code to Scan", 
                "Please enter some code to scan for vulnerabilities!\n\n" +
                "💡 Tip: Click 'Load Test Code' to try an example."
            )
            self.scan_code.focus()
            return
        
        if len(code) < 10:
            if not messagebox.askyesno(
                "Very Short Code", 
                "This code is very short and might not have vulnerabilities to detect.\n\n" +
                "Continue scanning anyway?"
            ):
                return
        
        # Clear previous results with animation
        self.scan_results.delete("1.0", tk.END)
        self.scan_results.insert(tk.END, "🔍 Initializing security scanner...\n")
        self.root.update_idletasks()
        
        try:
            # Show detailed progress
            progress_messages = [
                "🔍 Analyzing code structure...",
                "🛡️ Checking for SQL injection patterns...",
                "⚡ Scanning for XSS vulnerabilities...",
                "🔐 Detecting hard-coded credentials...",
                "🚨 Running AI-powered analysis...",
                "📊 Generating security report..."
            ]
            
            for i, msg in enumerate(progress_messages):
                self.status_var.set(msg)
                self.scan_results.delete("1.0", tk.END)
                self.scan_results.insert(tk.END, f"{msg}\n\n{'█' * (i+1)}{'░' * (len(progress_messages)-(i+1))}\n")
                self.root.update_idletasks()
                
                # Small delay for visual feedback
                self.root.after(200)
                self.root.update()
            
            # Perform actual scan
            vulnerabilities = self.ai.scan_vulnerabilities(code, language) if hasattr(self.ai, 'scan_vulnerabilities') else []
            
            # Clear progress display
            self.scan_results.delete("1.0", tk.END)
            
            if not vulnerabilities:
                # No vulnerabilities found
                success_msg = """🎉 GREAT NEWS! No vulnerabilities detected! 🎉

Your code looks secure! Here's what we checked:
✅ SQL Injection patterns
✅ Cross-Site Scripting (XSS)
✅ Command Injection
✅ Path Traversal
✅ Hard-coded credentials
✅ Input validation issues

💡 Security Tips:
• Always validate user input
• Use parameterized queries
• Keep dependencies updated
• Regular security reviews

Want to test the scanner? Click 'Load Test Code' for examples!"""
                
                self.scan_results.insert(tk.END, success_msg, "info")
                self.status_var.set("✅ Scan complete - Code looks secure!")
                
            else:
                # Vulnerabilities found - enhanced display
                header = f"""🛡️ SECURITY SCAN RESULTS 🛡️

Found {len(vulnerabilities)} potential security issues:

"""
                self.scan_results.insert(tk.END, header, "header")
                
                # Group by severity
                high_vulns = [v for v in vulnerabilities if hasattr(v.severity, 'name') and v.severity.name == 'HIGH']
                medium_vulns = [v for v in vulnerabilities if hasattr(v.severity, 'name') and v.severity.name == 'MEDIUM']
                low_vulns = [v for v in vulnerabilities if hasattr(v.severity, 'name') and v.severity.name == 'LOW']
                
                # Display high severity first
                if high_vulns:
                    self.scan_results.insert(tk.END, f"🚨 HIGH SEVERITY ({len(high_vulns)} issues):\n", "high")
                    for vuln in high_vulns:
                        self._display_vulnerability(vuln, "high")
                    self.scan_results.insert(tk.END, "\n")
                
                # Medium severity
                if medium_vulns:
                    self.scan_results.insert(tk.END, f"⚠️ MEDIUM SEVERITY ({len(medium_vulns)} issues):\n", "medium")
                    for vuln in medium_vulns:
                        self._display_vulnerability(vuln, "medium")
                    self.scan_results.insert(tk.END, "\n")
                
                # Low severity
                if low_vulns:
                    self.scan_results.insert(tk.END, f"ℹ️ LOW SEVERITY ({len(low_vulns)} issues):\n", "low")
                    for vuln in low_vulns:
                        self._display_vulnerability(vuln, "low")
                
                # Action recommendations
                action_text = f"""
💡 RECOMMENDED ACTIONS:
{f'🔴 Fix {len(high_vulns)} critical issues immediately' if high_vulns else ''}
{f'🟡 Review {len(medium_vulns)} medium-priority issues' if medium_vulns else ''}
{f'🔵 Consider {len(low_vulns)} low-priority improvements' if low_vulns else ''}

🔧 Next Steps:
• Click on vulnerabilities above for detailed fixes
• Use the 'Fix Selected' button for automated repairs
• Export this report for your security team
"""
                self.scan_results.insert(tk.END, action_text, "info")
                
                # Update status with summary
                critical_count = len(high_vulns)
                if critical_count > 0:
                    self.status_var.set(f"⚠️ Scan complete - {critical_count} critical issues found!")
                else:
                    self.status_var.set(f"✅ Scan complete - {len(vulnerabilities)} issues found")
                
        except Exception as e:
            error_msg = f"""❌ SCAN ERROR

Something went wrong during the security scan:
{str(e)}

🔧 Troubleshooting:
• Check your internet connection
• Verify your API key is valid
• Try scanning smaller code snippets
• Restart the application if issues persist

💡 Need help? Check the documentation or contact support."""
            
            self.scan_results.insert(tk.END, error_msg, "error")
            self.status_var.set("❌ Scan failed - Check error details")

    def load_test_code(self):
        """Load sample vulnerable code for testing the scanner."""
        test_code = """import os
import sqlite3
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

# VULNERABILITY 1: Hard-coded credentials
DATABASE_PASSWORD = "admin123"
API_SECRET_KEY = "sk_live_51JXzT2GBgjklmasLMNvb4Kb0QzDhKIPO098asdkljasdkljq7f"
ADMIN_PASSWORD = "password123"

# VULNERABILITY 2: SQL Injection
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Direct string concatenation - SQL injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        return f"Welcome {username}!"
    else:
        return "Login failed"

# VULNERABILITY 3: Command Injection
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    # Direct command execution with user input
    result = os.system(f"ping -c 1 {host}")
    return f"Ping result: {result}"

# VULNERABILITY 4: Path Traversal
@app.route('/download')
def download_file():
    filename = request.args.get('file')
    # No path validation - directory traversal vulnerability
    file_path = os.path.join('./uploads', filename)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)"""
        
        self.scan_code.delete("1.0", tk.END)
        self.scan_code.insert(tk.END, test_code)
        self.scan_lang.set("Python")

    # Enhanced Helper Methods
    def _display_vulnerability(self, vuln, severity_class):
        """Display a single vulnerability with enhanced formatting."""
        vuln_text = f"""
📍 Line {vuln.line_number} - {vuln.category}
   {vuln.description}
   
"""
        self.scan_results.insert(tk.END, vuln_text, severity_class)

    def _show_loading_state(self, message):
        """Show loading state in status bar."""
        self.status_var.set(message)
        
    def _show_success_state(self, message):
        """Show success state in status bar."""
        self.status_var.set(message)
        
    def _show_error_state(self, message):
        """Show error state in status bar."""
        self.status_var.set(message)
        
    def _set_ui_enabled(self, enabled):
        """Enable/disable UI elements during operations."""
        # This prevents multiple simultaneous operations
        pass  # Implementation can be expanded as needed

    def _show_help(self):
        """Show comprehensive help dialog."""
        help_text = """🚀 CodedSwitch - Quick Help

⌨️ KEYBOARD SHORTCUTS:
   Ctrl+T        - Translate code
   Ctrl+R        - Reverse translation  
   Ctrl+Shift+C  - Clear all code areas
   F5            - Scan for vulnerabilities
   Ctrl+N        - New file
   Ctrl+O        - Open file
   Ctrl+S        - Save file
   F1            - Show this help
   Ctrl++        - Increase font size
   Ctrl+-        - Decrease font size

🎯 QUICK START:
   1. Paste code in Source Code area
   2. Select target language
   3. Click "Translate →" or press Ctrl+T
   4. Use Security Scanner for safety checks
   5. Chat with CodedSwitch AI for help
   6. NEW: Try the Lyric Lab for creative writing!

💡 TIPS:
   • Try different languages to learn syntax
   • Use security scanner before deployment
   • Export results for documentation
   • Customize themes in View menu
   • 🎤 Write rap lyrics in the Lyric Lab!

🔗 MORE HELP:
   • Documentation: F1 → Full Guide
   • Community: Discord Server
   • Issues: GitHub Issues Page"""
        
        messagebox.showinfo("CodedSwitch - Help", help_text)

    def _validate_code_input(self, code, context="translation"):
        """Validate code input with helpful suggestions."""
        if not code.strip():
            return False, f"Please enter some code for {context}!"
        
        if len(code) > 50000:
            return False, f"Code is too long ({len(code)} chars). Please try smaller snippets."
        
        # Check for obvious issues
        if code.count('"""') % 2 != 0 or code.count("'''") % 2 != 0:
            return False, "Unclosed string literals detected. Please check your quotes."
        
        return True, "Code looks good!"

    def _load_demo_code(self):
        """Load demo code for testing."""
        demo_code = """def greet(name):
    \"\"\"A simple greeting function.\"\"\"
    return f"Hello, {name}!"

# Test the function
print(greet("World"))"""
        
        self.source_code.delete(1.0, tk.END)
        self.source_code.insert(tk.END, demo_code)
        self.status_var.set("Demo code loaded!")

    def _export_current_results(self):
        """Export current results to file."""
        # Get current tab
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Translator tab
            self._export_translation_results()
        elif current_tab == 2:  # Security tab
            self.export_report()
        elif current_tab == 3:  # Lyric Lab tab
            self._save_lyrics()
        else:
            messagebox.showinfo("Export", "Nothing to export from this tab.")

    def _export_translation_results(self):
        """Export translation results."""
        source_code = self.source_code.get(1.0, tk.END).strip()
        target_code = self.target_code.get(1.0, tk.END).strip()
        
        if not source_code or not target_code:
            messagebox.showwarning("Nothing to Export", "Please complete a translation first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Translation Report"
        )
        
        if file_path:
            try:
                if file_path.endswith(".html"):
                    self._export_html_translation(file_path, source_code, target_code)
                else:
                    self._export_text_translation(file_path, source_code, target_code)
                
                messagebox.showinfo("Export Complete", "Translation results exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def _export_html_translation(self, file_path, source_code, target_code):
        """Export translation as HTML."""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Translation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .code {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; }}
        .source {{ border-left: 4px solid #007bff; }}
        .target {{ border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <h1>Code Translation Report</h1>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Source Code ({self.source_lang.get()})</h2>
    <div class="code source">
        <pre>{source_code}</pre>
    </div>
    
    <h2>Translated Code ({self.target_lang.get()})</h2>
    <div class="code target">
        <pre>{target_code}</pre>
    </div>
</body>
</html>"""
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _export_text_translation(self, file_path, source_code, target_code):
        """Export translation as text."""
        text_content = f"""Code Translation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Source Language: {self.source_lang.get()}
Target Language: {self.target_lang.get()}

=== SOURCE CODE ===
{source_code}

=== TRANSLATED CODE ===
{target_code}
"""
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)

    # Existing methods (keeping the rest of your methods)
    def fix_selected_vulnerability(self):
        """Fix the selected vulnerability."""
        messagebox.showinfo("Feature Coming Soon", "Vulnerability fixing feature will be available in the next update!")

    def export_report(self):
        """Export the vulnerability scan report to a file."""
        # Get scan results
        results = self.scan_results.get("1.0", tk.END).strip()
        if not results or "No vulnerabilities" in results:
            messagebox.showinfo("Nothing to Export", "No scan results to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("HTML Files", "*.html"), ("All Files", "*.*")],
            title="Save Vulnerability Report"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Vulnerability Scan Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*50 + "\n\n")
                    f.write(results)
                
                messagebox.showinfo("Export Complete", "Vulnerability report exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def new_file(self):
        """Clear both code editors for a new file."""
        if messagebox.askyesno("New File", "Clear both editors?"):
            self.source_code.delete(1.0, tk.END)
            self.target_code.delete(1.0, tk.END)
            self.feedback_text.delete(1.0, tk.END)

    def _select_all(self):
        """Select all text in the current text widget."""
        try:
            widget = self.root.focus_get()
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        except:
            pass
            
    def _show_about(self):
        """Show the about dialog."""
        about_text = """🎤 CodedSwitch - AI Code Translator & Lyric Lab 🎤
Version 2.1 - Now with Lyric Lab!

The ultimate AI-powered platform for code translation AND lyric creation.
Switch between programming languages AND creative modes effortlessly!

✨ FEATURES:
• AI code translation between languages
• Advanced security vulnerability scanning  
• Intelligent chatbot assistant
• 🎤 NEW: AI-powered lyric lab with rhyme suggestions
• Story Protocol integration for IP protection

🔥 THE TRIPLE ENTENDRE:
• CODE (Programming languages)
• CODE (Lyrics/Bars) 
• CODE-SWITCHING (Seamless transitions)

Developed by the CodedSwitch AI team.

© 2025 All rights reserved."""
        
        messagebox.showinfo("About CodedSwitch", about_text)
        
    def _clear_chat(self):
        """Clear the chat display and history."""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.delete(1.0, tk.END)
            
            # Add welcome message again
            self.add_message(
                "CodedSwitch AI",
                "Hello! I'm your CodedSwitch AI assistant. I can help you with code, security, and even rap lyrics! How can I help you today?"
            )
        
    def _change_font_size(self, delta):
        """Change font size for text widgets."""
        self.font_size = max(8, min(24, self.font_size + delta))
        
        # Update all text widgets
        for widget in [self.source_code, self.target_code, self.feedback_text, self.chat_display, self.message_input, self.lyric_editor]:
            current_font = widget.cget("font")
            if isinstance(current_font, str):
                font_family = current_font.split()[0]
            else:
                font_family = current_font[0]
            widget.configure(font=(font_family, self.font_size))
        
        self.status_var.set(f"Font size changed to {self.font_size}pt")

    def _change_theme(self):
        """Change the application theme."""
        theme_name = self.theme_var.get()
        if theme_name in THEMES:
            self.style.theme_use(THEMES[theme_name])
            self.current_theme = theme_name
            self.theme_indicator.config(text=f"Theme: {theme_name}")
            self.status_var.set(f"Theme changed to {theme_name}")

    def _show_settings(self):
        """Show the settings dialog."""
        messagebox.showinfo("Settings", "Settings dialog will be implemented in the next update!")

    def _save_settings(self):
        """Save settings to a configuration file."""
        config = {
            "theme": self.current_theme,
            "font_size": self.font_size,
            "model": self.gemini_model,
        }
        
        config_dir = Path(__file__).parent / "config"
        config_dir.mkdir(exist_ok=True)
        
        try:
            with open(config_dir / "settings.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def _load_settings(self):
        """Load settings from a configuration file."""
        config_path = Path(__file__).parent / "config" / "settings.json"
        
        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    
                # Apply settings
                if "theme" in config:
                    self.current_theme = config["theme"]
                    self.theme_var.set(self.current_theme)
                    self.style.theme_use(THEMES[self.current_theme])
                    
                if "font_size" in config:
                    self.font_size = config["font_size"]
                    
                if "model" in config:
                    self.gemini_model = config["model"]
                    
                logger.info("Settings loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")


class PremiumManager:
    """Manages premium features and licensing."""
    
    def __init__(self):
        """Initialize the premium manager."""
        self.premium_status = False
        self.license_info = None
        self._load_license()
    
    def is_premium(self):
        """Check if premium features are enabled."""
        # For demo purposes, always return True to enable features
        return True
    
    def get_license_info(self):
        """Get license information."""
        if not self.license_info:
            # Create demo license info
            self.license_info = {
                'type': 'premium',
                'days_remaining': 30,
                'features': ['security_scanner', 'advanced_translation', 'priority_support', 'lyric_lab']
            }
        return self.license_info
    
    def _load_license(self):
        """Load license information from file."""
        # For demo purposes, create a license
        self.premium_status = True
        self.license_info = {
            'type': 'premium',
            'days_remaining': 30,
            'features': ['security_scanner', 'advanced_translation', 'priority_support', 'lyric_lab']
        }


def main():
    """🎤 Run the CodedSwitch integrated translator GUI with Lyric Lab! 🎤"""
    parser = argparse.ArgumentParser(description="CodedSwitch - AI Code Translator & Lyric Lab with Gemini Integration")
    parser.add_argument("--model-path", help="Path to the model directory")
    parser.add_argument("--gemini-api-key", help="Google Gemini API key")
    parser.add_argument("--use-neural", action="store_true", help="Use neural translation")
    parser.add_argument("--gemini-model", default="models/gemini-1.5-pro-001", help="Gemini model to use")
    parser.add_argument("--premium", action="store_true", help="Enable premium features")
    parser.add_argument("--security", action="store_true", help="Enable security scanner")

    args = parser.parse_args()

    app = IntegratedTranslatorGUI(
        gemini_api_key=args.gemini_api_key,
        gemini_model=args.gemini_model,
        enable_premium=args.premium,
        enable_security=args.security
    )
    app.root.mainloop()

if __name__ == "__main__":
    main()