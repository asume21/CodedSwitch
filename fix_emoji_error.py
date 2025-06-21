"""
Quick fix for emoji syntax error in integrated_gui.py
"""

def fix_emoji_error():
    """Fix the emoji character causing syntax error"""
    
    # Read the file
    with open("integrated_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the problematic emoji with text
    content = content.replace("🆓 The API is free with generous limits!", "The API is free with generous limits!")
    content = content.replace("🔒 Your key is stored securely on your computer.", "Your key is stored securely on your computer.")
    
    # Write back
    with open("integrated_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Fixed emoji syntax error in integrated_gui.py")
    print("🚀 Ready to run the application!")

if __name__ == "__main__":
    fix_emoji_error()
