"""
Comprehensive fix for audio broadcasting errors in Beat Studio
"""

def fix_audio_comprehensive():
    """Apply comprehensive fixes for audio shape mismatches."""
    
    # Read the current file
    with open('beat_studio_professional.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the kick drum method completely
    old_kick_method = '''@staticmethod
def kick(duration: float = 0.5) -> np.ndarray:
    """Generate a kick drum sound."""
    # Base frequencies for punch and sub
    punch_freq = 60
    sub_freq = 40
    
    # Generate punch (short sine with pitch envelope)
    t = np.linspace(0, duration, int(AudioConstants.SAMPLE_RATE * duration))
    pitch_env = np.exp(-35 * t)
    punch = np.sin(2 * np.pi * punch_freq * pitch_env * t)
    
    # Generate sub (longer sine)
    sub = Oscillator.sine(sub_freq, duration) * 0.7
    
    # Ensure same length for mixing
    min_len = min(len(punch), len(sub))
    punch = punch[:min_len]
    sub = sub[:min_len]
    
    # Mix and apply envelope
    kick = punch + sub
    env = Envelope(0.001, 0.01, 0.3, 0.2)
    kick = env.apply(kick, duration)
    
    # Add click for attack
    click = Oscillator.noise(0.003) * 0.3
    kick[:len(click)] += click
    
    return np.tanh(kick * 2) * 0.8  # Soft clipping'''
    
    new_kick_method = '''@staticmethod
def kick(duration: float = 0.5) -> np.ndarray:
    """Generate a kick drum sound."""
    # Base frequencies for punch and sub
    punch_freq = 60
    sub_freq = 40
    
    # Calculate exact sample count
    sample_count = int(AudioConstants.SAMPLE_RATE * duration)
    
    # Generate punch (short sine with pitch envelope)
    t = np.linspace(0, duration, sample_count)
    pitch_env = np.exp(-35 * t)
    punch = np.sin(2 * np.pi * punch_freq * pitch_env * t)
    
    # Generate sub (longer sine) with exact same length
    sub = np.sin(2 * np.pi * sub_freq * t) * 0.7
    
    # Mix and apply envelope
    kick = punch + sub
    env = Envelope(0.001, 0.01, 0.3, 0.2)
    kick = env.apply(kick, duration)
    
    # Add click for attack (ensure it doesn't exceed kick length)
    click_duration = min(0.003, duration)
    click_samples = int(AudioConstants.SAMPLE_RATE * click_duration)
    click = np.random.normal(0, 0.1, click_samples) * 0.3
    kick[:len(click)] += click
    
    return np.tanh(kick * 2) * 0.8  # Soft clipping'''
    
    content = content.replace(old_kick_method, new_kick_method)
    
    # Fix the snare method
    old_snare_search = '''@staticmethod
def snare(duration: float = 0.2) -> np.ndarray:
    """Generate a snare drum sound."""
    # Tone component (200Hz)
    tone = Oscillator.sine(200, duration) * 0.6
    
    # Noise component
    noise = Oscillator.noise(duration) * 0.8
    
    # Mix and apply envelope
    snare = tone + noise
    env = Envelope(0.001, 0.02, 0.1, 0.1)
    snare = env.apply(snare, duration)
    
    return np.tanh(snare * 1.5) * 0.7'''
    
    new_snare_method = '''@staticmethod
def snare(duration: float = 0.2) -> np.ndarray:
    """Generate a snare drum sound."""
    # Calculate exact sample count
    sample_count = int(AudioConstants.SAMPLE_RATE * duration)
    
    # Tone component (200Hz)
    t = np.linspace(0, duration, sample_count)
    tone = np.sin(2 * np.pi * 200 * t) * 0.6
    
    # Noise component with exact same length
    noise = np.random.normal(0, 0.1, sample_count) * 0.8
    
    # Mix and apply envelope
    snare = tone + noise
    env = Envelope(0.001, 0.02, 0.1, 0.1)
    snare = env.apply(snare, duration)
    
    return np.tanh(snare * 1.5) * 0.7'''
    
    # Find and replace snare method
    import re
    snare_pattern = r'@staticmethod\s+def snare\(duration: float = 0\.2\) -> np\.ndarray:.*?return np\.tanh\(snare \* 1\.5\) \* 0\.7'
    content = re.sub(snare_pattern, new_snare_method, content, flags=re.DOTALL)
    
    # Fix the hihat method
    hihat_pattern = r'@staticmethod\s+def hihat\(duration: float = 0\.1, open: bool = False\) -> np\.ndarray:.*?return np\.tanh\(hihat \* 1\.2\) \* 0\.5'
    
    new_hihat_method = '''@staticmethod
def hihat(duration: float = 0.1, open: bool = False) -> np.ndarray:
    """Generate a hi-hat sound."""
    # Calculate exact sample count
    sample_count = int(AudioConstants.SAMPLE_RATE * duration)
    
    # High frequency noise
    hihat = np.random.normal(0, 0.1, sample_count)
    
    # High-pass filter effect (simple)
    hihat = hihat * (1 + np.linspace(0, 2, sample_count))
    
    # Apply envelope
    if open:
        env = Envelope(0.001, 0.05, 0.3, 0.3)
    else:
        env = Envelope(0.001, 0.01, 0.1, 0.05)
    
    hihat = env.apply(hihat, duration)
    
    return np.tanh(hihat * 1.2) * 0.5'''
    
    content = re.sub(hihat_pattern, new_hihat_method, content, flags=re.DOTALL)
    
    # Write back the fixed content
    with open('beat_studio_professional.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Comprehensive audio fixes applied!")

if __name__ == "__main__":
    fix_audio_comprehensive()
