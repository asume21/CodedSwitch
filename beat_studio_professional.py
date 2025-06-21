"""
Beat Studio Module - Professional Audio Generation for CodedSwitch
This module provides comprehensive beat generation with synthesizers, drums, and melody generators.
"""

import numpy as np
import pygame
import threading
import queue
import json
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import wave
import struct
from scipy import signal
from scipy.io import wavfile
import logging

logger = logging.getLogger(__name__)
# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('beat_studio_debug.log'),
        logging.StreamHandler()
    ]
)


# ============================================================================
# AUDIO ENGINE CONSTANTS
# ============================================================================

class AudioConstants:
    SAMPLE_RATE = 44100
    CHANNELS = 2
    BUFFER_SIZE = 512
    BIT_DEPTH = 16
    TEMPO_MIN = 60
    TEMPO_MAX = 200
    MASTER_VOLUME = 0.8

# ============================================================================
# MUSIC THEORY HELPERS
# ============================================================================

class Scale(Enum):
    MAJOR = [0, 2, 4, 5, 7, 9, 11]
    MINOR = [0, 2, 3, 5, 7, 8, 10]
    PENTATONIC = [0, 2, 4, 7, 9]
    BLUES = [0, 3, 5, 6, 7, 10]
    CHROMATIC = list(range(12))

class Chord:
    MAJOR = [0, 4, 7]
    MINOR = [0, 3, 7]
    SEVENTH = [0, 4, 7, 10]
    MINOR_SEVENTH = [0, 3, 7, 10]
    DIMINISHED = [0, 3, 6]
    AUGMENTED = [0, 4, 8]

# ============================================================================
# SYNTHESIZER ENGINE
# ============================================================================

