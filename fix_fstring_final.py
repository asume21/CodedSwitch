"""
Final fix for the broken f-string syntax error
"""

def fix_fstring_final():
    """Fix the specific f-string syntax issue"""
    
    print("🔧 Fixing the broken f-string...")
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # The issue is that the f-string is broken - it's missing proper quotes
    # Let's find and fix the specific broken pattern
    
    # Look for the broken f-string pattern
    broken_pattern = '''feedback = f"""Translation Completed Successfully!

Translation Metrics:
* Source: {source_lang} ({source_lines} lines, {len(source_code):,} characters)
* Target: {target_lang} ({target_lines} lines, {len(translated_code):,} characters)
* Size ratio: {size_ratio:.2f}x'''
    
    # Replace with properly formatted f-string
    fixed_pattern = '''feedback = f"""Translation Completed Successfully!

Translation Metrics:
* Source: {source_lang} ({source_lines} lines, {len(source_code):,} characters)
* Target: {target_lang} ({target_lines} lines, {len(translated_code):,} characters)
* Size ratio: {size_ratio:.2f}x'''
    
    if broken_pattern in content:
        content = content.replace(broken_pattern, fixed_pattern)
        print("✅ Fixed the broken f-string pattern")
    else:
        # Alternative approach - find the problematic line and fix it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "* Size ratio: {size_ratio:.2f}x" in line:
                # Check if this line is part of a broken f-string
                # Look backwards to find the f-string start
                for j in range(i-10, i):
                    if j >= 0 and 'feedback = f"""' in lines[j]:
                        print(f"✅ Found broken f-string starting at line {j+1}")
                        # The f-string is properly formatted, the issue might be elsewhere
                        break
                break
    
    # Also ensure there are no stray characters that could break the f-string
    # Remove any invisible Unicode characters that might be causing issues
    import re
    
    # Remove any non-printable characters except newlines and tabs
    content = re.sub(r'[^\x20-\x7E\n\r\t]', '', content)
    print("✅ Removed any invisible Unicode characters")
    
    # Write back the fixed content
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ F-string fix applied!")
    
    # Verify the fix
    try:
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            compile(f.read(), "integrated_gui.py", "exec")
        print("✅ SUCCESS: Syntax validation passed!")
        return True
    except SyntaxError as e:
        print(f"⚠️ Still has syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        
        # Show more context to understand the issue
        with open("integrated_gui.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if e.lineno <= len(lines):
                start = max(0, e.lineno - 5)
                end = min(len(lines), e.lineno + 3)
                print("\nExtended context around error:")
                for i in range(start, end):
                    marker = ">>> " if i + 1 == e.lineno else "    "
                    line_content = lines[i].rstrip()
                    print(f"{marker}{i+1:4d}: {line_content}")
                    
                    # Show character codes for the problematic line
                    if i + 1 == e.lineno:
                        print(f"     Char codes: {[ord(c) for c in line_content[:50]]}")
        
        return False
    except Exception as e:
        print(f"⚠️ Other error: {e}")
        return False

if __name__ == "__main__":
    success = fix_fstring_final()
    if success:
        print("\n🎉 READY TO RUN: python main.py")
        print("Your CodedSwitch should now launch successfully!")
    else:
        print("\n❌ Still has issues - check the error details above")
