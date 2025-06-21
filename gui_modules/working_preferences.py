"""
Complete preferences system with working themes, settings persistence,
and beautiful dark themes for CodedSwitch
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap import Style
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PreferencesData:
    """Data class for all CodedSwitch preferences"""
    # Appearance
    theme: str = "superhero"  # Default dark theme
    font_size: int = 11
    font_family: str = "Consolas"
    
    # Audio
    sample_rate: int = 44100
    buffer_size: int = 512
    master_volume: float = 0.8
    audio_enabled: bool = True
    
    # AI Settings
    gemini_api_key: str = ""
    ai_model: str = "gemini-1.5-flash"
    ai_enabled: bool = True
    
    # Editor Settings
    auto_save: bool = True
    syntax_highlighting: bool = True
    line_numbers: bool = True
    word_wrap: bool = True
    
    # Window Settings
    window_width: int = 1200
    window_height: int = 800
    remember_window_size: bool = True
    
    # Recent Files
    max_recent_files: int = 10
    recent_files: list = None
    
    # Advanced
    debug_mode: bool = False
    auto_update_check: bool = True
    telemetry_enabled: bool = False
    
    def __post_init__(self):
        if self.recent_files is None:
            self.recent_files = []

class WorkingPreferencesManager:
    """Complete working preferences manager for CodedSwitch"""
    
    def __init__(self, app_instance=None):
        self.app = app_instance
        self.config_dir = Path.home() / ".codedswitch"
        self.config_file = self.config_dir / "preferences.json"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load preferences
        self.prefs = self._load_preferences()
        
        # Available themes with descriptions
        self.available_themes = {
            # Dark Themes (Recommended)
            "superhero": "🦸 Superhero - Dark blue with orange accents",
            "darkly": "🌙 Darkly - Professional dark theme",
            "cyborg": "🤖 Cyborg - Dark hacker theme with green accents",
            "vapor": "🌈 Vapor - Dark synthwave with neon colors",
            "solar": "☀️ Solar - Solarized dark theme",
            
            # Light Themes
            "cosmo": "🌟 Cosmo - Clean light theme",
            "flatly": "📱 Flatly - Modern flat design",
            "litera": "📚 Litera - Professional light theme",
            "journal": "📰 Journal - Classic newspaper style",
            "minty": "🍃 Minty - Fresh mint green",
            "yeti": "❄️ Yeti - Cool winter theme",
            
            # Colorful Themes
            "pulse": "💓 Pulse - Vibrant purple theme",
            "united": "🇺🇸 United - Bold patriotic theme",
            "sandstone": "🏜️ Sandstone - Warm desert colors",
            "lumen": "💡 Lumen - Bright and minimal"
        }
        
        logger.info(f"Preferences manager initialized. Current theme: {self.prefs.theme}")
    
    def _load_preferences(self) -> PreferencesData:
        """Load preferences from file or create defaults"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert to PreferencesData object
                prefs = PreferencesData(**data)
                logger.info(f"✅ Loaded preferences from {self.config_file}")
                return prefs
            else:
                logger.info("No preferences file found, using defaults")
                return PreferencesData()
                
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
            logger.info("Using default preferences")
            return PreferencesData()
    
    def save_preferences(self) -> bool:
        """Save preferences to file"""
        try:
            # Convert dataclass to dictionary
            data = asdict(self.prefs)
            
            # Add metadata
            data['_saved_at'] = datetime.now().isoformat()
            data['_version'] = "2.0.0"
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Preferences saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save preferences: {e}")
            return False
    
    def get_preference(self, key: str, default=None):
        """Get a preference value"""
        return getattr(self.prefs, key, default)
    
    def set_preference(self, key: str, value):
        """Set a preference value"""
        if hasattr(self.prefs, key):
            setattr(self.prefs, key, value)
            logger.debug(f"Set preference {key} = {value}")
        else:
            logger.warning(f"Unknown preference key: {key}")
    
    def apply_theme(self, theme_name: str) -> bool:
        """Apply a theme and save preference"""
        try:
            # Create new style instance
            style = Style()
            
            # Check if theme is available
            available_themes = style.theme_names()
            if theme_name not in available_themes:
                logger.error(f"Theme '{theme_name}' not available. Available: {available_themes}")
                return False
            
            # Apply the theme
            style.theme_use(theme_name)
            
            # Update preference
            self.prefs.theme = theme_name
            
            # Apply additional customizations for dark themes
            self._apply_custom_theme_styles(style, theme_name)
            
            logger.info(f"✅ Applied theme: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply theme {theme_name}: {e}")
            return False
    
    def _apply_custom_theme_styles(self, style: Style, theme_name: str):
        """Apply custom styles to enhance themes"""
        try:
            # Dark theme enhancements
            if theme_name in ['superhero', 'darkly', 'cyborg', 'vapor', 'solar']:
                # Configure custom colors for dark themes
                style.configure('Custom.TFrame', background='#2a2a2a')
                style.configure('Custom.TLabel', background='#2a2a2a', foreground='#ffffff')
                style.configure('Dark.TNotebook', background='#1a1a1a')
                style.configure('Dark.TNotebook.Tab', padding=[12, 8])
                
                # Beat Studio specific styles
                style.configure('BeatStudio.TFrame', background='#1a1a1a')
                style.configure('BeatStudio.TLabel', background='#1a1a1a', foreground='#ffffff')
                
            # Additional customizations can be added here
            logger.debug(f"Applied custom styles for {theme_name}")
            
        except Exception as e:
            logger.warning(f"Could not apply custom styles: {e}")
    
    def apply_font_settings(self) -> bool:
        """Apply font settings to the application"""
        try:
            if not self.app:
                return False
            
            font_config = (self.prefs.font_family, self.prefs.font_size)
            
            # Apply to main application if it has font methods
            if hasattr(self.app, '_apply_font_size'):
                self.app._apply_font_size(self.prefs.font_size)
            
            # Apply to specific components
            if hasattr(self.app, 'translator_tab_component'):
                try:
                    self.app.translator_tab_component.parent.source_code.configure(font=font_config)
                    self.app.translator_tab_component.parent.target_code.configure(font=font_config)
                except:
                    pass
            
            if hasattr(self.app, 'chatbot_tab_component'):
                try:
                    self.app.chatbot_tab_component.parent.chat_display.configure(font=font_config)
                except:
                    pass
            
            logger.info(f"✅ Applied font: {font_config}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply font settings: {e}")
            return False
    
    def apply_window_settings(self) -> bool:
        """Apply window size and position settings"""
        try:
            if not self.app or not hasattr(self.app, 'root'):
                return False
            
            if self.prefs.remember_window_size:
                geometry = f"{self.prefs.window_width}x{self.prefs.window_height}"
                self.app.root.geometry(geometry)
                logger.info(f"✅ Applied window size: {geometry}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply window settings: {e}")
            return False
    
    def add_recent_file(self, file_path: str):
        """Add file to recent files list"""
        try:
            # Remove if already exists
            if file_path in self.prefs.recent_files:
                self.prefs.recent_files.remove(file_path)
            
            # Add to beginning
            self.prefs.recent_files.insert(0, file_path)
            
            # Limit to max recent files
            self.prefs.recent_files = self.prefs.recent_files[:self.prefs.max_recent_files]
            
            logger.debug(f"Added recent file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error adding recent file: {e}")
    
    def get_recent_files(self) -> list:
        """Get list of recent files"""
        return self.prefs.recent_files.copy()
    
    def show_preferences_dialog(self, parent_window=None):
        """Show the complete preferences dialog"""
        PreferencesDialog(self, parent_window)

