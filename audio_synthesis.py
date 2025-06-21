# audio_synthesis.py - Complete Audio Engine for CodedSwitch DAW
import numpy as np
import threading
import time
from typing import Dict, List, Tuple

class AudioSynthesizer:
    """
    Complete audio synthesis engine for 12-instrument DAW
    Creates realistic drum and instrument sounds using mathematical formulas
    """
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.is_playing = False
        self.current_step = 0
        self.bpm = 120
        self.step_duration = 60.0 / (self.bpm * 4)  # 16th notes
        self.play_thread = None
        
        # Volume controls for each instrument (0.0 to 1.0)
        self.volumes = {
            'Kick': 0.8, 'Snare': 0.7, 'Hi-Hat': 0.5, 'Open Hat': 0.6,
            'Clap': 0.6, 'Crash': 0.4, 'Tom': 0.7, 'Bass': 0.6,
            'Piano': 0.5, 'Strings': 0.4, 'Brass': 0.5, 'Lead': 0.6
        }
        
        # Mute/Solo states
        self.muted = {inst: False for inst in self.volumes.keys()}
        self.soloed = {inst: False for inst in self.volumes.keys()}
        
        # Pattern storage (16 steps per instrument)
        self.patterns = {inst: [0] * 16 for inst in self.volumes.keys()}
        
        print("🎵 Audio Synthesizer initialized with 12 instruments")
    
    def generate_kick_drum(self, duration=0.5):
        """Generate realistic kick drum using sine wave + noise"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Low frequency sine wave (60Hz) with exponential decay
        fundamental = np.sin(2 * np.pi * 60 * t) * np.exp(-t * 8)
        
        # Add sub-bass (30Hz) for depth
        sub_bass = np.sin(2 * np.pi * 30 * t) * np.exp(-t * 5) * 0.3
        
        # Add click for attack
        click = np.sin(2 * np.pi * 2000 * t) * np.exp(-t * 50) * 0.1
        
        # Combine and normalize
        kick = (fundamental + sub_bass + click) * self.volumes['Kick']
        return np.clip(kick, -1.0, 1.0)
    
    def generate_snare_drum(self, duration=0.3):
        """Generate snare using noise + tone"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # White noise for snare rattle
        noise = np.random.normal(0, 0.1, samples) * np.exp(-t * 15)
        
        # Tone component (200Hz)
        tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 20) * 0.3
        
        # High frequency crack
        crack = np.sin(2 * np.pi * 8000 * t) * np.exp(-t * 40) * 0.2
        
        snare = (noise + tone + crack) * self.volumes['Snare']
        return np.clip(snare, -1.0, 1.0)
    
    def generate_hihat(self, duration=0.1, open=False):
        """Generate hi-hat using filtered noise"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # High frequency noise
        noise = np.random.normal(0, 0.05, samples)
        
        # Apply high-pass filtering effect
        for i in range(1, len(noise)):
            noise[i] = noise[i] + noise[i-1] * 0.8
        
        # Decay envelope
        decay_rate = 30 if not open else 8
        envelope = np.exp(-t * decay_rate)
        
        volume_key = 'Open Hat' if open else 'Hi-Hat'
        hihat = noise * envelope * self.volumes[volume_key]
        return np.clip(hihat, -1.0, 1.0)
    
    def generate_clap(self, duration=0.2):
        """Generate hand clap using multiple noise bursts"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Multiple quick noise bursts to simulate hand clap
        clap_sound = np.zeros(samples)
        for i, burst_time in enumerate([0.0, 0.01, 0.02, 0.035]):
            if burst_time < duration:
                start_sample = int(burst_time * self.sample_rate)
                burst_length = int(0.01 * self.sample_rate)
                end_sample = min(start_sample + burst_length, samples)
                
                if start_sample < samples:
                    burst = np.random.normal(0, 0.1, end_sample - start_sample)
                    burst *= np.exp(-np.linspace(0, 0.01, len(burst)) * 100)
                    clap_sound[start_sample:end_sample] += burst
        
        clap_sound *= self.volumes['Clap']
        return np.clip(clap_sound, -1.0, 1.0)
    
    def generate_crash(self, duration=1.0):
        """Generate crash cymbal using complex noise"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Complex noise with multiple frequency components
        noise = np.random.normal(0, 0.1, samples)
        
        # Add metallic ringing (multiple frequencies)
        for freq in [3000, 4500, 6000, 8000]:
            noise += np.sin(2 * np.pi * freq * t) * np.exp(-t * 2) * 0.1
        
        # Long decay
        envelope = np.exp(-t * 3)
        crash = noise * envelope * self.volumes['Crash']
        return np.clip(crash, -1.0, 1.0)
    
    def generate_tom(self, duration=0.4):
        """Generate tom drum with pitch bend"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Frequency sweep from 120Hz to 80Hz
        freq_sweep = 120 * np.exp(-t * 3) + 80
        
        # Generate tone with frequency sweep
        phase = 2 * np.pi * np.cumsum(freq_sweep) / self.sample_rate
        tom = np.sin(phase) * np.exp(-t * 6)
        
        # Add some noise for texture
        noise = np.random.normal(0, 0.02, samples) * np.exp(-t * 10)
        
        tom_sound = (tom + noise) * self.volumes['Tom']
        return np.clip(tom_sound, -1.0, 1.0)
    
    def generate_bass(self, frequency=55, duration=0.3):
        """Generate bass synth note"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Square wave bass with filter sweep
        square_wave = np.sign(np.sin(2 * np.pi * frequency * t))
        
        # Add sub harmonic
        sub = np.sin(2 * np.pi * frequency/2 * t) * 0.3
        
        # Filter envelope
        envelope = np.exp(-t * 8)
        
        bass = (square_wave + sub) * envelope * self.volumes['Bass'] * 0.3
        return np.clip(bass, -1.0, 1.0)
    
    def generate_piano(self, frequency=261.63, duration=0.5):  # C4 = 261.63 Hz
        """Generate piano note using multiple harmonics"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Piano has strong fundamental + harmonics
        piano = np.sin(2 * np.pi * frequency * t)  # Fundamental
        piano += np.sin(2 * np.pi * frequency * 2 * t) * 0.5  # 2nd harmonic
        piano += np.sin(2 * np.pi * frequency * 3 * t) * 0.25  # 3rd harmonic
        piano += np.sin(2 * np.pi * frequency * 4 * t) * 0.125  # 4th harmonic
        
        # Piano decay envelope
        envelope = np.exp(-t * 3)
        
        piano_sound = piano * envelope * self.volumes['Piano'] * 0.2
        return np.clip(piano_sound, -1.0, 1.0)
    
    def generate_strings(self, frequency=220, duration=0.8):  # A3 = 220 Hz
        """Generate string pad using sawtooth wave"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Sawtooth wave (good for strings)
        sawtooth = 2 * (frequency * t - np.floor(frequency * t + 0.5))
        
        # Add chorus effect (slight detuning)
        chorus = 2 * ((frequency * 1.02) * t - np.floor((frequency * 1.02) * t + 0.5)) * 0.3
        
        # Slow attack envelope (strings fade in)
        attack = np.minimum(t * 10, 1.0)
        sustain = np.exp(-t * 1)
        envelope = attack * sustain
        
        strings_sound = (sawtooth + chorus) * envelope * self.volumes['Strings'] * 0.15
        return np.clip(strings_sound, -1.0, 1.0)
    
    def generate_brass(self, frequency=349.23, duration=0.6):  # F4 = 349.23 Hz
        """Generate brass sound using square wave with harmonics"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Square wave base
        brass = np.sign(np.sin(2 * np.pi * frequency * t))
        
        # Add harmonics for brass timbre
        brass += np.sign(np.sin(2 * np.pi * frequency * 2 * t)) * 0.3
        brass += np.sign(np.sin(2 * np.pi * frequency * 3 * t)) * 0.2
        
        # Brass envelope (quick attack, sustained)
        envelope = np.minimum(t * 20, 1.0) * np.exp(-t * 2)
        
        brass_sound = brass * envelope * self.volumes['Brass'] * 0.2
        return np.clip(brass_sound, -1.0, 1.0)
    
    def generate_lead(self, frequency=523.25, duration=0.4):  # C5 = 523.25 Hz
        """Generate lead synth using triangle wave"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Triangle wave for smooth lead
        triangle = 2 * np.abs(2 * (frequency * t - np.floor(frequency * t + 0.5))) - 1
        
        # Add slight vibrato
        vibrato = np.sin(2 * np.pi * 5 * t) * 0.02  # 5Hz vibrato
        modulated_freq = frequency * (1 + vibrato)
        
        # Recalculate with vibrato
        phase = 2 * np.pi * np.cumsum(modulated_freq) / self.sample_rate
        lead = np.sin(phase)
        
        # Lead envelope
        envelope = np.exp(-t * 4)
        
        lead_sound = lead * envelope * self.volumes['Lead'] * 0.25
        return np.clip(lead_sound, -1.0, 1.0)
    
    def get_instrument_sound(self, instrument_name, step=0):
        """Get the appropriate sound for an instrument"""
        # Different notes for melodic instruments based on step
        note_frequencies = {
            4: 261.63,   # C4
            6: 293.66,   # D4  
            8: 329.63,   # E4
            10: 349.23,  # F4
            12: 392.00,  # G4
            14: 440.00   # A4
        }
        
        if instrument_name == 'Kick':
            return self.generate_kick_drum()
        elif instrument_name == 'Snare':
            return self.generate_snare_drum()
        elif instrument_name == 'Hi-Hat':
            return self.generate_hihat(open=False)
        elif instrument_name == 'Open Hat':
            return self.generate_hihat(open=True)
        elif instrument_name == 'Clap':
            return self.generate_clap()
        elif instrument_name == 'Crash':
            return self.generate_crash()
        elif instrument_name == 'Tom':
            return self.generate_tom()
        elif instrument_name == 'Bass':
            freq = note_frequencies.get(step, 55)
            return self.generate_bass(frequency=freq/4)  # Bass an octave lower
        elif instrument_name == 'Piano':
            freq = note_frequencies.get(step, 261.63)
            return self.generate_piano(frequency=freq)
        elif instrument_name == 'Strings':
            freq = note_frequencies.get(step, 220)
            return self.generate_strings(frequency=freq)
        elif instrument_name == 'Brass':
            freq = note_frequencies.get(step, 349.23)
            return self.generate_brass(frequency=freq)
        elif instrument_name == 'Lead':
            freq = note_frequencies.get(step, 523.25)
            return self.generate_lead(frequency=freq)
        else:
            # Fallback - generate silence
            return np.zeros(int(0.1 * self.sample_rate))
    
    def set_volume(self, instrument, volume):
        """Set volume for an instrument (0.0 to 1.0)"""
        if instrument in self.volumes:
            self.volumes[instrument] = max(0.0, min(1.0, volume))
            print(f"🔊 {instrument} volume: {volume:.2f}")
    
    def set_mute(self, instrument, muted):
        """Mute/unmute an instrument"""
        if instrument in self.muted:
            self.muted[instrument] = muted
            print(f"🔇 {instrument} {'muted' if muted else 'unmuted'}")
    
    def set_solo(self, instrument, soloed):
        """Solo/unsolo an instrument"""
        if instrument in self.soloed:
            self.soloed[instrument] = soloed
            print(f"🎯 {instrument} {'soloed' if soloed else 'unsoloed'}")
    
    def should_play_instrument(self, instrument):
        """Check if instrument should play based on mute/solo state"""
        # If any instrument is soloed, only play soloed instruments
        any_soloed = any(self.soloed.values())
        if any_soloed:
            return self.soloed[instrument]
        
        # Otherwise, play if not muted
        return not self.muted[instrument]
    
    def set_pattern(self, instrument, pattern):
        """Set the 16-step pattern for an instrument"""
        if instrument in self.patterns and len(pattern) == 16:
            self.patterns[instrument] = pattern.copy()
            print(f"🎼 {instrument} pattern updated")
    
    def play_step(self, step):
        """Play all instruments for a given step"""
        try:
            import sounddevice as sd
            
            # Mix all active instruments for this step
            mixed_audio = None
            
            for instrument, pattern in self.patterns.items():
                if pattern[step] and self.should_play_instrument(instrument):
                    sound = self.get_instrument_sound(instrument, step)
                    
                    if mixed_audio is None:
                        mixed_audio = sound.copy()
                    else:
                        # Make sure both arrays are the same length
                        min_length = min(len(mixed_audio), len(sound))
                        mixed_audio = mixed_audio[:min_length] + sound[:min_length]
            
            if mixed_audio is not None:
                # Normalize to prevent clipping
                max_amplitude = np.max(np.abs(mixed_audio))
                if max_amplitude > 0:
                    mixed_audio = mixed_audio / max_amplitude * 0.8
                
                # Play the mixed audio
                sd.play(mixed_audio, self.sample_rate, blocking=False)
                
        except ImportError:
            print(f"🎵 Step {step+1}: Would play audio (sounddevice not available)")
        except Exception as e:
            print(f"❌ Audio error: {e}")
    
    def start_playback(self):
        """Start the sequencer playback"""
        if self.is_playing:
            return
            
        self.is_playing = True
        self.current_step = 0
        
        def playback_loop():
            while self.is_playing:
                self.play_step(self.current_step)
                
                # Update step duration based on BPM
                self.step_duration = 60.0 / (self.bpm * 4)
                time.sleep(self.step_duration)
                
                self.current_step = (self.current_step + 1) % 16
        
        self.play_thread = threading.Thread(target=playback_loop)
        self.play_thread.daemon = True
        self.play_thread.start()
        
        print("▶️ Playback started")
    
    def stop_playback(self):
        """Stop the sequencer playback"""
        self.is_playing = False
        if self.play_thread:
            self.play_thread.join(timeout=1.0)
        
        try:
            import sounddevice as sd
            sd.stop()
        except ImportError:
            pass
        
        print("⏹️ Playback stopped")
    
    def set_bpm(self, bpm):
        """Set the BPM (beats per minute)"""
        self.bpm = max(60, min(200, bpm))
        self.step_duration = 60.0 / (self.bpm * 4)
        print(f"🎵 BPM set to {self.bpm}")


# Integration functions for your existing menu_handlers.py
def integrate_with_existing_daw(menu_handler_instance):
    """
    Integration function to connect this audio engine with your existing DAW
    Call this from your menu_handlers.py __init__ method
    """
    
    # Create the audio synthesizer
    menu_handler_instance.audio_synth = AudioSynthesizer()
    
    print("🎵 Audio engine integrated with CodedSwitch DAW!")
    print("📝 LEARNING NOTE: Now all 12 instruments will make sound!")
    
    # Override the existing play/stop methods
    original_start_playback = getattr(menu_handler_instance, '_start_playback', None)
    original_stop_playback = getattr(menu_handler_instance, '_stop_playback', None)
    
    def enhanced_start_playback():
        """Enhanced playback with real audio"""
        menu_handler_instance.audio_synth.start_playback()
        if original_start_playback:
            original_start_playback()
    
    def enhanced_stop_playback():
        """Enhanced stop with real audio"""
        menu_handler_instance.audio_synth.stop_playback()
        if original_stop_playback:
            original_stop_playback()
    
    # Replace methods
    menu_handler_instance._start_playback = enhanced_start_playback
    menu_handler_instance._stop_playback = enhanced_stop_playback
    
    return menu_handler_instance.audio_synth

# Example usage and testing
if __name__ == "__main__":
    print("🎵 Testing CodedSwitch Audio Engine...")
    
    # Create synthesizer
    synth = AudioSynthesizer()
    
    # Test all instruments
    instruments = ['Kick', 'Snare', 'Hi-Hat', 'Open Hat', 'Clap', 'Crash', 
                  'Tom', 'Bass', 'Piano', 'Strings', 'Brass', 'Lead']
    
    print("\n🔧 Testing individual instruments:")
    for i, instrument in enumerate(instruments):
        print(f"  {i+1}. {instrument}")
        sound = synth.get_instrument_sound(instrument, 0)
        print(f"     Generated {len(sound)} samples")
    
    # Test a simple pattern
    print("\n🎼 Setting up test pattern...")
    synth.set_pattern('Kick', [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0])
    synth.set_pattern('Snare', [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0])
    synth.set_pattern('Hi-Hat', [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
    
    print("✅ Audio engine ready! Integration instructions:")
    print("1. Add 'from audio_synthesis import integrate_with_existing_daw' to menu_handlers.py")
    print("2. Call 'integrate_with_existing_daw(self)' in your Beat Studio initialization")
    print("3. All 12 instruments will now produce realistic sounds!")