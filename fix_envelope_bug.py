"""
Fix the envelope broadcasting bug in beat_studio_professional.py
"""

def fix_envelope_bug():
    """Fix the envelope apply method that's causing broadcasting errors."""
    
    # Read the current file
    with open('beat_studio_professional.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic Envelope.apply method
    old_envelope_apply = '''def apply(self, signal: np.ndarray, note_duration: float, 
          sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
    total_samples = len(signal)
    attack_samples = int(self.attack * sample_rate)
    decay_samples = int(self.decay * sample_rate)
    release_samples = int(self.release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    envelope = np.ones(total_samples)
    
    # Attack
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    decay_start = attack_samples
    decay_end = decay_start + decay_samples
    envelope[decay_start:decay_end] = np.linspace(1, self.sustain, decay_samples)
    
    # Sustain
    sustain_start = decay_end
    sustain_end = sustain_start + sustain_samples
    envelope[sustain_start:sustain_end] = self.sustain
    
    # Release
    if release_samples > 0:
        envelope[sustain_end:] = np.linspace(self.sustain, 0, release_samples)
    
    return signal * envelope'''
    
    new_envelope_apply = '''def apply(self, signal: np.ndarray, note_duration: float, 
          sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
    total_samples = len(signal)
    attack_samples = int(self.attack * sample_rate)
    decay_samples = int(self.decay * sample_rate)
    release_samples = int(self.release * sample_rate)
    
    # Ensure we don't exceed total samples
    total_envelope_samples = attack_samples + decay_samples + release_samples
    if total_envelope_samples > total_samples:
        # Scale down proportionally
        scale_factor = total_samples / total_envelope_samples
        attack_samples = int(attack_samples * scale_factor)
        decay_samples = int(decay_samples * scale_factor)
        release_samples = int(release_samples * scale_factor)
    
    sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)
    
    envelope = np.ones(total_samples)
    
    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    decay_start = attack_samples
    decay_end = min(decay_start + decay_samples, total_samples)
    if decay_end > decay_start:
        envelope[decay_start:decay_end] = np.linspace(1, self.sustain, decay_end - decay_start)
    
    # Sustain
    sustain_start = decay_end
    sustain_end = min(sustain_start + sustain_samples, total_samples)
    if sustain_end > sustain_start:
        envelope[sustain_start:sustain_end] = self.sustain
    
    # Release
    if release_samples > 0 and sustain_end < total_samples:
        remaining_samples = total_samples - sustain_end
        envelope[sustain_end:] = np.linspace(self.sustain, 0, remaining_samples)
    
    return signal * envelope'''
    
    content = content.replace(old_envelope_apply, new_envelope_apply)
    
    # Write back the fixed content
    with open('beat_studio_professional.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Envelope broadcasting bug fixed!")

if __name__ == "__main__":
    fix_envelope_bug()
