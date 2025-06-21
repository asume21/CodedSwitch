"""
Fix the specific emoji characters visible in the code editor
"""

def fix_specific_emojis():
    """Remove the specific emojis causing syntax errors"""
    
    print("🔧 Fixing specific emoji characters...")
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Fix the specific emojis you can see in the editor
    specific_fixes = [
        # Demo mode button
        ('text="🚀 Demo Mode"', 'text="Demo Mode"'),
        
        # Help button  
        ('text="❓ Help"', 'text="? Help"'),
        
        # Any other common problematic patterns
        ('🚀', ''),
        ('❓', '?'),
        ('💡', ''),
        ('🔧', ''),
        ('✨', ''),
        ('→', '->'),
    ]
    
    changes_made = 0
    for old_pattern, new_pattern in specific_fixes:
        if old_pattern in content:
            count = content.count(old_pattern)
            content = content.replace(old_pattern, new_pattern)
            changes_made += count
            print(f"✅ Fixed {count} instances of: {old_pattern}")
    
    print(f"✅ Made {changes_made} specific emoji fixes")
    
    # Write back the fixed content
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Specific emoji fix applied!")
    
    # Verify the fix
    try:
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            compile(f.read(), "integrated_gui.py", "exec")
        print("✅ SUCCESS: Syntax validation passed!")
        return True
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        
        # Show context around the error
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if e.lineno <= len(lines):
                start = max(0, e.lineno - 2)
                end = min(len(lines), e.lineno + 1)
                print("\nContext around error:")
                for i in range(start, end):
                    marker = ">>> " if i + 1 == e.lineno else "    "
                    print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")
        
        return False
    except Exception as e:
        print(f"⚠️ Other error: {e}")
        return False

if __name__ == "__main__":
    success = fix_specific_emojis()
    if success:
        print("\n🎉 READY TO RUN: python main.py")
        print("Your CodedSwitch should now launch successfully!")
    else:
        print("\n❌ Still has issues - check the error details above")
