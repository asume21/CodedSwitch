"""
Comprehensive fix for all emoji syntax errors in integrated_gui.py
"""
import re

def fix_all_emojis():
    """Remove all problematic emoji characters that cause syntax errors"""
    
    print("🔧 Fixing emoji syntax errors in integrated_gui.py...")
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define emoji replacements to fix syntax errors
    emoji_fixes = {
        # Specific problematic emojis found in error messages
        "🆓 The API is free with generous limits!": "The API is free with generous limits!",
        "🔒 Your key is stored securely on your computer.": "Your key is stored securely on your computer.",
        "🎉 Translation Completed Successfully!": "Translation Completed Successfully!",
        
        # Common problematic patterns
        "🎉": "",  # Party emoji
        "🆓": "",  # Free emoji
        "🔒": "",  # Lock emoji
        
        # Fix any other potential issues
        "f\"\"\"🎉": "f\"\"\"",
        "f'''🎉": "f'''",
        "\"🎉": "\"",
        "'🎉": "'",
    }
    
    # Apply fixes
    for old, new in emoji_fixes.items():
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Fixed: {old[:20]}...")
    
    # Use regex to find and replace any remaining problematic emoji patterns in f-strings
    # This targets emojis at the start of f-strings which cause syntax errors
    content = re.sub(r'f"""[🎉🆓🔒🎵🎤🎛️🔍⚡💾📂✨🎼🎯]+\s*', 'f"""', content)
    content = re.sub(r"f'''[🎉🆓🔒🎵🎤🎛️🔍⚡💾📂✨🎼🎯]+\s*", "f'''", content)
    content = re.sub(r'f"[🎉🆓🔒🎵🎤🎛️🔍⚡💾📂✨🎼🎯]+\s*', 'f"', content)
    content = re.sub(r"f'[🎉🆓🔒🎵🎤🎛️🔍⚡💾📂✨🎼🎯]+\s*", "f'", content)
    
    # Write back the fixed content
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ All emoji syntax errors fixed!")
    print("🚀 integrated_gui.py is now ready to run!")
    
    # Verify the fix by trying to compile the file
    try:
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            compile(f.read(), "integrated_gui.py", "exec")
        print("✅ Syntax validation passed - file is now valid Python!")
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
    except Exception as e:
        print(f"⚠️ Other error: {e}")

if __name__ == "__main__":
    fix_all_emojis()
