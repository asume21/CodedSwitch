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
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    # Note: logger not available yet, will log later

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
            stream = self.stream
            # Replace any characters that can't be encoded with a replacement character
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # If we can't encode the message, try to log a simplified version
            try:
                stream.write(record.msg.encode('ascii', 'replace').decode('ascii') + '\n')
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
    logger.warning(f"Failed to import some modules: {e}. Using fallback implementations.")
    
    # Create fallback classes if imports fail
    class PremiumManager:
        def is_premium(self):
            return True
        def get_license_info(self):
            return {'type': 'premium', 'days_remaining': 30}
    
    class VulnerabilityScanner:
        def scan_code(self, code, language):
            return []
