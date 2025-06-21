"""
Fix for audio shape broadcasting errors in beat_studio_professional.py
"""

def fix_audio_shapes():
    """Fix the audio shape mismatches in the beat generation."""
    
    # Read the current file
    with open('beat_studio_professional.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic sections
    
    # Fix 1: Ensure consistent array lengths in kick drum generation
    old_kick = '''    # Generate sub (longer sine)
    sub = Oscillator.sine(sub_freq, duration) * 0.7
    
    # Mix and apply envelope
    kick = punch + sub'''
    
    new_kick = '''    # Generate sub (longer sine)
    sub = Oscillator.sine(sub_freq, duration) * 0.7
    
    # Ensure same length for mixing
    min_len = min(len(punch), len(sub))
    punch = punch[:min_len]
    sub = sub[:min_len]
    
    # Mix and apply envelope
    kick = punch + sub'''
    
    content = content.replace(old_kick, new_kick)
    
    # Fix 2: Ensure consistent array lengths in beat mixing
    old_mixing = '''        # Mix tracks
        final_mix = (
            drum_track * 0.8 +
            melody_track * 0.6 +
            bass_track * 0.7
        ) * AudioConstants.MASTER_VOLUME'''
    
    new_mixing = '''        # Ensure all tracks have same length
        min_length = min(len(drum_track), len(melody_track), len(bass_track))
        drum_track = drum_track[:min_length]
        melody_track = melody_track[:min_length]
        bass_track = bass_track[:min_length]
        
        # Mix tracks
        final_mix = (
            drum_track * 0.8 +
            melody_track * 0.6 +
            bass_track * 0.7
        ) * AudioConstants.MASTER_VOLUME'''
    
    content = content.replace(old_mixing, new_mixing)
    
    # Fix 3: Add safety check for sound array lengths in drum rendering
    old_drum_render = '''            sound *= note.velocity
            end_sample = min(start_sample + len(sound), total_samples)
            drum_track[start_sample:end_sample] += sound[:end_sample - start_sample]'''
    
    new_drum_render = '''            sound *= note.velocity
            end_sample = min(start_sample + len(sound), total_samples)
            if start_sample < total_samples:
                sound_length = min(len(sound), end_sample - start_sample)
                drum_track[start_sample:start_sample + sound_length] += sound[:sound_length]'''
    
    content = content.replace(old_drum_render, new_drum_render)
    
    # Fix 4: Add safety check for melody rendering
    old_melody_render = '''            end_sample = min(start_sample + len(sound), total_samples)
            melody_track[start_sample:end_sample] += sound[:end_sample - start_sample]'''
    
    new_melody_render = '''            end_sample = min(start_sample + len(sound), total_samples)
            if start_sample < total_samples:
                sound_length = min(len(sound), end_sample - start_sample)
                melody_track[start_sample:start_sample + sound_length] += sound[:sound_length]'''
    
    content = content.replace(old_melody_render, new_melody_render)
    
    # Fix 5: Add safety check for bass rendering
    old_bass_render = '''            end_sample = min(start_sample + len(sound), total_samples)
            bass_track[start_sample:end_sample] += sound[:end_sample - start_sample]'''
    
    new_bass_render = '''            end_sample = min(start_sample + len(sound), total_samples)
            if start_sample < total_samples:
                sound_length = min(len(sound), end_sample - start_sample)
                bass_track[start_sample:start_sample + sound_length] += sound[:sound_length]'''
    
    content = content.replace(old_bass_render, new_bass_render)
    
    # Write back the fixed content
    with open('beat_studio_professional.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Audio shape broadcasting errors fixed!")

if __name__ == "__main__":
    fix_audio_shapes()