class PreferencesDialog:
    """Complete preferences dialog with all settings"""
    
    def __init__(self, prefs_manager: WorkingPreferencesManager, parent=None):
        self.prefs_manager = prefs_manager
        self.prefs = prefs_manager.prefs
        self.parent = parent
        
        # Create dialog window
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("⚙️ CodedSwitch Preferences")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        if parent:
            self.window.transient(parent)
            self.window.grab_set()
        
        # Variables for UI binding
        self.setup_variables()
        
        # Create UI
        self.create_interface()
        
        # Center window
        self.center_window()
        
        logger.info("Preferences dialog opened")
    
    def setup_variables(self):
        """Set up tkinter variables for all preferences"""
        # Appearance
        self.theme_var = tk.StringVar(value=self.prefs.theme)
        self.font_size_var = tk.IntVar(value=self.prefs.font_size)
        self.font_family_var = tk.StringVar(value=self.prefs.font_family)
        
        # Audio
        self.sample_rate_var = tk.IntVar(value=self.prefs.sample_rate)
        self.buffer_size_var = tk.IntVar(value=self.prefs.buffer_size)
        self.master_volume_var = tk.DoubleVar(value=self.prefs.master_volume)
        self.audio_enabled_var = tk.BooleanVar(value=self.prefs.audio_enabled)
        
        # AI
        self.gemini_api_key_var = tk.StringVar(value=self.prefs.gemini_api_key)
        self.ai_model_var = tk.StringVar(value=self.prefs.ai_model)
        self.ai_enabled_var = tk.BooleanVar(value=self.prefs.ai_enabled)
        
        # Editor
        self.auto_save_var = tk.BooleanVar(value=self.prefs.auto_save)
        self.syntax_highlighting_var = tk.BooleanVar(value=self.prefs.syntax_highlighting)
        self.line_numbers_var = tk.BooleanVar(value=self.prefs.line_numbers)
        self.word_wrap_var = tk.BooleanVar(value=self.prefs.word_wrap)
        
        # Window
        self.window_width_var = tk.IntVar(value=self.prefs.window_width)
        self.window_height_var = tk.IntVar(value=self.prefs.window_height)
        self.remember_window_size_var = tk.BooleanVar(value=self.prefs.remember_window_size)
        
        # Advanced
        self.debug_mode_var = tk.BooleanVar(value=self.prefs.debug_mode)
        self.auto_update_check_var = tk.BooleanVar(value=self.prefs.auto_update_check)
        self.telemetry_enabled_var = tk.BooleanVar(value=self.prefs.telemetry_enabled)
    
    def create_interface(self):
        """Create the complete preferences interface"""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="⚙️ CodedSwitch Preferences", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create scrollable frame for content
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create notebook for categories inside scrollable frame
        self.notebook = ttk.Notebook(scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create tabs
        self.create_appearance_tab()
        self.create_audio_tab()
        self.create_ai_tab()
        self.create_editor_tab()
        self.create_window_tab()
        self.create_advanced_tab()
        
        # Buttons frame (outside scrollable area, at bottom)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        self.create_buttons(button_frame)
        
        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎨 Appearance")
        
        # Theme selection
        theme_frame = ttk.LabelFrame(frame, text="Theme", padding=15)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(theme_frame, text="Select Theme:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Theme buttons in a grid
        themes_per_row = 3
        current_theme = self.theme_var.get()
        
        for i, (theme_name, description) in enumerate(self.prefs_manager.available_themes.items()):
            row = i // themes_per_row
            col = i % themes_per_row
            
            # Create frame for each theme
            theme_btn_frame = ttk.Frame(theme_frame)
            if col == 0:
                theme_btn_frame.pack(fill=tk.X, pady=2)
            
            # Theme button
            is_selected = theme_name == current_theme
            btn_style = "success" if is_selected else "outline"
            
            btn = ttk.Button(theme_btn_frame, text=description, 
                           command=lambda t=theme_name: self.preview_theme(t),
                           bootstyle=btn_style, width=25)
            btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Current theme display
        self.current_theme_label = ttk.Label(theme_frame, 
                                           text=f"Current: {self.prefs_manager.available_themes[current_theme]}",
                                           font=('Arial', 10, 'bold'))
        self.current_theme_label.pack(pady=(10, 0))
        
        # Font settings
        font_frame = ttk.LabelFrame(frame, text="Font Settings", padding=15)
        font_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Font family
        font_family_frame = ttk.Frame(font_frame)
        font_family_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_family_frame, text="Font Family:", width=15).pack(side=tk.LEFT)
        font_families = ["Consolas", "Monaco", "Courier New", "Arial", "Helvetica"]
        font_combo = ttk.Combobox(font_family_frame, textvariable=self.font_family_var,
                                 values=font_families, width=20, state="readonly")
        font_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Font size
        font_size_frame = ttk.Frame(font_frame)
        font_size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_size_frame, text="Font Size:", width=15).pack(side=tk.LEFT)
        font_size_spin = ttk.Spinbox(font_size_frame, from_=8, to=24, 
                                    textvariable=self.font_size_var, width=10)
        font_size_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(font_size_frame, text="pixels").pack(side=tk.LEFT, padx=(5, 0))
    
    def create_audio_tab(self):
        """Create audio settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎵 Audio")
        
        # Audio engine settings
        engine_frame = ttk.LabelFrame(frame, text="Audio Engine", padding=15)
        engine_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(engine_frame, text="Enable Audio", 
                       variable=self.audio_enabled_var).pack(anchor=tk.W, pady=5)
        
        # Sample rate
        sample_rate_frame = ttk.Frame(engine_frame)
        sample_rate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sample_rate_frame, text="Sample Rate:", width=15).pack(side=tk.LEFT)
        sample_rates = [22050, 44100, 48000, 96000]
        sample_rate_combo = ttk.Combobox(sample_rate_frame, textvariable=self.sample_rate_var,
                                        values=sample_rates, width=10, state="readonly")
        sample_rate_combo.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(sample_rate_frame, text="Hz").pack(side=tk.LEFT, padx=(5, 0))
        
        # Buffer size
        buffer_frame = ttk.Frame(engine_frame)
        buffer_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(buffer_frame, text="Buffer Size:", width=15).pack(side=tk.LEFT)
        buffer_sizes = [128, 256, 512, 1024, 2048]
        buffer_combo = ttk.Combobox(buffer_frame, textvariable=self.buffer_size_var,
                                   values=buffer_sizes, width=10, state="readonly")
        buffer_combo.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(buffer_frame, text="samples").pack(side=tk.LEFT, padx=(5, 0))
        
        # Master volume
        volume_frame = ttk.Frame(engine_frame)
        volume_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(volume_frame, text="Master Volume:", width=15).pack(side=tk.LEFT)
        volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, 
                                variable=self.master_volume_var, length=200)
        volume_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        self.volume_label = ttk.Label(volume_frame, text=f"{self.master_volume_var.get():.2f}")
        self.volume_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update volume label
        volume_scale.configure(command=self.update_volume_label)
    
    def create_ai_tab(self):
        """Create AI settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🤖 AI")
        
        # AI configuration
        ai_frame = ttk.LabelFrame(frame, text="AI Configuration", padding=15)
        ai_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(ai_frame, text="Enable AI Features", 
                       variable=self.ai_enabled_var).pack(anchor=tk.W, pady=5)
        
        # API Key
        api_frame = ttk.Frame(ai_frame)
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="Gemini API Key:", width=15).pack(side=tk.LEFT)
        api_entry = ttk.Entry(api_frame, textvariable=self.gemini_api_key_var, 
                             width=40, show="*")
        api_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Model selection
        model_frame = ttk.Frame(ai_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="AI Model:", width=15).pack(side=tk.LEFT)
        models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        model_combo = ttk.Combobox(model_frame, textvariable=self.ai_model_var,
                                  values=models, width=20, state="readonly")
        model_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # API key info
        info_frame = ttk.Frame(ai_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = "💡 Get your free Gemini API key at: https://makersuite.google.com/app/apikey"
        ttk.Label(info_frame, text=info_text, foreground="blue").pack(anchor=tk.W)
    
    def create_editor_tab(self):
        """Create editor settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📝 Editor")
        
        # Editor options
        editor_frame = ttk.LabelFrame(frame, text="Editor Options", padding=15)
        editor_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(editor_frame, text="Auto-save files", 
                       variable=self.auto_save_var).pack(anchor=tk.W, pady=3)
        
        ttk.Checkbutton(editor_frame, text="Syntax highlighting", 
                       variable=self.syntax_highlighting_var).pack(anchor=tk.W, pady=3)
        
        ttk.Checkbutton(editor_frame, text="Show line numbers", 
                       variable=self.line_numbers_var).pack(anchor=tk.W, pady=3)
        
        ttk.Checkbutton(editor_frame, text="Word wrap", 
                       variable=self.word_wrap_var).pack(anchor=tk.W, pady=3)
    
    def create_window_tab(self):
        """Create window settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🪟 Window")
        
        # Window options
        window_frame = ttk.LabelFrame(frame, text="Window Options", padding=15)
        window_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(window_frame, text="Remember window size and position", 
                       variable=self.remember_window_size_var).pack(anchor=tk.W, pady=5)
        
        # Default window size
        size_frame = ttk.Frame(window_frame)
        size_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(size_frame, text="Default Size:", width=15).pack(side=tk.LEFT)
        
        ttk.Label(size_frame, text="Width:").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Spinbox(size_frame, from_=800, to=2560, textvariable=self.window_width_var, 
                   width=8).pack(side=tk.LEFT)
        
        ttk.Label(size_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Spinbox(size_frame, from_=600, to=1440, textvariable=self.window_height_var, 
                   width=8).pack(side=tk.LEFT)
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔧 Advanced")
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(frame, text="Advanced Options", padding=15)
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(advanced_frame, text="Enable debug mode", 
                       variable=self.debug_mode_var).pack(anchor=tk.W, pady=3)
        
        ttk.Checkbutton(advanced_frame, text="Check for updates automatically", 
                       variable=self.auto_update_check_var).pack(anchor=tk.W, pady=3)
        
        ttk.Checkbutton(advanced_frame, text="Enable telemetry (anonymous usage data)", 
                       variable=self.telemetry_enabled_var).pack(anchor=tk.W, pady=3)
        
        # Reset section
        reset_frame = ttk.LabelFrame(frame, text="Reset", padding=15)
        reset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(reset_frame, text="Reset all settings to defaults:").pack(anchor=tk.W, pady=(0, 10))
        ttk.Button(reset_frame, text="🔄 Reset All Settings", 
                  command=self.reset_to_defaults, bootstyle="danger").pack(anchor=tk.W)
    
    def create_buttons(self, parent):
        """Create dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Right side buttons
        ttk.Button(button_frame, text="❌ Cancel", command=self.cancel,
                  bootstyle="secondary").pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(button_frame, text="✅ Apply & Save", command=self.apply_and_save,
                  bootstyle="success").pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(button_frame, text="👁️ Apply", command=self.apply_settings,
                  bootstyle="primary").pack(side=tk.RIGHT, padx=(5, 0))
        
        # Left side buttons
        ttk.Button(button_frame, text="📁 Export Settings", command=self.export_settings,
                  bootstyle="info").pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="📂 Import Settings", command=self.import_settings,
                  bootstyle="info").pack(side=tk.LEFT, padx=(5, 0))
    
    def center_window(self):
        """Center the preferences window"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def preview_theme(self, theme_name: str):
        """Preview a theme without saving"""
        if self.prefs_manager.apply_theme(theme_name):
            self.theme_var.set(theme_name)
            description = self.prefs_manager.available_themes[theme_name]
            self.current_theme_label.configure(text=f"Previewing: {description}")
            logger.info(f"Previewing theme: {theme_name}")
    
    def update_volume_label(self, value):
        """Update volume label"""
        self.volume_label.configure(text=f"{float(value):.2f}")
    
    def apply_settings(self):
        """Apply settings without saving"""
        try:
            # Update preferences object
            self.update_preferences_from_ui()
            
            # Apply theme
            if self.prefs_manager.apply_theme(self.theme_var.get()):
                logger.info(f"Applied theme: {self.theme_var.get()}")
            
            # Apply font settings
            self.prefs_manager.apply_font_settings()
            
            # Apply window settings
            self.prefs_manager.apply_window_settings()
            
            # Update current theme label
            description = self.prefs_manager.available_themes[self.theme_var.get()]
            self.current_theme_label.configure(text=f"Current: {description}")
            
            messagebox.showinfo("Settings Applied", "✅ Settings applied successfully!\n\nNote: Some changes may require restart.")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            messagebox.showerror("Apply Error", f"Failed to apply settings: {str(e)}")
    
    def apply_and_save(self):
        """Apply settings and save to file"""
        try:
            # First apply settings
            self.apply_settings()
            
            # Then save preferences
            if self.prefs_manager.save_preferences():
                messagebox.showinfo("Settings Saved", "✅ Settings applied and saved successfully!")
                self.window.destroy()
            else:
                messagebox.showerror("Save Error", "Settings applied but failed to save to file.")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Save Error", f"Failed to save settings: {str(e)}")
    
    def cancel(self):
        """Cancel and close dialog"""
        # Restore original theme
        original_theme = self.prefs.theme
        if original_theme != self.theme_var.get():
            self.prefs_manager.apply_theme(original_theme)
        
        self.window.destroy()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset ALL settings to defaults?\n\n"
                              "This cannot be undone."):
            try:
                # Create new default preferences
                self.prefs_manager.prefs = PreferencesData()
                
                # Update UI variables
                self.update_ui_from_preferences()
                
                # Apply default theme
                self.prefs_manager.apply_theme(self.prefs_manager.prefs.theme)
                
                messagebox.showinfo("Reset Complete", "✅ All settings reset to defaults!")
                
            except Exception as e:
                logger.error(f"Error resetting settings: {e}")
                messagebox.showerror("Reset Error", f"Failed to reset settings: {str(e)}")
    
    def export_settings(self):
        """Export settings to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export CodedSwitch Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Update preferences from UI first
                self.update_preferences_from_ui()
                
                # Export to file
                data = asdict(self.prefs_manager.prefs)
                data['_exported_at'] = datetime.now().isoformat()
                data['_exported_from'] = "CodedSwitch Preferences Dialog"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Export Complete", f"✅ Settings exported to:\n{file_path}")
                
            except Exception as e:
                logger.error(f"Error exporting settings: {e}")
                messagebox.showerror("Export Error", f"Failed to export settings: {str(e)}")
    
    def import_settings(self):
        """Import settings from file"""
        file_path = filedialog.askopenfilename(
            title="Import CodedSwitch Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Remove metadata if present
                for key in ['_exported_at', '_exported_from', '_saved_at', '_version']:
                    data.pop(key, None)
                
                # Create preferences object
                imported_prefs = PreferencesData(**data)
                
                # Ask for confirmation
                if messagebox.askyesno("Import Settings", 
                                     f"Import settings from:\n{file_path}\n\n"
                                     "This will replace your current settings."):
                    
                    # Update preferences
                    self.prefs_manager.prefs = imported_prefs
                    
                    # Update UI
                    self.update_ui_from_preferences()
                    
                    messagebox.showinfo("Import Complete", "✅ Settings imported successfully!")
                
            except Exception as e:
                logger.error(f"Error importing settings: {e}")
                messagebox.showerror("Import Error", f"Failed to import settings: {str(e)}")
    
    def update_preferences_from_ui(self):
        """Update preferences object from UI variables"""
        # Appearance
        self.prefs_manager.prefs.theme = self.theme_var.get()
        self.prefs_manager.prefs.font_size = self.font_size_var.get()
        self.prefs_manager.prefs.font_family = self.font_family_var.get()
        
        # Audio
        self.prefs_manager.prefs.sample_rate = self.sample_rate_var.get()
        self.prefs_manager.prefs.buffer_size = self.buffer_size_var.get()
        self.prefs_manager.prefs.master_volume = self.master_volume_var.get()
        self.prefs_manager.prefs.audio_enabled = self.audio_enabled_var.get()
        
        # AI
        self.prefs_manager.prefs.gemini_api_key = self.gemini_api_key_var.get()
        self.prefs_manager.prefs.ai_model = self.ai_model_var.get()
        self.prefs_manager.prefs.ai_enabled = self.ai_enabled_var.get()
        
        # Editor
        self.prefs_manager.prefs.auto_save = self.auto_save_var.get()
        self.prefs_manager.prefs.syntax_highlighting = self.syntax_highlighting_var.get()
        self.prefs_manager.prefs.line_numbers = self.line_numbers_var.get()
        self.prefs_manager.prefs.word_wrap = self.word_wrap_var.get()
        
        # Window
        self.prefs_manager.prefs.window_width = self.window_width_var.get()
        self.prefs_manager.prefs.window_height = self.window_height_var.get()
        self.prefs_manager.prefs.remember_window_size = self.remember_window_size_var.get()
        
        # Advanced
        self.prefs_manager.prefs.debug_mode = self.debug_mode_var.get()
        self.prefs_manager.prefs.auto_update_check = self.auto_update_check_var.get()
        self.prefs_manager.prefs.telemetry_enabled = self.telemetry_enabled_var.get()
    
    def update_ui_from_preferences(self):
        """Update UI variables from preferences object"""
        prefs = self.prefs_manager.prefs
        
        # Appearance
        self.theme_var.set(prefs.theme)
        self.font_size_var.set(prefs.font_size)
        self.font_family_var.set(prefs.font_family)
        
        # Audio
        self.sample_rate_var.set(prefs.sample_rate)
        self.buffer_size_var.set(prefs.buffer_size)
        self.master_volume_var.set(prefs.master_volume)
        self.audio_enabled_var.set(prefs.audio_enabled)
        
        # AI
        self.gemini_api_key_var.set(prefs.gemini_api_key)
        self.ai_model_var.set(prefs.ai_model)
        self.ai_enabled_var.set(prefs.ai_enabled)
        
        # Editor
        self.auto_save_var.set(prefs.auto_save)
        self.syntax_highlighting_var.set(prefs.syntax_highlighting)
        self.line_numbers_var.set(prefs.line_numbers)
        self.word_wrap_var.set(prefs.word_wrap)
        
        # Window
        self.window_width_var.set(prefs.window_width)
        self.window_height_var.set(prefs.window_height)
        self.remember_window_size_var.set(prefs.remember_window_size)
        
        # Advanced
        self.debug_mode_var.set(prefs.debug_mode)
        self.auto_update_check_var.set(prefs.auto_update_check)
        self.telemetry_enabled_var.set(prefs.telemetry_enabled)


# === INTEGRATION WITH EXISTING CODEDSWITCH ===

def integrate_working_preferences(app_instance):
    """
    Integrate working preferences system with existing CodedSwitch application
    
    Call this from main_gui.py __init__ method
    """
    try:
        # Create preferences manager
        prefs_manager = WorkingPreferencesManager(app_instance)
        
        # Store reference in app
        app_instance.preferences_manager = prefs_manager
        
        # Apply saved preferences on startup
        prefs_manager.apply_theme(prefs_manager.prefs.theme)
        prefs_manager.apply_font_settings()
        prefs_manager.apply_window_settings()
        
        # Create method to show preferences dialog
        def show_preferences():
            prefs_manager.show_preferences_dialog(app_instance.root)
        
        # Replace existing preferences method
        if hasattr(app_instance, 'menu_handlers'):
            app_instance.menu_handlers._show_preferences = show_preferences
        
        logger.info("✅ Working preferences system integrated!")
        logger.info(f"🎨 Current theme: {prefs_manager.prefs.theme}")
        
        return prefs_manager
        
    except Exception as e:
        logger.error(f"❌ Failed to integrate preferences: {e}")
        return None

def apply_dark_theme_immediately(app_instance, theme_name="superhero"):
    """
    Immediately apply a dark theme to CodedSwitch
    
    Use this for quick dark theme application
    """
    try:
        style = Style()
        style.theme_use(theme_name)
        
        logger.info(f"✅ Applied dark theme: {theme_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply dark theme: {e}")
        return False


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    print("🎨 Testing Working Preferences System...")
    
    # Create test application
    root = tk.Tk()
    root.withdraw()  # Hide root window
    
    # Create preferences manager
    prefs_manager = WorkingPreferencesManager()
    
    print(f"✅ Preferences loaded. Current theme: {prefs_manager.prefs.theme}")
    
    # Show preferences dialog
    prefs_manager.show_preferences_dialog()
    
    root.mainloop()

"""
🚀 INTEGRATION INSTRUCTIONS:

1. Save this file as 'working_preferences.py' in your gui_modules folder

2. Update your main_gui.py __init__ method:
   
   Add this near the end of __init__:
   ```python
   from .working_preferences import integrate_working_preferences
   integrate_working_preferences(self)
   ```

3. Update your menu_handlers.py _show_preferences method:
   
   Replace the existing method with:
   ```python
   def _show_preferences(self):
       if hasattr(self.gui, 'preferences_manager'):
           self.gui.preferences_manager.show_preferences_dialog(self.gui.root)
       else:
           messagebox.showinfo("Preferences", "Preferences system not available")
   ```

4. For immediate dark theme, add to main_gui.py:
   ```python
   from .working_preferences import apply_dark_theme_immediately
   apply_dark_theme_immediately(self, "superhero")  # or "darkly", "cyborg", "vapor"
   ```

🎨 AVAILABLE DARK THEMES:
- superhero (Dark blue with orange - RECOMMENDED)
- darkly (Professional dark)
- cyborg (Dark hacker with green)
- vapor (Dark synthwave with neon)
- solar (Solarized dark)

Your preferences will be saved to ~/.codedswitch/preferences.json
and will persist between sessions!
"""