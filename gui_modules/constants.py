"""
Constants and Configuration for CodedSwitch Application - Fixed Version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class Constants:
    """Application constants for better maintainability."""
    
    # GUI Settings
    DEFAULT_FONT_SIZE = 10
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 24
    DEFAULT_WINDOW_SIZE = "1200x800"
    MIN_WINDOW_SIZE = (800, 600)
    
    # Audio Settings (Optional)
    SAMPLE_RATE = 44100
    AUDIO_BUFFER_SIZE = 512
    AUDIO_CHANNELS = 2
    AUDIO_FORMAT = -16
    
    # File Settings
    MAX_CODE_LENGTH = 50000
    CONFIG_DIR = "config"
    TEMP_FILE_PREFIX = "codedswitch_"
    
    # AI Settings
    DEFAULT_MODEL = "gemini-1.5-flash"
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30

# Define available themes
THEMES = {
    "Dark": "darkly",
    "Light": "cosmo", 
    "Monokai": "cyborg",
    "Solarized": "solar",
    "Default": "litera",
    "Superhero": "superhero"
}

# Programming language options
PROGRAMMING_LANGUAGES = [
    "Python", 
    "JavaScript", 
    "Java", 
    "C++", 
    "C#", 
    "PHP", 
    "Ruby", 
    "Go", 
    "Rust", 
    "TypeScript",
    "C",
    "Swift",
    "Kotlin",
    "Scala",
    "Perl"
]

# Enhanced Lyric styles for the Lyric Lab
LYRIC_STYLES = {
    "Boom Bap": {
        "description": "Classic hip-hop with strong emphasis on bars and wordplay",
        "characteristics": "4/4 time, strong snare on 2&4, complex rhyme schemes",
        "examples": "Nas, Jay-Z, Biggie style",
        "prompt_additions": "Focus on complex wordplay, multi-syllable rhymes, storytelling, and lyrical complexity."
    },
    "Trap": {
        "description": "Modern trap style with hard-hitting beats",
        "characteristics": "Hi-hats, 808s, dark atmosphere, aggressive energy",
        "examples": "Future, Migos, Travis Scott style",
        "prompt_additions": "Include triplet flows, ad-libs, repetitive hooks, and street/luxury themes."
    },
    "Drill": {
        "description": "Aggressive drill rap with distinctive flow patterns",
        "characteristics": "Dark beats, sliding 808s, rapid-fire delivery",
        "examples": "Pop Smoke, Fivio Foreign style",
        "prompt_additions": "Use aggressive delivery, street terminology, and drill-specific slang and flow patterns."
    },
    "Melodic": {
        "description": "Melodic rap with singing elements",
        "characteristics": "Autotune, melodic hooks, emotional content",
        "examples": "Drake, Juice WRLD, Lil Uzi style",
        "prompt_additions": "Include melodic hooks, emotional content, mix of singing and rapping, focus on catchiness."
    },
    "UK Drill": {
        "description": "British drill with unique slang and flow patterns",
        "characteristics": "Specific slang, different flow patterns, UK references",
        "examples": "Headie One, Digga D style",
        "prompt_additions": "Use UK slang, British references, and distinctive UK drill flow patterns."
    },
    "CodedSwitch": {
        "description": "Tech-themed rap perfect for CodedSwitch",
        "characteristics": "Programming references, debugging metaphors, tech culture",
        "examples": "Custom CodedSwitch style",
        "prompt_additions": "Heavy use of programming terminology, code metaphors, tech culture references, debugging/optimization themes."
    },
    "Pop": {
        "description": "Mainstream pop style with catchy hooks",
        "characteristics": "Catchy melodies, simple structure, mass appeal",
        "examples": "Taylor Swift, Ariana Grande style",
        "prompt_additions": "Focus on catchy hooks, relatable themes, and memorable choruses."
    },
    "R&B": {
        "description": "Smooth R&B with emotional depth",
        "characteristics": "Smooth vocals, emotional content, romantic themes",
        "examples": "The Weeknd, SZA style",
        "prompt_additions": "Emphasize smooth flow, emotional depth, and romantic or personal themes."
    }
}

# File type associations for different languages
LANGUAGE_EXTENSIONS = {
    "Python": ".py",
    "JavaScript": ".js",
    "Java": ".java",
    "C++": ".cpp",
    "C#": ".cs",
    "PHP": ".php",
    "Ruby": ".rb",
    "Go": ".go",
    "Rust": ".rs",
    "TypeScript": ".ts",
    "C": ".c",
    "Swift": ".swift",
    "Kotlin": ".kt",
    "Scala": ".scala",
    "Perl": ".pl"
}

# Common security vulnerability patterns
SECURITY_PATTERNS = {
    "SQL Injection": [
        r"execute\s*\(\s*[\"'].*?%.*?[\"']\s*%",
        r"cursor\.execute\s*\(\s*[\"'].*?\+.*?[\"']\s*\)",
        r"query\s*=.*?\+.*?input"
    ],
    "XSS Vulnerability": [
        r"innerHTML\s*=.*?input",
        r"document\.write\s*\(.*?input",
        r"eval\s*\(.*?input"
    ],
    "Path Traversal": [
        r"open\s*\(.*?\.\./",
        r"file\s*=.*?\.\./",
        r"path.*?\.\."
    ],
    "Command Injection": [
        r"os\.system\s*\(.*?input",
        r"subprocess\s*\(.*?input",
        r"exec\s*\(.*?input"
    ],
    "Hardcoded Secrets": [
        r"password\s*=\s*[\"'][^\"']+[\"']",
        r"api_key\s*=\s*[\"'][^\"']+[\"']",
        r"secret\s*=\s*[\"'][^\"']+[\"']"
    ]
}

# Error messages
ERROR_MESSAGES = {
    "NO_API_KEY": "AI interface not initialized. Please configure your API key.",
    "NO_CODE": "Please enter source code to translate.",
    "SAME_LANGUAGE": "Source and target languages cannot be the same.",
    "TRANSLATION_FAILED": "Translation failed. Please check your code and try again.",
    "NETWORK_ERROR": "Network error. Please check your internet connection.",
    "INVALID_CODE": "The provided code appears to be invalid or too long."
}

# Application info
APP_INFO = {
    "name": "CodedSwitch",
    "version": "2.0.0",
    "description": "AI-Powered Code Translator",
    "author": "CodedSwitch Team",
    "year": "2024"
}