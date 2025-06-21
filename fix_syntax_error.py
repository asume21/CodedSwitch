"""
Fix syntax errors in beat_studio_professional.py
"""

def fix_syntax_error():
    """Fix syntax errors in the beat_studio_professional.py file."""
    
    # Read the current file
    with open('beat_studio_professional.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific syntax error with the logger.debug line
    if 'bass_track[start_sample:end_sample] += sound[:end_sample - start_sample]        logger.debug' in content:
        content = content.replace(
            'bass_track[start_sample:end_sample] += sound[:end_sample - start_sample]        logger.debug',
            'bass_track[start_sample:end_sample] += sound[:end_sample - start_sample]\n        logger.debug'
        )
    
    # Fix any other potential syntax errors with missing newlines
    import re
    content = re.sub(r'(\S+)\s{2,}(logger\.debug)', r'\1\n        \2', content)
    
    # Write back the fixed content
    with open('beat_studio_professional.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Syntax errors fixed in beat_studio_professional.py!")

if __name__ == "__main__":
    fix_syntax_error()
