#!/usr/bin/env python3
"""
Quick Setup Script for AI Code Translator
Automates the entire installation process for new users.
"""

import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path

def print_banner():
    """Print welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🚀 AI Code Translator Setup 🚀                ║
║                                                              ║
║        Universal Code Translation & Security Platform        ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Error: Python 3.11+ is required!")
        print(f"   Your version: Python {version.major}.{version.minor}")
        print("   Please upgrade Python and try again.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor} detected - Compatible!")

def run_command(command, description):
    """Run a shell command with user feedback."""
    print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"   Error: {e.stderr}")
        return False

def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists!")
        return True
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    return True

def install_dependencies():
    """Install required packages."""
    system = platform.system()
    
    # Determine pip command based on OS
    if system == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def setup_api_key():
    """Guide user through API key setup."""
    print("\n🔑 API Key Setup:")
    print("   1. Visit: https://makersuite.google.com/app/apikey")
    print("   2. Sign in with your Google account")
    print("   3. Click 'Create API Key'")
    print("   4. Copy the generated key")
    
    open_browser = input("\n   Open API key page in browser? (y/n): ").lower()
    if open_browser in ['y', 'yes']:
        webbrowser.open("https://makersuite.google.com/app/apikey")
    
    api_key = input("\n   Paste your API key here (or press Enter to skip): ").strip()
    
    if api_key:
        # Save to environment file
        with open(".env", "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print("✅ API key saved!")
        return True
    else:
        print("⚠️  API key skipped - you can set it up later in the app")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)."""
    if platform.system() != "Windows":
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "AI Code Translator.lnk")
        target = os.path.join(os.getcwd(), "run.bat")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = target
        shortcut.save()
        
        print("✅ Desktop shortcut created!")
    except ImportError:
        print("⚠️  Desktop shortcut creation skipped (missing dependencies)")

def final_instructions():
    """Show final setup instructions."""
    system = platform.system()
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE! 🎉")
    print("="*60)
    
    print("\n🚀 How to run the application:")
    
    if system == "Windows":
        print("   Option 1: Double-click 'run.bat'")
        print("   Option 2: Run 'python integrated_gui.py'")
    else:
        print("   1. Activate environment: source venv/bin/activate")
        print("   2. Run application: python integrated_gui.py")
    
    print("\n📚 Quick Start Guide:")
    print("   1. Open the Translator tab")
    print("   2. Paste some Python code")
    print("   3. Select target language (JavaScript)")
    print("   4. Click translate and watch the magic!")
    
    print("\n🛡️ Try the Security Scanner:")
    print("   1. Go to Security Scanner tab")
    print("   2. Click 'Load Test Code'")
    print("   3. Click 'Scan for Vulnerabilities'")
    print("   4. See AI find 17+ security issues!")
    
    print("\n💬 Chat with Astutely:")
    print("   1. Open Astutely Chat tab")
    print("   2. Ask: 'Explain this Python code: print(\"Hello\")'")
    print("   3. Get instant AI assistance!")
    
    print("\n🎨 Customize Your Experience:")
    print("   • View → Theme to change appearance")
    print("   • Edit → Font Size to adjust text")
    print("   • View → Settings for advanced options")

def main():
    """Main setup routine."""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Setup steps
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📦 {step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("   Please check the error messages above.")
            input("Press Enter to exit...")
            sys.exit(1)
    
    # Optional steps
    print(f"\n🔑 Setting up API key...")
    setup_api_key()
    
    if platform.system() == "Windows":
        create_shortcut = input("\n   Create desktop shortcut? (y/n): ").lower()
        if create_shortcut in ['y', 'yes']:
            create_desktop_shortcut()
    
    # Success!
    final_instructions()
    
    # Ask to launch
    launch_now = input(f"\n🚀 Launch AI Code Translator now? (y/n): ").lower()
    if launch_now in ['y', 'yes']:
        if platform.system() == "Windows":
            subprocess.Popen(["run.bat"], shell=True)
        else:
            subprocess.Popen([sys.executable, "integrated_gui.py"])
    
    print("\n✨ Enjoy using AI Code Translator! ✨")
    input("Press Enter to exit setup...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   Please report this issue on GitHub.")
        input("Press Enter to exit...")
        sys.exit(1)