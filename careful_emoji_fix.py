"""
Careful emoji fix that preserves f-string syntax and only removes problematic emojis
"""
import re

def careful_emoji_fix():
    """Remove only the specific emojis causing syntax errors while preserving code structure"""
    
    print("🔧 Applying careful emoji fix to integrated_gui.py...")
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define only the specific problematic emojis that cause syntax errors
    # These are the ones that appear at the start of strings or in problematic positions
    specific_emoji_fixes = [
        # Specific problematic patterns from error messages
        ("🆓 The API is free with generous limits!", "The API is free with generous limits!"),
        ("🔒 Your key is stored securely on your computer.", "Your key is stored securely on your computer."),
        ("🎉 Translation Completed Successfully!", "Translation Completed Successfully!"),
        ("📊 Translation Metrics:", "Translation Metrics:"),
        
        # Remove standalone emojis that cause issues
        ("🆓", ""),
        ("🔒", ""),
        ("🎉", ""),
        ("📊", ""),
        ("•", "*"),  # Replace bullet with asterisk
        
        # Fix any f-string issues
        ('f"""🎉', 'f"""'),
        ('f"""📊', 'f"""'),
        ('f"""🆓', 'f"""'),
        ('f"""🔒', 'f"""'),
    ]
    
    # Apply specific fixes
    changes_made = 0
    for old_pattern, new_pattern in specific_emoji_fixes:
        if old_pattern in content:
            count = content.count(old_pattern)
            content = content.replace(old_pattern, new_pattern)
            changes_made += count
            print(f"✅ Fixed {count} instances of: {old_pattern[:30]}...")
    
    print(f"✅ Made {changes_made} specific fixes")
    
    # Write back the fixed content
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Careful emoji fix applied!")
    
    # Verify the fix by trying to compile the file
    try:
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            compile(f.read(), "integrated_gui.py", "exec")
        print("✅ SUCCESS: Syntax validation passed - file is now valid Python!")
        return True
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        
        # Show the problematic line
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if e.lineno <= len(lines):
                problematic_line = lines[e.lineno - 1].strip()
                print(f"Problematic line: {problematic_line}")
                
                # Check if it's an emoji issue
                emoji_chars = []
                for char in problematic_line:
                    if ord(char) > 127:  # Non-ASCII character
                        emoji_chars.append(f"'{char}' (U+{ord(char):04X})")
                
                if emoji_chars:
                    print(f"Non-ASCII characters found: {', '.join(emoji_chars)}")
        
        return False
    except Exception as e:
        print(f"⚠️ Other error: {e}")
        return False

if __name__ == "__main__":
    success = careful_emoji_fix()
    if success:
        print("\n🎉 READY TO RUN: python main.py")
        print("Your CodedSwitch with Lyric Lab is now ready!")
    else:
        print("\n❌ Still has issues - may need additional fixes")
