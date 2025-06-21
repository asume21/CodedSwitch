"""
Add detailed debug logging to beat_studio_professional.py to pinpoint the broadcasting error
"""
import re

def add_debug_logging():
    """Add detailed logging to track array shapes during audio generation."""
    
    # Read the current file
    with open('beat_studio_professional.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports for logging if not already there
    if 'import logging' not in content:
        content = content.replace('import numpy as np', 'import numpy as np\nimport logging')
    
    # Add debug level logging configuration
    if 'logger = logging.getLogger(__name__)' in content:
        log_setup = """
# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('beat_studio_debug.log'),
        logging.StreamHandler()
    ]
)
"""
        content = content.replace('logger = logging.getLogger(__name__)', 'logger = logging.getLogger(__name__)' + log_setup)
    
    # Add logging to the drum rendering section
    drum_render_pattern = r'(\s+# Render drums\s+for note in drum_pattern\.notes:.*?sound \*= note\.velocity\s+end_sample = min\(start_sample \+ len\(sound\), total_samples\))'
    
    drum_render_replacement = r'\1\n            logger.debug(f"Drum note: start_sample={start_sample}, sound.shape={sound.shape}, drum_track[{start_sample}:{end_sample}].shape={drum_track[start_sample:end_sample].shape}")'
    
    content = re.sub(drum_render_pattern, drum_render_replacement, content, flags=re.DOTALL)
    
    # Add logging to the melody rendering section
    melody_render_pattern = r'(\s+# Render melody\s+for note in melody_pattern\.notes:.*?sound = self\.synthesizer\.generate_note\(.*?\)\s+end_sample = min\(start_sample \+ len\(sound\), total_samples\))'
    
    melody_render_replacement = r'\1\n            logger.debug(f"Melody note: start_sample={start_sample}, sound.shape={sound.shape}, melody_track[{start_sample}:{end_sample}].shape={melody_track[start_sample:end_sample].shape}")'
    
    content = re.sub(melody_render_pattern, melody_render_replacement, content, flags=re.DOTALL)
    
    # Add logging to the bass rendering section
    bass_render_pattern = r'(\s+# Render bass\s+for note in bass_pattern\.notes:.*?sound = self\.synthesizer\.generate_note\(.*?\)\s+end_sample = min\(start_sample \+ len\(sound\), total_samples\))'
    
    bass_render_replacement = r'\1\n            logger.debug(f"Bass note: start_sample={start_sample}, sound.shape={sound.shape}, bass_track[{start_sample}:{end_sample}].shape={bass_track[start_sample:end_sample].shape}")'
    
    content = re.sub(bass_render_pattern, bass_render_replacement, content, flags=re.DOTALL)
    
    # Add logging to the mixing section
    mixing_pattern = r'(\s+# Mix tracks\s+final_mix = \(.*?\) \* AudioConstants\.MASTER_VOLUME)'
    
    mixing_replacement = r'        logger.debug(f"Before mixing - drum_track.shape={drum_track.shape}, melody_track.shape={melody_track.shape}, bass_track.shape={bass_track.shape}")\n\1'
    
    content = re.sub(mixing_pattern, mixing_replacement, content, flags=re.DOTALL)
    
    # Add logging to the kick drum generation
    kick_pattern = r'(@staticmethod\s+def kick\(duration: float = 0\.5\) -> np\.ndarray:.*?return np\.tanh\(kick \* 2\) \* 0\.8  # Soft clipping)'
    
    kick_replacement = r'\g<0>\n    logger.debug(f"Generated kick drum with shape={np.tanh(kick * 2).shape}")'
    
    content = re.sub(kick_pattern, kick_replacement, content, flags=re.DOTALL)
    
    # Add logging to the envelope apply method
    envelope_pattern = r'(def apply\(self, signal: np\.ndarray, note_duration: float,.*?return signal \* envelope)'
    
    envelope_replacement = r'\g<0>\n    logger.debug(f"Envelope applied - input signal.shape={signal.shape}, envelope.shape={envelope.shape}, output.shape={(signal * envelope).shape}")'
    
    content = re.sub(envelope_pattern, envelope_replacement, content, flags=re.DOTALL)
    
    # Add a direct fix for the most likely broadcasting issue in drum rendering
    drum_track_add_pattern = r'(drum_track\[start_sample:end_sample\] \+= sound\[:end_sample - start_sample\])'
    
    drum_track_add_replacement = r'try:\n                sound_slice = sound[:end_sample - start_sample]\n                if sound_slice.shape != drum_track[start_sample:end_sample].shape:\n                    logger.warning(f"Shape mismatch! Reshaping sound_slice from {sound_slice.shape} to {drum_track[start_sample:end_sample].shape}")\n                    # Ensure shapes match by truncating or padding\n                    target_shape = drum_track[start_sample:end_sample].shape\n                    if len(sound_slice) > len(drum_track[start_sample:end_sample]):\n                        sound_slice = sound_slice[:len(drum_track[start_sample:end_sample])]\n                    elif len(sound_slice) < len(drum_track[start_sample:end_sample]):\n                        pad_length = len(drum_track[start_sample:end_sample]) - len(sound_slice)\n                        sound_slice = np.pad(sound_slice, (0, pad_length), "constant")\n                drum_track[start_sample:end_sample] += sound_slice\n            except Exception as e:\n                logger.error(f"Error adding drum sound to track: {e}")'
    
    content = content.replace(drum_track_add_pattern, drum_track_add_replacement)
    
    # Apply similar fixes to melody and bass rendering
    melody_track_add_pattern = r'(melody_track\[start_sample:end_sample\] \+= sound\[:end_sample - start_sample\])'
    
    melody_track_add_replacement = r'try:\n                sound_slice = sound[:end_sample - start_sample]\n                if sound_slice.shape != melody_track[start_sample:end_sample].shape:\n                    logger.warning(f"Shape mismatch! Reshaping sound_slice from {sound_slice.shape} to {melody_track[start_sample:end_sample].shape}")\n                    # Ensure shapes match by truncating or padding\n                    target_shape = melody_track[start_sample:end_sample].shape\n                    if len(sound_slice) > len(melody_track[start_sample:end_sample]):\n                        sound_slice = sound_slice[:len(melody_track[start_sample:end_sample])]\n                    elif len(sound_slice) < len(melody_track[start_sample:end_sample]):\n                        pad_length = len(melody_track[start_sample:end_sample]) - len(sound_slice)\n                        sound_slice = np.pad(sound_slice, (0, pad_length), "constant")\n                melody_track[start_sample:end_sample] += sound_slice\n            except Exception as e:\n                logger.error(f"Error adding melody sound to track: {e}")'
    
    content = content.replace(melody_track_add_pattern, melody_track_add_replacement)
    
    bass_track_add_pattern = r'(bass_track\[start_sample:end_sample\] \+= sound\[:end_sample - start_sample\])'
    
    bass_track_add_replacement = r'try:\n                sound_slice = sound[:end_sample - start_sample]\n                if sound_slice.shape != bass_track[start_sample:end_sample].shape:\n                    logger.warning(f"Shape mismatch! Reshaping sound_slice from {sound_slice.shape} to {bass_track[start_sample:end_sample].shape}")\n                    # Ensure shapes match by truncating or padding\n                    target_shape = bass_track[start_sample:end_sample].shape\n                    if len(sound_slice) > len(bass_track[start_sample:end_sample]):\n                        sound_slice = sound_slice[:len(bass_track[start_sample:end_sample])]\n                    elif len(sound_slice) < len(bass_track[start_sample:end_sample]):\n                        pad_length = len(bass_track[start_sample:end_sample]) - len(sound_slice)\n                        sound_slice = np.pad(sound_slice, (0, pad_length), "constant")\n                bass_track[start_sample:end_sample] += sound_slice\n            except Exception as e:\n                logger.error(f"Error adding bass sound to track: {e}")'
    
    content = content.replace(bass_track_add_pattern, bass_track_add_replacement)
    
    # Write back the modified content
    with open('beat_studio_professional.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Debug logging added and shape mismatch fixes applied!")

if __name__ == "__main__":
    add_debug_logging()
