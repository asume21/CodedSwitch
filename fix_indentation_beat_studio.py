"""
Fix indentation errors in beat_studio_professional.py
"""

def fix_indentation():
    """Fix indentation errors in the beat_studio_professional.py file."""
    
    # Read the current file
    with open('beat_studio_professional.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and fix indentation issues
    fixed_lines = []
    in_try_block = False
    proper_indent = ""
    
    for line in lines:
        # Check if we're entering a try block
        if "try:" in line and not in_try_block:
            in_try_block = True
            # Store the proper indentation level
            proper_indent = line[:line.find("try:")]
            fixed_lines.append(line)
        # Check if we're in a try block and need to fix indentation
        elif in_try_block and "drum_track[start_sample:end_sample]" in line:
            # Fix the indentation
            fixed_line = proper_indent + "    " + line.lstrip()
            fixed_lines.append(fixed_line)
        # Check if we're in a try block and need to fix indentation
        elif in_try_block and "melody_track[start_sample:end_sample]" in line:
            # Fix the indentation
            fixed_line = proper_indent + "    " + line.lstrip()
            fixed_lines.append(fixed_line)
        # Check if we're in a try block and need to fix indentation
        elif in_try_block and "bass_track[start_sample:end_sample]" in line:
            # Fix the indentation
            fixed_line = proper_indent + "    " + line.lstrip()
            fixed_lines.append(fixed_line)
        # Check if we're exiting a try block
        elif in_try_block and "except Exception as e:" in line:
            in_try_block = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write back the fixed content
    with open('beat_studio_professional.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Indentation errors fixed in beat_studio_professional.py!")

if __name__ == "__main__":
    fix_indentation()
