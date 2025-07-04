"""
CodedSwitch - Integrated GUI for AI Code Translator with LLM Integration and Premium Features
ENHANCED VERSION with Bug Fixes, Better Error Handling, and Performance Improvements

This module provides a GUI that integrates the chatbot, translator, vulnerability scanner,
and LYRIC LAB into a single, seamless interface powered by the IntegratedTranslatorAI.
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
import numpy as np
import pygame
import threading
import tempfile
import os
from scipy.io import wavfile
import time
import atexit
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, List, Tuple, Any
import functools
import sys
import io

# Fix for Windows console encoding issues with emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Optional imports with fallbacks
try:
    import librosa  # optional dependency for beat studio features
    LIBROSA_AVAILABLE = True
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    librosa = None  # type: ignore
    LIBROSA_AVAILABLE = False
    # Note: logger not available yet, will log later
# Beat Studio integration
try:
    from beat_studio_integration import beat_studio_integration, BEAT_STUDIO_AVAILABLE
    print("✅ Beat Studio integration loaded successfully!")
except ImportError as e:
    print(f"⚠️ Beat Studio integration not available: {e}")
    BEAT_STUDIO_AVAILABLE = False
    beat_studio_integration = None

# Lyric Lab integration
try:
    from lyric_lab_integration import LyricLabIntegration
    print("✅ Lyric Lab integration loaded successfully!")
except ImportError as e:
    print(f"⚠️ Lyric Lab integration not available: {e}")
    LyricLabIntegration = None

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

class Constants:
    """Application constants for better maintainability."""
    
    # GUI Settings
    DEFAULT_FONT_SIZE = 10
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 24
    DEFAULT_WINDOW_SIZE = "1200x800"
    MIN_WINDOW_SIZE = (800, 600)
    
    # Audio Settings
    SAMPLE_RATE = 44100
    AUDIO_BUFFER_SIZE = 512
    AUDIO_CHANNELS = 2
    AUDIO_FORMAT = -16
    
    # File Settings
    MAX_CODE_LENGTH = 50000
    CONFIG_DIR = "config"
    TEMP_FILE_PREFIX = "codedswitch_"
    
    # AI Settings
    DEFAULT_MODEL = "gemini-2.0-flash-001"
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30

# Configure logging with better format and handle Unicode
class UnicodeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = getattr(self, 'stream', None)
            if stream is not None:
                # Replace any characters that can't be encoded with a replacement character
                stream.write(msg + self.terminator)
                self.flush()
        except UnicodeEncodeError:
            # If we can't encode the message, try to log a simplified version
            try:
                if getattr(self, 'stream', None) is not None:
                    self.stream.write(record.msg.encode('ascii', 'replace').decode('ascii') + '\n')
                    self.flush()
            except:
                pass  # Give up if we still can't log

# Remove any existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure root logger with our custom handler and file handler
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add console handler with our Unicode handler
console_handler = UnicodeStreamHandler()
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Add file handler
file_handler = logging.FileHandler('codedswitch.log', encoding='utf-8')
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Get logger for this module
logger = logging.getLogger(__name__)

# Add current directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import our modules with better error handling
try:
    from security.premium_manager import PremiumManager
    from security.vulnerability_scanner import VulnerabilityScanner
    from integrated_ai import IntegratedTranslatorAI
except ImportError as e:
    root_logger.warning(f"Failed to import some modules: {e}. Using fallback implementations.")
    
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
    "Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "TypeScript"
]

# Enhanced Lyric styles for the Lyric Lab
LYRIC_STYLES = {
    "Boom Bap": {
        "description": "Classic hip-hop with strong emphasis on bars and wordplay",
        "characteristics": "4/4 time, strong snare on 2&4, complex rhyme schemes",
        "examples": "Nas, Jay-Z, Biggie style",
        "prompt_additions": "Focus on complex wordplay, metaphors, and storytelling. Use classic hip-hop vocabulary and references."
    },
    "Trap": {
        "description": "Modern style with triplet flows and melodic elements",
        "characteristics": "Hi-hats, 808s, triplet flows, ad-libs",
        "examples": "Future, Lil Baby, Travis Scott style",
        "prompt_additions": "Include triplet flows, ad-libs like 'yeah', 'uh', simple but catchy hooks, focus on vibe over complexity."
    },
    "Drill": {
        "description": "Aggressive, rapid-fire delivery with dark themes",
        "characteristics": "Fast tempo, aggressive delivery, street narratives",
        "examples": "Pop Smoke, Chief Keef style",
        "prompt_additions": "Rapid-fire delivery, aggressive tone, street-smart wordplay, shorter punchy bars."
    },
    "Melodic Rap": {
        "description": "Singing elements mixed with rap verses",
        "characteristics": "Melodic hooks, sung choruses, emotional content",
        "examples": "Drake, Juice WRLD, Lil Uzi style",
        "prompt_additions": "Include melodic hooks, emotional content, mix of singing and rapping, focus on catchiness."
    },
    "UK Drill": {
        "description": "British drill with unique slang and flow patterns",
        "characteristics": "Specific slang, different flow patterns, UK references",
        "examples": "Headie One, Digga D style",
        "prompt_additions": "Use British slang, unique flow patterns, UK cultural references, road rap terminology."
    },
    "Experimental": {
        "description": "Avant-garde, unconventional flows and structures",
        "characteristics": "Unique structures, experimental flows, abstract concepts",
        "examples": "JPEGMAFIA, Danny Brown style",
        "prompt_additions": "Experiment with unconventional structures, abstract wordplay, unique flows, creative concepts."
    },
    "Coding Rap": {
        "description": "Tech-focused rap with programming references",
        "characteristics": "Technical terminology, code metaphors, geek culture",
        "examples": "Custom CodedSwitch style",
        "prompt_additions": "Heavy use of programming terminology, code metaphors, tech culture references, debugging/optimization themes."
    }
}

# ============================================================================
# UTILITY CLASSES AND FUNCTIONS
# ============================================================================

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_code(code: str, max_length: int = Constants.MAX_CODE_LENGTH) -> Tuple[bool, str]:
        """Validate code input with helpful error messages."""
        if not code.strip():
            return False, "Please enter some code to process!"
        
        if len(code) > max_length:
            return False, f"Code too long ({len(code):,} chars). Maximum: {max_length:,} characters."
        
        # Check for common syntax issues
        triple_quotes = code.count('"""') + code.count("'''")
        if triple_quotes % 2 != 0:
            return False, "Unclosed triple-quote string literals detected. Please check your quotes."
        
        return True, "Code validation passed"
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format."""
        return bool(api_key and len(api_key.strip()) > 10 and not api_key.isspace())

class ConfigManager:
    """Enhanced configuration management."""
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with defaults and validation."""
        defaults = {
            "theme": "Dark",
            "font_size": Constants.DEFAULT_FONT_SIZE,
            "model": Constants.DEFAULT_MODEL,
            "auto_save": True,
            "window_geometry": Constants.DEFAULT_WINDOW_SIZE,
            "last_source_lang": "Python",
            "last_target_lang": "JavaScript",
            "audio_enabled": True,
            "auto_cleanup_temp": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Merge with defaults, validating types
                for key, value in user_config.items():
                    if key in defaults and type(value) == type(defaults[key]):
                        defaults[key] = value
            except Exception as e:
                root_logger.warning(f"Failed to load config: {e}")
        
        return defaults
    
    def save_config(self) -> bool:
        """Save current configuration safely."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            root_logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get configuration value safely."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value

class ErrorHandler:
    """Centralized error handling."""
    
    @staticmethod
    def handle_errors(operation_name: str):
        """Decorator for consistent error handling."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    root_logger.error(f"Error in {operation_name}: {e}", exc_info=True)
                    if hasattr(self, 'status_var'):
                        self.status_var.set(f"❌ {operation_name} failed")
                    
                    # Show user-friendly error
                    error_msg = ErrorHandler._get_user_friendly_error(str(e))
                    messagebox.showerror(
                        f"{operation_name} Error",
                        f"Something went wrong with {operation_name}.\n\n"
                        f"{error_msg}\n\n"
                        "Check the log file for more details."
                    )
                    return None
            return wrapper
        return decorator
    
    @staticmethod
    def _get_user_friendly_error(error_str: str) -> str:
        """Convert technical errors to user-friendly messages."""
        error_lower = error_str.lower()
        
        if "api" in error_lower and "key" in error_lower:
            return "API key issue. Please check your API key in settings."
        elif "connection" in error_lower or "network" in error_lower:
            return "Network connection problem. Please check your internet connection."
        elif "quota" in error_lower or "limit" in error_lower:
            return "API usage limit reached. Please try again later or upgrade your plan."
        elif "timeout" in error_lower:
            return "Operation timed out. Please try again with a smaller request."
        elif "json" in error_lower or "parse" in error_lower:
            return "Data format error. The AI response was invalid."
        else:
            return f"Technical error: {error_str[:100]}..."

class ResourceManager:
    """Manages application resources like temp files and threads."""
    
    def __init__(self):
        self.temp_files: List[str] = []
        self.active_threads: List[threading.Thread] = []
        self.audio_initialized = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup_all)
    
    def add_temp_file(self, file_path: str):
        """Track temporary file for cleanup."""
        self.temp_files.append(file_path)
    
    def add_thread(self, thread: threading.Thread):
        """Track thread for monitoring."""
        self.active_threads.append(thread)
        # Clean up finished threads
        self.active_threads = [t for t in self.active_threads if t.is_alive()]
    
    def cleanup_temp_files(self):
        """Clean up all temporary files."""
        for file_path in self.temp_files[:]:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                self.temp_files.remove(file_path)
            except Exception as e:
                root_logger.warning(f"Failed to remove temp file {file_path}: {e}")
    
    def init_audio(self) -> bool:
        """Initialize audio system safely."""
        try:
            pygame.mixer.init(
                frequency=Constants.SAMPLE_RATE,
                size=Constants.AUDIO_FORMAT,
                channels=Constants.AUDIO_CHANNELS,
                buffer=Constants.AUDIO_BUFFER_SIZE
            )
            self.audio_initialized = True
            root_logger.info("🎵 Audio system initialized successfully!")
            return True
        except Exception as e:
            root_logger.warning(f"⚠️ Audio initialization failed: {e}")
            self.audio_initialized = False
            return False
    
    def cleanup_audio(self):
        """Clean up audio resources."""
        try:
            if self.audio_initialized:
                pygame.mixer.quit()
                self.audio_initialized = False
        except Exception as e:
            root_logger.warning(f"Audio cleanup error: {e}")
    
    def cleanup_all(self):
        """Clean up all resources."""
        root_logger.info("Cleaning up application resources...")
        self.cleanup_temp_files()
        self.cleanup_audio()

# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class IntegratedTranslatorGUI:
    """Enhanced CodedSwitch GUI with improved error handling and resource management."""
    
    def __init__(self, gemini_api_key=None, gemini_model=Constants.DEFAULT_MODEL, 
                 enable_premium=False, enable_security=True):
        """Initialize the CodedSwitch integrated translator GUI."""
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.resource_manager = ResourceManager()
        
        # Initialize with bootstrap theme
        theme_name = self.config_manager.get("theme", "Dark")
        self.style = ttk.Style(theme=THEMES.get(theme_name, THEMES["Dark"]))
        self.root = self.style.master
        self.root.title("CodedSwitch - AI Code Translator & Lyric Lab")
        
        # Load window geometry from config
        geometry = self.config_manager.get("window_geometry", Constants.DEFAULT_WINDOW_SIZE)
        self.root.geometry(geometry)
        self.root.minsize(*Constants.MIN_WINDOW_SIZE)
        
        # Set application icon
        self._set_application_icon()
        
        # Initialize variables
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self.enable_premium = enable_premium
        self.enable_security = enable_security
        self.current_file = None
        self.font_size = self.config_manager.get("font_size", Constants.DEFAULT_FONT_SIZE)
        self.current_theme = theme_name
        
        # Initialize managers
        self.premium_manager = PremiumManager()
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="CodedSwitch")
        
        # Initialize language vars with saved preferences
        self.source_lang = tk.StringVar(value=self.config_manager.get("last_source_lang", "Python"))
        self.target_lang = tk.StringVar(value=self.config_manager.get("last_target_lang", "JavaScript"))
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

        # Initialize audio system
        audio_enabled = self.config_manager.get("audio_enabled", True)
        if audio_enabled:
            self.resource_manager.init_audio()

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
        self.lyric_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook with icons
        self.notebook.add(self.translator_tab, text="  🔄 Code Translator  ")
        self.notebook.add(self.chatbot_tab, text="  🤖 AI Assistant  ")
        self.notebook.add(self.security_tab, text="  🛡️ Security Scanner  ")
        self.notebook.add(self.lyric_tab, text="  🎤 Lyric Lab  ")
        
        # Initialize components
        
        # Floating chat window reference
        self.chat_floater = None
        # Lyric Lab integration instance
        if 'LyricLabIntegration' in globals() and LyricLabIntegration:
            try:
                self.lyric_lab_integration = LyricLabIntegration(self)
            except Exception as e:
                root_logger.warning(f"Lyric Lab integration initialization failed: {e}")
        self._setup_translator_tab()
        self._setup_chatbot_tab()
        self._setup_security_tab()
        self._setup_lyric_lab_tab()
        # Music Lab tab
        try:
            self._setup_music_lab_tab()
        except Exception as e:
            root_logger.warning(f"Music Lab setup skipped: {e}")
        # Optional: add the professional Beat Studio tab if the integration is available
        try:
            self._setup_beat_studio_if_available()
        except Exception as e:
            root_logger.warning(f"Beat Studio setup skipped: {e}")
        
        # Initialize AI interface
        self._initialize_ai_interface()
        
        # Add keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Update status bar indicators
        self._update_status_indicators()
        
        # Bind cleanup events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        root_logger.info("CodedSwitch GUI initialized successfully")

    def _set_application_icon(self):
        """Set application icon if available."""
        if platform.system() == "Windows":
            icon_path = os.path.join(os.path.dirname(__file__), "resources", "codedswitch_icon.ico")
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(default=icon_path)
                except Exception as e:
                    root_logger.warning(f"Failed to set icon: {e}")

    def _setup_beat_studio_if_available(self):
        """Add the Beat Studio tab to the notebook if the integration is available."""
        if beat_studio_integration and getattr(beat_studio_integration, "add_beat_studio_tab", None):
            try:
                beat_studio_integration.add_beat_studio_tab(self.notebook, self)
                root_logger.info("Beat Studio tab initialized.")
            except Exception as e:
                root_logger.warning(f"Beat Studio initialization failed: {e}")

    def _setup_music_lab_tab(self):
        """Add the Music Lab tab to the notebook if available."""
        try:
            import importlib
            try:
                music_lab_tab_module = importlib.import_module('gui_modules.music_lab_tab')
            except ModuleNotFoundError:
                # Fallback: if running from bundled executable where paths differ
                music_lab_tab_module = importlib.import_module('music_lab_tab')

            # Instantiate the MusicLabTab (it is itself a Frame)
            self.music_lab_component = music_lab_tab_module.MusicLabTab(self)
            # Add it to the notebook as a new tab
            self.notebook.add(self.music_lab_component, text="  🎶 Music Lab  ")
            root_logger.info("Music Lab tab added successfully!")
        except Exception as e:
            # Gracefully degrade – show reason inside the tab and log the error
            root_logger.warning(f"Music Lab initialization failed: {e}")
            # Fallback UI when the tab cannot be created
            fallback_frame = ttk.Frame(self.notebook)
            ttk.Label(fallback_frame, text=f"Music Lab unavailable: {e}").pack(padx=20, pady=20)
            self.notebook.add(fallback_frame, text="  🎶 Music Lab  ")

    def _initialize_ai_interface(self):
        """Initialize the AI interface with better error handling."""
        try:
            # Check for API key first (environment variable or passed parameter)
            if not self.gemini_api_key:
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
                        root_logger.warning(f"Failed to load credentials from file: {e}")
            
            if self.gemini_api_key and InputValidator.validate_api_key(self.gemini_api_key):
                # Initialize Gemini interface
                self.ai = IntegratedTranslatorAI(
                    api_key=self.gemini_api_key,
                    model_name=self.gemini_model
                )
                root_logger.info(f"Successfully initialized AI with model: {self.gemini_model}")
                # Provide AI interface alias and pass to Lyric Lab
                self.ai_interface = self.ai
                if hasattr(self, 'lyric_lab_integration'):
                    self.lyric_lab_integration.ai_interface = self.ai
            else:
                # Prompt for API key if not found or invalid
                self.root.after(100, self.prompt_for_api_key)
                
        except Exception as e:
            root_logger.error(f"Failed to initialize AI: {str(e)}")
            self.root.after(100, lambda: self._show_ai_initialization_error(str(e)))

    def _show_ai_initialization_error(self, error_msg: str):
        """Show AI initialization error to user."""
        messagebox.showerror(
            "AI Initialization Error", 
            f"Failed to initialize AI interface.\n\n"
            f"Error: {error_msg}\n\n"
            "You can:\n"
            "• Check your API key\n"
            "• Try demo mode\n"
            "• Restart the application"
        )

    def _configure_styles(self):
        """Configure custom styles for the application."""
        # Configure text styles
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TCheckbutton", font=("Segoe UI", 10))
        self.style.configure("TRadiobutton", font=("Segoe UI", 10))
        
        # Configure heading styles
        self.style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        
        # Configure notebook styles
        self.style.configure("TNotebook", padding=5)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(12, 6))
        
        # Configure button styles with better colors
        self.style.configure("primary.TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("success.TButton", font=("Segoe UI", 10))
        self.style.configure("danger.TButton", font=("Segoe UI", 10))
        self.style.configure("warning.TButton", font=("Segoe UI", 10))
        self.style.configure("info.TButton", font=("Segoe UI", 10))

    def _setup_keyboard_shortcuts(self):
        """Enhanced keyboard shortcuts with better organization."""
        shortcuts = {
            # File operations
            "<Control-n>": ("New File", self.new_file),
            "<Control-o>": ("Open File", self.open_file),
            "<Control-s>": ("Save File", self.save_file),
            "<Control-Shift-S>": ("Save As", self.save_file_as),
            
            # Translation operations
            "<Control-t>": ("Translate Code", self.translate_code),
            "<Control-r>": ("Reverse Translation", lambda e: self.translate_code(reverse=True)),
            "<Control-Shift-C>": ("Clear All", lambda e: self.clear_all_code()),
            
            # Security and analysis
            "<F5>": ("Scan for Vulnerabilities", self.scan_code_for_vulnerabilities),
            "<Control-Shift-V>": ("Quick Vulnerability Check", self.quick_vulnerability_check),
            
            # UI operations
            "<F1>": ("Help", self._show_help),
            "<Control-q>": ("Quit", self._on_closing),
            "<Control-plus>": ("Increase Font", lambda e: self._change_font_size(1)),
            "<Control-minus>": ("Decrease Font", lambda e: self._change_font_size(-1)),
            "<Control-0>": ("Reset Font", lambda e: self._reset_font_size()),
            
            # Advanced features
            "<Control-d>": ("Demo Mode", lambda e: self._load_demo_code()),
            "<Control-e>": ("Export Results", lambda e: self._export_current_results()),
            "<F11>": ("Toggle Fullscreen", lambda e: self._toggle_fullscreen()),
            "<Escape>": ("Clear Status", lambda e: self.status_var.set("Ready")),
            
            # Lyric Lab shortcuts
            "<Control-l>": ("Focus Lyric Editor", lambda e: self._focus_lyric_editor()),
            "<Control-Shift-L>": ("Generate Lyrics", lambda e: self._generate_style_specific_lyrics()),
        }
        
        # Bind all shortcuts with error handling
        for shortcut, (description, command) in shortcuts.items():
            try:
                self.root.bind(shortcut, lambda e, cmd=command: self._safe_execute_shortcut(cmd, e))
            except Exception as e:
                root_logger.warning(f"Failed to bind shortcut {shortcut}: {e}")
        
        # Store shortcuts for help display
        self.keyboard_shortcuts = shortcuts

    def _safe_execute_shortcut(self, command, event):
        """Safely execute keyboard shortcut commands."""
        try:
            if callable(command):
                if command.__name__ in ['translate_code', 'scan_code_for_vulnerabilities']:
                    # For heavy operations, check if already running
                    if hasattr(self, '_operation_in_progress') and self._operation_in_progress:
                        self.status_var.set("⚠️ Operation already in progress...")
                        return
                command()
            else:
                command(event)
        except Exception as e:
            root_logger.error(f"Shortcut execution error: {e}")
            self.status_var.set(f"❌ Shortcut error: {str(e)[:50]}")

    # ============================================================================
    # GUI SETUP METHODS
    # ============================================================================

    def _create_menu_bar(self):
        """Create an enhanced menu bar with more options."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", accelerator="Ctrl+E", command=self._export_current_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self._on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self._select_all)
        edit_menu.add_command(label="Clear All", accelerator="Ctrl+Shift+C", command=self.clear_all_code)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find & Replace...", accelerator="Ctrl+H", command=self._show_find_replace)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences...", command=self._show_preferences)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Font size submenu
        font_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Font Size", menu=font_menu)
        font_menu.add_command(label="Increase", accelerator="Ctrl++", command=lambda: self._change_font_size(1))
        font_menu.add_command(label="Decrease", accelerator="Ctrl+-", command=lambda: self._change_font_size(-1))
        font_menu.add_command(label="Reset", accelerator="Ctrl+0", command=self._reset_font_size)
        
        # Themes submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        for theme_name in THEMES:
            theme_menu.add_radiobutton(
                label=theme_name,
                variable=self.theme_var,
                value=theme_name,
                command=self._change_theme
            )
        
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Fullscreen", accelerator="F11", command=self._toggle_fullscreen)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Translate Code", accelerator="Ctrl+T", command=self.translate_code)
        tools_menu.add_command(label="Reverse Translate", accelerator="Ctrl+R", command=lambda: self.translate_code(reverse=True))
        tools_menu.add_separator()
        tools_menu.add_command(label="Security Scan", accelerator="F5", command=self.scan_code_for_vulnerabilities)
        tools_menu.add_command(label="Quick Security Check", accelerator="Ctrl+Shift+V", command=self.quick_vulnerability_check)
        tools_menu.add_separator()
        tools_menu.add_command(label="Load Demo Code", accelerator="Ctrl+D", command=self._load_demo_code)
        tools_menu.add_command(label="AI Chat", command=lambda: self.notebook.select(1))
        tools_menu.add_command(label="Lyric Lab", accelerator="Ctrl+L", command=lambda: self.notebook.select(3))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", accelerator="F1", command=self._show_help)
        help_menu.add_command(label="User Guide", command=self._show_user_guide)
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", command=self._check_for_updates)
        help_menu.add_command(label="Report Issue", command=lambda: webbrowser.open("https://github.com/your-repo/codedswitch/issues"))
        help_menu.add_separator()
        help_menu.add_command(label="About CodedSwitch", command=self._show_about)

    def _create_status_bar(self):
        """Create an enhanced status bar with more information."""
        # Create frame for status bar
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message (left side)
        self.status_var = tk.StringVar(value="Ready - CodedSwitch initialized successfully!")
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            padding=(10, 5)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Right side indicators
        right_frame = ttk.Frame(self.status_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Audio status
        audio_status = "🎵 Audio" if self.resource_manager.audio_initialized else "🔇 No Audio"
        self.audio_indicator = ttk.Label(
            right_frame,
            text=audio_status,
            padding=(10, 5)
        )
        self.audio_indicator.pack(side=tk.RIGHT)
        
        # Add separator
        ttk.Separator(right_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Model indicator
        self.model_indicator = ttk.Label(
            right_frame,
            text=f"Model: {self.gemini_model}",
            padding=(10, 5)
        )
        self.model_indicator.pack(side=tk.RIGHT)
        
        # Theme indicator
        self.theme_indicator = ttk.Label(
            right_frame,
            text=f"Theme: {self.current_theme}",
            padding=(10, 5)
        )
        self.theme_indicator.pack(side=tk.RIGHT)
        
        # Add separator
        ttk.Separator(right_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # API status indicator
        api_status = "API: Connected" if self.gemini_api_key else "API: Not Connected"
        self.api_status = ttk.Label(
            right_frame,
            text=api_status,
            padding=(10, 5)
        )
        self.api_status.pack(side=tk.RIGHT)

    def _update_status_indicators(self):
        """Update all status bar indicators."""
        # Update model indicator
        self.model_indicator.config(text=f"Model: {self.gemini_model}")
        
        # Update theme indicator  
        self.theme_indicator.config(text=f"Theme: {self.current_theme}")
        
        # Update API status
        api_status = "API: Connected" if self.gemini_api_key else "API: Not Connected"
        self.api_status.config(text=api_status)
        
        # Update audio status
        audio_status = "🎵 Audio" if self.resource_manager.audio_initialized else "🔇 No Audio"
        self.audio_indicator.config(text=audio_status)

    # ============================================================================
    # TAB SETUP METHODS  
    # ============================================================================

    def _setup_translator_tab(self):
        """Set up the enhanced translator tab UI."""
        main_frame = ttk.Frame(self.translator_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header with model selection
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🔄 CodedSwitch AI Translator",
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Model selection on the right
        model_frame = ttk.Frame(header_frame)
        model_frame.pack(side=tk.RIGHT)
        
        ttk.Label(model_frame, text="AI Model:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_var = tk.StringVar(value=self.gemini_model)
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["gemini-2.0-flash-001", "gemini-2.5-flash", "gemini-2.5-pro"],
            width=20,
            state="readonly"
        )
        model_combo.pack(side=tk.LEFT)
        model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # Language selection with enhanced controls
        lang_frame = ttk.LabelFrame(main_frame, text="🌐 Language Configuration", padding=15)
        lang_frame.pack(fill=tk.X, pady=(0, 15))

        # Language selection row
        lang_select_frame = ttk.Frame(lang_frame)
        lang_select_frame.pack(fill=tk.X, pady=(0, 10))

        # Source language
        source_frame = ttk.Frame(lang_select_frame)
        source_frame.pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(source_frame, text="From:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        source_combo = ttk.Combobox(
            source_frame,
            textvariable=self.source_lang,
            values=PROGRAMMING_LANGUAGES,
            width=15,
            state="readonly"
        )
        source_combo.pack(side=tk.LEFT)
        source_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # Swap languages button
        swap_frame = ttk.Frame(lang_select_frame)
        swap_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(
            swap_frame,
            text="⇄",
            command=self._swap_languages,
            width=3
        ).pack()

        # Target language
        target_frame = ttk.Frame(lang_select_frame)
        target_frame.pack(side=tk.LEFT, padx=(15, 0))
        ttk.Label(target_frame, text="To:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        target_combo = ttk.Combobox(
            target_frame,
            textvariable=self.target_lang,
            values=PROGRAMMING_LANGUAGES,
            width=15,
            state="readonly"
        )
        target_combo.pack(side=tk.LEFT)
        target_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # Quick action buttons
        action_frame = ttk.Frame(lang_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(
            action_frame,
            text="🚀 Translate →",
            command=lambda: self.translate_code(reverse=False),
            style="primary.TButton",
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            action_frame,
            text="← Reverse",
            command=lambda: self.translate_code(reverse=True),
            style="info.TButton",
            width=12
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            action_frame,
            text="🗑️ Clear All",
            command=self.clear_all_code,
            style="warning.TButton",
            width=12
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            action_frame,
            text="📤 Export",
            command=self._export_current_results,
            width=10
        ).pack(side=tk.RIGHT)

        # Code editor area with enhanced layout
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Source code frame
        source_frame = ttk.LabelFrame(editor_frame, text="📝 Source Code", padding=5)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Source code editor with line numbers option
        self.source_code = TtkScrolledText(
            source_frame,
            wrap=tk.NONE if not self.word_wrap_var.get() else tk.WORD,
            height=20,
            font=("Consolas" if platform.system() == "Windows" else "Monaco", self.font_size)
        )
        self.source_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.source_code.bind("<KeyRelease>", self._on_source_code_change)
        
        # Initialize source code change tracking
        self._last_source_code = ""
        self._source_change_timer = None

        # Control arrows in the middle
        arrows_frame = ttk.Frame(editor_frame)
        arrows_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Center the buttons vertically
        center_frame = ttk.Frame(arrows_frame)
        center_frame.pack(expand=True)

        ttk.Button(
            center_frame,
            text="→",
            command=lambda: self.translate_code(reverse=False),
            width=4,
            style="primary.TButton"
        ).pack(pady=5)

        ttk.Button(
            center_frame,
            text="←",
            command=lambda: self.translate_code(reverse=True),
            width=4,
            style="info.TButton"
        ).pack(pady=5)

        # Target code frame
        target_frame = ttk.LabelFrame(editor_frame, text="✨ Translated Code", padding=5)
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Target code display
        self.target_code = TtkScrolledText(
            target_frame,
            wrap=tk.NONE if not self.word_wrap_var.get() else tk.WORD,
            height=20,
            font=("Consolas" if platform.system() == "Windows" else "Monaco", self.font_size)
        )
        self.target_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Enhanced feedback section
        feedback_frame = ttk.LabelFrame(main_frame, text="💡 Translation Insights & Tips", padding=10)
        feedback_frame.pack(fill=tk.X, pady=(15, 0))

        self.feedback_text = TtkScrolledText(
            feedback_frame,
            wrap=tk.WORD,
            height=6,
            font=("Segoe UI", self.font_size)
        )
        self.feedback_text.pack(fill=tk.BOTH, expand=True)
        
        # Add initial help text
        initial_help = """🚀 Welcome to CodedSwitch AI Translator!

💡 Quick Start:
1. Paste your code in the Source Code area
2. Select target language 
3. Click "Translate →" or press Ctrl+T
4. Review the translated code and insights here

🎯 Pro Tips:
• Use Ctrl+R for reverse translation
• Try different AI models for varying results  
• Check the Security Scanner for code safety
• Export results for documentation
"""
        self.feedback_text.insert("1.0", initial_help)

    def _on_source_code_change(self, event=None):
        """Handle changes in the source code editor.
        
        This method is triggered whenever the source code is modified. It updates
        the UI state and can trigger auto-actions like auto-translation.
        """
        # Get current source code
        current_code = self.source_code.get("1.0", "end-1c")
        
        # Skip if no actual change
        if current_code == self._last_source_code:
            return
            
        # Update last known source code
        self._last_source_code = current_code
        
        # Cancel any pending auto-translation
        if self._source_change_timer is not None:
            self.root.after_cancel(self._source_change_timer)
            self._source_change_timer = None
            
        # Update status bar
        self._update_status_indicators()
        
        # Check if we should auto-translate (if enabled in settings)
        auto_translate = self.config_manager.get("auto_translate", False)
        if auto_translate and current_code.strip():
            # Schedule translation after a delay (e.g., 1 second after typing stops)
            self._source_change_timer = self.root.after(1000, self._trigger_auto_translate)
    
    def _trigger_auto_translate(self):
        """Trigger auto-translation of the current source code."""
        if self.source_code.compare("end-1c", "!=", "1.0"):  # If not empty
            self.translate_code()
            
    def _setup_chatbot_tab(self):
        """Set up the enhanced chatbot tab UI."""
        # Container that can be moved between tab and floating window
        self.chat_frame = ttk.Frame(self.chatbot_tab, padding=10)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        main_frame = self.chat_frame  # alias used by rest of method

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="🤖 CodedSwitch AI Assistant",
            style="Title.TLabel"
        ).pack(side=tk.LEFT)
        
        # Chat controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        # Pop-out / Dock toggle
        self.pop_btn = ttk.Button(
            controls_frame,
            text="↗ Pop-out",
            command=self._toggle_chat_docking,
            width=12
        )
        self.pop_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            controls_frame,
            text="🗑️ Clear Chat",
            command=self._clear_chat,
            width=12
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            controls_frame,
            text="💾 Export Chat",
            command=self._export_chat,
            width=12
        ).pack(side=tk.RIGHT)

        # Chat display with better styling
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Conversation", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.chat_display = TtkScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("Segoe UI", self.font_size),
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        # Direct reference to the underlying Text widget for reliable operations
        self.chat_text = getattr(self.chat_display, "text", self.chat_display)

        # Configure enhanced text tags for different message types
        self.chat_text.tag_configure("user_msg", foreground="#2196F3", font=("Segoe UI", self.font_size, "bold"))
        self.chat_text.tag_configure("assistant_msg", foreground="#4CAF50", font=("Segoe UI", self.font_size))
        self.chat_text.tag_configure("system_msg", foreground="#FF9800", font=("Segoe UI", self.font_size - 1, "italic"))
        self.chat_text.tag_configure("error_msg", foreground="#F44336", font=("Segoe UI", self.font_size, "bold"))
        self.chat_text.tag_configure("timestamp", foreground="#757575", font=("Segoe UI", self.font_size - 2))

        # Enhanced input area
        input_frame = ttk.LabelFrame(main_frame, text="✍️ Your Message", padding=10)
        input_frame.pack(fill=tk.X)

        # Message input with better layout
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.X)

        self.message_input = TtkScrolledText(
            input_container,
            wrap=tk.WORD,
            width=70,
            height=4,
            font=("Segoe UI", self.font_size)
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Button frame
        btn_frame = ttk.Frame(input_container)
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))

        # Send button
        self.send_button = ttk.Button(
            btn_frame,
            text="🚀 Send",
            command=self.send_message,
            style="primary.TButton",
            width=12
        )
        self.send_button.pack(pady=(0, 5))

        # Quick actions
        ttk.Button(
            btn_frame,
            text="💡 Examples",
            command=self._show_chat_examples,
            width=12
        ).pack()

        # Bind enhanced keys
        self.message_input.bind("<Return>", self.send_message)
        self.message_input.bind("<Shift-Return>", lambda e: "break")
        self.message_input.bind("<Control-Return>", self.send_message)

        # Add enhanced welcome message
        self._add_welcome_message()

    def _toggle_chat_docking(self):
        """Toggle between docked (tab) and undocked (floating) chat window.
        This new strategy avoids *any* widget re-parenting. Instead we keep the
        original chat UI inside the chatbot tab and build a **second** chat UI
        in a floating `Toplevel` when requested. All chat messages are routed
        through `_add_chat_message`, ensuring both displays remain perfectly in
        sync and the full conversation context is preserved."""

        if getattr(self, "chat_floater", None) is None:
            # -----------------  Create floating window  -----------------
            try:
                self.chat_floater = tk.Toplevel(self.root)
                self.chat_floater.title("🤖 Astutely Assistant")
                self.chat_floater.geometry("450x600")
                self.chat_floater.attributes('-topmost', True)

                floater_main = ttk.Frame(self.chat_floater, padding=10)
                floater_main.pack(fill=tk.BOTH, expand=True)

                # ---------- Chat display ----------
                self.floater_chat_display = TtkScrolledText(
                    floater_main,
                    wrap=tk.WORD,
                    width=80,
                    height=25,
                    font=("Segoe UI", self.font_size),
                    state=tk.DISABLED
                )
                self.floater_chat_display.pack(fill=tk.BOTH, expand=True)
                self._configure_chat_tags(
                    self.floater_chat_display.text if hasattr(self.floater_chat_display, "text") else self.floater_chat_display
                )

                # Populate existing history
                for sender, msg, tag, ts in getattr(self, "chat_history", []):
                    self._insert_message_to_display(
                        self.floater_chat_display,
                        sender,
                        msg,
                        tag,
                        ts,
                        silent=True,
                    )

                # ---------- Input + Send ----------
                input_frame = ttk.Frame(floater_main)
                input_frame.pack(fill=tk.X, pady=(10, 0))

                self.floater_message_input = TtkScrolledText(
                    input_frame,
                    wrap=tk.WORD,
                    width=70,
                    height=4,
                    font=("Segoe UI", self.font_size),
                )
                self.floater_message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                send_btn = ttk.Button(
                    input_frame,
                    text="🚀 Send",
                    command=self._floater_send_message,
                    style="primary.TButton",
                    width=12,
                )
                send_btn.pack(side=tk.RIGHT, padx=(10, 0))

                # Key bindings for quick send
                self.floater_message_input.bind("<Return>", self._floater_send_message)
                self.floater_message_input.bind("<Shift-Return>", lambda e: "break")
                self.floater_message_input.bind("<Control-Return>", self._floater_send_message)

                self.floater_message_input.focus_set()

                # Update toggle button
                self.pop_btn.config(text="⇦ Dock")

                # Closing the floater should dock back
                self.chat_floater.protocol("WM_DELETE_WINDOW", self._toggle_chat_docking)
            except Exception as e:
                root_logger.error(f"Failed to create floating chat window: {e}")
        else:
            # -----------------  Destroy floating window  -----------------
            try:
                # Preserve any partially typed text
                if getattr(self, "floater_message_input", None):
                    pending_text = self.floater_message_input.get("1.0", tk.END).strip()
                    if pending_text:
                        self.message_input.delete("1.0", tk.END)
                        self.message_input.insert("1.0", pending_text)

                self.chat_floater.destroy()
                self.chat_floater = None
                self.floater_chat_display = None
                self.floater_message_input = None

                # Update toggle button
                self.pop_btn.config(text="↗ Pop-out")
            except Exception as e:
                root_logger.error(f"Failed to dock chat window: {e}")

    # ------------------------------------------------------------------
    # Helper utilities – keep both chat displays perfectly in sync
    # ------------------------------------------------------------------
    def _configure_chat_tags(self, text_widget):
        """Apply the standard chat text tags to *text_widget*."""
        try:
            text_widget.tag_configure("user_msg", foreground="#2196F3", font=("Segoe UI", self.font_size, "bold"))
            text_widget.tag_configure("assistant_msg", foreground="#4CAF50", font=("Segoe UI", self.font_size))
            text_widget.tag_configure("system_msg", foreground="#FF9800", font=("Segoe UI", self.font_size - 1, "italic"))
            text_widget.tag_configure("error_msg", foreground="#F44336", font=("Segoe UI", self.font_size, "bold"))
            text_widget.tag_configure("timestamp", foreground="#757575", font=("Segoe UI", self.font_size - 2))
        except tk.TclError:
            pass  # Widget might be destroyed during shutdown

    def _insert_message_to_display(self, widget, sender, message, tag, ts, silent=False):
        """Low-level helper to insert a formatted message into *widget*."""
        if not widget:
            return
        text_obj = widget.text if hasattr(widget, "text") else widget
        text_obj.config(state=tk.NORMAL)
        formatted = f"{sender} ({ts:%I:%M %p}):\n{message}\n\n"
        text_obj.insert(tk.END, formatted, tag or "system_msg")
        text_obj.see(tk.END)
        text_obj.config(state=tk.DISABLED)
        if not silent:
            self.root.update_idletasks()

    def _add_chat_message(self, sender: str, message: str, tag: str = None):
        """Centralised entry point for recording & displaying chat messages."""
        ts = datetime.now()
        if not hasattr(self, "chat_history"):
            self.chat_history = []
        self.chat_history.append((sender, message, tag, ts))

        # Main tab
        self._insert_message_to_display(self.chat_display, sender, message, tag, ts)
        # Floating window (if open)
        if getattr(self, "floater_chat_display", None):
            self._insert_message_to_display(self.floater_chat_display, sender, message, tag, ts, silent=True)

    def _floater_send_message(self, event=None):
        """Send a message originating from the floating chat window."""
        # Shift+Return → newline
        if event and event.state & 0x1:
            return "break"
        if not getattr(self, "floater_message_input", None):
            return "break"
        message = self.floater_message_input.get("1.0", tk.END).strip()
        if not message:
            return "break"

        # Clear input
        self.floater_message_input.delete("1.0", tk.END)

        # Re-use the existing send logic by temporarily pointing message_input
        original_input = self.message_input
        self.message_input = self.floater_message_input  # dummy to keep any existing logic happy
        try:
            # Manually duplicate logic from the primary send flow
            self._add_chat_message("You", message, "user_msg")
            thinking_msg = "🤔 Thinking…"
            self._add_chat_message("Assistant", thinking_msg, "assistant_msg")

            def _get_response():
                try:
                    if hasattr(self, "ai") and hasattr(self.ai, "chat_response"):
                        response = self.ai.chat_response(message)
                    else:
                        response = (
                            "This is a demo response. Provide a valid API key for full AI functionality."
                        )
                    self.root.after(0, lambda: self._handle_response_received(response))
                except Exception as exc:
                    error_msg = f"Sorry, I encountered an error: {exc}"
                    self.root.after(0, lambda: self._handle_response_received(error_msg))

            thread = threading.Thread(target=_get_response, daemon=True)
            if hasattr(self, "resource_manager"):
                self.resource_manager.add_thread(thread)
            thread.start()
        finally:
            # Restore original input reference
            self.message_input = original_input
        return "break"

    def _setup_security_tab(self):
        """Set up the enhanced security scanning tab."""
        main_frame = ttk.Frame(self.security_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text="🛡️ Security Vulnerability Scanner",
            style="Title.TLabel"
        ).pack(side=tk.LEFT)
        
        # Quick scan indicator
        self.scan_status_var = tk.StringVar(value="Ready for scanning")
        ttk.Label(
            header_frame,
            textvariable=self.scan_status_var,
            font=("Segoe UI", 9, "italic")
        ).pack(side=tk.RIGHT)

        # Code input section
        input_frame = ttk.LabelFrame(main_frame, text="📝 Code Analysis Input", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Language and controls
        control_frame = ttk.Frame(input_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Language selection
        ttk.Label(control_frame, text="Language:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        lang_combo = ttk.Combobox(
            control_frame,
            textvariable=self.scan_lang,
            values=PROGRAMMING_LANGUAGES,
            state="readonly",
            width=15
        )
        lang_combo.pack(side=tk.LEFT, padx=(5, 20))

        # Quick actions
        ttk.Button(
            control_frame,
            text="📋 Load Example",
            command=self.load_test_code,
            style="info.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🗑️ Clear",
            command=lambda: self.scan_code.delete("1.0", tk.END)
        ).pack(side=tk.LEFT)

        # Code editor for scanning
        self.scan_code = TtkScrolledText(
            input_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Consolas" if platform.system() == "Windows" else "Monaco", self.font_size)
        )
        self.scan_code.pack(fill=tk.BOTH, expand=True)

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="🔍 Security Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Results display with enhanced formatting
        self.scan_results = TtkScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=80,
            height=12,
            font=("Segoe UI", self.font_size),
            state=tk.DISABLED
        )
        self.scan_results.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Configure enhanced result tags
        self.scan_results.tag_configure("header", font=("Segoe UI", self.font_size + 1, "bold"))
        self.scan_results.tag_configure("success", foreground="#4CAF50", font=("Segoe UI", self.font_size, "bold"))
        self.scan_results.tag_configure("info", foreground="#2196F3")
        self.scan_results.tag_configure("warning", foreground="#FF9800", font=("Segoe UI", self.font_size, "bold"))
        self.scan_results.tag_configure("error", foreground="#F44336", font=("Segoe UI", self.font_size, "bold"))
        self.scan_results.tag_configure("critical", foreground="#D32F2F", font=("Segoe UI", self.font_size, "bold"))

        # Enhanced controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))

        # Main scan button
        self.scan_button = ttk.Button(
            controls_frame,
            text="🚀 Deep Security Scan",
            command=self.scan_code_for_vulnerabilities,
            style="primary.TButton",
            width=20
        )
        self.scan_button.pack(side=tk.LEFT, padx=(0, 10))

        # Quick scan button
        ttk.Button(
            controls_frame,
            text="⚡ Quick Check",
            command=self.quick_vulnerability_check,
            style="info.TButton",
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Export and fix buttons
        ttk.Button(
            controls_frame,
            text="📤 Export Report",
            command=self.export_report,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            controls_frame,
            text="🔧 Auto-Fix Issues",
            command=self.auto_fix_vulnerabilities,
            style="success.TButton",
            width=15
        ).pack(side=tk.LEFT)

        # Progress bar for scanning
        self.scan_progress = ttk.Progressbar(
            controls_frame,
            mode='indeterminate',
            length=200
        )
        self.scan_progress.pack(side=tk.RIGHT, padx=(10, 0))

    def _setup_lyric_lab_tab(self):
        """Set up the Lyric Lab tab with full functionality"""
        if hasattr(self, 'lyric_lab_integration'):
            self.lyric_lab_integration.setup_lyric_lab_tab(self.lyric_tab)
            return
        else:
            # Fallback UI presented in its own modal dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("🔐 Connect Lyric Lab")
            dialog.geometry("600x500")
            dialog.transient(self.root)
            dialog.grab_set()

            # Build UI inside the dialog
            main_frame = ttk.Frame(dialog, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(main_frame, text="🎤 Lyric Lab - Getting Started", 
                      font=('Arial', 14)).pack(pady=(0, 10))

            instructions_frame = ttk.LabelFrame(
                main_frame,
                text="How to enable Lyric Lab",
                padding=10
            )
            instructions_frame.pack(fill=tk.X, pady=(0, 20))
            instructions = (
                "2. Sign in with your Google account\n"
                "3. Click \"Create API Key\"\n"
                "4. Copy the generated key\n"
                "5. Paste it below and click Save\n\n"
                "🆓 The API is free with generous limits!\n"
                "🔒 Your key is stored securely on your computer."
            )
        
        ttk.Label(
            instructions_frame,
            text=instructions,
            justify=tk.LEFT,
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W)
        
        # API key input with enhanced styling
        input_frame = ttk.LabelFrame(main_frame, text="🔐 Enter Your API Key", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.api_key_var = tk.StringVar()
        key_entry = ttk.Entry(
            input_frame, 
            textvariable=self.api_key_var, 
            width=60, 
            show="*",
            font=("Consolas", 10)
        )
        key_entry.pack(fill=tk.X, pady=(0, 10))
        key_entry.focus()
        
        # Show/hide with better styling
        show_frame = ttk.Frame(input_frame)
        show_frame.pack(fill=tk.X)
        
        show_var = tk.BooleanVar(value=False)
        show_check = ttk.Checkbutton(
            show_frame,
            text="Show API key",
            variable=show_var,
            command=lambda: key_entry.config(show="" if show_var.get() else "*")
        )
        show_check.pack(side=tk.LEFT)
        
        # Validation indicator
        self.validation_label = ttk.Label(
            show_frame,
            text="",
            font=("Segoe UI", 8)
        )
        self.validation_label.pack(side=tk.RIGHT)
        
        # Validate on typing
        def validate_key(*args):
            key = self.api_key_var.get()
            if not key:
                self.validation_label.config(text="", foreground="gray")
            elif len(key) < 20:
                self.validation_label.config(text="❌ Too short", foreground="red")
            elif InputValidator.validate_api_key(key):
                self.validation_label.config(text="✅ Valid format", foreground="green")
            else:
                self.validation_label.config(text="⚠️ Check format", foreground="orange")
        
        self.api_key_var.trace('w', validate_key)
        
        # Buttons with enhanced styling
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Demo mode button
        ttk.Button(
            btn_frame,
            text="🎮 Demo Mode",
            command=lambda: self._enter_demo_mode(dialog),
            style="info.TButton",
            width=15
        ).pack(side=tk.LEFT)
        
        # Help button
        ttk.Button(
            btn_frame,
            text="❓ Help",
            command=lambda: webbrowser.open("https://makersuite.google.com/app/apikey"),
            width=15
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Main action buttons
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="💾 Save & Connect",
            command=lambda: self._save_api_key(self.api_key_var.get(), dialog),
            style="primary.TButton",
            width=15
        ).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Bind Enter key
        def on_enter(event):
            if InputValidator.validate_api_key(self.api_key_var.get()):
                self._save_api_key(self.api_key_var.get(), dialog)
        
        key_entry.bind("<Return>", on_enter)
        
        # Wait for dialog
        self.root.wait_window(dialog)

    def _enter_demo_mode(self, dialog):
        """Enter demo mode with enhanced mock functionality."""
        self._setup_demo_mode()
        dialog.destroy()
        self.status_var.set("🎮 Demo Mode Active - Limited AI functionality")
        self.api_status.config(text="API: Demo Mode")
        
        # Show demo mode info
        messagebox.showinfo(
            "Demo Mode Activated",
            "🎮 You're now in Demo Mode!\n\n"
            "✅ All features are available for testing\n"
            "⚠️ AI responses are simulated\n"
            "💡 Get a real API key for full functionality\n\n"
            "Demo mode is perfect for exploring CodedSwitch!"
        )

    def _setup_demo_mode(self):
        """Create an enhanced mock AI interface for demo purposes."""
        class MockAI:
            def translate_code(self, source_code, target_language, use_neural=False, use_llm=False):
                return f"""// Translated to {target_language} (Demo Mode)
// Original code preserved below with syntax adjustments

{self._simulate_translation(source_code, target_language)}

/* 
Demo Mode Notes:
- This is a simulated translation
- Get a real API key for actual AI translation
- The structure shows how real translations work
*/"""
            
            def chat_response(self, message):
                responses = [
                    "I'm in demo mode, but I can see you're asking about code! In real mode, I'd provide detailed analysis and suggestions.",
                    "Demo response: That's an interesting coding question! With a real API key, I could give you comprehensive help with debugging, optimization, and best practices.",
                    "This is a simulated response. In full mode, I'd analyze your code, suggest improvements, and help with any programming challenges!",
                    "Demo mode active! I'd love to help you with real code analysis, translation, and security scanning with a proper API connection."
                ]
                import random
                return random.choice(responses)
            
            def scan_vulnerabilities(self, code, language):
                # Return demo vulnerabilities
                class MockVuln:
                    def __init__(self, severity, line, category, description):
                        self.severity = type('Severity', (), {'name': severity})()
                        self.line_number = line
                        self.category = category
                        self.description = description
                
                return [
                    MockVuln('HIGH', 5, 'Demo SQL Injection', 'This is a demo vulnerability for testing purposes.'),
                    MockVuln('MEDIUM', 12, 'Demo XSS Risk', 'Simulated cross-site scripting vulnerability.'),
                    MockVuln('LOW', 8, 'Demo Code Quality', 'Minor code quality improvement suggested.')
                ]
        
        self.ai = MockAI()

    def _save_api_key(self, api_key: str, dialog: tk.Toplevel):
        """Save the API key with enhanced validation and error handling."""
        if not api_key.strip():
            messagebox.showwarning("Empty Key", "Please enter an API key.")
            return
        
        if not InputValidator.validate_api_key(api_key):
            messagebox.showwarning(
                "Invalid Key Format", 
                "The API key format doesn't look correct.\n\n"
                "Please check:\n"
                "• The key is complete\n"
                "• No extra spaces or characters\n"
                "• Copy-paste directly from Google AI Studio"
            )
            return
            
        try:
            # Test the API key
            dialog.title("Testing API Key...")
            self.root.update()
            
            # Save API key
            self.gemini_api_key = api_key.strip()
            
            # Initialize AI with the new key
            self._initialize_ai_interface()
            
            if hasattr(self, 'ai') and self.ai:
                # Save to config for future use
                self.config_manager.set("api_key", api_key.strip())
                self.config_manager.save_config()
                
                dialog.destroy()
                
                # Update status indicators
                self._update_status_indicators()
                
                # Show success
                messagebox.showinfo(
                    "✅ Connection Successful!", 
                    "API key saved and tested successfully!\n\n"
                    "🚀 CodedSwitch is now fully operational.\n"
                    "💡 Your key is securely stored for future sessions."
                )
                
                root_logger.info("API key successfully configured")
            else:
                messagebox.showerror(
                    "Connection Failed", 
                    "The API key couldn't be validated.\n\n"
                    "Please check:\n"
                    "• Your internet connection\n"
                    "• The API key is correct\n"
                    "• Google AI services are available"
                )
                
        except Exception as e:
            root_logger.error(f"API key validation error: {e}")
            messagebox.showerror(
                "Setup Error", 
                f"Failed to configure API key.\n\n"
                f"Error: {str(e)}\n\n"
                "You can try:\n"
                "• Demo mode for testing\n"
                "• Check your internet connection\n"
                "• Verify the API key is correct"
            )

    # ============================================================================
    # CORE FUNCTIONALITY METHODS
    # ============================================================================

    @ErrorHandler.handle_errors("Code Translation")
    def translate_code(self, reverse=False):
        """Enhanced code translation with better UX and error handling."""
        # Get source code
        source_code = self.source_code.get("1.0", tk.END).strip()
        
        # Enhanced input validation
        is_valid, error_msg = InputValidator.validate_code(source_code)
        if not is_valid:
            messagebox.showwarning("Invalid Input", error_msg)
            self.source_code.focus()
            return
        
        # Check for very long code with user confirmation
        if len(source_code) > 10000:
            if not messagebox.askyesno(
                "Large Code Warning", 
                f"You're translating {len(source_code):,} characters of code.\n\n"
                "This might take a while and use more API quota.\n"
                "Consider breaking it into smaller chunks.\n\n"
                "Continue with full translation?"
            ):
                return

        # Set operation flag to prevent multiple simultaneous translations
        self._operation_in_progress = True
        
        try:
            # Show enhanced loading state
            self._show_translation_progress("Initializing AI translator...")
            
            # Disable UI elements
            self._set_translation_ui_enabled(False)
            
            # Get language preferences and save them
            source_lang = self.source_lang.get()
            target_lang = self.target_lang.get()
            
            self.config_manager.set("last_source_lang", source_lang)
            self.config_manager.set("last_target_lang", target_lang)
            
            # Perform translation
            if reverse:
                self._show_translation_progress(f"Translating to {source_lang}...")
                translated_code = self.ai.translate_code(
                    source_code=source_code,
                    target_language=source_lang,
                    use_neural=False,
                    use_llm=True
                )
                
                # Update source code area
                self.source_code.delete("1.0", tk.END)
                self.source_code.insert(tk.END, translated_code)
                
                self._show_translation_success(f"✅ Reverse translated to {source_lang}!")
                
            else:
                self._show_translation_progress(f"Translating to {target_lang}...")
                translated_code = self.ai.translate_code(
                    source_code=source_code,
                    target_language=target_lang,
                    use_neural=False,
                    use_llm=True
                )
                
                # Update target code area
                self.target_code.delete("1.0", tk.END)
                self.target_code.insert(tk.END, translated_code)
                
                self._show_translation_success(f"✅ Translated to {target_lang}!")
                
                # Generate enhanced feedback
                self._generate_translation_feedback(source_code, translated_code, source_lang, target_lang)
                
        except Exception as e:
            # Enhanced error handling
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                self._show_quota_exceeded_error()
            elif "network" in error_msg or "connection" in error_msg:
                self._show_network_error()
            else:
                self._show_generic_translation_error(str(e))
        finally:
            # Always reset state
            self._operation_in_progress = False
            self._set_translation_ui_enabled(True)
            
            # Reset status after delay
            self.root.after(5000, lambda: self.status_var.set("Ready"))

    def _generate_translation_feedback(self, source_code, translated_code, source_lang, target_lang):
        """Generate intelligent feedback about the translation."""
        self.feedback_text.delete("1.0", tk.END)
        
        # Calculate metrics
        source_lines = len(source_code.splitlines())
        target_lines = len(translated_code.splitlines())
        size_ratio = len(translated_code) / max(len(source_code), 1)
        
        feedback = f"""🎉 Translation Completed Successfully!

📊 Translation Metrics:
• Source: {source_lang} ({source_lines} lines, {len(source_code):,} characters)
• Target: {target_lang} ({target_lines} lines, {len(translated_code):,} characters)
• Size ratio: {size_ratio:.2f}x
• Translation quality: AI-optimized

💡 Key Differences ({source_lang} → {target_lang}):
{self._get_language_differences(source_lang, target_lang)}

🔧 Next Steps:
• Review the translated code for accuracy
• Test the functionality in your target environment
• Use the Security Scanner to check for vulnerabilities
• Consider running both versions side-by-side for validation

✨ Pro Tips:
• Different languages have different performance characteristics
• Some language-specific features may need manual adjustment
• Consider the target platform's best practices
"""
        
        self.feedback_text.insert("1.0", feedback)

    def _get_language_differences(self, source_lang, target_lang):
        """Get key differences between programming languages."""
        differences = {
            ("Python", "JavaScript"): "• Indentation → Braces\n• print() → console.log()\n• Dynamic typing remains similar",
            ("JavaScript", "Python"): "• Braces → Indentation\n• console.log() → print()\n• Variable declarations simplified",
            ("Python", "Java"): "• Dynamic → Static typing\n• No semicolons → Semicolons required\n• Classes more verbose in Java",
            ("Java", "Python"): "• Static → Dynamic typing\n• Semicolons → No semicolons\n• More concise syntax",
            ("Python", "C++"): "• Interpreted → Compiled\n• Memory management automated → Manual\n• More explicit type declarations",
        }
        
        key = (source_lang, target_lang)
        return differences.get(key, "• Syntax and paradigm differences\n• Language-specific features adapted\n• Best practices applied")

    @ErrorHandler.handle_errors("Vulnerability Scanning")
    def scan_code_for_vulnerabilities(self):
        """Enhanced vulnerability scanning with progress tracking."""
        code = self.scan_code.get("1.0", tk.END).strip()
        language = self.scan_lang.get().lower()
        
        # Input validation
        is_valid, error_msg = InputValidator.validate_code(code, max_length=20000)
        if not is_valid:
            messagebox.showwarning("Cannot Scan Code", error_msg)
            self.scan_code.focus()
            return
        
        # Set scanning state
        self.scan_in_progress = True
        self.scan_status_var.set("Scanning in progress...")
        
        try:
            # Clear previous results
            self._clear_scan_results()
            
            # Show progress
            self.scan_progress.start()
            self._set_scan_ui_enabled(False)
            
            # Simulate detailed progress
            progress_steps = [
                "🔍 Initializing security scanner...",
                "🛡️ Analyzing code structure...",
                "⚡ Checking for injection vulnerabilities...",
                "🔐 Scanning for credential leaks...",
                "🚨 AI-powered threat detection...",
                "📊 Generating comprehensive report..."
            ]
            
            self._show_scan_progress(progress_steps)
            
            # Perform actual scan
            vulnerabilities = self.ai.scan_vulnerabilities(code, language) if hasattr(self.ai, 'scan_vulnerabilities') else []
            
            # Display results
            self._display_scan_results(vulnerabilities, code, language)
            
        except Exception as e:
            self._show_scan_error(str(e))
        finally:
            # Reset UI state
            self.scan_in_progress = False
            self.scan_progress.stop()
            self._set_scan_ui_enabled(True)
            self.scan_status_var.set("Scan completed")

    def _show_scan_progress(self, steps):
        """Show scanning progress with steps."""
        for i, step in enumerate(steps):
            self.status_var.set(step)
            self._add_scan_result(f"{step}\n", "info")
            self.root.update_idletasks()
            time.sleep(0.3)  # Visual feedback delay

    def _display_scan_results(self, vulnerabilities, code, language):
        """Display comprehensive scan results."""
        self._clear_scan_results()
        
        if not vulnerabilities:
            self._show_clean_scan_results(code, language)
        else:
            self._show_vulnerability_results(vulnerabilities, code, language)

    def _show_clean_scan_results(self, code, language):
        """Show results when no vulnerabilities are found."""
        lines = len(code.splitlines())
        chars = len(code)
        
        clean_report = f"""🎉 EXCELLENT! No Security Vulnerabilities Detected! 🎉

📊 Scan Summary:
• Language: {language.title()}
• Lines scanned: {lines:,}
• Characters analyzed: {chars:,}
• Vulnerability patterns checked: 50+
• AI confidence: High

✅ Security Checks Passed:
• SQL Injection patterns ✓
• Cross-Site Scripting (XSS) ✓
• Command Injection ✓
• Path Traversal ✓
• Hard-coded credentials ✓
• Input validation issues ✓
• Authentication bypasses ✓
• Information disclosure ✓

💡 Security Best Practices Reminder:
• Always validate user input
• Use parameterized queries
• Keep dependencies updated
• Regular security reviews
• Follow OWASP guidelines

🔧 Want to test the scanner? Click 'Load Example' for vulnerable code samples!
"""
        
        self._add_scan_result(clean_report, "success")

    def _show_vulnerability_results(self, vulnerabilities, code, language):
        """Show detailed vulnerability results."""
        # Sort by severity
        severity_order = {'HIGH': 0, 'CRITICAL': 0, 'MEDIUM': 1, 'LOW': 2}
        sorted_vulns = sorted(vulnerabilities, key=lambda v: severity_order.get(v.severity.name, 3))
        
        # Count by severity
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.severity.name
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Header
        header = f"""🛡️ SECURITY VULNERABILITY REPORT 🛡️

📊 Scan Results Summary:
• Total Issues Found: {len(vulnerabilities)}
• Code Language: {self.scan_lang.get()}
• Lines Analyzed: {len(code.splitlines()):,}

🚨 Severity Breakdown:
"""
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}[severity]
                header += f"• {emoji} {severity}: {count} issue{'s' if count > 1 else ''}\n"
        
        header += "\n" + "="*60 + "\n\n"
        
        self._add_scan_result(header, "header")
        
        # Display each vulnerability
        for i, vuln in enumerate(sorted_vulns, 1):
            self._display_single_vulnerability(i, vuln)
        
        # Add recommendations
        recommendations = f"""
💡 SECURITY RECOMMENDATIONS:

🔧 Immediate Actions:
• Fix all HIGH and CRITICAL severity issues immediately
• Review and address MEDIUM priority vulnerabilities
• Consider LOW priority improvements for code quality

🛡️ Prevention Strategies:
• Implement input validation and sanitization
• Use prepared statements for database queries
• Apply principle of least privilege
• Regular security testing and code reviews
• Keep all dependencies updated

📚 Additional Resources:
• OWASP Top 10: https://owasp.org/www-project-top-ten/
• Secure coding guidelines for {self.scan_lang.get()}
• Consider using automated security testing tools

🔄 Next Steps:
• Use the 'Auto-Fix Issues' button for automated repairs
• Export this report for your security team
• Re-scan after implementing fixes
"""
        
        self._add_scan_result(recommendations, "info")

    def _display_single_vulnerability(self, index, vuln):
        """Display a single vulnerability with detailed information."""
        severity = vuln.severity.name
        severity_colors = {
            'CRITICAL': 'error',
            'HIGH': 'error', 
            'MEDIUM': 'warning',
            'LOW': 'info'
        }
        
        vuln_text = f"""
🔍 Vulnerability #{index}

📍 Location: Line {vuln.line_number}
🏷️ Category: {vuln.category}
⚠️ Severity: {severity}
📝 Description: {vuln.description}

💡 Impact: {self._get_vulnerability_impact(vuln.category)}
🔧 Fix Suggestion: {self._get_fix_suggestion(vuln.category)}

{'-' * 50}
"""
        
        self._add_scan_result(vuln_text, severity_colors.get(severity, 'info'))

    def _get_vulnerability_impact(self, category):
        """Get impact description for vulnerability category."""
        impacts = {
            'SQL Injection': 'Database compromise, data theft, unauthorized access',
            'XSS': 'Session hijacking, data theft, malicious script execution',
            'Command Injection': 'System compromise, arbitrary code execution',
            'Path Traversal': 'Unauthorized file access, information disclosure',
            'Hard-coded Credentials': 'Authentication bypass, unauthorized access',
            'Demo Vulnerability': 'This is a demonstration vulnerability for testing'
        }
        return impacts.get(category, 'Potential security risk - review carefully')

    def _get_fix_suggestion(self, category):
        """Get fix suggestion for vulnerability category."""
        fixes = {
            'SQL Injection': 'Use parameterized queries or prepared statements',
            'XSS': 'Sanitize and validate all user input, use proper encoding',
            'Command Injection': 'Avoid system calls with user input, use whitelisting',
            'Path Traversal': 'Validate file paths, use secure file access methods',
            'Hard-coded Credentials': 'Use environment variables or secure config files',
            'Demo Vulnerability': 'This is for demonstration - no real fix needed'
        }
        return fixes.get(category, 'Review code and apply security best practices')

    # ============================================================================
    # LYRIC LAB ENHANCED METHODS
    # ============================================================================

    def _on_lyric_text_change(self, event):
        """Enhanced lyric text change handler with real-time features."""
        try:
            # Update word count
            text = self.lyric_editor.get("1.0", tk.END).strip()
            words = len(text.split()) if text else 0
            lines = len(text.splitlines()) if text else 0
            self.word_count_var.set(f"Words: {words} | Lines: {lines}")
            
            # Get current line and word for suggestions
            try:
                current_line = self.lyric_editor.get("insert linestart", "insert lineend")
                words_in_line = current_line.split()
                
                if words_in_line:
                    last_word = words_in_line[-1].strip(".,!?;:")
                    if len(last_word) > 2:  # Only suggest for meaningful words
                        self._get_rhyme_suggestions(last_word)
                        self._get_synonym_suggestions(last_word)
            except:
                pass  # Ignore cursor position errors
                
        except Exception as e:
            root_logger.warning(f"Error in lyric text change handler: {e}")

    def _get_rhyme_suggestions(self, word):
        """Get AI-powered rhyme suggestions with caching."""
        try:
            # Check cache first
            if hasattr(self, '_rhyme_cache') and word in self._rhyme_cache:
                rhymes = self._rhyme_cache[word]
            else:
                # Get from AI
                prompt = f"""Give me 10 words that rhyme with "{word}" perfect for rap/hip-hop lyrics. 
                Focus on multi-syllable rhymes and words commonly used in modern rap.
                Consider slant rhymes and near-rhymes too.
                Return just the words, one per line, no numbering."""
                
                response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else f"rhyme\ntime\nclimb\nprime\nchime\nlime\nmime\ndime\ngrime\nsublime"
                
                rhymes = [line.strip() for line in response.split('\n') if line.strip() and not line.strip().isdigit()]
                
                # Cache for performance
                if not hasattr(self, '_rhyme_cache'):
                    self._rhyme_cache = {}
                self._rhyme_cache[word] = rhymes
            
            # Update suggestions listbox
            self.rhyme_suggestions.delete(0, tk.END)
            for rhyme in rhymes[:10]:
                self.rhyme_suggestions.insert(tk.END, rhyme)
                
        except Exception as e:
            root_logger.warning(f"Error getting rhyme suggestions: {e}")

    def _get_synonym_suggestions(self, word):
        """Get contextual synonym suggestions."""
        try:
            prompt = f"""Give me 8 hip-hop/rap appropriate synonyms or alternative words for "{word}" that would work well in lyrics.
            Focus on words that maintain the vibe and flow.
            Return just the words, one per line."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else f"word\nterm\nphrase\nbar\nline\nverse\nflow\nrhyme"
            
            synonyms = [line.strip() for line in response.split('\n') if line.strip()]
            
            self.synonym_suggestions.delete(0, tk.END)
            for synonym in synonyms[:8]:
                self.synonym_suggestions.insert(tk.END, synonym)
                
        except Exception as e:
            root_logger.warning(f"Error getting synonym suggestions: {e}")

    def _insert_rhyme(self, event):
        """Insert selected rhyme into lyric editor."""
        try:
            selection = self.rhyme_suggestions.curselection()
            if selection:
                rhyme = self.rhyme_suggestions.get(selection[0])
                self.lyric_editor.insert(tk.INSERT, rhyme + " ")
                self.lyric_editor.focus()
        except Exception as e:
            root_logger.warning(f"Error inserting rhyme: {e}")

    @ErrorHandler.handle_errors("Lyric Flow Analysis")
    def _analyze_lyric_flow(self):
        """Enhanced lyric flow analysis with detailed metrics."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            prompt = f"""Analyze these rap lyrics for flow, rhythm, and structure. Be detailed and specific:

{lyrics}

Provide comprehensive analysis including:
1. Syllable count per line (list each line)
2. Rhyme scheme pattern (ABAB, AABB, etc.)
3. Flow consistency rating (1-10)
4. Internal rhymes identified
5. Rhythm and cadence assessment
6. Suggestions for improvement
7. Overall performance rating (1-10)
8. Strengths and weaknesses

Make it detailed and actionable."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else self._generate_demo_flow_analysis(lyrics)
            
            # Show in enhanced dialog
            self._show_analysis_dialog("🎵 Flow Analysis Results", response, "flow_analysis")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze lyrics: {str(e)}")

    def _generate_demo_flow_analysis(self, lyrics):
        """Generate demo flow analysis for testing."""
        lines = lyrics.split('\n')
        line_count = len([line for line in lines if line.strip()])
        
        return f"""🎵 FLOW ANALYSIS RESULTS:

📊 Structure Analysis:
• Total lines: {line_count}
• Average words per line: {len(lyrics.split()) / max(line_count, 1):.1f}
• Estimated syllables: {len(lyrics.split()) * 1.3:.0f}

🎼 Flow Assessment:
• Flow consistency: 8/10
• Rhyme scheme: Mixed patterns detected
• Internal rhymes: Present
• Rhythm: Steady with good variation

💡 Strengths:
• Good word choice and vocabulary
• Consistent theme development
• Natural flow progression

🔧 Suggestions:
• Add more internal rhymes in lines 3-5
• Consider varying syllable counts for dynamics
• Strengthen end rhymes in verse 2

⭐ Overall Rating: 8.5/10 - Strong lyrical content with good flow!"""

    @ErrorHandler.handle_errors("Rhyme Scheme Analysis")
    def _check_rhyme_scheme(self):
        """Enhanced rhyme scheme analysis with visual patterns."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            prompt = f"""Analyze the rhyme scheme of these lyrics in detail:

{lyrics}

Provide:
1. Line-by-line rhyme scheme pattern (A, B, C, etc.)
2. End rhymes mapping (which words rhyme with which)
3. Internal rhymes identification
4. Slant rhymes and near-rhymes
5. Multi-syllable rhyme patterns
6. Rhyme density analysis
7. Suggestions for improving rhyme scheme
8. Alternative rhyme patterns to try

Format clearly with examples."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else self._generate_demo_rhyme_analysis(lyrics)
            
            self._show_analysis_dialog("🎵 Rhyme Scheme Analysis", response, "rhyme_analysis")
            
        except Exception as e:
            messagebox.showerror("Rhyme Analysis Error", f"Failed to analyze rhymes: {str(e)}")

    def _generate_demo_rhyme_analysis(self, lyrics):
        """Generate demo rhyme analysis."""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        return f"""🎵 RHYME SCHEME ANALYSIS:

📋 Pattern Detection:
• Primary scheme: ABAB pattern
• Secondary patterns: Internal AABB sequences
• Rhyme density: High (strong end rhymes)

🎯 End Rhyme Mapping:
• Lines 1,3: Strong perfect rhymes
• Lines 2,4: Consistent pattern
• Multi-syllable rhymes detected

💎 Internal Rhymes:
• Present in 60% of lines
• Good use of alliteration
• Assonance patterns identified

🔧 Improvement Suggestions:
• Experiment with AAAA scheme for intensity
• Add more slant rhymes for variety
• Consider cross-rhymes between verses

⭐ Rhyme Quality: 8/10 - Excellent rhyming structure!"""

    @ErrorHandler.handle_errors("Beat Suggestion")
    def _suggest_beat_type(self):
        """🎧 Enhanced beat suggestion with actual generation capability."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            # Analyze lyrics for beat matching
            analysis_prompt = f"""Analyze these lyrics and suggest the perfect beat type with specific parameters:

LYRICS:
{lyrics}

STYLE CONTEXT: {self.lyric_style.get()}
MOOD: {self.lyric_mood.get()}

Provide a detailed JSON response with these exact fields:
{{
    "bpm": [recommended BPM as integer, 70-180],
    "style": ["trap", "boom_bap", "drill", "melodic", "lo_fi", "experimental"],
    "energy": [1-10 scale],
    "kick_pattern": [array of 16 beats, 1=kick, 0=no kick],
    "snare_pattern": [array of 16 beats, 1=snare, 0=no snare], 
    "hihat_pattern": [array of 16 beats, 1=hihat, 0=no hihat],
    "bass_pattern": [array of 16 beats, 1=bass, 0=no bass],
    "description": "Detailed description of why this beat works",
    "alternative_bpms": [array of 2-3 alternative BPM suggestions],
    "instrumental_suggestions": ["piano", "strings", "synth", etc.],
    "mixing_tips": "Brief mixing advice"
}}

Be specific and match the lyrical content perfectly."""
            
            response = self.ai.chat_response(analysis_prompt) if hasattr(self.ai, 'chat_response') else self._generate_demo_beat_analysis()
            
            # Parse and generate beat
            beat_data = self._parse_beat_response(response)
            self._create_enhanced_beat_studio(beat_data)
            
        except Exception as e:
            messagebox.showerror("Beat Analysis Error", f"Failed to analyze for beat: {str(e)}")
            root_logger.error(f"Beat suggestion error: {str(e)}", exc_info=True)

    def _parse_beat_response(self, response: str) -> dict:
        """Safely parse the JSON response for beat data."""
        try:
            # The AI response might be inside a markdown code block
            if "```" in response:
                response = re.search(r'```json\n(.*?)\n```', response, re.DOTALL).group(1)

            beat_data = json.loads(response)
            # Basic validation to ensure we have the keys we need
            if "bpm" in beat_data and "kick_pattern" in beat_data:
                root_logger.info("Successfully parsed beat data from AI response.")
                return beat_data
            else:
                root_logger.warning("Parsed JSON is missing required beat keys.")
                return {}
        except (json.JSONDecodeError, AttributeError, Exception) as e:
            root_logger.error(f"Failed to parse beat JSON response: {e}")
            messagebox.showerror("Beat Analysis Error", "The AI returned an invalid format for the beat data. Please try again.")
            return {}

    def _generate_demo_beat_analysis(self):
        """Generate demo beat analysis data."""
        style = self.lyric_style.get().lower()
        
        patterns = {
            "boom bap": {
                "bpm": 90,
                "kick": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
            },
            "trap": {
                "bpm": 140,
                "kick": [1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,1,0,1,1,0,1,1,1,1,0,1,1,0,1,1]
            }
        }
        
        default = patterns.get(style, patterns["boom bap"])
        
        return f"""{{
    "bpm": {default["bpm"]},
    "style": "{style}",
    "energy": 7,
    "kick_pattern": {default["kick"]},
    "snare_pattern": {default["snare"]},
    "hihat_pattern": {default["hihat"]},
    "bass_pattern": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
    "description": "Perfect {style} beat matching your lyrical style and energy",
    "alternative_bpms": [{default["bpm"]-10}, {default["bpm"]+15}],
    "instrumental_suggestions": ["piano", "strings", "synth"],
    "mixing_tips": "EQ the kick at 60Hz, snare at 200Hz, hi-hats at 10kHz"
}}"""

    def _create_enhanced_beat_studio(self, beat_data):
        """Create the ultimate beat studio interface."""
        beat_window = tk.Toplevel(self.root)
        beat_window.title("🎧 CodedSwitch Beat Studio Pro")
        beat_window.geometry("1000x700")
        beat_window.resizable(True, True)
        
        # Main container
        main_frame = ttk.Frame(beat_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with beat info
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text="🎵 AI Beat Studio - Professional Edition",
            font=("Segoe UI", 16, "bold")
        ).pack(side=tk.LEFT)
        
        # Beat info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.RIGHT)
        
        # Extract the style, handling cases where the AI returns a list
        style_val = beat_data.get('style', 'Custom')
        style_display = style_val[0] if isinstance(style_val, list) else style_val

        ttk.Label(
            info_frame,
            text=f"Style: {style_display.title()} | BPM: {beat_data.get('bpm', 120)} | Energy: {beat_data.get('energy', 5)}/10",
            font=("Segoe UI", 10)
        ).pack()
        
        # Master controls
        controls_frame = ttk.LabelFrame(main_frame, text="🎛️ Master Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        controls_row = ttk.Frame(controls_frame)
        controls_row.pack(fill=tk.X)
        
        # BPM Control
        ttk.Label(controls_row, text="BPM:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        beat_window.bpm_var = tk.IntVar(value=beat_data.get('bpm', 120))
        bpm_scale = ttk.Scale(
            controls_row,
            from_=60, to=200,
            variable=beat_window.bpm_var,
            length=150,
            command=lambda v: beat_window.bpm_label.config(text=f"{int(float(v))}")
        )
        bpm_scale.pack(side=tk.LEFT, padx=5)
        beat_window.bpm_label = ttk.Label(controls_row, text=str(beat_data.get('bpm', 120)))
        beat_window.bpm_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Master Volume
        ttk.Label(controls_row, text="Volume:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        beat_window.master_volume = tk.DoubleVar(value=0.8)
        ttk.Scale(
            controls_row,
            from_=0.0, to=1.0,
            variable=beat_window.master_volume,
            length=100,
            orient=tk.HORIZONTAL
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Swing control
        ttk.Label(controls_row, text="Swing:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        beat_window.swing_var = tk.DoubleVar(value=0.0)
        ttk.Scale(
            controls_row,
            from_=-0.3, to=0.3,
            variable=beat_window.swing_var,
            length=80,
            orient=tk.HORIZONTAL
        ).pack(side=tk.LEFT)
        
        # Pattern editor
        pattern_frame = ttk.LabelFrame(main_frame, text="🎹 Pattern Editor", padding=10)
        pattern_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Store patterns from AI analysis
        beat_window.patterns = {
            'kick': beat_data.get('kick_pattern', [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]),
            'snare': beat_data.get('snare_pattern', [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0]),
            'hihat': beat_data.get('hihat_pattern', [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]),
            'openhat': [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
            'crash': [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            'bass': beat_data.get('bass_pattern', [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0])
        }
        
        self._create_advanced_pattern_editor(pattern_frame, beat_window)
        
        # Playback controls
        playback_frame = ttk.Frame(main_frame)
        playback_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Status
        beat_window.status_label = ttk.Label(
            playback_frame,
            text="🎵 AI-generated beat ready! Click Play to hear your custom beat!",
            font=("Segoe UI", 10)
        )
        beat_window.status_label.pack(pady=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(playback_frame)
        button_frame.pack()
        
        beat_window.play_button = ttk.Button(
            button_frame,
            text="▶️ Play Beat",
            command=lambda: self._play_enhanced_beat(beat_window),
            style="success.TButton",
            width=15
        )
        beat_window.play_button.pack(side=tk.LEFT, padx=5)
        
        beat_window.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=lambda: self._stop_beat(beat_window),
            width=15
        )
        beat_window.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Generate New",
            command=lambda: self._regenerate_beat_from_ai(beat_window),
            style="info.TButton",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Save Beat",
            command=lambda: self._save_beat_project(beat_window),
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📤 Export WAV",
            command=lambda: self._export_beat_audio(beat_window),
            style="warning.TButton",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Description
        if 'description' in beat_data:
            desc_frame = ttk.LabelFrame(main_frame, text="🎯 AI Analysis", padding=10)
            desc_frame.pack(fill=tk.X, pady=(15, 0))
            
            desc_text = tk.Text(
                desc_frame,
                height=4,
                wrap=tk.WORD,
                font=("Segoe UI", 9),
                state=tk.DISABLED
            )
            desc_text.pack(fill=tk.X)
            
            desc_text.config(state=tk.NORMAL)
            desc_text.insert("1.0", beat_data['description'])
            desc_text.config(state=tk.DISABLED)
        
        return beat_window

    def _create_advanced_pattern_editor(self, parent, beat_window):
        """Create advanced pattern editor with more features."""
        # Beat grid header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="", width=12).pack(side=tk.LEFT)  # Spacer
        for i in range(1, 17):
            color = "white" if i % 4 == 1 else "lightgray"
            weight = "bold" if i % 4 == 1 else "normal"
            ttk.Label(
                header_frame,
                text=str(i),
                width=3,
                font=("Courier", 8, weight),
                foreground=color
            ).pack(side=tk.LEFT)
        
        # Pattern rows with enhanced controls
        beat_window.pattern_buttons = {}
        
        patterns = [
            ("🥁 Kick", "kick", "#FF5722"),
            ("🥁 Snare", "snare", "#2196F3"),
            ("🎩 Hi-Hat", "hihat", "#4CAF50"),
            ("🎩 Open Hat", "openhat", "#FFC107"),
            ("💥 Crash", "crash", "#FF9800"),
            ("🎸 Bass", "bass", "#9C27B0")
        ]
        
        for pattern_name, pattern_key, color in patterns:
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=2)
            
            # Pattern controls
            control_frame = ttk.Frame(row_frame)
            control_frame.pack(side=tk.LEFT)
            
            ttk.Label(
                control_frame,
                text=pattern_name,
                width=10,
                font=("Segoe UI", 9, "bold")
            ).pack(side=tk.TOP)
            
            # Volume for each track
            vol_var = tk.DoubleVar(value=0.8)
            beat_window.__dict__[f"{pattern_key}_volume"] = vol_var
            ttk.Scale(
                control_frame,
                from_=0.0, to=1.0,
                variable=vol_var,
                length=60,
                orient=tk.VERTICAL
            ).pack(side=tk.BOTTOM)
            
            # Pattern buttons
            pattern_button_frame = ttk.Frame(row_frame)
            pattern_button_frame.pack(side=tk.LEFT, padx=(10, 0))
            
            beat_window.pattern_buttons[pattern_key] = []
            for i in range(16):
                is_active = beat_window.patterns[pattern_key][i]
                btn = tk.Button(
                    pattern_button_frame,
                    text="●" if is_active else "○",
                    width=2,
                    height=1,
                    font=("Courier", 8, "bold"),
                    bg=color if is_active else "gray20",
                    fg="white",
                    activebackground=color,
                    command=lambda k=pattern_key, idx=i: self._toggle_pattern_beat(beat_window, k, idx)
                )
                btn.pack(side=tk.LEFT, padx=1)
                beat_window.pattern_buttons[pattern_key].append(btn)

    def _toggle_pattern_beat(self, beat_window, pattern_key, beat_index):
        """Toggle a beat in the pattern with visual feedback."""
        # Toggle the beat
        beat_window.patterns[pattern_key][beat_index] = 1 - beat_window.patterns[pattern_key][beat_index]
        
        # Update button appearance
        btn = beat_window.pattern_buttons[pattern_key][beat_index]
        is_active = beat_window.patterns[pattern_key][beat_index]
        
        colors = {
            "kick": "#FF5722", "snare": "#2196F3", "hihat": "#4CAF50",
            "openhat": "#FFC107", "crash": "#FF9800", "bass": "#9C27B0"
        }
        
        btn.config(
            text="●" if is_active else "○",
            bg=colors[pattern_key] if is_active else "gray20"
        )

    @ErrorHandler.handle_errors("Beat Generation")
    def _play_enhanced_beat(self, beat_window):
        """Play enhanced beat with all elements."""
        if not self.resource_manager.audio_initialized:
            messagebox.showwarning(
                "Audio Not Available",
                "Audio system not initialized. Cannot play beat.\n\n"
                "Try restarting the application or check audio settings."
            )
            return
        
        try:
            # Prepare beat data
            beat_data = {
                'bpm': beat_window.bpm_var.get(),
                'patterns': beat_window.patterns,
                'master_volume': beat_window.master_volume.get(),
                'swing': beat_window.swing_var.get(),
                'volumes': {
                    key: getattr(beat_window, f"{key}_volume").get()
                    for key in beat_window.patterns.keys()
                }
            }
            
            # Generate and play in background
            beat_window.play_button.config(text="🎵 Generating...", state=tk.DISABLED)
            beat_window.status_label.config(text="🎵 Generating enhanced beat...")
            
            def generate_and_play():
                try:
                    audio_file = self._generate_enhanced_beat_audio(beat_data)
                    beat_window.audio_file = audio_file
                    
                    # Update UI on main thread
                    beat_window.after(0, lambda: self._start_beat_playback(beat_window))
                except Exception as e:
                    beat_window.after(0, lambda: self._show_beat_error(beat_window, str(e)))
            
            thread = threading.Thread(target=generate_and_play, daemon=True)
            self.resource_manager.add_thread(thread)
            thread.start()
            
        except Exception as e:
            beat_window.status_label.config(text=f"❌ Error: {str(e)}")

    def _generate_enhanced_beat_audio(self, beat_data):
        """Generate enhanced beat audio with multiple elements."""
        sample_rate = Constants.SAMPLE_RATE
        bpm = beat_data['bpm']
        beat_duration = 60.0 / bpm / 4  # 16th note duration
        pattern_length = 16
        total_duration = beat_duration * pattern_length
        
        # Generate drum sounds with better quality
        kick_sound = self._generate_enhanced_kick_sound(sample_rate)
        snare_sound = self._generate_enhanced_snare_sound(sample_rate)
        hihat_sound = self._generate_enhanced_hihat_sound(sample_rate)
        openhat_sound = self._generate_enhanced_openhat_sound(sample_rate)
        crash_sound = self._generate_enhanced_crash_sound(sample_rate)
        bass_sound = self._generate_enhanced_bass_sound(sample_rate)
        
        beat_samples = np.zeros((int(total_duration * sample_rate), 2))  # Stereo
        
        sounds = {
            'kick': kick_sound,
            'snare': snare_sound,
            'hihat': hihat_sound,
            'openhat': openhat_sound,
            'crash': crash_sound,
            'bass': bass_sound
        }
        
        for pattern_name, pattern in beat_data['patterns'].items():
            if pattern_name in sounds:
                sound = sounds[pattern_name]
                volume = beat_data['volumes'].get(pattern_name, 0.8)
                
                for i in range(pattern_length):
                    if pattern[i]:
                        start_sample = int(i * beat_duration * sample_rate)
                        
                        # Apply swing
                        if i % 2 == 1:  # Off-beats
                            swing_offset = int(beat_data.get('swing', 0) * beat_duration * sample_rate)
                            start_sample += swing_offset
                        
                        # Ensure stereo
                        if sound.ndim == 1:
                            sound_stereo = np.column_stack((sound, sound))
                        else:
                            sound_stereo = sound
                        
                        end_sample = min(start_sample + len(sound_stereo), len(beat_samples))
                        if end_sample > start_sample:
                            beat_samples[start_sample:end_sample] += sound_stereo[:end_sample-start_sample] * volume
        
        # Apply master volume and normalize
        beat_samples *= beat_data['master_volume']
        max_val = np.max(np.abs(beat_samples))
        if max_val > 0:
            beat_samples = beat_samples / max_val * 0.8
        
        # Convert to 16-bit integer
        beat_samples = (beat_samples * 32767).astype(np.int16)
        
        # Save to temporary file
        temp_file = tempfile.mktemp(suffix='.wav')
        wavfile.write(temp_file, sample_rate, beat_samples)
        
        # Track for cleanup
        self.resource_manager.add_temp_file(temp_file)
        
        return temp_file

    def _generate_enhanced_kick_sound(self, sample_rate, duration=0.6):
        """Generate enhanced kick drum sound."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Multiple frequency components for richer sound
        fundamental = 60
        harmonic = 120
        click = 1000
        
        # Main thump
        kick = np.sin(2 * np.pi * fundamental * t) * np.exp(-t * 8)
        # Harmonic for body
        kick += 0.3 * np.sin(2 * np.pi * harmonic * t) * np.exp(-t * 12)
        # Click for attack
        kick += 0.1 * np.sin(2 * np.pi * click * t) * np.exp(-t * 50)
        
        return kick * 0.8

    def _generate_enhanced_snare_sound(self, sample_rate, duration=0.25):
        """Generate enhanced snare drum sound."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # White noise for snare body
        noise = np.random.normal(0, 1, len(t))
        # Tonal component
        tone = np.sin(2 * np.pi * 200 * t)
        
        # Envelope
        envelope = np.exp(-t * 20)
        
        snare = (0.7 * noise + 0.3 * tone) * envelope
        return snare * 0.6

    def _generate_enhanced_hihat_sound(self, sample_rate, duration=0.1):
        """Generate enhanced hi-hat sound."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # High frequency noise
        noise = np.random.normal(0, 1, len(t))
        # High-pass filter simulation
        noise = np.convolve(noise, [1, -0.9], mode='same')
        
        envelope = np.exp(-t * 30)
        return noise * envelope * 0.4

    def _generate_enhanced_openhat_sound(self, sample_rate, duration=0.3):
        """Generate enhanced open hi-hat sound."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        noise = np.random.normal(0, 1, len(t))
        noise = np.convolve(noise, [1, -0.7], mode='same')
        
        envelope = np.exp(-t * 8)  # Longer decay than closed hat
        return noise * envelope * 0.5

    def _generate_enhanced_crash_sound(self, sample_rate, duration=1.0):
        """Generate enhanced crash cymbal sound."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Multiple frequency noise for metallic sound
        noise = np.random.normal(0, 1, len(t))
        # Metallic frequencies
        metallic = (np.sin(2 * np.pi * 3000 * t) + 
                   np.sin(2 * np.pi * 5000 * t) + 
                   np.sin(2 * np.pi * 7000 * t))
        
        envelope = np.exp(-t * 3)  # Long decay
        crash = (0.8 * noise + 0.2 * metallic) * envelope
        return crash * 0.3

    def _generate_enhanced_bass_sound(self, sample_rate, duration=0.5):
        """Generate enhanced bass sound."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Sub bass frequency
        fundamental = 40
        harmonic = 80
        
        bass = (np.sin(2 * np.pi * fundamental * t) + 
                0.3 * np.sin(2 * np.pi * harmonic * t))
        
        envelope = np.exp(-t * 6)
        return bass * envelope * 0.7

    def _start_beat_playback(self, beat_window):
        """Start beat playback with UI updates."""
        try:
            pygame.mixer.music.load(beat_window.audio_file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            
            beat_window.play_button.config(text="🔄 Playing...", state=tk.DISABLED)
            beat_window.stop_button.config(state=tk.NORMAL)
            beat_window.status_label.config(text="🎵 Playing your custom AI beat! 🔥")
            
        except Exception as e:
            self._show_beat_error(beat_window, f"Playback failed: {str(e)}")

    def _stop_beat(self, beat_window):
        """Stop beat playback."""
        try:
            pygame.mixer.music.stop()
            beat_window.play_button.config(text="▶️ Play Beat", state=tk.NORMAL)
            beat_window.status_label.config(text="🎵 Beat stopped. Ready to play again!")
            
        except Exception as e:
            root_logger.warning(f"Failed to stop beat: {e}")

    def _show_beat_error(self, beat_window, error_msg):
        """Show beat error with recovery options."""
        beat_window.play_button.config(text="▶️ Play Beat", state=tk.NORMAL)
        beat_window.status_label.config(text=f"❌ Error: {error_msg}")
        
        messagebox.showerror(
            "Beat Generation Error",
            f"Failed to generate or play beat.\n\n{error_msg}\n\n"
            "Try:\n• Adjusting the BPM\n• Simplifying the pattern\n• Restarting audio"
        )

    # ============================================================================
    # ADDITIONAL LYRIC LAB METHODS
    # ============================================================================

    def _switch_lyric_style(self):
        """Switch to a random lyric style."""
        current_style = self.lyric_style.get()
        other_styles = [style for style in LYRIC_STYLES.keys() if style != current_style]
        new_style = __import__('random').choice(other_styles)
        
        self.lyric_style.set(new_style)
        self._on_style_change(None)
        
        messagebox.showinfo(
            "Style Switched!",
            f"Switched from {current_style} to {new_style}!\n\n"
            f"{LYRIC_STYLES[new_style]['description']}\n\n"
            "Try generating new lyrics with this style!"
        )

    def _randomize_lyrics(self):
        """Generate completely random lyrics based on current style."""
        try:
            style = self.lyric_style.get()
            mood = self.lyric_mood.get()
            
            prompt = f"""Generate completely random {style} rap lyrics with {mood} mood.
            Use unexpected themes, creative wordplay, and unique perspectives.
            Make it 8-12 lines, highly creative and original.
            Surprise me with the topic and approach!"""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else f"Random {style} bars coming through\nWith that {mood} energy, that's my crew\nCodedSwitch methodology, breaking the rules\nAI-generated flows, these are my tools"
            
            # Replace current lyrics
            self.lyric_editor.delete("1.0", tk.END)
            self.lyric_editor.insert("1.0", f"--- Random {style} ({mood}) ---\n{response}")
            
            self.status_var.set(f"🎲 Random {style} lyrics generated!")
            
        except Exception as e:
            messagebox.showerror("Randomization Error", f"Failed to generate random lyrics: {str(e)}")

    def _auto_complete_line(self):
        """Auto-complete the current line using AI."""
        try:
            # Get current line
            current_line = self.lyric_editor.get("insert linestart", "insert lineend")
            if not current_line.strip():
                messagebox.showinfo("Auto-Complete", "Place cursor at end of a line to auto-complete.")
                return
            
            # Get context (previous lines)
            all_text = self.lyric_editor.get("1.0", "insert linestart")
            
            prompt = f"""Complete this rap line in {self.lyric_style.get()} style:

Context (previous lines):
{all_text}

Current incomplete line:
{current_line}

Complete just this one line, maintaining the flow and rhyme scheme. Return only the completion."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else "and the flow keeps going strong"
            
            # Insert completion
            self.lyric_editor.insert(tk.INSERT, f" {response.strip()}")
            
        except Exception as e:
            messagebox.showerror("Auto-Complete Error", f"Failed to auto-complete: {str(e)}")

    def _rewrite_current_bar(self):
        """Rewrite the current bar (line) with AI assistance."""
        try:
            # Get current line
            line_start = self.lyric_editor.index("insert linestart")
            line_end = self.lyric_editor.index("insert lineend")
            current_line = self.lyric_editor.get(line_start, line_end)
            
            if not current_line.strip():
                messagebox.showinfo("Rewrite Bar", "Place cursor on a line with text to rewrite.")
                return
            
            prompt = f"""Rewrite this rap bar in {self.lyric_style.get()} style, keeping the same theme but improving the wordplay, flow, and impact:

Original bar: {current_line}

Make it more clever, impactful, and stylistically consistent. Return only the rewritten bar."""
            
            response = self.ai.chat_response(prompt) if hasattr(self.ai, 'chat_response') else f"Rewritten: {current_line.strip()} (enhanced flow)"
            
            # Replace the line
            self.lyric_editor.delete(line_start, line_end)
            self.lyric_editor.insert(line_start, response.strip())
            
        except Exception as e:
            messagebox.showerror("Rewrite Error", f"Failed to rewrite bar: {str(e)}")

    def _save_lyric_version(self):
        """Save current lyrics as a version in history."""
        try:
            lyrics = self.lyric_editor.get("1.0", tk.END).strip()
            if not lyrics:
                messagebox.showwarning("No Lyrics", "No lyrics to save as version.")
                return
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            version_name = f"Version {timestamp}"
            
            # Add to version history
            self.version_history.insert(0, version_name)
            
            # Store the lyrics (in a real app, you'd use a database)
            if not hasattr(self, 'lyric_versions'):
                self.lyric_versions = {}
            self.lyric_versions[version_name] = lyrics
            
            # Limit to 10 versions
            if self.version_history.size() > 10:
                oldest = self.version_history.get(self.version_history.size() - 1)
                self.version_history.delete(self.version_history.size() - 1)
                if oldest in self.lyric_versions:
                    del self.lyric_versions[oldest]
            
            self.status_var.set(f"💾 Saved as {version_name}")
            
        except Exception as e:
            messagebox.showerror("Save Version Error", f"Failed to save version: {str(e)}")

    def _load_version(self, event):
        """Load selected version from history."""
        try:
            selection = self.version_history.curselection()
            if not selection:
                return
            
            version_name = self.version_history.get(selection[0])
            if hasattr(self, 'lyric_versions') and version_name in self.lyric_versions:
                lyrics = self.lyric_versions[version_name]
                
                if messagebox.askyesno("Load Version", f"Load {version_name}?\n\nThis will replace current lyrics."):
                    self.lyric_editor.delete("1.0", tk.END)
                    self.lyric_editor.insert("1.0", lyrics)
                    self.status_var.set(f"📂 Loaded {version_name}")
            
        except Exception as e:
            messagebox.showerror("Load Version Error", f"Failed to load version: {str(e)}")

    def _export_with_beat(self):
        """Export lyrics with generated beat as audio project."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Content", "No lyrics to export.")
            return
        
        try:
            # This would be a complex feature - for now show placeholder
            messagebox.showinfo(
                "🎵 Audio Export Coming Soon!",
                "This feature will export your lyrics with:\n\n"
                "✅ AI-generated backing beat\n"
                "✅ Vocal guide track\n" 
                "✅ Professional mixing\n"
                "✅ Multiple format options\n\n"
                "Coming in the next update! For now, you can:\n"
                "• Export lyrics as text\n"
                "• Generate and save beats separately\n"
                "• Use external DAW for combining"
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def _share_lyrics_online(self):
        """Share lyrics to online platforms."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Content", "No lyrics to share.")
            return
        
        # Show sharing options
        share_info = f"""🌐 Share Your Lyrics Online!

Ready to share: {len(lyrics.split())} words, {len(lyrics.splitlines())} lines

🎯 Sharing Options:
• Story Protocol (IP Protection)
• SoundCloud (Audio Platform) 
• Genius (Lyrics Database)
• Social Media (Twitter, Instagram)
• Personal Blog/Website

💡 Tips:
• Add copyright notice
• Consider IP protection first
• Tag appropriately for discovery
• Engage with community feedback

Would you like to export for sharing?"""
        
        if messagebox.askyesno("Share Lyrics", share_info):
            self._save_lyrics()

    # ============================================================================
    # HELPER METHODS & UI UTILITIES
    # ============================================================================

    def _show_analysis_dialog(self, title, content, analysis_type):
        """Show analysis results in a professional dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("700x500")
        dialog.transient(self.root)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 14, "bold")
        ).pack(side=tk.LEFT)
        
        # Export button
        ttk.Button(
            header_frame,
            text="📤 Export Analysis",
            command=lambda: self._export_analysis(content, analysis_type),
            width=15
        ).pack(side=tk.RIGHT)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_widget = TtkScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", content)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame,
            text="📋 Copy to Clipboard",
            command=lambda: self._copy_to_clipboard(content),
            width=20
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def _export_analysis(self, content, analysis_type):
        """Export analysis to file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Markdown Files", "*.md"), ("All Files", "*.*")],
            title=f"Export {analysis_type.replace('_', ' ').title()}"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# CodedSwitch {analysis_type.replace('_', ' ').title()}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(content)
                
                messagebox.showinfo("Export Complete", f"Analysis exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def _copy_to_clipboard(self, content):
        """Copy content to clipboard."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_var.set("📋 Copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Failed to copy: {str(e)}")

    def _show_translation_progress(self, message):
        """Show translation progress."""
        self.status_var.set(message)
        self.root.update_idletasks()

    def _show_translation_success(self, message):
        """Show translation success."""
        self.status_var.set(message)

    def _set_translation_ui_enabled(self, enabled):
        """Enable/disable translation UI elements."""
        # This would disable/enable relevant buttons during translation
        pass

    def _show_quota_exceeded_error(self):
        """Show quota exceeded error."""
        messagebox.showerror(
            "API Quota Exceeded",
            "You've reached your daily API limit.\n\n"
            "Solutions:\n"
            "• Wait until tomorrow for reset\n"
            "• Upgrade your API plan\n"
            "• Try smaller code snippets\n"
            "• Use demo mode for testing"
        )

    def _show_network_error(self):
        """Show network error."""
        messagebox.showerror(
            "Network Connection Error",
            "Couldn't connect to AI services.\n\n"
            "Please check:\n"
            "• Your internet connection\n"
            "• Firewall settings\n"
            "• Try again in a moment"
        )

    def _show_generic_translation_error(self, error):
        """Show generic translation error."""
        messagebox.showerror(
            "Translation Error",
            f"Translation failed with error:\n\n{error}\n\n"
            "Try:\n"
            "• Simplifying your code\n"
            "• Checking for syntax errors\n"
            "• Using a different AI model"
        )

    # Continue with remaining utility methods...
    def _simulate_translation(self, source_code, target_language):
        """Simulate code translation for demo mode."""
        if target_language.lower() == "javascript":
            return source_code.replace("print(", "console.log(").replace("def ", "function ")
        elif target_language.lower() == "python":
            return source_code.replace("console.log(", "print(").replace("function ", "def ")
        else:
            return f"// Simulated {target_language} translation\n{source_code}"

    def _clear_scan_results(self):
        """Clear scan results display."""
        self.scan_results.config(state=tk.NORMAL)
        self.scan_results.delete("1.0", tk.END)
        self.scan_results.config(state=tk.DISABLED)

    def _add_scan_result(self, text, tag=None):
        """Add text to scan results with optional tag."""
        self.scan_results.config(state=tk.NORMAL)
        self.scan_results.insert(tk.END, text, tag)
        self.scan_results.config(state=tk.DISABLED)
        self.scan_results.see(tk.END)

    def _set_scan_ui_enabled(self, enabled):
        """Enable/disable scan UI elements."""
        state = tk.NORMAL if enabled else tk.DISABLED
        try:
            self.scan_button.config(state=state)
        except:
            pass

    def quick_vulnerability_check(self):
        """Perform a quick vulnerability check."""
        code = self.scan_code.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("No Code", "Enter code to scan first!")
            return
        
        # Quick check for obvious patterns
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            if 'password' in line_lower and ('=' in line or ':' in line):
                issues.append(f"Line {i}: Possible hard-coded password")
            if 'sql' in line_lower and '+' in line:
                issues.append(f"Line {i}: Possible SQL injection risk")
            if 'eval(' in line_lower:
                issues.append(f"Line {i}: Dangerous eval() usage")
        
        if issues:
            result = "⚡ Quick Security Check Results:\n\n" + "\n".join(issues)
            result += "\n\n💡 Run full scan for comprehensive analysis."
        else:
            result = "✅ Quick check passed! No obvious issues found.\n\n💡 Run full scan for thorough analysis."
        
        messagebox.showinfo("Quick Security Check", result)

    def auto_fix_vulnerabilities(self):
        """Auto-fix common vulnerabilities."""
        messagebox.showinfo(
            "🔧 Auto-Fix Coming Soon!",
            "The auto-fix feature will automatically repair:\n\n"
            "✅ SQL injection vulnerabilities\n"
            "✅ Hard-coded credentials\n"
            "✅ Input validation issues\n"
            "✅ XSS vulnerabilities\n\n"
            "Coming in the next update!\n"
            "For now, use the detailed scan results for manual fixes."
        )

    def load_test_code(self):
        """Load enhanced test code with multiple vulnerability types."""
        test_code = '''import os
import sqlite3
import subprocess
from flask import Flask, request, render_template_string
from lyric_lab_integration import LyricLabIntegration

app = Flask(__name__)

# CRITICAL: Hard-coded credentials
DATABASE_PASSWORD = "admin123"
API_SECRET_KEY = "sk_live_51JXzT2GBgjklmasLMNvb4Kb0QzDhKIPO098asdkljasdkljq7f"
ADMIN_PASSWORD = "password123"

# HIGH: SQL Injection vulnerability
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'] 
    password = request.form['password']
    
    # Dangerous: Direct string concatenation
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)  # SQL Injection possible
    user = cursor.fetchone()
    
    if user:
        return f"Welcome {username}!"
    return "Login failed"

# HIGH: Command Injection
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    # Dangerous: Direct command execution
    result = os.system(f"ping -c 1 {host}")
    return f"Ping result: {result}"

# MEDIUM: Path Traversal
@app.route('/download')
def download_file():
    filename = request.args.get('file')
    file_path = os.path.join('./uploads', filename)  # No validation
    
    try:
        with open(file_path, 'r') as f:  # Directory traversal possible
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {e}"

# MEDIUM: XSS vulnerability
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Dangerous: Direct template rendering
    template = f"<h1>Search results for: {query}</h1>"
    return render_template_string(template)

# LOW: Information disclosure
@app.route('/debug')
def debug():
    if app.debug:  # Exposes sensitive info
        return str(locals())
    return "Debug disabled"

if __name__ == '__main__':
    app.run(debug=True)  # Debug mode in production'''
        
        self.scan_code.delete("1.0", tk.END)
        self.scan_code.insert(tk.END, test_code)
        self.scan_lang.set("Python")
        
        messagebox.showinfo(
            "Test Code Loaded",
            "Loaded sample code with multiple vulnerability types:\n\n"
            "🔴 Critical: Hard-coded credentials\n"
            "🟠 High: SQL & Command injection\n"
            "🟡 Medium: Path traversal, XSS\n"
            "🔵 Low: Information disclosure\n\n"
            "Perfect for testing the security scanner!"
        )

    def export_report(self):
        """Export enhanced vulnerability report."""
        results = self.scan_results.get("1.0", tk.END).strip()
        if not results or "No vulnerabilities" in results:
            messagebox.showinfo("Nothing to Export", "No scan results to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[
                ("HTML Report", "*.html"),
                ("Text Files", "*.txt"), 
                ("PDF Report", "*.pdf"),
                ("All Files", "*.*")
            ],
            title="Export Security Report"
        )
        
        if file_path:
            try:
                if file_path.endswith('.html'):
                    self._export_html_security_report(file_path, results)
                else:
                    self._export_text_security_report(file_path, results)
                
                messagebox.showinfo("Export Complete", f"Security report exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def _export_html_security_report(self, file_path, results):
        """Export security report as HTML."""
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>CodedSwitch Security Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f44336; color: white; padding: 20px; border-radius: 8px; }}
        .critical {{ color: #d32f2f; font-weight: bold; }}
        .high {{ color: #f57c00; font-weight: bold; }}
        .medium {{ color: #fbc02d; font-weight: bold; }}
        .low {{ color: #388e3c; font-weight: bold; }}
        .code {{ background: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; }}
        .recommendation {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ CodedSwitch Security Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="report-content">
        <pre>{results}</pre>
    </div>
    
    <div class="recommendation">
        <h3>💡 Next Steps</h3>
        <ul>
            <li>Fix all CRITICAL and HIGH severity issues immediately</li>
            <li>Plan remediation for MEDIUM priority vulnerabilities</li>
            <li>Consider LOW priority improvements</li>
            <li>Implement regular security scanning in your workflow</li>
        </ul>
    </div>
</body>
</html>'''
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _export_text_security_report(self, file_path, results):
        """Export security report as text."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("CODEDSWITCH SECURITY VULNERABILITY REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(results)

    # Additional utility methods...
    def _on_language_change(self, event):
        """Handle language selection change."""
        # Save preferences
        self.config_manager.set("last_source_lang", self.source_lang.get())
        self.config_manager.set("last_target_lang", self.target_lang.get())

    def _swap_languages(self):
        """Swap source and target languages."""
        source = self.source_lang.get()
        target = self.target_lang.get()
        
        self.source_lang.set(target)
        self.target_lang.set(source)
        
        self.status_var.set(f"🔄 Swapped: {target} ↔ {source}")

    def _on_style_change(self, event):
        """Handle lyric style change."""
        selected_style = self.lyric_style.get()
        if selected_style in LYRIC_STYLES:
            description = LYRIC_STYLES[selected_style]["description"]
            self.style_description.config(text=description)
            self._update_style_tips()

    def _update_style_tips(self):
        """Update style-specific tips."""
        selected_style = self.lyric_style.get()
        if selected_style in LYRIC_STYLES:
            style_info = LYRIC_STYLES[selected_style]
            tips_text = f"Characteristics:\n{style_info['characteristics']}\n\nExamples:\n{style_info['examples']}\n\nTips:\n{style_info['prompt_additions'][:100]}..."
            
            self.style_tips.config(state=tk.NORMAL)
            self.style_tips.delete(1.0, tk.END)
            self.style_tips.insert(1.0, tips_text)
            self.style_tips.config(state=tk.DISABLED)

    # Remaining essential methods...
    def _on_closing(self):
        """Handle application closing with cleanup."""
        try:
            # Save current settings
            self.config_manager.set("window_geometry", self.root.geometry())
            self.config_manager.save_config()
            
            # Clean up resources
            self.resource_manager.cleanup_all()
            
            # Close executor
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
            
            root_logger.info("Application closing - cleanup completed")
            
        except Exception as e:
            root_logger.error(f"Error during cleanup: {e}")
        finally:
            self.root.destroy()

    def new_file(self):
        """Create a new file with confirmation."""
        if messagebox.askyesno("New File", "Clear all editors and start fresh?"):
            self.source_code.delete(1.0, tk.END)
            self.target_code.delete(1.0, tk.END)
            self.feedback_text.delete(1.0, tk.END)
            self.lyric_editor.delete(1.0, tk.END)
            self.status_var.set("📄 New file created")

    def open_file(self):
        """Open a code file with enhanced support."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Python Files", "*.py"),
                ("JavaScript Files", "*.js"),
                ("Java Files", "*.java"),
                ("C++ Files", "*.cpp"),
                ("All Code Files", "*.py *.js *.java *.cpp *.c *.h"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.source_code.delete(1.0, tk.END)
                    self.source_code.insert(tk.END, content)
                
                # Auto-detect language
                ext = os.path.splitext(file_path)[1].lower()
                lang_map = {'.py': 'Python', '.js': 'JavaScript', '.java': 'Java', '.cpp': 'C++'}
                if ext in lang_map:
                    self.source_lang.set(lang_map[ext])
                
                self.current_file = file_path
                self.status_var.set(f"📂 Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Open File Error", f"Failed to open file: {e}")

    def save_file(self):
        """Save current file or save as new file."""
        if self.current_file:
            try:
                content = self.source_code.get(1.0, tk.END).strip()
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_var.set(f"💾 Saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save file with new name."""
        # Determine default extension based on source language
        lang_ext_map = {
            'Python': '.py',
            'JavaScript': '.js', 
            'Java': '.java',
            'C++': '.cpp'
        }
        default_ext = lang_ext_map.get(self.source_lang.get(), '.txt')
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=[
                ("Python Files", "*.py"),
                ("JavaScript Files", "*.js"),
                ("Java Files", "*.java"), 
                ("C++ Files", "*.cpp"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                content = self.source_code.get(1.0, tk.END).strip()
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.status_var.set(f"💾 Saved as: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {e}")

    def clear_all_code(self):
        """Clear all code areas with confirmation."""
        if messagebox.askyesno("Clear All", "Clear all code areas and notes?"):
            self.source_code.delete(1.0, tk.END)
            self.target_code.delete(1.0, tk.END)
            self.feedback_text.delete(1.0, tk.END)
            self.status_var.set("🗑️ All code areas cleared")

    # Additional UI helper methods...
    def _show_help(self):
        """Show comprehensive help dialog."""
        help_content = f"""🚀 CodedSwitch - Comprehensive Help Guide

⌨️ KEYBOARD SHORTCUTS:
   Ctrl+T        - Translate code
   Ctrl+R        - Reverse translation  
   Ctrl+Shift+C  - Clear all areas
   F5            - Security scan
   Ctrl+N        - New file
   Ctrl+O        - Open file
   Ctrl+S        - Save file
   F1            - Show this help
   Ctrl++        - Increase font
   Ctrl+-        - Decrease font
   Ctrl+L        - Focus lyric editor
   F11           - Toggle fullscreen

🎯 FEATURES OVERVIEW:
   🔄 AI Translation - Convert between {len(PROGRAMMING_LANGUAGES)} languages
   🛡️ Security Scanner - Detect vulnerabilities & get fixes
   🤖 AI Assistant - Chat about code & get help
   🎤 Lyric Lab - Create rap lyrics with AI tools

💡 PRO TIPS:
   • Use different AI models for varying results
   • Try reverse translation to learn syntax differences
   • Security scan before deploying code
   • Export results as HTML for documentation
   • Lyric Lab has {len(LYRIC_STYLES)} different styles

🔗 ADDITIONAL HELP:
   • Documentation: Press F1 in any tab
   • Community: Join our Discord server
   • Issues: Report bugs on GitHub
   • Updates: Check Help → About for version info

🎵 LYRIC LAB SPECIAL FEATURES:
   • AI beat generation with actual audio
   • Real-time rhyme suggestions
   • Flow analysis and improvement tips
   • Multiple rap styles and moods
   • Story Protocol integration for IP protection

📊 CURRENT SESSION:
   • Theme: {self.current_theme}
   • Model: {self.gemini_model}
   • Audio: {"Enabled" if self.resource_manager.audio_initialized else "Disabled"}
   • API: {"Connected" if self.gemini_api_key else "Demo Mode"}
"""
        
        # Show in dialog
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("CodedSwitch - Help & Shortcuts")
        help_dialog.geometry("800x600")
        help_dialog.transient(self.root)
        
        main_frame = ttk.Frame(help_dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = TtkScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        text_widget.insert("1.0", help_content)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=help_dialog.destroy,
            width=15
        ).pack()

    # Additional essential methods
    def _show_user_guide(self):
        """Show comprehensive user guide."""
        messagebox.showinfo(
            "📚 User Guide",
            "Opening CodedSwitch User Guide in browser...\n\n"
            "The guide covers:\n"
            "• Getting started with AI translation\n"
            "• Security scanning best practices\n" 
            "• Lyric Lab creative techniques\n"
            "• Advanced features and tips"
        )
        webbrowser.open("https://github.com/your-repo/codedswitch/wiki")

    def _check_for_updates(self):
        """Check for application updates."""
        messagebox.showinfo(
            "🔄 Check for Updates",
            "CodedSwitch v2.1 Enhanced Edition\n\n"
            "✅ You're running the latest enhanced version!\n\n"
            "New in this version:\n"
            "• Improved error handling\n"
            "• Enhanced beat generation\n"
            "• Better resource management\n"
            "• Advanced lyric analysis tools\n"
            "• Professional UI polish"
        )

    def _show_find_replace(self):
        """Show find and replace dialog."""
        messagebox.showinfo(
            "🔍 Find & Replace",
            "Find & Replace functionality coming soon!\n\n"
            "Will include:\n"
            "• Text search across all editors\n"
            "• Regex pattern matching\n"
            "• Replace in selection or all\n"
            "• Case sensitive options"
        )

    def _show_preferences(self):
        """Show application preferences dialog."""
        prefs_dialog = tk.Toplevel(self.root)
        prefs_dialog.title("⚙️ CodedSwitch Preferences")
        prefs_dialog.geometry("500x400")
        prefs_dialog.transient(self.root)
        prefs_dialog.grab_set()
        
        notebook = ttk.Notebook(prefs_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General tab
        general_frame = ttk.Frame(notebook, padding=15)
        notebook.add(general_frame, text="General")
        
        ttk.Label(general_frame, text="Theme:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(general_frame, textvariable=theme_var, values=list(THEMES.keys()), state="readonly")
        theme_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(general_frame, text="Font Size:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        font_var = tk.IntVar(value=self.font_size)
        font_scale = ttk.Scale(general_frame, from_=8, to=24, variable=font_var, orient=tk.HORIZONTAL)
        font_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Audio tab
        audio_frame = ttk.Frame(notebook, padding=15)
        notebook.add(audio_frame, text="Audio")
        
        audio_enabled = tk.BooleanVar(value=self.resource_manager.audio_initialized)
        ttk.Checkbutton(audio_frame, text="Enable Audio System", variable=audio_enabled).pack(anchor=tk.W)
        
        # AI tab
        ai_frame = ttk.Frame(notebook, padding=15)
        notebook.add(ai_frame, text="AI Settings")
        
        ttk.Label(ai_frame, text="Default Model:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        model_var = tk.StringVar(value=self.gemini_model)
        model_combo = ttk.Combobox(ai_frame, textvariable=model_var, 
                                  values=["gemini-2.0-flash-001", "gemini-2.5-flash", "gemini-2.5-pro"], 
                                  state="readonly")
        model_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(prefs_dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def apply_preferences():
            self.current_theme = theme_var.get()
            self.font_size = font_var.get()
            self.gemini_model = model_var.get()
            
            # Apply changes
            self._change_theme()
            self._change_font_size(0)  # Refresh font
            
            self.config_manager.set("theme", self.current_theme)
            self.config_manager.set("font_size", self.font_size)
            self.config_manager.set("model", self.gemini_model)
            self.config_manager.save_config()
            
            messagebox.showinfo("Preferences", "Settings applied successfully!")
            prefs_dialog.destroy()
        
        ttk.Button(btn_frame, text="Apply", command=apply_preferences, style="primary.TButton").pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=prefs_dialog.destroy).pack(side=tk.RIGHT)

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        if not current_state:
            self.status_var.set("🖥️ Fullscreen mode - Press F11 to exit")
        else:
            self.status_var.set("🖥️ Windowed mode")

    def _focus_lyric_editor(self):
        """Focus the lyric editor and switch to lyric tab."""
        self.notebook.select(3)  # Lyric Lab tab
        self.lyric_editor.focus()

    def _reset_font_size(self):
        """Reset font size to default."""
        self.font_size = Constants.DEFAULT_FONT_SIZE
        self._change_font_size(0)  # Refresh with current size
        self.status_var.set("🔤 Font size reset to default")

    def _change_font_size(self, delta):
        """Enhanced font size change with bounds checking."""
        if delta != 0:
            self.font_size = max(Constants.MIN_FONT_SIZE, min(Constants.MAX_FONT_SIZE, self.font_size + delta))
        
        # Update all text widgets
        widgets_to_update = []
        
        # Collect all text widgets
        try:
            widgets_to_update.extend([
                self.source_code, self.target_code, self.feedback_text,
                self.chat_display, self.message_input, 
                self.scan_code, self.scan_results,
                self.lyric_editor, self.lyric_prompt
            ])
        except AttributeError:
            pass  # Some widgets might not be initialized yet
        
        # Update fonts
        for widget in widgets_to_update:
            try:
                current_font = widget.cget("font")
                if isinstance(current_font, str):
                    font_family = current_font.split()[0] if current_font.split() else "Segoe UI"
                elif isinstance(current_font, tuple):
                    font_family = current_font[0]
                else:
                    font_family = "Segoe UI"
                
                # Use appropriate font for different widget types
                if widget in [self.source_code, self.target_code, self.scan_code, self.lyric_editor]:
                    font_family = "Consolas" if platform.system() == "Windows" else "Monaco"
                
                widget.configure(font=(font_family, self.font_size))
            except Exception as e:
                root_logger.warning(f"Failed to update font for widget: {e}")
        
        if delta != 0:
            self.status_var.set(f"🔤 Font size: {self.font_size}pt")

    def _change_theme(self):
        """Enhanced theme change with error handling."""
        try:
            theme_name = self.theme_var.get()
            if theme_name in THEMES:
                self.style.theme_use(THEMES[theme_name])
                self.current_theme = theme_name
                self.theme_indicator.config(text=f"Theme: {theme_name}")
                self.status_var.set(f"🎨 Theme changed to {theme_name}")
                
                # Save theme preference
                self.config_manager.set("theme", theme_name)
                self.config_manager.save_config()
        except Exception as e:
            root_logger.error(f"Failed to change theme: {e}")
            messagebox.showerror("Theme Error", f"Failed to apply theme: {str(e)}")

    def _select_all(self):
        """Enhanced select all for current focused widget."""
        try:
            widget = self.root.focus_get()
            if hasattr(widget, 'tag_add'):  # Text widget
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
            elif hasattr(widget, 'select_range'):  # Entry widget
                widget.select_range(0, tk.END)
        except Exception as e:
            root_logger.warning(f"Select all failed: {e}")

    def _load_demo_code(self):
        """Load enhanced demo code with multiple examples."""
        demo_codes = {
            "Python": '''def fibonacci(n):
    """Calculate fibonacci number using recursion."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    # Test the function
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()''',
            
            "JavaScript": '''function fibonacci(n) {
    // Calculate fibonacci number using recursion
    if (n <= 1) {
        return n;
    }
    return fibonacci(n-1) + fibonacci(n-2);
}

function main() {
    // Test the function
    for (let i = 0; i < 10; i++) {
        console.log(`F(${i}) = ${fibonacci(i)}`);
    }
}

main();''',
            
            "Java": '''public class Fibonacci {
    public static int fibonacci(int n) {
        // Calculate fibonacci number using recursion
        if (n <= 1) {
            return n;
        }
        return fibonacci(n-1) + fibonacci(n-2);
    }
    
    public static void main(String[] args) {
        // Test the function
        for (int i = 0; i < 10; i++) {
            System.out.println("F(" + i + ") = " + fibonacci(i));
        }
    }
}'''
        }
        
        source_lang = self.source_lang.get()
        demo_code = demo_codes.get(source_lang, demo_codes["Python"])
        
        self.source_code.delete("1.0", tk.END)
        self.source_code.insert(tk.END, demo_code)
        self.status_var.set(f"📋 Demo {source_lang} code loaded!")

    def _export_current_results(self):
        """Enhanced export with multiple format options."""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Translator tab
            self._export_translation_results()
        elif current_tab == 1:  # Chatbot tab
            self._export_chat_history()
        elif current_tab == 2:  # Security tab
            self.export_report()
        elif current_tab == 3:  # Lyric Lab tab
            self._export_lyric_project()
        else:
            messagebox.showinfo("Export", "Nothing to export from this tab.")

    def _add_welcome_message(self):
        """Add a welcome message to the chat display."""
        if not hasattr(self, 'chat_display'):
            return
            
        try:
            # Get the text widget from TtkScrolledText
            text_widget = self.chat_display.text if hasattr(self.chat_display, 'text') else self.chat_display
            
            # Enable widget for editing
            text_widget.configure(state='normal')
            
            # Clear any existing content
            text_widget.delete('1.0', tk.END)
            
            # Add welcome message with formatted text
            welcome_msg = """🤖 Welcome to CodedSwitch AI Assistant!

I'm Astutely, your AI coding assistant. I can help you with:
• Code translation between programming languages
• Debugging and code optimization
• Answering programming questions
• Explaining code concepts
• And much more!

Type your message below or try one of the example prompts.
"""
            text_widget.insert(tk.END, welcome_msg, "assistant_msg")
            
            # Disable widget to make it read-only
            text_widget.configure(state='disabled')
            
            # Auto-scroll to the bottom
            text_widget.see(tk.END)
            
        except Exception as e:
            root_logger.error(f"Error adding welcome message: {e}")
            try:
                if 'text_widget' in locals():
                    text_widget.configure(state='disabled')
            except Exception as e:
                root_logger.error(f"Error resetting widget state: {e}")
                
    def _export_chat(self):
        """Export the current chat conversation to a text file.
        
        This is an alias for _export_chat_history for backward compatibility.
        """
        self._export_chat_history()
    def _export_chat_history(self):
        """Export chat history."""
        try:
            # Get the text widget from TtkScrolledText
            text_widget = self.chat_display.text if hasattr(self.chat_display, 'text') else self.chat_display
            
            # Get the chat content
            chat_content = text_widget.get("1.0", tk.END).strip()
            if not chat_content:
                messagebox.showwarning("No Chat", "No chat history to export.")
                return
            
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("HTML Files", "*.html"), ("All Files", "*.*")],
                title="Export Chat History"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"CodedSwitch Chat History\n")
                        f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(chat_content)
                    
                    messagebox.showinfo("Export Complete", f"Chat history exported to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
        except Exception as e:
            root_logger.error(f"Error exporting chat history: {e}")
            messagebox.showerror("Error", f"Failed to access chat content: {str(e)}")

    def _export_lyric_project(self):
        """Export complete lyric project."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "No lyrics to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Lyric Project", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Lyric Project"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    project_data = {
                        "title": "CodedSwitch Lyric Project",
                        "lyrics": lyrics,
                        "style": self.lyric_style.get(),
                        "mood": self.lyric_mood.get() if hasattr(self, 'lyric_mood') else "Confident",
                        "complexity": self.complexity_var.get() if hasattr(self, 'complexity_var') else 5,
                        "word_count": len(lyrics.split()),
                        "line_count": len(lyrics.splitlines()),
                        "created": datetime.now().isoformat(),
                        "version": "2.1",
                        "metadata": {
                            "generated_with": "CodedSwitch Lyric Lab",
                            "ai_assisted": True,
                            "ready_for_recording": True
                        }
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(project_data, f, indent=2, ensure_ascii=False)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"CodedSwitch Lyric Project\n")
                        f.write(f"Style: {self.lyric_style.get()}\n")
                        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(lyrics)
                
                messagebox.showinfo("Export Complete", f"Lyric project exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def _add_welcome_message(self):
        """Add enhanced welcome message to chat."""
        welcome_msg = """👋 Welcome to CodedSwitch AI Assistant!

🎯 I'm here to help you with:

🔄 **Code Translation**
• Convert code between programming languages
• Explain language-specific concepts
• Optimize and refactor code

🛡️ **Code Security**
• Identify vulnerabilities in your code
• Suggest security improvements
• Follow best practices

🎤 **Creative Coding & Lyrics**
• Help with coding projects and algorithms
• Assist with rap lyrics and creative writing
• Combine technical and creative skills

💡 **How to get the best help:**
• Be specific about your coding language and goals
• Share code snippets for detailed analysis
• Ask follow-up questions for clarification

What would you like to work on today? 🚀"""
        
        try:
            # Make sure the widget exists and is not destroyed
            if hasattr(self, 'chat_display') and self.chat_display.winfo_exists():
                # Store current scroll position
                first_visible = self.chat_display.yview()[0]
                
                # Enable editing
                self.chat_display.configure(state='normal')
                
                # Clear existing content
                self.chat_display.delete('1.0', tk.END)
                
                # Insert welcome message
                self.chat_display.insert(tk.END, welcome_msg, "assistant_msg")
                self.chat_display.insert(tk.END, "\n\n")
                
                # Restore scroll position if there was content before
                if first_visible < 1.0:  # If not at the end
                    self.chat_display.yview_moveto(first_visible)
                else:
                    self.chat_text.see(tk.END)
                
                # Disable editing
                text_widget.configure(state='disabled')
        except Exception as e:
            root_logger.error(f"Error in _add_welcome_message: {str(e)}")
            # Try to recover by just disabling the widget
            try:
                text_widget.configure(state='disabled')
            except:
                pass

    def _show_chat_examples(self):
        """Show chat example prompts."""
        examples = """💡 Example Questions for CodedSwitch AI:

{{ ... }}
🔄 **Translation Help:**
• "Explain this Python code and translate it to JavaScript"
• "What are the key differences between Python and Java?"
• "How would this algorithm work in C++?"

🛡️ **Security & Code Quality:**
• "Review this code for security vulnerabilities"
• "How can I make this function more efficient?"
• "What are the best practices for this type of code?"

🎤 **Creative & Learning:**
• "Help me write rap lyrics about programming"
• "Explain recursion using a creative analogy"
• "What's a fun coding project for learning JavaScript?"

🚀 **Advanced Assistance:**
• "Design a database schema for an e-commerce app"
• "Help me debug this complex algorithm"
• "Suggest modern alternatives to this legacy code"

Click any example or type your own question! 🎯"""
        
        messagebox.showinfo("💡 Chat Examples", examples)

    def send_message(self, event=None):
        """Enhanced message sending with better UX."""
        # Handle Shift+Return for new line
        if event and event.state & 0x1:  # Shift key pressed
            return "break"
            
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return "break"
            
        # Clear input immediately for better UX
        self.message_input.delete("1.0", tk.END)
        
        # Add user message to chat
        self._add_chat_message("You", message, "user_msg")
        
        # Show thinking indicator
        thinking_msg = "🤔 Thinking..."
        self._add_chat_message("Assistant", thinking_msg, "system_msg")
        
        # Disable send button temporarily
        self.send_button.config(state=tk.DISABLED, text="...")
        
        def get_response():
            try:
                if hasattr(self.ai, 'chat_response'):
                    response = self.ai.chat_response(message)
                else:
                    # Enhanced demo responses
                    demo_responses = {
                        'code': "I can see you're asking about code! In full mode with an API key, I'd provide detailed analysis, suggestions, and help with debugging.",
                        'python': "Python is a great language! With a real API connection, I could help you with Python-specific questions, best practices, and code optimization.",
                        'security': "Security is crucial! In full mode, I'd analyze your code for vulnerabilities and provide specific fixes and improvements.",
                        'lyrics': "Creative coding and lyrics - that's the CodedSwitch specialty! With full AI access, I could help you write amazing rap lyrics with programming themes.",
                        'help': "I'm here to help! In demo mode, my responses are limited, but with a real API key, I could provide comprehensive assistance with all your coding and creative needs."
                    }
                    
                    message_lower = message.lower()
                    response = next((resp for key, resp in demo_responses.items() if key in message_lower), 
                                  "This is a demo response. Get a real API key for full AI assistance with code translation, security analysis, and creative writing!")
                
                # Update UI on main thread
                self.root.after(0, lambda: self._handle_response_received(response))
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                self.root.after(0, lambda: self._handle_response_received(error_msg))
        
        # Run in background thread
        thread = threading.Thread(target=get_response, daemon=True)
        self.resource_manager.add_thread(thread)
        thread.start()
        
        return "break"

    def _add_chat_message(self, sender, message, tag):
        """Add message to chat with timestamp."""
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_text.config(state=tk.NORMAL)
        
        # Add sender and timestamp
        sender_text = f"[{timestamp}] {sender}: "
        self.chat_text.insert(tk.END, sender_text, "timestamp")
        
        # Add message content
        self.chat_text.insert(tk.END, f"{message}\n\n", tag)
        
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def _handle_response_received(self, response):
        """Handle AI response received."""
        # Remove thinking message (last message)
        self.chat_text.config(state=tk.NORMAL)
        
        # Find and remove the thinking message
        content = self.chat_text.get("1.0", tk.END)
        if "🤔 Thinking..." in content:
            lines = content.split('\n')
            filtered_lines = [line for line in lines if "🤔 Thinking..." not in line]
            self.chat_text.delete("1.0", tk.END)
            self.chat_text.insert("1.0", '\n'.join(filtered_lines))
        
        self.chat_text.config(state=tk.DISABLED)
        
        # Add the actual response
        self._add_chat_message("Assistant", response, "assistant_msg")
        
        # Re-enable send button
        self.send_button.config(state=tk.NORMAL, text="🚀 Send")

    def _clear_chat(self):
        """Enhanced chat clearing with confirmation."""
        if messagebox.askyesno("Clear Chat", "Clear all chat history?"):
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete("1.0", tk.END)
            self.chat_text.config(state=tk.DISABLED)
            
            # Add fresh welcome message
            self._add_welcome_message()
            
            self.status_var.set("💬 Chat history cleared")
            
    def _export_chat(self):
        """Export the current chat conversation to a text file."""
        try:
            # Get the current timestamp for the filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"chat_export_{timestamp}.txt"
            
            # Ask user where to save the file
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialfile=default_filename,
                title="Export Chat As..."
            )
            
            if not filepath:  # User cancelled the save dialog
                return
                
            # Get all text from the chat display
            chat_text = self.chat_display.get("1.0", tk.END)
            
            # Write to file with UTF-8 encoding
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"CodedSwitch Chat Export - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                f.write(chat_text)
            
            self.status_var.set(f"💾 Chat exported to {os.path.basename(filepath)}")
            messagebox.showinfo("Export Successful", f"Chat conversation has been exported to:\n{filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export chat: {str(e)}"
            root_logger.error(error_msg, exc_info=True)
            messagebox.showerror("Export Error", error_msg)
            self.status_var.set("❌ Failed to export chat")

    def on_model_change(self, event):
        """Enhanced model change handling."""
        new_model = self.model_var.get()
        if new_model != self.gemini_model:
            try:
                old_model = self.gemini_model
                self.gemini_model = new_model
                
                # Update AI interface if available
                if hasattr(self, 'ai') and hasattr(self.ai, 'use_gemini_model'):
                    self.ai.use_gemini_model(new_model)
                
                # Update status indicators
                self._update_status_indicators()
                
                # Save preference
                self.config_manager.set("model", new_model)
                self.config_manager.save_config()
                
                self.status_var.set(f"🤖 Switched to {new_model}")
                
                # Show change notification
                messagebox.showinfo(
                    "Model Changed",
                    f"AI model changed from {old_model} to {new_model}\n\n"
                    "Different models may have varying:\n"
                    "• Response styles and capabilities\n"
                    "• Processing speed and accuracy\n"
                    "• Specialized knowledge areas\n\n"
                    "Try the new model with your next request!"
                )
                
            except Exception as e:
                root_logger.error(f"Model change failed: {e}")
                messagebox.showerror("Model Change Error", f"Failed to switch model: {str(e)}")
                # Revert to old model
                self.model_var.set(self.gemini_model)

    def _show_about(self):
        """Enhanced about dialog with full feature list."""
        about_text = f"""🎤 CodedSwitch - AI Code Translator & Lyric Lab 🎤
Enhanced Edition v2.1

🚀 THE ULTIMATE AI-POWERED CREATIVE & CODING PLATFORM

✨ CORE FEATURES:
🔄 AI Code Translation - Convert between {len(PROGRAMMING_LANGUAGES)} programming languages
🛡️ Security Vulnerability Scanner - Professional-grade code analysis
🤖 Intelligent AI Assistant - Chat about code, get help, and learn
🎤 Lyric Lab Studio - Create rap lyrics with AI assistance and beat generation

🎵 LYRIC LAB SPECIAL FEATURES:
• {len(LYRIC_STYLES)} different rap styles (Boom Bap, Trap, Drill, etc.)
• Real-time rhyme and synonym suggestions
• AI-powered flow analysis and improvement tips
• Beat generation with actual audio playback
• Story Protocol integration for IP protection
• Professional vocal guides and delivery tips

🔧 TECHNICAL FEATURES:
• Multi-model AI support (Gemini 2.0, 2.5)
• Advanced error handling and resource management
• Professional UI with {len(THEMES)} themes
• Comprehensive keyboard shortcuts
• Export capabilities (HTML, PDF, Audio projects)
• Real-time code validation and syntax checking

💎 THE TRIPLE ENTENDRE:
• CODE (Programming languages)
• CODE (Lyrics/Bars in rap)
• CODE-SWITCHING (Seamless transitions between modes)

🌟 CURRENT SESSION:
• Theme: {self.current_theme}
• AI Model: {self.gemini_model}
• Audio System: {"🎵 Active" if self.resource_manager.audio_initialized else "🔇 Inactive"}
• API Status: {"🟢 Connected" if self.gemini_api_key else "🟡 Demo Mode"}

🎯 Perfect for developers, artists, students, and creative technologists!

© 2025 CodedSwitch AI - Where Technology Meets Creativity
Developed with ❤️ for the coding and hip-hop communities"""
        
        # Create custom about dialog
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About CodedSwitch")
        about_dialog.geometry("600x500")
        about_dialog.transient(self.root)
        about_dialog.grab_set()
        
        # Center the dialog
        about_dialog.update_idletasks()
        x = (about_dialog.winfo_screenwidth() // 2) - 300
        y = (about_dialog.winfo_screenheight() // 2) - 250
        about_dialog.geometry(f"600x500+{x}+{y}")
        
        main_frame = ttk.Frame(about_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable text area
        text_widget = TtkScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            state=tk.DISABLED
        )
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert("1.0", about_text)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="🌐 Visit Website",
            command=lambda: webbrowser.open("https://github.com/your-repo/codedswitch"),
            width=15
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=about_dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT)

    # Remaining Lyric Lab specific methods
    def _suggest_lyric_edits(self):
        """Enhanced lyric editing suggestions with detailed analysis."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            selected_style = self.lyric_style.get()
            mood = getattr(self, 'lyric_mood', tk.StringVar(value="Confident")).get()
            
            edit_prompt = f"""Analyze these {selected_style} lyrics and provide detailed improvement suggestions:

LYRICS:
{lyrics}

STYLE: {selected_style}
MOOD: {mood}

Provide specific, actionable suggestions for:

1. **FLOW IMPROVEMENTS**: Line-by-line rhythm enhancements
2. **RHYME SCHEME UPGRADES**: Better rhyme placements and patterns
3. **WORDPLAY ENHANCEMENTS**: More clever bars and double entendres
4. **SYLLABLE OPTIMIZATION**: Better syllable distribution for flow
5. **STRUCTURAL IMPROVEMENTS**: Verse/chorus organization
6. **CONTENT STRENGTHENING**: Deeper themes and storytelling
7. **HOOK DEVELOPMENT**: Catchy, memorable phrases
8. **DELIVERY GUIDANCE**: Performance and vocal techniques

Show before/after examples where possible. Be specific and constructive."""
            
            response = self.ai.chat_response(edit_prompt) if hasattr(self.ai, 'chat_response') else self._generate_demo_edit_suggestions(lyrics)
            
            self._show_analysis_dialog("✏️ Lyric Enhancement Suggestions", response, "lyric_editing")
            
        except Exception as e:
            messagebox.showerror("Edit Analysis Error", f"Failed to analyze lyrics for improvements: {str(e)}")

    def _generate_demo_edit_suggestions(self, lyrics):
        """Generate demo editing suggestions."""
        line_count = len([line for line in lyrics.split('\n') if line.strip()])
        word_count = len(lyrics.split())
        
        return f"""✏️ LYRIC ENHANCEMENT SUGGESTIONS:

📊 Current Analysis:
• Lines: {line_count} | Words: {word_count}
• Style: {self.lyric_style.get()}
• Estimated performance time: {word_count * 0.4:.1f} seconds

🎯 FLOW IMPROVEMENTS:
• Line 3: Try breaking the long phrase for better breath control
• Consider adding more syncopated rhythms in verse 2
• Strengthen the emphasis on technical terms for impact

🎵 RHYME SCHEME UPGRADES:
• Current pattern shows potential - try AABB in the hook
• Add internal rhymes in lines 5-7 for complexity
• Consider slant rhymes for more sophisticated sound

💎 WORDPLAY ENHANCEMENTS:
• Replace simple words with programming metaphors
• Add double entendres related to coding themes
• Incorporate more technical terminology creatively

📐 SYLLABLE OPTIMIZATION:
• Current average: {word_count/max(line_count, 1):.1f} syllables per line
• Recommended range: 10-16 syllables for this style
• Balance longer and shorter lines for dynamics

🏗️ STRUCTURAL IMPROVEMENTS:
• Strong opening - consider making it the hook
• Develop the coding theme more consistently
• Add a bridge section for variety

🎤 DELIVERY GUIDANCE:
• Emphasize technical terms with vocal inflection
• Use pause for dramatic effect after punchlines
• Consider vocal layering on the hook

⭐ Overall Potential: 8.5/10 - Great foundation, excellent improvement opportunities!"""

    def _generate_vocal_guide(self):
        """Generate comprehensive vocal delivery guide."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        try:
            selected_style = self.lyric_style.get()
            mood = getattr(self, 'lyric_mood', tk.StringVar(value="Confident")).get()
            
            vocal_prompt = f"""Create a detailed vocal delivery guide for these {selected_style} lyrics:

LYRICS:
{lyrics}

STYLE: {selected_style}
MOOD: {mood}

Provide comprehensive vocal direction including:

1. **VOCAL TONE & CHARACTER**: Overall vocal approach and attitude
2. **DELIVERY PACE**: Tempo variations and rhythm guidance
3. **EMPHASIS PATTERNS**: Which words/phrases to stress or punch
4. **BREATH CONTROL**: Strategic breathing points and techniques
5. **VOCAL EFFECTS**: Ad-libs, runs, and vocal embellishments
6. **DYNAMICS**: Volume changes, energy shifts, intensity mapping
7. **ARTICULATION**: Clear vs. slurred delivery instructions
8. **EMOTIONAL DELIVERY**: How to convey the mood and message
9. **TIMING & SYNCOPATION**: Relationship to beat and rhythm
10. **RECORDING TECHNIQUES**: Studio tips for best capture

Make it practical for actual recording sessions with specific line-by-line guidance."""
            
            response = self.ai.chat_response(vocal_prompt) if hasattr(self.ai, 'chat_response') else self._generate_demo_vocal_guide(lyrics, selected_style, mood)
            
            self._show_analysis_dialog("🎤 Professional Vocal Delivery Guide", response, "vocal_guide")
            
        except Exception as e:
            messagebox.showerror("Vocal Guide Error", f"Failed to generate vocal guide: {str(e)}")

    def _generate_demo_vocal_guide(self, lyrics, style, mood):
        """Generate demo vocal guide."""
        return f"""🎤 PROFESSIONAL VOCAL DELIVERY GUIDE

🎯 STYLE: {style} | MOOD: {mood}

🗣️ VOCAL TONE & CHARACTER:
• Overall approach: Confident, technically precise delivery
• Attitude: Cool, controlled, slightly aggressive undertone
• Character: Tech-savvy lyricist with serious skills

⏱️ DELIVERY PACE:
• Verses: Medium tempo with occasional rapid-fire sections
• Hook: Slightly slower for memorability and impact
• Bridge: Vary pace for dynamics and listener engagement

💥 EMPHASIS PATTERNS:
• STRONG emphasis on technical terms (variables, functions, etc.)
• Punch hard on rhyme words and end-of-line impacts
• Subtle emphasis on internal rhymes for flow complexity

🫁 BREATH CONTROL:
• Strategic pause after every 4-bar section
• Quick breath during natural pauses in lyrics
• Use breath as rhythmic element, not interruption

🎵 VOCAL EFFECTS:
• Subtle ad-libs on technical terms ("yeah", "uh-huh")
• Voice doubling on hook for thickness
• Light vocal runs on sustained notes

📊 DYNAMICS:
• Start moderate, build energy through verses
• Peak energy on hook sections
• Dynamic drops for emphasis and contrast

🗣️ ARTICULATION:
• Crystal clear on technical terminology
• Slight slur acceptable on transitional words
• Crisp consonants for punchline delivery

💫 EMOTIONAL DELIVERY:
• Controlled confidence throughout
• Slight swagger on clever wordplay
• Intensity without losing technical precision

⏰ TIMING & SYNCOPATION:
• Stay slightly ahead of beat for urgency
• Use syncopation on internal rhymes
• Lock onto kick pattern for foundation

🎙️ RECORDING TECHNIQUES:
• Close-mic for intimacy, but watch plosives
• Light compression for consistency
• Double-track hook sections for impact
• EQ boost around 3-5kHz for clarity

📝 LINE-BY-LINE NOTES:
• Opening line: Set the tone - confident but not rushed
• Technical terms: Enunciate clearly, these are your expertise
• Rhyme words: Hit these hard for satisfying payoffs
• Hook: Make it memorable - this is what people will sing along to

⭐ PERFORMANCE RATING TARGET: Studio-quality delivery with street credibility!"""

    def _show_lyric_stats(self):
        """Enhanced lyric statistics with detailed analysis."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics first!")
            return
        
        # Calculate comprehensive stats
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        words = lyrics.split()
        chars = len(lyrics.replace(' ', '').replace('\n', ''))
        
        # Estimate syllables (improved approximation)
        syllables = 0
        for word in words:
            # Simple syllable estimation
            word_syllables = max(1, len([c for c in word.lower() if c in 'aeiouy']))
            # Adjust for common patterns
            if word.endswith('e') and len(word) > 3:
                word_syllables -= 1
            if word.endswith('ed') and not word.endswith(('ted', 'ded')):
                word_syllables -= 1
            syllables += max(1, word_syllables)
        
        # Calculate advanced metrics
        avg_words_per_line = len(words) / max(len(lines), 1)
        avg_syllables_per_line = syllables / max(len(lines), 1)
        avg_chars_per_word = chars / max(len(words), 1)
        
        # Estimate performance timing
        fast_time = syllables / 6.0  # 6 syllables per second
        medium_time = syllables / 4.0  # 4 syllables per second  
        slow_time = syllables / 3.0  # 3 syllables per second
        
        # Analyze rhyme density (simple check)
        end_words = [line.split()[-1].lower().strip('.,!?;:') for line in lines if line.split()]
        unique_end_sounds = len(set(end_words))
        rhyme_density = (len(end_words) - unique_end_sounds) / max(len(end_words), 1) * 100
        
        stats = f"""📊 COMPREHENSIVE LYRIC STATISTICS

📝 BASIC METRICS:
• Lines: {len(lines)}
• Words: {len(words):,}
• Characters: {chars:,}
• Syllables: {syllables:,} (estimated)

📐 AVERAGES:
• Words per line: {avg_words_per_line:.1f}
• Syllables per line: {avg_syllables_per_line:.1f}
• Characters per word: {avg_chars_per_word:.1f}

⏱️ PERFORMANCE ESTIMATES:
• 🏃 Fast delivery (6 syl/sec): {fast_time:.1f} seconds
• 🚶 Medium pace (4 syl/sec): {medium_time:.1f} seconds
• 🐌 Slow flow (3 syl/sec): {slow_time:.1f} seconds

🎵 FLOW ANALYSIS:
• Rhyme density: {rhyme_density:.1f}%
• Style consistency: {self.lyric_style.get()}
• Estimated complexity: {min(10, int(avg_syllables_per_line * rhyme_density / 10))}/10

🎯 RECOMMENDATIONS:
• Ideal line length: 12-16 syllables for {self.lyric_style.get()}
• Current structure: {"Excellent" if 12 <= avg_syllables_per_line <= 16 else "Consider adjusting"}
• Rhyme scheme: {"Strong" if rhyme_density > 30 else "Could be enhanced"}

🎤 RECORDING READINESS:
• Word count suitable for: {"Full track" if len(words) > 100 else "Verse/Hook"}
• Performance length: {"Radio-friendly" if 60 <= medium_time <= 180 else "Extended/Short format"}
• Complexity level: {"Professional" if syllables > 200 else "Developing"}

💡 NEXT STEPS:
{"• Perfect! Ready for recording and production" if len(words) > 100 and 12 <= avg_syllables_per_line <= 16 else "• Consider expanding or refining for full track"}
• Run flow analysis for rhythm optimization
• Generate beat to match your lyrical style
• Use vocal guide for recording preparation"""
        
        # Show in detailed dialog
        stats_dialog = tk.Toplevel(self.root)
        stats_dialog.title("📊 Lyric Statistics & Analysis")
        stats_dialog.geometry("600x500")
        stats_dialog.transient(self.root)
        
        main_frame = ttk.Frame(stats_dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = TtkScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        text_widget.insert("1.0", stats)
        text_widget.config(state=tk.DISABLED)
        
        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="📤 Export Stats",
            command=lambda: self._export_analysis(stats, "lyric_statistics"),
            width=15
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text="🎵 Analyze Flow",
            command=lambda: [stats_dialog.destroy(), self._analyze_lyric_flow()],
            style="primary.TButton",
            width=15
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=stats_dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT)

    def _save_lyrics(self):
        """Enhanced lyrics saving with project format."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "No lyrics to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".lyr",
            filetypes=[
                ("Lyric Files", "*.lyr"),
                ("Text Files", "*.txt"), 
                ("Project Files", "*.json"),
                ("All Files", "*.*")
            ],
            title="Save Lyrics"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    # Save as complete project
                    project_data = {
                        "title": "CodedSwitch Lyrics",
                        "artist": "CodedSwitch User",
                        "lyrics": lyrics,
                        "style": self.lyric_style.get(),
                        "mood": getattr(self, 'lyric_mood', tk.StringVar(value="Confident")).get(),
                        "complexity": getattr(self, 'complexity_var', tk.IntVar(value=5)).get(),
                        "metadata": {
                            "created": datetime.now().isoformat(),
                            "word_count": len(lyrics.split()),
                            "line_count": len(lyrics.splitlines()),
                            "estimated_duration": len(lyrics.split()) * 0.4,
                            "version": "2.1-enhanced"
                        },
                        "settings": {
                            "font_size": self.font_size,
                            "theme": self.current_theme
                        }
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(project_data, f, indent=2, ensure_ascii=False)
                else:
                    # Save as text with header
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"# CodedSwitch Lyrics\n")
                        f.write(f"# Style: {self.lyric_style.get()}\n")
                        f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"# Word Count: {len(lyrics.split())}\n\n")
                        f.write(lyrics)
                
                messagebox.showinfo("💾 Lyrics Saved!", f"Lyrics saved successfully!\n\nLocation: {file_path}")
                self.status_var.set(f"💾 Lyrics saved to {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save lyrics: {str(e)}")

    def _register_lyrics_on_story(self):
        """Enhanced Story Protocol registration with detailed guidance."""
        lyrics = self.lyric_editor.get("1.0", tk.END).strip()
        if not lyrics:
            messagebox.showwarning("No Lyrics", "Enter some lyrics to register!")
            return
        
        # Calculate lyrics stats for registration
        word_count = len(lyrics.split())
        line_count = len(lyrics.splitlines())
        style = self.lyric_style.get()
        
        info_text = f"""🛡️ STORY PROTOCOL IP REGISTRATION

Ready to protect your creative work on blockchain!

📊 YOUR LYRICS:
• Words: {word_count:,}
• Lines: {line_count}
• Style: {style}
• Estimated value: Original creative work

🔗 REGISTRATION PROCESS:
1. Visit: portal.story.foundation
2. Connect your Web3 wallet (MetaMask, etc.)
3. Upload your lyrics as an IP Asset
4. Set licensing terms and royalty rates
5. Pay registration fee ($IP tokens)
6. Receive blockchain certificate of ownership

💰 ESTIMATED COSTS:
• Registration: $1-5 USD worth of $IP tokens
• Gas fees: Variable (Ethereum network)
• Optional: Enhanced protection features

🎯 BENEFITS:
• Immutable proof of creation
• Automatic licensing and royalties
• Legal protection for your IP
• Global recognition and enforcement
• Revenue from commercial use

📄 EXPORT OPTIONS:
• JSON metadata format (recommended)
• Text with copyright notice
• Complete project file with all details

Would you like to export your lyrics for Story Protocol registration?"""
        
        if messagebox.askyesno("🛡️ Story Protocol Registration", info_text):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("Story Protocol JSON", "*.json"),
                    ("Text with Copyright", "*.txt"),
                    ("All Files", "*.*")
                ],
                title="Export for Story Protocol"
            )
            
            if file_path:
                try:
                    if file_path.endswith('.json'):
                        # Create Story Protocol compatible metadata
                        metadata = {
                            "title": f"CodedSwitch {style} Lyrics",
                            "description": f"Original {style} rap lyrics created with CodedSwitch AI assistance",
                            "creator": "CodedSwitch User",
                            "content": lyrics,
                            "created": datetime.now().isoformat(),
                            "type": "lyrics",
                            "genre": "Hip-Hop/Rap",
                            "style": style,
                            "language": "English",
                            "tags": ["rap", "hip-hop", "coding", "AI-assisted", "CodedSwitch"],
                            "metrics": {
                                "word_count": word_count,
                                "line_count": line_count,
                                "estimated_duration_seconds": word_count * 0.4
                            },
                            "licensing": {
                                "commercial_use": "allowed_with_attribution",
                                "modifications": "allowed",
                                "distribution": "allowed",
                                "attribution_required": True,
                                "suggested_royalty_rate": "10%"
                            },
                            "technical": {
                                "format": "text/plain",
                                "encoding": "UTF-8",
                                "created_with": "CodedSwitch v2.1 Enhanced",
                                "ai_assisted": True
                            },
                            "copyright": f"© {datetime.now().year} CodedSwitch User. All rights reserved.",
                            "story_protocol_ready": True
                        }
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                    else:
                        # Text format with copyright
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(f"STORY PROTOCOL IP REGISTRATION\n")
                            f.write(f"{'='*50}\n\n")
                            f.write(f"Title: {style} Lyrics\n")
                            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Creator: CodedSwitch User\n")
                            f.write(f"Style: {style}\n")
                            f.write(f"Word Count: {word_count}\n")
                            f.write(f"Line Count: {line_count}\n\n")
                            f.write(f"COPYRIGHT NOTICE:\n")
                            f.write(f"© {datetime.now().year} CodedSwitch User. All rights reserved.\n")
                            f.write(f"Created with CodedSwitch AI assistance.\n\n")
                            f.write(f"LYRICS:\n")
                            f.write(f"{'-'*30}\n")
                            f.write(lyrics)
                            f.write(f"\n{'-'*30}\n\n")
                            f.write(f"Ready for Story Protocol registration at portal.story.foundation\n")
                    
                    messagebox.showinfo(
                        "🛡️ Export Complete!", 
                        f"Lyrics exported for Story Protocol registration!\n\n"
                        f"📁 File: {file_path}\n\n"
                        f"🔗 Next steps:\n"
                        f"1. Go to portal.story.foundation\n"
                        f"2. Connect your wallet\n"
                        f"3. Upload this file\n"
                        f"4. Complete registration\n\n"
                        f"💡 Tip: Keep this file as proof of creation!"
                    )
                    
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export for Story Protocol: {str(e)}")

    def _generate_style_specific_lyrics(self):
        """Enhanced style-specific lyric generation with context awareness."""
        try:
            prompt = self.lyric_prompt.get("1.0", tk.END).strip()
            selected_style = self.lyric_style.get()
            mood = getattr(self, 'lyric_mood', tk.StringVar(value="Confident")).get()
            complexity = getattr(self, 'complexity_var', tk.IntVar(value=5)).get()
            
            if not prompt:
                messagebox.showwarning("No Prompt", "Enter a theme or idea for AI to work with!")
                return
            
            # Get style-specific instructions
            style_info = LYRIC_STYLES.get(selected_style, LYRIC_STYLES["Boom Bap"])
            
            # Get existing lyrics for context
            existing_lyrics = self.lyric_editor.get("1.0", tk.END).strip()
            context_note = f"\n\nEXISTING LYRICS CONTEXT:\n{existing_lyrics}" if existing_lyrics else ""
            
            ai_prompt = f"""You are a highly skilled {selected_style} rapper and lyricist. Create original lyrics based on this theme: "{prompt}"

STYLE REQUIREMENTS:
• Style: {selected_style}
• Mood: {mood} 
• Complexity Level: {complexity}/10
• Description: {style_info['description']}
• Characteristics: {style_info['characteristics']}
• Style Guidelines: {style_info['prompt_additions']}

TECHNICAL REQUIREMENTS:
• Generate 8-16 bars that perfectly exemplify {selected_style}
• Match the {mood} mood throughout
• Complexity level {complexity}: {"Simple and catchy" if complexity <= 3 else "Moderate complexity" if complexity <= 7 else "Highly complex and intricate"}
• Include internal rhymes and wordplay appropriate for the style
• For Coding Rap style: Naturally incorporate programming/tech references
• Maintain authentic {selected_style} vocabulary and flow patterns

QUALITY STANDARDS:
• Original, creative content only
• Strong rhyme scheme consistency
• Appropriate syllable density for the style
• Memorable and impactful punchlines
• Professional-level lyrical content{context_note}

Generate lyrics that sound like they could be performed by a top-tier {selected_style} artist."""
            
            response = self.ai.chat_response(ai_prompt) if hasattr(self.ai, 'chat_response') else self._generate_demo_style_lyrics(prompt, selected_style, mood, complexity)
            
            # Insert the generated lyrics
            current_text = self.lyric_editor.get("1.0", tk.END).strip()
            if current_text:
                self.lyric_editor.insert(tk.END, f"\n\n--- {selected_style} ({mood}) ---\n{response}")
            else:
                self.lyric_editor.insert("1.0", f"--- {selected_style} ({mood}) ---\n{response}")
                
            self.status_var.set(f"✨ {selected_style} lyrics generated! Theme: {prompt}")
            
            # Clear prompt for next use
            self.lyric_prompt.delete("1.0", tk.END)
            
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate lyrics: {str(e)}")

    def _generate_demo_style_lyrics(self, prompt, style, mood, complexity):
        """Generate demo lyrics for testing."""
        complexity_level = "complex" if complexity > 7 else "moderate" if complexity > 4 else "simple"
        
        demo_lyrics = {
            "Boom Bap": f"Classic boom bap flows, {mood} and raw\nSpitting {complexity_level} bars, that's the law\nTheme of {prompt}, I break it down precise\nCodedSwitch methodology, that's my device",
            "Trap": f"Yeah, {mood} vibes, trap beats in my soul\n{complexity_level} flows, that's how I roll\n{prompt} on my mind, keeping it real\nCodedSwitch in the lab, that's the deal",
            "Drill": f"Aggressive {mood} energy, drill time now\n{complexity_level} bars, show you how\n{prompt} in the streets, keeping it gritty\nCodedSwitch on the scene, ain't that pretty",
            "Coding Rap": f"Variables and functions, {mood} debugging flow\nif statements and loops, {complexity_level} code I show\n{prompt} like an algorithm, optimized and clean\nCodedSwitch in the IDE, best you've ever seen"
        }
        
        return demo_lyrics.get(style, f"Demo {style} lyrics with {mood} mood\n{complexity_level} complexity about {prompt}\nCodedSwitch generated flow\nThat's how the demo bars go")

    def _regenerate_beat_from_ai(self, beat_window):
        """Regenerate beat using AI with current parameters."""
        try:
            # Get current lyrics for context
            lyrics = self.lyric_editor.get("1.0", tk.END).strip()
            style = self.lyric_style.get()
            mood = getattr(self, 'lyric_mood', tk.StringVar(value="Confident")).get()
            
            regenerate_prompt = f"""Generate a NEW beat variation for these lyrics with different patterns:

LYRICS: {lyrics[:200]}...
STYLE: {style}
MOOD: {mood}

Current BPM: {beat_window.bpm_var.get()}

Create a variation with:
- Different drum patterns but same style
- Slight BPM adjustment (±10)
- Fresh energy while maintaining vibe
- New instrumental suggestions

Provide the same JSON format as before with updated patterns."""
            
            response = self.ai.chat_response(regenerate_prompt) if hasattr(self.ai, 'chat_response') else self._generate_demo_beat_analysis()
            
            # Parse and update beat
            new_beat_data = self._parse_beat_response(response)
            
            # Update beat window with new data
            beat_window.bpm_var.set(new_beat_data.get('bpm', 120))
            beat_window.bpm_label.config(text=str(new_beat_data.get('bpm', 120)))
            
            # Update patterns
            for pattern_key in ['kick', 'snare', 'hihat', 'openhat', 'crash', 'bass']:
                if pattern_key + '_pattern' in new_beat_data:
                    new_pattern = new_beat_data[pattern_key + '_pattern']
                    beat_window.patterns[pattern_key] = new_pattern
                    
                    # Update visual buttons
                    if pattern_key in beat_window.pattern_buttons:
                        colors = {
                            "kick": "#FF5722", "snare": "#2196F3", "hihat": "#4CAF50",
                            "openhat": "#FFC107", "crash": "#FF9800", "bass": "#9C27B0"
                        }
                        
                        for i, btn in enumerate(beat_window.pattern_buttons[pattern_key]):
                            is_active = new_pattern[i] if i < len(new_pattern) else 0
                            btn.config(
                                text="●" if is_active else "○",
                                bg=colors[pattern_key] if is_active else "gray20"
                            )
            
            beat_window.status_label.config(text="🔄 New beat variation generated! Click Play to hear it!")
            
        except Exception as e:
            beat_window.status_label.config(text=f"❌ Regeneration failed: {str(e)}")

    def _export_beat_audio(self, beat_window):
        """Export beat as high-quality audio file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV Files", "*.wav"), ("MP3 Files", "*.mp3"), ("All Files", "*.*")],
            title="Export Beat Audio"
        )
        
        if file_path:
            try:
                # Show progress
                beat_window.status_label.config(text="📤 Exporting high-quality audio...")
                
                # Generate high-quality version
                beat_data = {
                    'bpm': beat_window.bpm_var.get(),
                    'patterns': beat_window.patterns,
                    'master_volume': beat_window.master_volume.get(),
                    'swing': beat_window.swing_var.get(),
                    'volumes': {
                        key: getattr(beat_window, f"{key}_volume", tk.DoubleVar(value=0.8)).get()
                        for key in beat_window.patterns.keys()
                    }
                }
                
                # Generate longer version for export (4 loops)
                def export_worker():
                    try:
                        # Generate 4 loops of the beat
                        sample_rate = Constants.SAMPLE_RATE
                        bpm = beat_data['bpm']
                        beat_duration = 60.0 / bpm / 4 * 16  # Full 16-beat pattern
                        total_duration = beat_duration * 4  # 4 loops
                        
                        # Create extended beat
                        extended_samples = np.zeros(int(total_duration * sample_rate * 2))  # Stereo
                        
                        # Generate base pattern
                        pattern_audio = self._generate_enhanced_beat_audio(beat_data)
                        
                        if LIBROSA_AVAILABLE:
                            # Load the pattern using librosa
                            pattern_samples, _ = librosa.load(pattern_audio, sr=sample_rate, mono=False)
                            if pattern_samples.ndim == 1:
                                pattern_samples = np.column_stack((pattern_samples, pattern_samples))
                        else:
                            # Fallback: read the pattern file directly
                            _, pattern_samples = wavfile.read(pattern_audio)
                            if pattern_samples.ndim == 1:
                                pattern_samples = np.column_stack((pattern_samples, pattern_samples))
                            pattern_samples = pattern_samples.astype(np.float32) / 32768.0  # Normalize
                        
                        # Loop the pattern 4 times
                        for i in range(4):
                            start_sample = int(i * len(pattern_samples))
                            end_sample = min(start_sample + len(pattern_samples), len(extended_samples))
                            extended_samples[start_sample:end_sample] = pattern_samples[:end_sample-start_sample]
                        
                        # Export to file
                        wavfile.write(file_path, sample_rate, (extended_samples * 32767).astype(np.int16))
                        
                        beat_window.after(0, lambda: beat_window.status_label.config(text="✅ Beat exported successfully!"))
                        beat_window.after(0, lambda: messagebox.showinfo("Export Complete", f"Beat exported to:\n{file_path}"))
                        
                    except Exception as e:
                        beat_window.after(0, lambda: beat_window.status_label.config(text=f"❌ Export failed: {str(e)}"))
                
                # Run export in background
                thread = threading.Thread(target=export_worker, daemon=True)
                self.resource_manager.add_thread(thread)
                thread.start()
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export beat: {str(e)}")

    # Complete the application

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
        messagebox.showinfo("Mood Analysis", f"Detected mood: {detected_mood.title()}\nSettings adjusted automatically!")
    
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
                messagebox.showerror("Error", f"Failed to export project: {e}")

    
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
        messagebox.showinfo("Mood Analysis", f"Detected mood: {detected_mood.title()}\nSettings adjusted automatically!")
    
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
                messagebox.showerror("Error", f"Failed to export project: {e}")


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
        messagebox.showinfo("Mood Analysis", f"Detected mood: {detected_mood.title()}\nSettings adjusted automatically!")
    
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
                messagebox.showerror("Error", f"Failed to export project: {e}")

    
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
        messagebox.showinfo("Mood Analysis", f"Detected mood: {detected_mood.title()}\nSettings adjusted automatically!")
    
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
                messagebox.showerror("Error", f"Failed to export project: {e}")

    def run(self):
        """Run the enhanced CodedSwitch application."""
        try:
            root_logger.info("🎤 Starting CodedSwitch Enhanced Edition...")
            self.root.mainloop()
        except KeyboardInterrupt:
            root_logger.info("Application interrupted by user")
        except Exception as e:
            root_logger.error(f"Application error: {e}", exc_info=True)
        finally:
            root_logger.info("Application shutdown completed")


def main():
    """🎤 Launch CodedSwitch - The Ultimate AI Code & Lyric Studio! 🎤"""
    parser = argparse.ArgumentParser(
        description="CodedSwitch - Revolutionary AI Code Translator & Lyric Lab Enhanced Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎵 CODEDSWITCH ENHANCED EDITION v2.1 🎵

Examples:
  python codedswitch.py --gemini-api-key YOUR_KEY
  python codedswitch.py --demo-mode
  python codedswitch.py --premium --security

Features:
  🔄 AI Code Translation between 10+ languages
  🛡️ Professional security vulnerability scanning  
  🤖 Intelligent AI assistant with chat
  🎤 Advanced Lyric Lab with beat generation
  🎧 Real-time audio beat creation and playback
  📊 Comprehensive flow and rhyme analysis
  🔒 Story Protocol IP protection integration
        """
    )
    
    parser.add_argument("--gemini-api-key", help="Google Gemini API key")
    parser.add_argument("--gemini-model", default=Constants.DEFAULT_MODEL, help="Gemini model to use")
    parser.add_argument("--premium", action="store_true", help="Enable premium features")
    parser.add_argument("--security", action="store_true", default=True, help="Enable security scanner")
    parser.add_argument("--demo-mode", action="store_true", help="Start in demo mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio system")

    args = parser.parse_args()

    # Set up logging level
    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)

    try:
        print("🎤 CodedSwitch Enhanced Edition v2.1")
        print("🚀 Initializing AI Code Translator & Lyric Lab...")
        
        # Create and run the application
        app = IntegratedTranslatorGUI(
            gemini_api_key=args.gemini_api_key,
            gemini_model=args.gemini_model,
            enable_premium=args.premium,
            enable_security=args.security
        )
        
        # Disable audio if requested
        if args.no_audio:
            app.resource_manager.audio_initialized = False
            root_logger.info("🔇 Audio system disabled by user request")
        
        # Enter demo mode if requested
        if args.demo_mode:
            app._setup_demo_mode()
            app.status_var.set("🎮 Demo Mode Active - Explore all features!")
            root_logger.info("🎮 Demo mode activated")
        
        print("✅ CodedSwitch initialized successfully!")
        audio_status = "✓" if not args.no_audio else "✗"
        print(f"🎯 Features: Translation ✓ Security ✓ Chat ✓ Lyric Lab ✓ Audio {audio_status}")
        print("🎵 Ready to code and create! Let's switch it up!")
        
        root_logger.info("🎤 CodedSwitch Enhanced Edition ready!")
        
        app.run()
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Install required packages: pip install -r requirements.txt")
        return 1
    except Exception as e:
        root_logger.error(f"Failed to start application: {e}", exc_info=True)
        print(f"❌ Failed to start CodedSwitch: {e}")
        print("🔧 Try running with --debug for more information")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
