"""
Remove ALL emoji characters from integrated_gui.py to fix syntax errors
"""
import re

def remove_all_emojis():
    """Remove all emoji characters that could cause syntax errors"""
    
    print("🔧 Removing ALL emojis from integrated_gui.py...")
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define emoji pattern - matches most Unicode emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+", 
        flags=re.UNICODE
    )
    
    # Count emojis before removal
    emojis_found = emoji_pattern.findall(content)
    print(f"Found {len(emojis_found)} emoji characters to remove")
    
    # Remove all emojis
    content_clean = emoji_pattern.sub('', content)
    
    # Clean up any double spaces left by emoji removal
    content_clean = re.sub(r'  +', ' ', content_clean)
    
    # Clean up lines that might be empty after emoji removal
    content_clean = re.sub(r'\n\s*\n\s*\n', '\n\n', content_clean)
    
    # Write back the cleaned content
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content_clean)
    
    print(f"✅ Removed {len(emojis_found)} emoji characters!")
    print("🚀 integrated_gui.py should now be syntax-error free!")
    
    # Verify the fix by trying to compile the file
    try:
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            compile(f.read(), "integrated_gui.py", "exec")
        print("✅ SUCCESS: Syntax validation passed - file is now valid Python!")
        return True
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"⚠️ Other error: {e}")
        return False

if __name__ == "__main__":
    success = remove_all_emojis()
    if success:
        print("\n🎉 Ready to run: python main.py")
    else:
        print("\n❌ Still has issues - may need manual fixing")