class Oscillator:
    """Advanced oscillator with multiple waveforms and modulation."""
    
    @staticmethod
    def sine(frequency: float, duration: float, sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration))
        return np.sin(2 * np.pi * frequency * t)
    
    @staticmethod
    def square(frequency: float, duration: float, sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration))
        return signal.square(2 * np.pi * frequency * t)
    
    @staticmethod
    def sawtooth(frequency: float, duration: float, sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration))
        return signal.sawtooth(2 * np.pi * frequency * t)
    
    @staticmethod
    def triangle(frequency: float, duration: float, sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration))
        return signal.sawtooth(2 * np.pi * frequency * t, 0.5)
    
    @staticmethod
    def noise(duration: float, sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
        return np.random.uniform(-1, 1, int(sample_rate * duration))

class Envelope:
    """ADSR envelope generator for shaping sounds."""
    
    def __init__(self, attack: float = 0.01, decay: float = 0.1, 
                 sustain: float = 0.7, release: float = 0.2):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
    
    def apply(self, signal: np.ndarray, note_duration: float, 
              sample_rate: int = AudioConstants.SAMPLE_RATE) -> np.ndarray:
        total_samples = len(signal)
        attack_samples = int(self.attack * sample_rate)
        decay_samples = int(self.decay * sample_rate)
        release_samples = int(self.release * sample_rate)

        # Ensure the ADSR segments fit into the total duration
        min_required = attack_samples + decay_samples + release_samples
        if min_required > total_samples:
            # Scale down the segments proportionally
            scale = total_samples / max(min_required, 1)
            attack_samples = int(attack_samples * scale)
            decay_samples = int(decay_samples * scale)
            release_samples = max(total_samples - attack_samples - decay_samples, 0)

        sustain_samples = max(total_samples - attack_samples - decay_samples - release_samples, 0)
        
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
        if release_samples > 0 and sustain_end < total_samples:
            envelope[sustain_end:] = np.linspace(self.sustain, 0, release_samples)
        
        return signal * envelope
        logger.debug(f"Envelope applied - input signal.shape={signal.shape}, envelope.shape={envelope.shape}, output.shape={(signal * envelope).shape}")

class Synthesizer:
    """Professional synthesizer with multiple oscillators and effects."""
    
    def __init__(self):
        self.oscillators = {
            'sine': Oscillator.sine,
            'square': Oscillator.square,
            'saw': Oscillator.sawtooth,
            'triangle': Oscillator.triangle,
            'noise': Oscillator.noise
        }
        self.envelope = Envelope()
        self.filters = {}
    
    def generate_note(self, frequency: float, duration: float, 
                     waveform: str = 'sine', velocity: float = 1.0) -> np.ndarray:
        """Generate a single note with envelope and velocity."""
        if waveform not in self.oscillators:
            waveform = 'sine'
        
        # Generate base waveform
        wave = self.oscillators[waveform](frequency, duration)
        
        # Apply envelope
        wave = self.envelope.apply(wave, duration)
        
        # Apply velocity
        wave *= velocity
        
        return wave
    
    def generate_chord(self, root_freq: float, chord_type: List[int], 
                      duration: float, waveform: str = 'sine') -> np.ndarray:
        """Generate a chord based on intervals."""
        chord_wave = np.zeros(int(AudioConstants.SAMPLE_RATE * duration))
        
        for interval in chord_type:
            note_freq = root_freq * (2 ** (interval / 12))
            chord_wave += self.generate_note(note_freq, duration, waveform, 0.3)
        
        return chord_wave / len(chord_type)

# ============================================================================
# DRUM SYNTHESIZER
# ============================================================================

class DrumSynthesizer:
    """Synthesizer specifically for drum sounds."""
    
    @staticmethod
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
        
        # Mix and apply envelope
        kick = punch + sub
        env = Envelope(0.001, 0.01, 0.3, 0.2)
        kick = env.apply(kick, duration)
        
        # Add click for attack
        click = Oscillator.noise(0.003) * 0.3
        kick[:len(click)] += click
        
        return np.tanh(kick * 2) * 0.8  # Soft clipping
        logger.debug(f"Generated kick drum with shape={np.tanh(kick * 2).shape}")
    
    @staticmethod
    def snare(duration: float = 0.2) -> np.ndarray:
        """Generate a snare drum sound."""
        # Tone component (200-250 Hz)
        tone1 = Oscillator.sine(200, duration) * 0.5
        tone2 = Oscillator.sine(250, duration) * 0.3
        
        # Noise component
        noise = Oscillator.noise(duration) * 0.8
        
        # Mix components
        snare = (tone1 + tone2) * 0.6 + noise * 0.4
        
        # Apply envelope
        env = Envelope(0.001, 0.02, 0.1, 0.05)
        return env.apply(snare, duration)
    
    @staticmethod
    def hihat(duration: float = 0.1, open: bool = False) -> np.ndarray:
        """Generate a hi-hat sound."""
        # High frequency noise
        noise = Oscillator.noise(duration)
        
        # Apply envelope
        if open:
            env = Envelope(0.001, 0.02, 0.3, 0.3)
        else:
            env = Envelope(0.001, 0.01, 0.0, 0.02)
        
        return env.apply(noise, duration) * 0.5

# ============================================================================
# PATTERN SEQUENCER
# ============================================================================

@dataclass
class Note:
    pitch: int  # MIDI note number
    velocity: float
    duration: float
    start_time: float

@dataclass
class Pattern:
    notes: List[Note]
    length: float  # Pattern length in beats
    channel: str  # 'melody', 'bass', 'drums', etc.

class Sequencer:
    """Pattern-based sequencer for creating beats."""
    
    def __init__(self, tempo: int = 120):
        self.tempo = tempo
        self.patterns: Dict[str, Pattern] = {}
        self.beat_duration = 60.0 / tempo
    
    def add_pattern(self, name: str, pattern: Pattern):
        """Add a pattern to the sequencer."""
        self.patterns[name] = pattern
    
    def generate_drum_pattern(self, pattern_type: str = 'basic') -> Pattern:
        """Generate common drum patterns."""
        patterns = {
            'basic': [
                ('kick', [0, 2]),
                ('snare', [1, 3]),
                ('hihat', [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5])
            ],
            'hiphop': [
                ('kick', [0, 0.75, 2.5]),
                ('snare', [1, 3]),
                ('hihat', [0, 0.5, 1, 1.5, 2, 2.25, 2.5, 3, 3.5])
            ],
            'trap': [
                ('kick', [0, 0.75, 2.75]),
                ('snare', [1, 3]),
                ('hihat', [0, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.125, 2.25, 2.5, 3, 3.5])
            ]
        }
        
        notes = []
        for drum, beats in patterns.get(pattern_type, patterns['basic']):
            for beat in beats:
                notes.append(Note(
                    pitch=60 if drum == 'kick' else 62 if drum == 'snare' else 64,
                    velocity=1.0 if beat % 1 == 0 else 0.7,
                    duration=0.1,
                    start_time=beat
                ))
        
        return Pattern(notes=notes, length=4.0, channel='drums')

# ============================================================================
# MELODY GENERATOR
# ============================================================================

class MelodyGenerator:
    """AI-assisted melody generation based on scales and patterns."""
    
    def __init__(self, scale: Scale = Scale.MAJOR, root_note: int = 60):
        self.scale = scale
        self.root_note = root_note
        self.note_pool = self._generate_note_pool()
    
    def _generate_note_pool(self) -> List[int]:
        """Generate available notes based on scale."""
        notes = []
        for octave in range(-1, 2):  # 3 octaves
            for interval in self.scale.value:
                notes.append(self.root_note + (octave * 12) + interval)
        return notes
    
    def generate_melody(self, length: int = 8, pattern: str = 'random') -> List[Note]:
        """Generate a melody based on patterns."""
        melody = []
        
        if pattern == 'random':
            for i in range(length):
                pitch = np.random.choice(self.note_pool)
                duration = np.random.choice([0.25, 0.5, 1.0])
                velocity = np.random.uniform(0.6, 1.0)
                start_time = sum(n.duration for n in melody)
                melody.append(Note(pitch, velocity, duration, start_time))
        
        elif pattern == 'ascending':
            for i in range(length):
                pitch = self.note_pool[i % len(self.note_pool)]
                duration = 0.5
                velocity = 0.8
                start_time = i * duration
                melody.append(Note(pitch, velocity, duration, start_time))
        
        elif pattern == 'call_response':
            # Create a call and response pattern
            call = []
            for i in range(4):
                pitch = np.random.choice(self.note_pool[len(self.note_pool)//2:])
                duration = 0.25
                velocity = 0.9
                start_time = i * duration
                call.append(Note(pitch, velocity, duration, start_time))
            
            # Response (variation of call)
            response = []
            for i, note in enumerate(call):
                pitch = note.pitch - 5 if note.pitch - 5 in self.note_pool else note.pitch
                duration = note.duration
                velocity = note.velocity * 0.8
                start_time = (4 + i) * duration
                response.append(Note(pitch, velocity, duration, start_time))
            
            melody = call + response
        
        return melody

# ============================================================================
# BEAT STUDIO ENGINE
# ============================================================================

class BeatStudioEngine:
    """Main engine for generating beats from lyrics or patterns."""
    
    def __init__(self):
        self.synthesizer = Synthesizer()
        self.drum_synth = DrumSynthesizer()
        self.sequencer = Sequencer()
        self.melody_gen = MelodyGenerator()
        self.mixer_queue = queue.Queue()
        self.is_playing = False
        self.current_position = 0
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(
                frequency=AudioConstants.SAMPLE_RATE,
                size=AudioConstants.BIT_DEPTH * -1,
                channels=AudioConstants.CHANNELS,
                buffer=AudioConstants.BUFFER_SIZE
            )
        except Exception as e:
            logger.warning(f"Could not initialize pygame mixer: {e}")
    
    def analyze_lyrics_mood(self, lyrics: str) -> Dict[str, Any]:
        """Analyze lyrics to determine musical parameters."""
        # Simple mood analysis based on keywords
        mood_keywords = {
            'happy': ['happy', 'joy', 'love', 'bright', 'smile', 'dance'],
            'sad': ['sad', 'cry', 'tears', 'lonely', 'miss', 'gone'],
            'energetic': ['run', 'jump', 'party', 'wild', 'free', 'alive'],
            'chill': ['relax', 'calm', 'peace', 'quiet', 'rest', 'easy']
        }
        
        lyrics_lower = lyrics.lower()
        mood_scores = {}
        
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in lyrics_lower)
            mood_scores[mood] = score
        
        # Determine dominant mood
        dominant_mood = max(mood_scores, key=mood_scores.get) if any(mood_scores.values()) else 'neutral'
        
        # Set musical parameters based on mood
        params = {
            'happy': {
                'tempo': 128,
                'scale': Scale.MAJOR,
                'drum_pattern': 'basic',
                'synth_type': 'square'
            },
            'sad': {
                'tempo': 70,
                'scale': Scale.MINOR,
                'drum_pattern': 'basic',
                'synth_type': 'sine'
            },
            'energetic': {
                'tempo': 140,
                'scale': Scale.PENTATONIC,
                'drum_pattern': 'trap',
                'synth_type': 'saw'
            },
            'chill': {
                'tempo': 90,
                'scale': Scale.MINOR,
                'drum_pattern': 'hiphop',
                'synth_type': 'triangle'
            },
            'neutral': {
                'tempo': 120,
                'scale': Scale.MAJOR,
                'drum_pattern': 'basic',
                'synth_type': 'sine'
            }
        }
        
        return params.get(dominant_mood, params['neutral'])
    
    def generate_beat_from_lyrics(self, lyrics: str, duration: float = 8.0) -> np.ndarray:
        """Generate a complete beat based on lyrics analysis."""
        try:
            # Analyze lyrics
            params = self.analyze_lyrics_mood(lyrics)
            
            # Update components with parameters
            self.sequencer.tempo = params['tempo']
            self.melody_gen = MelodyGenerator(params['scale'])
        
            # Generate patterns
            drum_pattern = self.sequencer.generate_drum_pattern(params['drum_pattern'])
            melody_pattern = Pattern(
                notes=self.melody_gen.generate_melody(16, 'call_response'),
                length=8.0,
                channel='melody'
            )
        
            # Generate bass line (simple root notes)
            bass_pattern = Pattern(
                notes=[
                    Note(48, 0.8, 1.0, 0),
                    Note(48, 0.8, 1.0, 1),
                    Note(53, 0.8, 1.0, 2),
                    Note(48, 0.8, 1.0, 3),
                    Note(46, 0.8, 1.0, 4),
                    Note(46, 0.8, 1.0, 5),
                    Note(48, 0.8, 1.0, 6),
                    Note(48, 0.8, 1.0, 7),
                ],
                length=8.0,
                channel='bass'
            )
        
            # Render all tracks
            beat_duration = 60.0 / params['tempo']
            samples_per_beat = int(AudioConstants.SAMPLE_RATE * beat_duration)
            total_samples = int(AudioConstants.SAMPLE_RATE * duration)
        
            # Initialize tracks
            drum_track = np.zeros(total_samples)
            melody_track = np.zeros(total_samples)
            bass_track = np.zeros(total_samples)
        
            # Render drums
            for note in drum_pattern.notes:
                start_sample = int(note.start_time * samples_per_beat)
                if note.pitch == 60:  # Kick
                    sound = self.drum_synth.kick(note.duration)
                elif note.pitch == 62:  # Snare
                    sound = self.drum_synth.snare(note.duration)
                else:  # Hi-hat
                    sound = self.drum_synth.hihat(note.duration)
                sound *= note.velocity
                end_sample = min(start_sample + len(sound), total_samples)
                sound_slice = sound[:end_sample - start_sample]
                target_len = end_sample - start_sample
                if len(sound_slice) < target_len:
                    sound_slice = np.pad(sound_slice, (0, target_len - len(sound_slice)), mode='constant')
                drum_track[start_sample:end_sample] += sound_slice
            
            # Render melody
            for note in melody_pattern.notes:
                start_sample = int(note.start_time * samples_per_beat)
                frequency = 440 * (2 ** ((note.pitch - 69) / 12))
                sound = self.synthesizer.generate_note(
                    frequency, note.duration, params['synth_type'], note.velocity
                )
                end_sample = min(start_sample + len(sound), total_samples)
                # --- Robust shape fix ---
                sound_slice = sound[:end_sample - start_sample]
                target_len = end_sample - start_sample
                if len(sound_slice) < target_len:
                    sound_slice = np.pad(sound_slice, (0, target_len - len(sound_slice)), mode='constant')
                melody_track[start_sample:end_sample] += sound_slice
        
        # Render bass
            for note in bass_pattern.notes:
                start_sample = int(note.start_time * samples_per_beat)
                frequency = 440 * (2 ** ((note.pitch - 69) / 12))
                sound = self.synthesizer.generate_note(
                    frequency, note.duration, 'sine', note.velocity
                )
                end_sample = min(start_sample + len(sound), total_samples)
                sound_slice = sound[:end_sample - start_sample]
                target_len = end_sample - start_sample
                if len(sound_slice) < target_len:
                    sound_slice = np.pad(sound_slice, (0, target_len - len(sound_slice)), mode='constant')
                bass_track[start_sample:end_sample] += sound_slice
        
        
        

        
        
            # Mix tracks
            final_mix = (
                drum_track * 0.8 +
                melody_track * 0.6 +
                bass_track * 0.7
            ) * AudioConstants.MASTER_VOLUME
        
            # Normalize and prevent clipping
            max_val = np.max(np.abs(final_mix))
            if max_val > 1.0:
                final_mix /= max_val
        
            return final_mix
        
        except Exception as e:
            logger.error(f"Error generating beat: {e}")
            # Return silence on error
            return np.zeros(int(AudioConstants.SAMPLE_RATE * duration))
    
    def preview_drum(self, instrument: str, velocity: float = 1.0):
        """Play a short one-shot drum sound for UI preview."""
        try:
            duration = 0.5  # half-second hit
            if instrument.lower() in ("kick", "bd", "bass"):
                sound = self.drum_synth.kick(duration)
            elif instrument.lower() in ("snare", "sd"):
                sound = self.drum_synth.snare(duration)
            elif instrument.lower() in ("hihat", "hh"):
                sound = self.drum_synth.hihat(duration, open=False)
            elif instrument.lower() in ("openhat", "oh"):
                sound = self.drum_synth.hihat(duration, open=True)
            elif instrument.lower() in ("crash", "cymbal"):
                # Simple reuse of open hat for now
                sound = self.drum_synth.hihat(duration, open=True) * 0.7
            else:
                logger.warning(f"Unknown drum instrument preview: {instrument}")
                return
            sound *= velocity
            self.play_audio(sound)
        except Exception as e:
            logger.error(f"Failed drum preview: {e}")

    def play_audio(self, audio_data: np.ndarray):
        """Play audio using pygame mixer."""
        try:
            # Convert to 16-bit integers
            audio_data = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
            
            # Create stereo if mono
            if len(audio_data.shape) == 1:
                audio_data = np.column_stack((audio_data, audio_data))
            
            # Convert to pygame sound
            sound = pygame.sndarray.make_sound(audio_data)
            
            # Play
            self.is_playing = True
            sound.play()
            
            # Wait for playback to complete
            while pygame.mixer.get_busy():
                pygame.time.Clock().tick(10)
            
            self.is_playing = False
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            self.is_playing = False
    
    def save_audio(self, audio_data: np.ndarray, filename: str):
        """Save audio to WAV file."""
        try:
            # Ensure audio is in the correct format
            audio_data = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
            
            # Save using scipy
            wavfile.write(filename, AudioConstants.SAMPLE_RATE, audio_data)
            
            logger.info(f"Audio saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
    
    def stop_playback(self):
        """Stop current playback."""
        try:
            pygame.mixer.stop()
            self.is_playing = False
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")

# ============================================================================
# EFFECTS PROCESSOR
# ============================================================================

class EffectsProcessor:
    """Audio effects for post-processing."""
    
    @staticmethod
    def reverb(audio: np.ndarray, room_size: float = 0.5, 
               damping: float = 0.5) -> np.ndarray:
        """Simple reverb effect using comb filters."""
        try:
            # Comb filter delays (in samples)
            delays = [1557, 1617, 1491, 1422, 1277, 1356, 1188, 1116]
            
            output = audio.copy()
            
            for delay in delays:
                # Create delayed signal
                delayed = np.zeros_like(audio)
                delayed[delay:] = audio[:-delay] * room_size
                
                # Apply damping
                delayed *= (1 - damping)
                
                # Mix with output
                output += delayed * 0.1
            
            return output
        except Exception as e:
            logger.error(f"Error applying reverb: {e}")
            return audio
    
    @staticmethod
    def compressor(audio: np.ndarray, threshold: float = 0.7, 
                   ratio: float = 4.0) -> np.ndarray:
        """Dynamic range compression."""
        try:
            # Calculate envelope
            envelope = np.abs(audio)
            
            # Apply compression
            compressed = audio.copy()
            mask = envelope > threshold
            compressed[mask] = np.sign(audio[mask]) * (
                threshold + (envelope[mask] - threshold) / ratio
            )
            
            # Makeup gain
            max_before = np.max(np.abs(audio))
            max_after = np.max(np.abs(compressed))
            if max_after > 0:
                compressed *= max_before / max_after
            
            return compressed
        except Exception as e:
            logger.error(f"Error applying compression: {e}")
            return audio

# ============================================================================
# PRESET MANAGER
# ============================================================================

class PresetManager:
    """Manage beat presets and templates."""
    
    def __init__(self, preset_dir: str = "beat_presets"):
        self.preset_dir = preset_dir
        try:
            os.makedirs(preset_dir, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create preset directory: {e}")
        self.presets = self.load_presets()
    
    def load_presets(self) -> Dict[str, Dict]:
        """Load all presets from directory."""
        presets = {}
        
        # Default presets
        presets['Hip Hop Classic'] = {
            'tempo': 90,
            'drum_pattern': 'hiphop',
            'scale': 'minor',
            'synth_type': 'sine',
            'effects': {'reverb': 0.3, 'compression': True}
        }
        
        presets['Trap Banger'] = {
            'tempo': 140,
            'drum_pattern': 'trap',
            'scale': 'minor',
            'synth_type': 'saw',
            'effects': {'reverb': 0.2, 'compression': True}
        }
        
        presets['Lo-Fi Chill'] = {
            'tempo': 75,
            'drum_pattern': 'basic',
            'scale': 'major',
            'synth_type': 'triangle',
            'effects': {'reverb': 0.5, 'compression': False}
        }
        
        return presets
    
    def save_preset(self, name: str, preset: Dict):
        """Save a preset to file."""
        try:
            filename = os.path.join(self.preset_dir, f"{name}.json")
            with open(filename, 'w') as f:
                json.dump(preset, f, indent=2)
            self.presets[name] = preset
            logger.info(f"Saved preset: {name}")
        except Exception as e:
            logger.error(f"Error saving preset: {e}")

# Main function for integration
def create_beat_from_lyrics(lyrics: str, preset: Optional[str] = None) -> Tuple[np.ndarray, Dict]:
    """Main function to create a beat from lyrics."""
    try:
        engine = BeatStudioEngine()
        preset_manager = PresetManager()
        effects = EffectsProcessor()
        
        # Generate the beat
        beat_audio = engine.generate_beat_from_lyrics(lyrics, duration=16.0)
        
        # Apply preset if specified
        if preset and preset in preset_manager.presets:
            preset_data = preset_manager.presets[preset]
            
            # Apply effects from preset
            if 'effects' in preset_data:
                if preset_data['effects'].get('reverb'):
                    beat_audio = effects.reverb(beat_audio, preset_data['effects']['reverb'])
                
                if preset_data['effects'].get('compression'):
                    beat_audio = effects.compressor(beat_audio)
        
        # Return audio and metadata
        metadata = {
            'tempo': engine.sequencer.tempo,
            'duration': len(beat_audio) / AudioConstants.SAMPLE_RATE,
            'preset': preset,
            'lyrics': lyrics[:100] + '...' if len(lyrics) > 100 else lyrics
        }
        
        return beat_audio, metadata
    
    except Exception as e:
        logger.error(f"Error in create_beat_from_lyrics: {e}")
        # Return silence and error metadata
        silence = np.zeros(int(AudioConstants.SAMPLE_RATE * 8.0))
        metadata = {'error': str(e), 'tempo': 120, 'duration': 8.0}
        return silence, metadata
