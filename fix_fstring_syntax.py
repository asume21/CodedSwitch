"""
Fix the specific f-string syntax error in integrated_gui.py
"""

def fix_fstring_syntax():
    """Fix the broken f-string and remove remaining problematic emojis"""
    
    print("🔧 Fixing f-string syntax error...")
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Fix the specific broken f-string
    broken_fstring = '''feedback = f"""Translation Completed Successfully!

Translation Metrics:'''
    
    fixed_fstring = '''feedback = f"""Translation Completed Successfully!

Translation Metrics:'''
    
    if broken_fstring in content:
        content = content.replace(broken_fstring, fixed_fstring)
        print("✅ Fixed broken f-string")
    
    # Remove remaining problematic emojis
    emoji_fixes = {
        "💡": "",
        "🔧": "",
        "✨": "",
        "→": "->",
    }
    
    for emoji, replacement in emoji_fixes.items():
        if emoji in content:
            count = content.count(emoji)
            content = content.replace(emoji, replacement)
            print(f"✅ Replaced {count} instances of '{emoji}'")
    
    # Write back the fixed content
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ F-string syntax fixed!")
    
    # Verify the fix
    try:
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            compile(f.read(), "integrated_gui.py", "exec")
        print("✅ SUCCESS: Syntax validation passed!")
        return True
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"⚠️ Other error: {e}")
        return False

if __name__ == "__main__":
    success = fix_fstring_syntax()
    if success:
        print("\n🎉 READY TO RUN: python main.py")
    else:
        print("\n❌ Still has issues")
