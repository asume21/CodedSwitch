"""
beat_studio_advanced.py - Advanced features for professional beat production
Extends the base Beat Studio with additional capabilities
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os
import logging
from dataclasses import dataclass
from scipy import signal
from scipy.io import wavfile
import threading
import queue

logger = logging.getLogger(__name__)

# ============================================================================
# ADVANCED AUDIO PROCESSORS
# ============================================================================

class AdvancedEffects:
    """Professional-grade audio effects."""
    
    @staticmethod
    def sidechain_compression(audio: np.ndarray, trigger: np.ndarray, 
                            ratio: float = 4.0, threshold: float = 0.5,
                            attack: float = 0.001, release: float = 0.1,
                            sample_rate: int = 44100) -> np.ndarray:
        """Apply sidechain compression (ducking effect)."""
        # Create envelope follower from trigger signal
        trigger_envelope = np.abs(trigger)
        
        # Smooth the envelope
        attack_samples = int(attack * sample_rate)
        release_samples = int(release * sample_rate)
        
        smoothed_envelope = np.zeros_like(trigger_envelope)
        current_level = 0.0
        
        for i in range(len(trigger_envelope)):
            if trigger_envelope[i] > current_level:
                # Attack
                current_level += (trigger_envelope[i] - current_level) / attack_samples
            else:
                # Release
                current_level -= current_level / release_samples
            
            smoothed_envelope[i] = current_level
        
        # Apply compression based on trigger envelope
        gain_reduction = np.ones_like(audio)
        mask = smoothed_envelope > threshold
        gain_reduction[mask] = 1.0 - ((smoothed_envelope[mask] - threshold) * (1 - 1/ratio))
        
        return audio * gain_reduction
    
    @staticmethod
    def distortion(audio: np.ndarray, drive: float = 2.0, 
                  tone: float = 0.5, mix: float = 0.5) -> np.ndarray:
        """Apply warm distortion/saturation."""
        # Pre-gain
        driven = audio * drive
        
        # Soft clipping using tanh
        distorted = np.tanh(driven)
        
        # Tone control (simple low-pass filter)
        if tone < 1.0:
            b, a = signal.butter(2, tone * 0.5, btype='low')
            distorted = signal.filtfilt(b, a, distorted)
        
        # Mix dry and wet signals
        return audio * (1 - mix) + distorted * mix
    
    @staticmethod
    def delay(audio: np.ndarray, delay_time: float = 0.25, 
             feedback: float = 0.4, mix: float = 0.3,
             sample_rate: int = 44100) -> np.ndarray:
        """Apply delay effect."""
        delay_samples = int(delay_time * sample_rate)
        delayed = np.zeros(len(audio) + delay_samples)
        
        # Initial signal
        delayed[:len(audio)] = audio
        
        # Create delay taps with feedback
        for i in range(int(1 / (1 - feedback))):
            start_idx = delay_samples * (i + 1)
            if start_idx < len(delayed):
                end_idx = min(start_idx + len(audio), len(delayed))
                delayed[start_idx:end_idx] += audio[:end_idx-start_idx] * (feedback ** (i + 1))
        
        # Trim to original length and mix
        delayed = delayed[:len(audio)]
        return audio * (1 - mix) + delayed * mix
    
    @staticmethod
    def stereo_width(audio: np.ndarray, width: float = 1.5) -> np.ndarray:
        """Enhance stereo width."""
        if audio.ndim != 2 or audio.shape[1] != 2:
            # Convert mono to stereo first
            if audio.ndim == 1:
                audio = np.column_stack((audio, audio))
            else:
                return audio
        
        # Extract mid/side
        mid = (audio[:, 0] + audio[:, 1]) / 2
        side = (audio[:, 0] - audio[:, 1]) / 2
        
        # Apply width
        side *= width
        
        # Convert back to L/R
        left = mid + side
        right = mid - side
        
        return np.column_stack((left, right))

# ============================================================================
# ADVANCED PATTERN GENERATORS
# ============================================================================

class PatternGenerator:
    """Generate complex drum patterns algorithmically."""
    
    @staticmethod
    def generate_trap_hihat_pattern(length: int = 16, complexity: float = 0.7) -> List[int]:
        """Generate trap-style hi-hat patterns with rolls."""
        pattern = [0] * length
        
        # Base pattern
        base_positions = [0, 2, 4, 6, 8, 10, 12, 14]
        for pos in base_positions:
            pattern[pos] = 1
        
        # Add complexity (rolls and triplets)
        if complexity > 0.3:
            # Add some off-beat hits
            for i in range(1, length, 4):
                if np.random.random() < complexity:
                    pattern[i] = 1
        
        if complexity > 0.6:
            # Add rapid rolls
            roll_start = np.random.choice([3, 7, 11, 15])
            for i in range(min(3, length - roll_start)):
                pattern[roll_start + i] = 1
        
        return pattern
    
    @staticmethod
    def generate_breakbeat_pattern(length: int = 16) -> Dict[str, List[int]]:
        """Generate classic breakbeat pattern."""
        return {
            'kick': [1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0],
            'snare': [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            'hihat': [1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1]
        }
    
    @staticmethod
    def generate_afrobeat_pattern(length: int = 16) -> Dict[str, List[int]]:
        """Generate Afrobeat-inspired pattern."""
        return {
            'kick': [1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0],
            'snare': [0,0,1,0,0,1,0,0,0,0,1,0,0,1,0,0],
            'hihat': [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0],
            'conga': [0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0]
        }
    
    @staticmethod
    def humanize_pattern(pattern: List[int], timing_variance: float = 0.1,
                        velocity_variance: float = 0.2) -> List[Tuple[float, float]]:
        """Add human-like timing and velocity variations."""
        humanized = []
        
        for i, hit in enumerate(pattern):
            if hit:
                # Add timing variance (in fractions of a step)
                timing_offset = np.random.normal(0, timing_variance)
                timing = i + timing_offset
                
                # Add velocity variance
                velocity = 0.8 + np.random.normal(0, velocity_variance)
                velocity = np.clip(velocity, 0.1, 1.0)
                
                humanized.append((timing, velocity))
        
        return humanized

# ============================================================================
# CHORD PROGRESSION GENERATOR
# ============================================================================

class ChordProgressionGenerator:
    """Generate chord progressions for harmonic content."""
    
    # Common progressions in different styles
    PROGRESSIONS = {
        'pop': ['I', 'V', 'vi', 'IV'],  # 1-5-6-4
        'jazz': ['IIM7', 'V7', 'IM7', 'IM7'],  # 2-5-1
        'blues': ['I7', 'I7', 'I7', 'I7', 'IV7', 'IV7', 'I7', 'I7', 'V7', 'IV7', 'I7', 'V7'],
        'trap': ['i', 'i', 'VI', 'VII'],  # Minor progression
        'rock': ['I', 'IV', 'V', 'I']
    }
    
    # Chord intervals (semitones from root)
    CHORD_TYPES = {
        'major': [0, 4, 7],
        'minor': [0, 3, 7],
        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        'dom7': [0, 4, 7, 10],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8]
    }
    
    @classmethod
    def generate_progression(cls, style: str = 'pop', key: str = 'C', 
                           length: int = 4) -> List[List[int]]:
        """Generate chord progression in MIDI note numbers."""
        # Note mapping
        notes = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}
        root = notes.get(key, 60)
        
        # Get progression template
        progression = cls.PROGRESSIONS.get(style, cls.PROGRESSIONS['pop'])
        
        # Scale degrees for major scale
        scale_degrees = {
            'I': 0, 'II': 2, 'III': 4, 'IV': 5, 'V': 7, 'VI': 9, 'VII': 11,
            'i': 0, 'ii': 2, 'iii': 4, 'iv': 5, 'v': 7, 'vi': 9, 'vii': 11
        }
        
        chords = []
        for chord_symbol in progression[:length]:
            # Parse chord symbol
            degree = chord_symbol.rstrip('M7m7')
            chord_type = 'major'
            
            if 'M7' in chord_symbol:
                chord_type = 'maj7'
            elif 'm7' in chord_symbol:
                chord_type = 'min7'
            elif '7' in chord_symbol:
                chord_type = 'dom7'
            elif degree.islower():
                chord_type = 'minor'
            
            # Get root note
            degree_offset = scale_degrees.get(degree.upper(), 0)
            chord_root = root + degree_offset
            
            # Build chord
            intervals = cls.CHORD_TYPES[chord_type]
            chord = [chord_root + interval for interval in intervals]
            chords.append(chord)
        
        return chords

# ============================================================================
# ADVANCED BEAT ANALYZER
# ============================================================================

class BeatAnalyzer:
    """Analyze existing beats and extract patterns."""
    
    @staticmethod
    def extract_tempo_from_audio(audio: np.ndarray, sample_rate: int = 44100) -> float:
        """Extract tempo (BPM) from audio using onset detection."""
        # Simple onset detection using energy
        frame_size = 2048
        hop_size = 512
        
        # Calculate energy for each frame
        energy = []
        for i in range(0, len(audio) - frame_size, hop_size):
            frame = audio[i:i + frame_size]
            energy.append(np.sum(frame ** 2))
        
        energy = np.array(energy)
        
        # Find peaks (onsets)
        mean_energy = np.mean(energy)
        threshold = mean_energy * 1.5
        peaks = signal.find_peaks(energy, height=threshold, distance=10)[0]
        
        if len(peaks) < 2:
            return 120.0  # Default tempo
        
        # Calculate intervals between peaks
        intervals = np.diff(peaks) * hop_size / sample_rate
        
        # Find most common interval (likely beat interval)
        hist, bins = np.histogram(intervals, bins=50)
        beat_interval = bins[np.argmax(hist)]
        
        # Convert to BPM
        bpm = 60.0 / beat_interval
        
        # Ensure reasonable range
        while bpm < 60:
            bpm *= 2
        while bpm > 200:
            bpm /= 2
        
        return round(bpm)
    
    @staticmethod
    def analyze_rhythm_complexity(pattern: Dict[str, List[int]]) -> float:
        """Analyze rhythmic complexity of a pattern."""
        complexity = 0.0
        
        for instrument, hits in pattern.items():
            # Count syncopation (off-beat hits)
            syncopation = sum(1 for i, hit in enumerate(hits) if hit and i % 4 not in [0, 2])
            
            # Count density
            density = sum(hits) / len(hits)
            
            # Combine metrics
            complexity += (syncopation / len(hits)) * 0.5 + density * 0.5
        
        return complexity / len(pattern)

# ============================================================================
# AUDIO MIXER WITH ADVANCED FEATURES
# ============================================================================

class AdvancedMixer:
    """Professional mixing console with routing and effects."""
    
    def __init__(self, num_channels: int = 8):
        self.num_channels = num_channels
        self.channels = []
        
        for i in range(num_channels):
            self.channels.append({
                'audio': None,
                'volume': 1.0,
                'pan': 0.0,  # -1 to 1
                'mute': False,
                'solo': False,
                'eq': {'low': 0, 'mid': 0, 'high': 0},
                'sends': {'reverb': 0, 'delay': 0}
            })
    
    def set_channel_audio(self, channel: int, audio: np.ndarray):
        """Set audio for a channel."""
        if 0 <= channel < self.num_channels:
            self.channels[channel]['audio'] = audio
    
    def set_channel_volume(self, channel: int, volume: float):
        """Set channel volume (0-1)."""
        if 0 <= channel < self.num_channels:
            self.channels[channel]['volume'] = np.clip(volume, 0, 1)
    
    def set_channel_pan(self, channel: int, pan: float):
        """Set channel pan (-1 to 1)."""
        if 0 <= channel < self.num_channels:
            self.channels[channel]['pan'] = np.clip(pan, -1, 1)
    
    def mix(self, length: int, sample_rate: int = 44100) -> np.ndarray:
        """Mix all channels to stereo output."""
        output = np.zeros((length, 2))
        
        # Check for solo channels
        solo_channels = [ch for ch in self.channels if ch['solo']]
        use_solo = len(solo_channels) > 0
        
        for channel in self.channels:
            if channel['audio'] is None or channel['mute']:
                continue
            
            if use_solo and channel not in solo_channels:
                continue
            
            # Get audio (handle mono/stereo)
            audio = channel['audio']
            if audio.ndim == 1:
                audio = np.column_stack((audio, audio))
            
            # Apply volume
            audio = audio * channel['volume']
            
            # Apply pan
            pan = channel['pan']
            left_gain = 1.0 - max(0, pan)
            right_gain = 1.0 + min(0, pan)
            audio[:, 0] *= left_gain
            audio[:, 1] *= right_gain
            
            # Add to output
            min_len = min(len(audio), length)
            output[:min_len] += audio[:min_len]
        
        return output

# ============================================================================
# SAMPLE LIBRARY MANAGER
# ============================================================================

class SampleLibrary:
    """Manage and organize audio samples."""
    
    def __init__(self, library_path: str = "samples"):
        self.library_path = library_path
        self.samples = {}
        self.categories = {
            'kicks': [],
            'snares': [],
            'hihats': [],
            'percussion': [],
            'fx': [],
            'vocals': []
        }
        
        # Create directory structure
        os.makedirs(library_path, exist_ok=True)
        for category in self.categories:
            os.makedirs(os.path.join(library_path, category), exist_ok=True)
    
    def load_sample(self, name: str, category: str = None) -> Optional[np.ndarray]:
        """Load a sample from the library."""
        if name in self.samples:
            return self.samples[name]
        
        # Search in category or all categories
        search_dirs = [category] if category else self.categories.keys()
        
        for cat in search_dirs:
            file_path = os.path.join(self.library_path, cat, f"{name}.wav")
            if os.path.exists(file_path):
                try:
                    sample_rate, audio = wavfile.read(file_path)
                    # Normalize to float32
                    audio = audio.astype(np.float32) / 32768.0
                    self.samples[name] = audio
                    return audio
                except Exception as e:
                    logger.error(f"Failed to load sample {name}: {e}")
        
        return None
    
    def save_sample(self, name: str, audio: np.ndarray, category: str):
        """Save a sample to the library."""
        if category not in self.categories:
            category = 'fx'
        
        file_path = os.path.join(self.library_path, category, f"{name}.wav")
        
        try:
            # Convert to 16-bit
            audio_16bit = (audio * 32767).astype(np.int16)
            wavfile.write(file_path, 44100, audio_16bit)
            
            # Cache it
            self.samples[name] = audio
            self.categories[category].append(name)
            
            logger.info(f"Saved sample {name} to {category}")
            return True
        except Exception as e:
            logger.error(f"Failed to save sample: {e}")
            return False

# ============================================================================
# LIVE PERFORMANCE MODE
# ============================================================================

class LivePerformance:
    """Real-time beat manipulation and performance features."""
    
    def __init__(self, engine):
        self.engine = engine
        self.is_playing = False
        self.current_position = 0
        self.loop_length = 4  # bars
        self.bpm = 120
        self.effects_queue = queue.Queue()
        
        # Performance pads (like MPC)
        self.pads = {
            i: {'sound': None, 'volume': 1.0, 'pitch': 1.0}
            for i in range(16)
        }
    
    def assign_sound_to_pad(self, pad: int, sound: np.ndarray):
        """Assign a sound to a performance pad."""
        if 0 <= pad < 16:
            self.pads[pad]['sound'] = sound
    
    def trigger_pad(self, pad: int, velocity: float = 1.0):
        """Trigger a pad with velocity sensitivity."""
        if self.pads[pad]['sound'] is not None:
            sound = self.pads[pad]['sound'].copy()
            
            # Apply velocity
            sound *= velocity * self.pads[pad]['volume']
            
            # Apply pitch shift if needed
            if self.pads[pad]['pitch'] != 1.0:
                # Simple pitch shift by resampling
                indices = np.arange(0, len(sound), self.pads[pad]['pitch'])
                indices = indices.astype(int)
                indices = indices[indices < len(sound)]
                sound = sound[indices]
            
            # Queue for playback
            self.effects_queue.put(('play', sound))
    
    def apply_effect(self, effect_type: str, params: Dict):
        """Apply real-time effect."""
        self.effects_queue.put((effect_type, params))
    
    def start_loop(self, pattern: np.ndarray):
        """Start looped playback."""
        self.is_playing = True
        self.current_position = 0
        
        def playback_thread():
            while self.is_playing:
                # Play pattern
                pygame.mixer.Sound(pattern).play()
                
                # Process effect queue
                while not self.effects_queue.empty():
                    effect_type, data = self.effects_queue.get()
                    if effect_type == 'play':
                        pygame.mixer.Sound(data).play()
                    # Add other effects as needed
                
                # Wait for loop duration
                loop_duration = (60.0 / self.bpm) * self.loop_length
                pygame.time.wait(int(loop_duration * 1000))
        
        thread = threading.Thread(target=playback_thread, daemon=True)
        thread.start()
    
    def stop_loop(self):
        """Stop looped playback."""
        self.is_playing = False
        pygame.mixer.stop()

# ============================================================================
# MACHINE LEARNING BEAT SUGGESTIONS
# ============================================================================

class BeatSuggestionEngine:
    """ML-based beat suggestions based on lyrics and style."""
    
    def __init__(self):
        self.style_patterns = {
            'aggressive': {
                'tempo_range': (140, 180),
                'preferred_patterns': ['trap', 'drill'],
                'energy': 0.8,
                'complexity': 0.7
            },
            'chill': {
                'tempo_range': (70, 100),
                'preferred_patterns': ['lofi', 'jazz'],
                'energy': 0.3,
                'complexity': 0.4
            },
            'party': {
                'tempo_range': (120, 130),
                'preferred_patterns': ['edm', 'house'],
                'energy': 0.9,
                'complexity': 0.6
            },
            'emotional': {
                'tempo_range': (60, 90),
                'preferred_patterns': ['ballad', 'rnb'],
                'energy': 0.4,
                'complexity': 0.5
            }
        }
    
    def analyze_lyrics_sentiment(self, lyrics: str) -> str:
        """Simple sentiment analysis for lyrics."""
        # Keywords for different moods
        mood_keywords = {
            'aggressive': ['fight', 'battle', 'hard', 'strong', 'power'],
            'chill': ['relax', 'calm', 'peace', 'easy', 'smooth'],
            'party': ['dance', 'party', 'fun', 'celebrate', 'wild'],
            'emotional': ['love', 'heart', 'feel', 'cry', 'soul']
        }
        
        lyrics_lower = lyrics.lower()
        scores = {}
        
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in lyrics_lower)
            scores[mood] = score
        
        return max(scores, key=scores.get) if any(scores.values()) else 'chill'
    
    def suggest_beat_parameters(self, lyrics: str) -> Dict:
        """Suggest beat parameters based on lyrics."""
        sentiment = self.analyze_lyrics_sentiment(lyrics)
        style_params = self.style_patterns.get(sentiment, self.style_patterns['chill'])
        
        # Select tempo from range
        tempo = np.random.randint(*style_params['tempo_range'])
        
        return {
            'tempo': tempo,
            'pattern': np.random.choice(style_params['preferred_patterns']),
            'energy': style_params['energy'],
            'complexity': style_params['complexity'],
            'suggested_effects': {
                'reverb': 0.3 if sentiment == 'emotional' else 0.1,
                'delay': 0.2 if sentiment in ['chill', 'emotional'] else 0.0,
                'distortion': 0.3 if sentiment == 'aggressive' else 0.0
            }
        }

# ============================================================================
# EXPORT TO DAW FORMATS
# ============================================================================

class DAWExporter:
    """Export beats to various DAW formats."""
    
    @staticmethod
    def export_as_stems(beat_data: Dict[str, np.ndarray], output_dir: str):
        """Export individual tracks as stems."""
        os.makedirs(output_dir, exist_ok=True)
        
        for track_name, audio in beat_data.items():
            file_path = os.path.join(output_dir, f"{track_name}_stem.wav")
            
            # Ensure proper format
            if audio.dtype != np.int16:
                audio = (audio * 32767).astype(np.int16)
            
            wavfile.write(file_path, 44100, audio)
            logger.info(f"Exported stem: {track_name}")
    
    @staticmethod
    def export_midi_pattern(pattern: Dict[str, List[int]], output_file: str, 
                           tempo: int = 120):
        """Export pattern as MIDI file."""
        try:
            from midiutil import MIDIFile
            
            midi = MIDIFile(1)
            midi.addTempo(0, 0, tempo)
            
            # MIDI drum mapping
            drum_map = {
                'kick': 36,
                'snare': 38,
                'hihat': 42,
                'openhat': 46,
                'crash': 49,
                'ride': 51
            }
            
            # Add notes
            for instrument, hits in pattern.items():
                if instrument in drum_map:
                    pitch = drum_map[instrument]
                    for i, hit in enumerate(hits):
                        if hit:
                            time = i * 0.25  # 16th notes
                            midi.addNote(0, 9, pitch, time, 0.25, 100)  # Channel 9 for drums
            
            with open(output_file, 'wb') as f:
                midi.writeFile(f)
            
            logger.info(f"Exported MIDI pattern to {output_file}")
            return True
            
        except ImportError:
            logger.warning("midiutil not installed - MIDI export unavailable")
            return False
    
    @staticmethod
    def create_ableton_project_folder(project_name: str, beat_data: Dict):
        """Create Ableton-compatible project structure."""
        project_dir = f"{project_name} Project"
        os.makedirs(project_dir, exist_ok=True)
        
        # Create subdirectories
        samples_dir = os.path.join(project_dir, "Samples", "Imported")
        os.makedirs(samples_dir, exist_ok=True)
        
        # Export audio files
        DAWExporter.export_as_stems(beat_data, samples_dir)
        
        # Create project info file
        info = {
            'project': project_name,
            'created': datetime.now().isoformat(),
            'tempo': beat_data.get('tempo', 120),
            'time_signature': '4/4'
        }
        
        with open(os.path.join(project_dir, 'project_info.json'), 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Created Ableton-compatible project: {project_dir}")

# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def enhance_beat_studio_integration(integration_instance):
    """Add advanced features to existing beat studio integration."""
    
    # Add advanced effects
    integration_instance.advanced_effects = AdvancedEffects()
    
    # Add pattern generator
    integration_instance.pattern_generator = PatternGenerator()
    
    # Add chord generator
    integration_instance.chord_generator = ChordProgressionGenerator()
    
    # Add beat analyzer
    integration_instance.beat_analyzer = BeatAnalyzer()
    
    # Add mixer
    integration_instance.mixer = AdvancedMixer()
    
    # Add sample library
    integration_instance.sample_library = SampleLibrary()
    
    # Add live performance
    integration_instance.live_performance = LivePerformance(integration_instance.engine)
    
    # Add ML suggestions
    integration_instance.suggestion_engine = BeatSuggestionEngine()
    
    # Add DAW exporter
    integration_instance.daw_exporter = DAWExporter()
    
    logger.info("✨ Advanced beat studio features loaded!")
    
    return integration_instance