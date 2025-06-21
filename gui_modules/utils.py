"""
Utility Classes and Functions for CodedSwitch Application - Fixed Version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import json
import functools
from pathlib import Path
from typing import Any, Optional
from tkinter import messagebox

logger = logging.getLogger(__name__)

# Import constants safely
try:
    from .constants import Constants
except ImportError:
    try:
        from constants import Constants
    except ImportError:
        # Fallback constants
        class Constants:
            MAX_CODE_LENGTH = 50000
            DEFAULT_FONT_SIZE = 10
            MIN_FONT_SIZE = 8
            MAX_FONT_SIZE = 24
            DEFAULT_WINDOW_SIZE = "1200x800"
            MIN_WINDOW_SIZE = (800, 600)
            CONFIG_DIR = "config"
            DEFAULT_MODEL = "gemini-1.5-flash"
            MAX_RETRIES = 3
            TIMEOUT_SECONDS = 30

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_code(code: str, max_length: int = Constants.MAX_CODE_LENGTH) -> tuple[bool, str]:
        """Validate code input with helpful error messages."""
        if not code or not code.strip():
            return False, "Code cannot be empty"
        
        if len(code) > max_length:
            return False, f"Code exceeds maximum length of {max_length} characters"
        
        # Check for suspicious patterns
        suspicious_patterns = ['rm -rf', 'del /f', 'format c:', 'sudo rm']
        for pattern in suspicious_patterns:
            if pattern in code.lower():
                return False, f"Potentially dangerous command detected: {pattern}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_api_key(api_key: str) -> tuple[bool, str]:
        """Validate API key format."""
        if not api_key or not api_key.strip():
            return False, "API key cannot be empty"
        
        if len(api_key) < 10:
            return False, "API key appears too short"
        
        return True, "Valid"

class ConfigManager:
    """Enhanced configuration management."""
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration with defaults and validation."""
        default_config = {
            "theme": "Dark",
            "font_size": Constants.DEFAULT_FONT_SIZE,
            "window_size": Constants.DEFAULT_WINDOW_SIZE,
            "auto_save": True,
            "gemini_model": Constants.DEFAULT_MODEL,
            "audio_enabled": True,
            "premium_features": False,
            "security_scanning": True,
            "last_source_lang": "Python",
            "last_target_lang": "JavaScript"
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            else:
                # Create config directory if it doesn't exist
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                self.save_config()
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        return default_config
    
    def save_config(self) -> bool:
        """Save current configuration safely."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value safely."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

class ErrorHandler:
    """Centralized error handling and user messaging."""
    
    @staticmethod
    def handle_error(operation_name: str):
        """Decorator for consistent error handling."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {operation_name}: {e}", exc_info=True)
                    if hasattr(self, 'parent') and hasattr(self.parent, 'status_var'):
                        self.parent.status_var.set(f"❌ {operation_name} failed")
                    elif hasattr(self, 'status_var'):
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
            return "Network connection issue. Please check your internet connection."
        elif "timeout" in error_lower:
            return "Operation timed out. Please try again."
        elif "file" in error_lower and "not found" in error_lower:
            return "Required file not found. Please check file paths."
        elif "permission" in error_lower:
            return "Permission denied. Please check file permissions."
        elif "import" in error_lower or "module" in error_lower:
            return "Missing dependency. Please install required packages."
        else:
            return "An unexpected error occurred."

class ResourceManager:
    """Manages application resources and cleanup."""
    
    def __init__(self):
        self.temp_files = []
        self.audio_initialized = False
        self.threads = []
    
    def add_temp_file(self, file_path: str):
        """Add temporary file for cleanup."""
        self.temp_files.append(file_path)
    
    def cleanup_resources(self):
        """Clean up all resources."""
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                Path(temp_file).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {e}")
        
        # Stop audio system if initialized
        if self.audio_initialized:
            try:
                import pygame
                pygame.mixer.quit()
                pygame.quit()
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Failed to cleanup audio: {e}")
        
        logger.info("Resource cleanup completed")

# Utility functions
def safe_import(module_name, fallback=None):
    """Safely import a module with fallback."""
    try:
        return __import__(module_name)
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {e}")
        return fallback

def get_language_extension(language: str) -> str:
    """Get file extension for programming language."""
    extensions = {
        "python": ".py",
        "javascript": ".js",
        "java": ".java",
        "c++": ".cpp",
        "c#": ".cs",
        "php": ".php",
        "ruby": ".rb",
        "go": ".go",
        "rust": ".rs",
        "typescript": ".ts",
        "c": ".c",
        "swift": ".swift",
        "kotlin": ".kt"
    }
    return extensions.get(language.lower(), ".txt")

def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
    """Validate file size."""
    try:
        file_size = Path(file_path).stat().st_size
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    except Exception:
        return False