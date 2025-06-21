"""
Final fix to remove ALL problematic Unicode characters from integrated_gui.py
"""
import re

def final_unicode_fix():
    """Remove all problematic Unicode characters including bullets, special symbols, etc."""
    
    print("🔧 Final Unicode cleanup for integrated_gui.py...")
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define problematic Unicode characters and their replacements
    unicode_fixes = {
        # Bullet points and list markers
        "•": "*",  # Bullet point
        "‣": "*",  # Triangular bullet
        "◦": "*",  # White bullet
        "▪": "*",  # Black small square
        "▫": "*",  # White small square
        "‒": "-",  # Figure dash
        "–": "-",  # En dash
        "—": "-",  # Em dash
        "―": "-",  # Horizontal bar
        
        # Quotation marks
        """: '"',  # Left double quotation mark
        """: '"',  # Right double quotation mark
        "'": "'",  # Left single quotation mark
        "'": "'",  # Right single quotation mark
        
        # Other problematic symbols
        "…": "...",  # Horizontal ellipsis
        "′": "'",    # Prime
        "″": '"',    # Double prime
        "‰": "%",    # Per mille sign
        "§": "section",  # Section sign
        "¶": "paragraph",  # Pilcrow sign
        "†": "+",    # Dagger
        "‡": "++",   # Double dagger
        "•": "*",    # Another bullet variant
        "◦": "*",    # Another bullet variant
        "▪": "*",    # Another bullet variant
        "▫": "*",    # Another bullet variant
    }
    
    # Apply character replacements
    for old_char, new_char in unicode_fixes.items():
        if old_char in content:
            count = content.count(old_char)
            content = content.replace(old_char, new_char)
            print(f"✅ Replaced {count} instances of '{old_char}' with '{new_char}'")
    
    # Additional regex patterns for any remaining problematic Unicode
    # Remove any remaining Unicode characters that might cause issues
    # Keep only ASCII printable characters, newlines, tabs, and basic punctuation
    content = re.sub(r'[^\x00-\x7F\n\r\t]', '', content)
    
    # Clean up any formatting issues from replacements
    content = re.sub(r'  +', ' ', content)  # Multiple spaces
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Multiple newlines
    
    # Write back the cleaned content
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ All problematic Unicode characters removed!")
    print("🚀 integrated_gui.py should now be completely syntax-error free!")
    
    # Verify the fix by trying to compile the file
    try:
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            compile(f.read(), "integrated_gui.py", "exec")
        print("✅ SUCCESS: Syntax validation passed - file is now valid Python!")
        return True
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        
        # Show the problematic line and surrounding context
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if e.lineno <= len(lines):
                start = max(0, e.lineno - 3)
                end = min(len(lines), e.lineno + 2)
                print("\nContext around error:")
                for i in range(start, end):
                    marker = ">>> " if i + 1 == e.lineno else "    "
                    print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")
        
        return False
    except Exception as e:
        print(f"⚠️ Other error: {e}")
        return False

if __name__ == "__main__":
    success = final_unicode_fix()
    if success:
        print("\n🎉 READY TO RUN: python main.py")
        print("Your CodedSwitch with Lyric Lab is now ready!")
    else:
        print("\n❌ Still has issues - check the error details above")
