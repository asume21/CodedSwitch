# GUI Modules Package
"""
CodedSwitch GUI Modules Package - Fixed Version

This package contains modularized GUI components for the CodedSwitch application:
- constants: Application constants and configuration
- utils: Utility classes and error handling
- translator_tab: Code translation functionality
- chatbot_tab: AI chatbot interface
- security_tab: Security vulnerability scanner
- lyric_lab_tab: Lyric generation and analysis
- menu_handlers: Menu bar functionality
- main_gui: Main GUI integration class
"""

# Version info
__version__ = "2.0.0"
__author__ = "CodedSwitch Team"

# Safe imports with fallbacks
def safe_import(module_name, fallback_class=None):
    """Safely import modules with fallback options."""
    try:
        module = __import__(f"gui_modules.{module_name}", fromlist=[module_name])
        return module
    except ImportError:
        try:
            # Try direct import
            module = __import__(module_name)
            return module
        except ImportError:
            if fallback_class:
                return fallback_class
            return None

# Try to import main components
try:
    from .main_gui import IntegratedTranslatorGUI
except ImportError:
    try:
        from main_gui import IntegratedTranslatorGUI
    except ImportError:
        IntegratedTranslatorGUI = None

try:
    from .constants import *
except ImportError:
    try:
        from constants import *
    except ImportError:
        # Fallback constants
        PROGRAMMING_LANGUAGES = ["Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "TypeScript"]

try:
    from .utils import ErrorHandler, ConfigManager, ResourceManager
except ImportError:
    try:
        from utils import ErrorHandler, ConfigManager, ResourceManager
    except ImportError:
        # Minimal fallback classes
        class ErrorHandler:
            @staticmethod
            def handle_error(operation_name: str):
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            import logging
                            logging.error(f"Error in {operation_name}: {e}")
                            import tkinter.messagebox as messagebox
                            messagebox.showerror(f"{operation_name} Error", f"An error occurred: {e}")
                            return None
                    return wrapper
                return decorator
        
        class ConfigManager:
            def __init__(self):
                self.config = {}
            def get(self, key, default=None):
                return self.config.get(key, default)
            def set(self, key, value):
                self.config[key] = value
            def save_config(self):
                pass
        
        class ResourceManager:
            def __init__(self):
                pass
            def cleanup_resources(self):
                pass

# Import tab components with safe fallbacks
try:
    from .translator_tab import TranslatorTab
except ImportError:
    try:
        from translator_tab import TranslatorTab
    except ImportError:
        TranslatorTab = None

try:
    from .chatbot_tab import ChatbotTab
except ImportError:
    try:
        from chatbot_tab import ChatbotTab
    except ImportError:
        ChatbotTab = None

try:
    from .security_tab import SecurityTab
except ImportError:
    try:
        from security_tab import SecurityTab
    except ImportError:
        SecurityTab = None

try:
    from .lyric_lab_tab import LyricLabTab
except ImportError:
    try:
        from lyric_lab_tab import LyricLabTab
    except ImportError:
        LyricLabTab = None

try:
    from .menu_handlers import MenuHandlers
except ImportError:
    try:
        from menu_handlers import MenuHandlers
    except ImportError:
        MenuHandlers = None

# Export main classes
__all__ = [
    'IntegratedTranslatorGUI',
    'TranslatorTab',
    'ChatbotTab', 
    'SecurityTab',
    'LyricLabTab',
    'MenuHandlers',
    'ErrorHandler',
    'ConfigManager',
    'ResourceManager'
]

# Remove None values from __all__
__all__ = [item for item in __all__ if globals().get(item) is not None]