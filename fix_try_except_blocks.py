"""
Fix try-except blocks in beat_studio_professional.py
"""

def fix_try_except_blocks():
    """Fix the broken try-except blocks in beat_studio_professional.py."""
    
    # Read the current file
    with open('beat_studio_professional.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a clean version of the file without our broken modifications
    # First, backup the current broken file
    with open('beat_studio_professional.py.broken', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Backed up broken file to beat_studio_professional.py.broken")
    
    # Get the original file from a backup if available, or create a clean version
    try:
        with open('beat_studio_professional.py.orig', 'r', encoding='utf-8') as f:
            original_content = f.read()
        print("✅ Using original backup file")
    except FileNotFoundError:
        # No backup available, we'll need to clean up the file manually
        print("⚠️ No original backup found. Creating a clean version manually...")
        
        # Replace broken try-except blocks with original code
        # This is a simplified approach - in a real scenario we might need more sophisticated parsing
        
        # Fix drum track rendering
        if "try:" in content and "drum_track[start_sample:end_sample]" in content:
            content = content.replace(
                "try:\n                sound_slice = sound[:end_sample - start_sample]\n                if sound_slice.shape != drum_track[start_sample:end_sample].shape:\n                    logger.warning(f\"Shape mismatch! Reshaping sound_slice from {sound_slice.shape} to {drum_track[start_sample:end_sample].shape}\")\n                    # Ensure shapes match by truncating or padding\n                    target_shape = drum_track[start_sample:end_sample].shape\n                    if len(sound_slice) > len(drum_track[start_sample:end_sample]):\n                        sound_slice = sound_slice[:len(drum_track[start_sample:end_sample])]\n                    elif len(sound_slice) < len(drum_track[start_sample:end_sample]):\n                        pad_length = len(drum_track[start_sample:end_sample]) - len(sound_slice)\n                        sound_slice = np.pad(sound_slice, (0, pad_length), \"constant\")\n                drum_track[start_sample:end_sample] += sound_slice\n            except Exception as e:\n                logger.error(f\"Error adding drum sound to track: {e}\")",
                "drum_track[start_sample:end_sample] += sound[:end_sample - start_sample]"
            )
        
        # Fix melody track rendering
        if "try:" in content and "melody_track[start_sample:end_sample]" in content:
            content = content.replace(
                "try:\n                sound_slice = sound[:end_sample - start_sample]\n                if sound_slice.shape != melody_track[start_sample:end_sample].shape:\n                    logger.warning(f\"Shape mismatch! Reshaping sound_slice from {sound_slice.shape} to {melody_track[start_sample:end_sample].shape}\")\n                    # Ensure shapes match by truncating or padding\n                    target_shape = melody_track[start_sample:end_sample].shape\n                    if len(sound_slice) > len(melody_track[start_sample:end_sample]):\n                        sound_slice = sound_slice[:len(melody_track[start_sample:end_sample])]\n                    elif len(sound_slice) < len(melody_track[start_sample:end_sample]):\n                        pad_length = len(melody_track[start_sample:end_sample]) - len(sound_slice)\n                        sound_slice = np.pad(sound_slice, (0, pad_length), \"constant\")\n                melody_track[start_sample:end_sample] += sound_slice\n            except Exception as e:\n                logger.error(f\"Error adding melody sound to track: {e}\")",
                "melody_track[start_sample:end_sample] += sound[:end_sample - start_sample]"
            )
        
        # Fix bass track rendering
        if "try:" in content and "bass_track[start_sample:end_sample]" in content:
            content = content.replace(
                "try:\n                sound_slice = sound[:end_sample - start_sample]\n                if sound_slice.shape != bass_track[start_sample:end_sample].shape:\n                    logger.warning(f\"Shape mismatch! Reshaping sound_slice from {sound_slice.shape} to {bass_track[start_sample:end_sample].shape}\")\n                    # Ensure shapes match by truncating or padding\n                    target_shape = bass_track[start_sample:end_sample].shape\n                    if len(sound_slice) > len(bass_track[start_sample:end_sample]):\n                        sound_slice = sound_slice[:len(bass_track[start_sample:end_sample])]\n                    elif len(sound_slice) < len(bass_track[start_sample:end_sample]):\n                        pad_length = len(bass_track[start_sample:end_sample]) - len(sound_slice)\n                        sound_slice = np.pad(sound_slice, (0, pad_length), \"constant\")\n                bass_track[start_sample:end_sample] += sound_slice\n            except Exception as e:\n                logger.error(f\"Error adding bass sound to track: {e}\")",
                "bass_track[start_sample:end_sample] += sound[:end_sample - start_sample]"
            )
        
        # Remove any debug logging statements that might be causing issues
        import re
        content = re.sub(r'logger\.debug\(.*?\)', '', content)
        
        # Remove any import logging statements
        content = content.replace('import logging', '')
        
        # Remove any logger configuration
        content = re.sub(r'logging\.basicConfig\(.*?\)', '', content, flags=re.DOTALL)
        
        # Remove logger initialization
        content = re.sub(r'logger = logging\.getLogger\(__name__\).*', '', content)
        
        original_content = content
    
    # Now add a simple fix for the broadcasting error
    # This adds a safety check before adding sounds to tracks
    
    # Fix for drum track
    drum_pattern = "drum_track[start_sample:end_sample] += sound[:end_sample - start_sample]"
    drum_replacement = """# Ensure sound array matches the target slice length
                sound_slice = sound[:end_sample - start_sample]
                if len(sound_slice) > len(drum_track[start_sample:end_sample]):
                    sound_slice = sound_slice[:len(drum_track[start_sample:end_sample])]
                elif len(sound_slice) < len(drum_track[start_sample:end_sample]):
                    # Pad with zeros if too short
                    pad_length = len(drum_track[start_sample:end_sample]) - len(sound_slice)
                    sound_slice = np.pad(sound_slice, (0, pad_length), "constant")
                drum_track[start_sample:end_sample] += sound_slice"""
    
    original_content = original_content.replace(drum_pattern, drum_replacement)
    
    # Fix for melody track
    melody_pattern = "melody_track[start_sample:end_sample] += sound[:end_sample - start_sample]"
    melody_replacement = """# Ensure sound array matches the target slice length
                sound_slice = sound[:end_sample - start_sample]
                if len(sound_slice) > len(melody_track[start_sample:end_sample]):
                    sound_slice = sound_slice[:len(melody_track[start_sample:end_sample])]
                elif len(sound_slice) < len(melody_track[start_sample:end_sample]):
                    # Pad with zeros if too short
                    pad_length = len(melody_track[start_sample:end_sample]) - len(sound_slice)
                    sound_slice = np.pad(sound_slice, (0, pad_length), "constant")
                melody_track[start_sample:end_sample] += sound_slice"""
    
    original_content = original_content.replace(melody_pattern, melody_replacement)
    
    # Fix for bass track
    bass_pattern = "bass_track[start_sample:end_sample] += sound[:end_sample - start_sample]"
    bass_replacement = """# Ensure sound array matches the target slice length
                sound_slice = sound[:end_sample - start_sample]
                if len(sound_slice) > len(bass_track[start_sample:end_sample]):
                    sound_slice = sound_slice[:len(bass_track[start_sample:end_sample])]
                elif len(sound_slice) < len(bass_track[start_sample:end_sample]):
                    # Pad with zeros if too short
                    pad_length = len(bass_track[start_sample:end_sample]) - len(sound_slice)
                    sound_slice = np.pad(sound_slice, (0, pad_length), "constant")
                bass_track[start_sample:end_sample] += sound_slice"""
    
    original_content = original_content.replace(bass_pattern, bass_replacement)
    
    # Write back the fixed content
    with open('beat_studio_professional.py', 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    # Save a copy of the original file for future reference
    with open('beat_studio_professional.py.orig', 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print("✅ Fixed try-except blocks and added array shape safety checks!")

if __name__ == "__main__":
    fix_try_except_blocks()
