#!/usr/bin/env python3
"""
CodedSwitch - AI Code Translator
Fixed Production Entry Point

A powerful AI-powered code translation tool with advanced features including:
- Multi-language code translation
- AI chatbot assistance
- Security vulnerability scanning
- Lyric generation and analysis
- Modern GUI with ttkbootstrap styling

Author: CodedSwitch Development Team
Version: 2.0.0 (Production Fixed)
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Add your Gemini API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo'

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_production_logging():
    """Set up production-level logging configuration."""
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    log_filename = logs_dir / f"codedswitch_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("🚀 CodedSwitch Production Launch (Fixed)")
    logger.info(f"📁 Working Directory: {os.getcwd()}")
    logger.info(f"🐍 Python Version: {sys.version}")
    logger.info("=" * 60)
    
    return logger

def check_core_dependencies():
    """Check and validate core required dependencies."""
    core_modules = [
        'tkinter',
        'ttkbootstrap',
        'threading',
        'json',
        'datetime',
        're'
    ]
    
    logger = logging.getLogger(__name__)
    missing_modules = []
    
    for module in core_modules:
        try:
            __import__(module)
            logger.debug(f"✅ {module} - OK")
        except ImportError:
            missing_modules.append(module)
            logger.error(f"❌ {module} - MISSING")
    
    # Special check for ttkbootstrap since it's critical
    try:
        import ttkbootstrap as ttk
        logger.info("✅ ttkbootstrap imported successfully")
        
        # Test creating a simple style to make sure it works
        try:
            style = ttk.Style()
            logger.info(f"✅ ttkbootstrap Style created successfully - Theme: {style.theme_use()}")
        except Exception as e:
            logger.warning(f"⚠️ ttkbootstrap Style creation failed: {e}")
    except ImportError:
        logger.error("❌ ttkbootstrap is MISSING - this is critical for the GUI!")
        missing_modules.append('ttkbootstrap')
    
    if missing_modules:
        logger.error(f"Missing required modules: {missing_modules}")
        print("\n🚨 Missing Core Dependencies!")
        print("Please install required modules:")
        if 'ttkbootstrap' in missing_modules:
            print("pip install ttkbootstrap")
        if 'tkinter' in missing_modules:
            print("\nNote: tkinter should come with Python. You may need to install python3-tk on Linux.")
        return False
    
    logger.info("✅ All core dependencies satisfied")
    return True

def check_optional_dependencies():
    """Check optional dependencies and warn if missing."""
    optional_modules = {
        'pygame': 'Audio playback features',
        'numpy': 'Advanced audio processing',
        'scipy': 'Audio analysis features',
        'sounddevice': 'Audio recording',
        'google.generativeai': 'AI features (Gemini)'
    }
    
    logger = logging.getLogger(__name__)
    available_features = []
    missing_features = []
    
    for module, feature in optional_modules.items():
        try:
            __import__(module)
            available_features.append(feature)
            logger.debug(f"✅ {module} - {feature} available")
        except ImportError:
            missing_features.append(f"{module} ({feature})")
            logger.warning(f"⚠️ {module} - {feature} not available")
    
    if missing_features:
        logger.info("Some optional features are not available:")
        for feature in missing_features:
            logger.info(f"  - {feature}")
        logger.info("Install optional dependencies for full functionality")
    
    return len(available_features) > 0

def setup_environment():
    """Set up environment variables and configuration."""
    logger = logging.getLogger(__name__)
    
    # Check for API keys
    api_keys = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'API_KEY': os.getenv('API_KEY')
    }
    
    has_api_key = any(api_keys.values())
    
    if has_api_key:
        logger.info("🔑 API key(s) detected - AI features will be available")
    else:
        logger.warning("⚠️  No API keys found - AI features will use fallback mode")
        logger.info("💡 Set GEMINI_API_KEY environment variable for full AI functionality")
    
    return has_api_key

def import_gui_safely():
    """Import GUI modules with proper error handling."""
    logger = logging.getLogger(__name__)
    
    try:
        # Import from the working integrated_gui.py file
        logger.info("🔧 Attempting to import from integrated_gui.py...")
        from integrated_gui import IntegratedTranslatorGUI
        logger.info("✅ GUI imported successfully from integrated_gui.py")
        return IntegratedTranslatorGUI
        
    except ImportError as e:
        logger.error(f"❌ Failed to import from integrated_gui.py: {e}")
        logger.error(f"📁 Current working directory: {os.getcwd()}")
        
        # Check if integrated_gui.py exists
        if not os.path.exists('integrated_gui.py'):
            logger.error("❌ integrated_gui.py not found!")
            raise ImportError("integrated_gui.py file is missing from the current directory")
        
        logger.error("❌ integrated_gui.py exists but import failed")
        logger.error("This might be due to missing dependencies in integrated_gui.py")
        
        raise ImportError(f"Could not import from integrated_gui.py: {e}")
    
    except Exception as e:
        logger.error(f"❌ Unexpected error importing GUI: {e}")
        logger.error(traceback.format_exc())
        raise ImportError(f"Unexpected error importing GUI: {e}")

def initialize_ai_interface():
    """Initialize AI interface with proper error handling."""
    logger = logging.getLogger(__name__)
    
    try:
        # Check if integrated_ai.py exists
        if not os.path.exists('integrated_ai.py'):
            logger.warning("⚠️ integrated_ai.py not found - AI features will be limited")
            return None
        
        # Try to import and initialize AI interface
        logger.info("🤖 Importing AI interface...")
        from integrated_ai import IntegratedTranslatorAI
        
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY') or os.getenv('API_KEY')
        
        if api_key:
            logger.info("🔑 API key found, initializing AI interface...")
            ai_interface = IntegratedTranslatorAI(api_key=api_key)
            logger.info("🤖 AI interface initialized successfully with API key")
            return ai_interface
        else:
            logger.warning("⚠️ No API key found - AI features will be limited")
            logger.info("💡 Set GEMINI_API_KEY environment variable for full AI functionality")
            logger.info("💡 You can still use CodedSwitch, but AI features won't work")
            logger.info("💡 Set GEMINI_API_KEY environment variable for full functionality")
            return None
            
    except ImportError as e:
        logger.warning(f"⚠️ AI interface import failed: {e}")
        logger.info("💡 You can still use CodedSwitch without AI features")
        return None
    except Exception as e:
        logger.warning(f"⚠️ AI interface initialization failed: {e}")
        logger.info("💡 You can still use CodedSwitch without AI features")
        return None

def verify_file_structure():
    """Verify that all required files are present."""
    logger = logging.getLogger(__name__)
    
    # Check for integrated_gui.py first
    if not os.path.exists('integrated_gui.py'):
        logger.error("❌ integrated_gui.py not found!")
        return False
    
    # Also check for integrated_ai.py in root
    if not os.path.exists('integrated_ai.py'):
        logger.warning("⚠️ integrated_ai.py not found in root directory")
    else:
        logger.debug("✅ Found: integrated_ai.py")
    
    logger.info("✅ All required GUI files found")
    return True

def main():
    """Main production entry point with comprehensive error handling."""
    try:
        # Setup logging first
        logger = setup_production_logging()
        
        # Verify file structure
        logger.info("📂 Checking file structure...")
        if not verify_file_structure():
            print("\n💥 Critical Error: Missing required files!")
            print("Please ensure all CodedSwitch files are in the same directory.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Check core dependencies
        logger.info("🔍 Checking dependencies...")
        if not check_core_dependencies():
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        # Check optional dependencies (warnings only)
        check_optional_dependencies()
        
        # Setup environment
        has_api_key = setup_environment()
        
        # Import GUI safely
        logger.info("🔧 Importing GUI modules...")
        try:
            IntegratedTranslatorGUI = import_gui_safely()
        except ImportError as e:
            logger.error(f"💥 Critical error: Could not import GUI: {e}")
            print(f"\n💥 Critical Error: {e}")
            print("\nTroubleshooting steps:")
            print("1. Make sure all .py files are in the same directory")
            print("2. Check that integrated_gui.py exists and is not corrupted")
            print("3. Try running: pip install ttkbootstrap")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        # Initialize AI interface
        logger.info("🤖 Initializing AI interface...")
        ai_interface = initialize_ai_interface()
        
        if ai_interface:
            logger.info("🚀 AI features enabled!")
        else:
            logger.info("🚀 Starting without AI features")
        
        # Create and start GUI
        logger.info("🎨 Creating GUI application...")
        try:
            app = IntegratedTranslatorGUI(
                gemini_api_key=os.environ.get("GEMINI_API_KEY"),
                gemini_model="gemini-1.5-flash",
                enable_premium=True,
                enable_security=True
            )
            logger.info("✅ GUI created successfully!")
            
            # Check if the GUI actually has a root window
            if hasattr(app, 'root') and app.root:
                logger.info("✅ GUI root window exists")
                logger.info(f"📐 Window geometry: {app.root.geometry()}")
                logger.info(f"🎨 Window title: {app.root.title()}")
                
                # Check if tabs were created
                if hasattr(app, 'notebook') and app.notebook:
                    tab_count = len(app.notebook.tabs())
                    logger.info(f"📂 Number of tabs created: {tab_count}")
                    if tab_count == 0:
                        logger.warning("⚠️ No tabs were created - this might explain the blank window!")
                    else:
                        for i in range(tab_count):
                            tab_text = app.notebook.tab(i, "text")
                            logger.info(f"📋 Tab {i}: {tab_text}")
                else:
                    logger.warning("⚠️ Notebook widget not created!")
            else:
                logger.error("❌ GUI root window not created properly!")
                
        except Exception as e:
            logger.error(f"💥 Failed to create GUI: {e}")
            logger.error(traceback.format_exc())
            print(f"\n💥 Failed to create GUI: {e}")
            print("\nThis might be due to:")
            print("1. Missing ttkbootstrap: pip install ttkbootstrap")
            print("2. Display issues (if running remotely)")
            print("3. Import errors in GUI modules")
            print("4. Check the log file for detailed error information")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        logger.info("🎯 Launching CodedSwitch interface...")
        logger.info("✅ CodedSwitch launched successfully!")
        
        # Start the main event loop
        try:
            logger.info("🔄 Starting main event loop...")
            app.run()
        except Exception as e:
            logger.error(f"💥 Error during GUI execution: {e}")
            logger.error(traceback.format_exc())
            print(f"\n💥 Runtime Error: {e}")
            input("\nPress Enter to exit...")
        
        logger.info("👋 CodedSwitch session ended normally")
        
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user (Ctrl+C)")
        
    except Exception as e:
        logger.error("💥 Critical error in main application:")
        logger.error(traceback.format_exc())
        print(f"\n💥 Critical Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nPlease check the log file for detailed error information.")
        print(f"Log location: {project_root}/logs/")
        
        # Additional troubleshooting info
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're running Python 3.7 or higher")
        print("2. Install dependencies: pip install ttkbootstrap")
        print("3. Ensure all .py files are in the same directory")
        print("4. Check the log file for more details")
        
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    # Production banner
    print("🚀 CodedSwitch - AI Code Translator v2.0.0 (Fixed)")
    print("=" * 55)
    print("🎯 Production Mode - Enhanced Error Handling")
    print("📚 Loading application components...")
    print()
    
    main()