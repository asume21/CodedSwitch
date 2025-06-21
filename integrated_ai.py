# --- ENHANCED integrated_ai.py with Beat Studio Integration ---

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import os
import logging
import json
import re
from typing import List, Dict, Any
import random

# This is the critical missing import!
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Fallback Classes ---
# Since you likely don't have the full 'ai_code_translator' package,
# these simple classes will prevent the script from crashing on imports.

class Vulnerability:
    """A simple placeholder for a vulnerability object."""
    def __init__(self, description, severity, line_number, category="AI Suggestion"):
        self.description = description
        self.severity = type('Severity', (), {'name': severity})() # Mock severity enum
        self.line_number = line_number
        self.category = category
        self.confidence = "High"

class VulnerabilityScanner:
    """A fallback vulnerability scanner."""
    def scan_code(self, code: str, language: str) -> List[Vulnerability]:
        logger.info("Using fallback vulnerability scanner. For full analysis, a dedicated scanner module is needed.")
        # Returns an empty list, as the AI will provide the main analysis.
        return []

# --- Enhanced AI Interface Class with Beat Studio Integration ---

class IntegratedTranslatorAI:
    """
    Enhanced AI interface designed to work with CodedSwitch AND the Advanced Beat Studio.
    This version adds music production capabilities while maintaining all existing functionality.
    """
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """Initialize the IntegratedTranslatorAI."""
        if not api_key:
            raise ValueError("An API key for Gemini is required.")

        self.model_name = model_name
        self.scanner = VulnerabilityScanner()
        
        # Music production knowledge
        self.music_styles = {
            "Hip-Hop": {
                "characteristics": "Strong beats, syncopated rhythms, sample-based",
                "typical_bpm": "80-140",
                "drum_patterns": "Heavy kick on 1 and 3, snare on 2 and 4"
            },
            "Electronic": {
                "characteristics": "Synthesized sounds, precise timing, layered textures",
                "typical_bpm": "120-140",
                "drum_patterns": "Four-on-floor kick, electronic percussion"
            },
            "Trap": {
                "characteristics": "Rolling hi-hats, heavy 808s, dark atmosphere",
                "typical_bpm": "130-170",
                "drum_patterns": "Fast hi-hats, heavy sub-bass kicks"
            },
            "Rock": {
                "characteristics": "Live drums, guitar-driven, powerful",
                "typical_bpm": "110-140",
                "drum_patterns": "Steady kick/snare alternation, crash accents"
            },
            "Jazz": {
                "characteristics": "Swing rhythms, complex harmonies, improvisation",
                "typical_bpm": "120-180",
                "drum_patterns": "Swing patterns, brush techniques, syncopation"
            }
        }
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.chat_session = self.model.start_chat(history=[])
            logger.info(f"Successfully initialized Gemini interface with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini interface: {e}")
            raise

    def use_gemini_model(self, model_name: str):
        """Switches to a new Gemini model."""
        try:
            self.model_name = model_name
            self.model = genai.GenerativeModel(self.model_name)
            self.chat_session = self.model.start_chat(history=[])
            logger.info(f"Successfully switched to model: {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to model {model_name}: {e}")
            return False

    def translate_code(self, source_code: str, target_language: str, **kwargs) -> str:
        """Translates source code to the target language using the Gemini LLM."""
        if not source_code or not target_language:
            return "// Error: Source code and target language cannot be empty."

        logger.info(f"Starting translation to {target_language} using model {self.model_name}")
        
        prompt = f"""
        Translate the following code into {target_language}.
        Only return the raw, translated code inside a single code block. Do not add explanations.

        SOURCE CODE:
        {source_code}
        """
        try:
            response = self.model.generate_content(prompt)
            # Use regex to reliably extract code from markdown blocks
            match = re.search(r"```(?:\w+\n)?(.*)```", response.text, re.DOTALL)
            if match:
                return match.group(1).strip()
            return response.text.strip() # Fallback if no code block is found
        except Exception as e:
            logger.error(f"Error during translation: {e}")
            return f"// Translation failed: {e}"

    def scan_vulnerabilities(self, code: str, language: str) -> List[Vulnerability]:
        """Scans code for vulnerabilities using the AI model."""
        logger.info(f"Starting AI vulnerability scan for {language} code.")
        
        prompt = f"""
        Analyze the following {language} code for security vulnerabilities.
        For each vulnerability found, describe it in one sentence and provide the severity (LOW, MEDIUM, HIGH, or CRITICAL) and the line number.
        Format each finding as:
        SEVERITY | Line XXX | Description

        If no vulnerabilities are found, return the single word "CLEAN".

        CODE:
        {code}
        """
        try:
            response = self.model.generate_content(prompt)
            vulnerabilities = []
            
            if response.text.strip().upper() == "CLEAN":
                return []

            lines = response.text.strip().split('\n')
            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) == 3:
                    severity, line_num_str, desc = parts
                    line_num = int(re.search(r'\d+', line_num_str).group()) if re.search(r'\d+', line_num_str) else 0
                    vulnerabilities.append(Vulnerability(desc, severity, line_num))
            
            return vulnerabilities
        except Exception as e:
            logger.error(f"Error during vulnerability scan: {e}")
            return []

    def chat_response(self, message: str) -> str:
        """
        Generates a response to a chat message using the persistent chat session.
        Enhanced to understand music production terminology.
        """
        logger.info(f"Sending message to chat: '{message[:50]}...'")
        try:
            # Enhanced prompt for music-aware responses
            if any(word in message.lower() for word in ['beat', 'music', 'melody', 'rhythm', 'song', 'studio', 'bpm']):
                enhanced_message = f"""
                You are Astutely, an AI assistant for CodedSwitch with expertise in both programming AND music production.
                The user is asking about: {message}
                
                Provide helpful advice about music production, beat making, melody composition, or any musical concepts mentioned.
                Be knowledgeable about music theory, production techniques, and creative processes.
                """
                response = self.chat_session.send_message(enhanced_message)
            else:
                # Use the persistent chat session for conversation context
                response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            logger.error(f"Error in chat response: {e}")
            return f"I'm sorry, I encountered an error: {e}"
            
    # Alias for backward compatibility
    def chat_with_ai(self, message: str, conversation_history: list = None) -> str:
        """
        Alias for chat_response to maintain backward compatibility with existing code.
        """
        return self.chat_response(message)

    # === NEW BEAT STUDIO INTEGRATION METHODS ===
    
    def generate_beat_pattern(self, style: str = "Hip-Hop", bpm: int = 120) -> Dict[str, List[int]]:
        """
        Generate beat patterns for the Beat Studio using AI.
        
        Args:
            style: Musical style (Hip-Hop, Electronic, Trap, etc.)
            bpm: Beats per minute
            
        Returns:
            Dictionary with drum patterns for each track
        """
        logger.info(f"Generating {style} beat pattern at {bpm} BPM")
        
        style_info = self.music_styles.get(style, self.music_styles["Hip-Hop"])
        
        prompt = f"""
        Create a {style} drum pattern with these characteristics:
        - Style: {style}
        - BPM: {bpm}
        - Characteristics: {style_info['characteristics']}
        - Typical patterns: {style_info['drum_patterns']}
        
        Generate a 16-step pattern for these tracks:
        - kick: Main kick drum (emphasis on strong beats)
        - snare: Snare drum (typically on beats 2 and 4)
        - hihat: Hi-hat (steady rhythm, often 8th or 16th notes)
        - bass: Bass line (fundamental rhythm)
        
        Return ONLY a JSON object in this exact format:
        {{
            "kick": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
            "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
            "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
            "bass": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]
        }}
        
        Use 1 for hits and 0 for silence. Make it musically appropriate for {style}.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                pattern_data = json.loads(json_match.group())
                
                # Validate and return patterns
                valid_patterns = {}
                for track in ['kick', 'snare', 'hihat', 'bass']:
                    if track in pattern_data and isinstance(pattern_data[track], list):
                        pattern = pattern_data[track][:16]  # Ensure 16 steps
                        # Pad if too short
                        while len(pattern) < 16:
                            pattern.append(0)
                        valid_patterns[track] = pattern
                    else:
                        # Fallback pattern
                        valid_patterns[track] = self._get_fallback_pattern(track, style)
                
                logger.info(f"Successfully generated {style} beat pattern")
                return valid_patterns
            else:
                logger.warning("Could not parse JSON from AI response, using fallback")
                return self._get_fallback_beat_patterns(style)
                
        except Exception as e:
            logger.error(f"Error generating beat pattern: {e}")
            return self._get_fallback_beat_patterns(style)
    
    def generate_melody_sequence(self, key: str = "C", scale: str = "Major", style: str = "Hip-Hop", length: int = 8) -> List[Dict]:
        """
        Generate melody sequences for the Beat Studio piano roll.
        
        Args:
            key: Musical key (C, D, E, F, G, A, B)
            scale: Scale type (Major, Minor, Pentatonic, etc.)
            style: Musical style for melody characteristics
            length: Number of notes to generate
            
        Returns:
            List of note dictionaries with pitch, start, length, velocity
        """
        logger.info(f"Generating {length}-note melody in {key} {scale} for {style}")
        
        prompt = f"""
        Create a {style} melody in {key} {scale} scale with {length} notes.
        
        Musical guidelines:
        - Key: {key}
        - Scale: {scale}
        - Style: {style}
        - Length: {length} notes
        - Make it musically coherent and pleasing
        - Use appropriate intervals for the style
        
        Return ONLY a JSON array of notes in this exact format:
        [
            {{"pitch": 60, "start": 0, "length": 1, "velocity": 80}},
            {{"pitch": 62, "start": 1, "length": 1, "velocity": 75}},
            {{"pitch": 64, "start": 2, "length": 2, "velocity": 85}}
        ]
        
        Where:
        - pitch: MIDI note number (60 = C4, 62 = D4, etc.)
        - start: Beat position (0, 1, 2, 3...)
        - length: Note duration in beats (1 = quarter note, 0.5 = eighth note)
        - velocity: Volume (20-127, typically 60-100)
        
        Create a melody that fits {style} characteristics and sounds good in {key} {scale}.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                melody_data = json.loads(json_match.group())
                
                # Validate and process notes
                valid_notes = []
                for i, note in enumerate(melody_data[:length]):
                    if all(key in note for key in ['pitch', 'start', 'length', 'velocity']):
                        valid_note = {
                            'id': i,
                            'pitch': int(note['pitch']),
                            'start': float(note['start']),
                            'length': float(note['length']),
                            'velocity': int(note['velocity'])
                        }
                        valid_notes.append(valid_note)
                
                if valid_notes:
                    logger.info(f"Successfully generated {len(valid_notes)}-note melody")
                    return valid_notes
                else:
                    logger.warning("No valid notes in AI response, using fallback")
                    return self._get_fallback_melody(key, scale, length)
            else:
                logger.warning("Could not parse JSON from AI response, using fallback")
                return self._get_fallback_melody(key, scale, length)
                
        except Exception as e:
            logger.error(f"Error generating melody: {e}")
            return self._get_fallback_melody(key, scale, length)
    
    def generate_lyrics(self, prompt: str, style: str = "Rap") -> str:
        """
        Enhanced lyric generation with better AI integration.
        
        Args:
            prompt: What the lyrics should be about
            style: Musical style (Rap, Pop, Rock, etc.)
            
        Returns:
            Generated lyrics as string
        """
        logger.info(f"Generating {style} lyrics for prompt: {prompt}")
        
        style_guidance = {
            "Rap": "Use complex rhyme schemes, wordplay, and rhythmic flow. Focus on bars and verses.",
            "Pop": "Create catchy, memorable hooks and relatable themes. Use simple, effective language.",
            "Rock": "Write powerful, emotional lyrics with strong imagery. Use repetitive choruses.",
            "R&B": "Focus on smooth, melodic flow with emotional depth and romantic themes.",
            "CodedSwitch": "Use programming terminology, tech metaphors, and developer culture references."
        }
        
        guidance = style_guidance.get(style, style_guidance["Rap"])
        
        ai_prompt = f"""
        Write {style} lyrics based on this prompt: {prompt}
        
        Style guidance: {guidance}
        
        Requirements:
        - Create 8-16 lines of original lyrics
        - Match the {style} style and rhythm
        - Use creative wordplay and metaphors
        - Keep it appropriate and engaging
        - Focus on the theme: {prompt}
        - Make it catchy and memorable
        
        Write only the lyrics, no explanations.
        """
        
        try:
            response = self.model.generate_content(ai_prompt)
            lyrics = response.text.strip()
            
            if lyrics and len(lyrics) > 20:  # Basic validation
                logger.info(f"Successfully generated {style} lyrics")
                return lyrics
            else:
                logger.warning("AI response too short, using fallback")
                return self._get_fallback_lyrics(prompt, style)
                
        except Exception as e:
            logger.error(f"Error generating lyrics: {e}")
            return self._get_fallback_lyrics(prompt, style)
    
    def analyze_music_for_suggestions(self, current_patterns: Dict, current_melody: List, style: str) -> str:
        """
        Analyze current music and provide creative suggestions.
        
        Args:
            current_patterns: Current drum patterns
            current_melody: Current melody notes
            style: Musical style
            
        Returns:
            Analysis and suggestions as string
        """
        logger.info(f"Analyzing music for {style} suggestions")
        
        prompt = f"""
        Analyze this {style} music composition and provide creative suggestions:
        
        Current drum patterns: {current_patterns}
        Current melody notes: {len(current_melody)} notes
        Style: {style}
        
        Provide suggestions for:
        1. Improving the drum patterns
        2. Enhancing the melody
        3. Adding musical elements
        4. Overall composition tips
        5. Style-specific recommendations
        
        Be specific and actionable in your advice.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error analyzing music: {e}")
            return f"Analysis temporarily unavailable. Try adjusting the BPM, adding swing, or experimenting with different patterns for your {style} track."
    
    # === FALLBACK METHODS ===
    
    def _get_fallback_beat_patterns(self, style: str) -> Dict[str, List[int]]:
        """Generate fallback beat patterns when AI fails."""
        patterns = {
            "Hip-Hop": {
                "kick": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
                "bass": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]
            },
            "Electronic": {
                "kick": [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                "bass": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
            },
            "Trap": {
                "kick": [1,0,0,0,0,0,1,0,0,1,0,0,0,0,1,0],
                "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
                "hihat": [1,1,0,1,1,0,1,1,1,0,1,1,0,1,1,0],
                "bass": [1,0,0,0,0,0,1,0,0,1,0,0,0,0,1,0]
            }
        }
        
        return patterns.get(style, patterns["Hip-Hop"])
    
    def _get_fallback_pattern(self, track: str, style: str) -> List[int]:
        """Get fallback pattern for a specific track."""
        patterns = self._get_fallback_beat_patterns(style)
        return patterns.get(track, [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0])
    
    def _get_fallback_melody(self, key: str, scale: str, length: int) -> List[Dict]:
        """Generate fallback melody when AI fails."""
        # Simple scale-based melody generation
        scale_intervals = {
            "Major": [0, 2, 4, 5, 7, 9, 11],
            "Minor": [0, 2, 3, 5, 7, 8, 10],
            "Pentatonic": [0, 2, 4, 7, 9]
        }
        
        intervals = scale_intervals.get(scale, scale_intervals["Major"])
        base_note = 60  # C4
        
        # Add key offset
        key_offsets = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
        base_note += key_offsets.get(key, 0)
        
        notes = []
        for i in range(length):
            interval = intervals[i % len(intervals)]
            octave_offset = (i // len(intervals)) * 12
            
            note = {
                'id': i,
                'pitch': base_note + interval + octave_offset,
                'start': i,
                'length': 1,
                'velocity': 70 + random.randint(-10, 10)
            }
            notes.append(note)
        
        return notes
    
    def _get_fallback_lyrics(self, prompt: str, style: str) -> str:
        """Generate fallback lyrics when AI fails."""
        templates = {
            "Rap": [
                f"Started with a vision, now I'm here to say",
                f"Working on my craft every single day",
                f"Got that {prompt} running through my mind",
                f"Leave the competition far behind",
                f"This is my moment, this is my time",
                f"Dropping these bars with a perfect rhyme",
                f"From the ground up, building my way",
                f"Never looking back, moving forward today"
            ],
            "CodedSwitch": [
                f"Writing code like poetry, {prompt} in my mind",
                f"Debugging all the errors, leaving bugs behind",
                f"Functions and variables, arrays in a line",
                f"Compiling my dreams with a design so fine",
                f"From Python to JavaScript, languages I know",
                f"Building applications, watch my skills grow",
                f"CodedSwitch in the house, AI by my side",
                f"Translation made easy, I code with pride"
            ],
            "Pop": [
                f"Dreaming about {prompt} every night",
                f"Everything feels so right",
                f"Dancing to the rhythm of my heart",
                f"This is just the start",
                f"Singing out loud, feeling so free",
                f"This is who I'm meant to be",
                f"Shining like a star so bright",
                f"Everything's gonna be alright"
            ]
        }
        
        lyrics = templates.get(style, templates["Rap"])
        return "\n".join(lyrics)