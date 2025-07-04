import os
import re
import random
from ai_code_translator.gemini_interface import GeminiInterface  # Adjust import as needed

# --- AI-powered analysis ---
def analyze_lyrics_with_ai(lyrics: str) -> dict:
    """
    Use Gemini/OpenAI to extract music intent from lyrics.
    Returns a dict: {'mood': str, 'tempo': int, 'key': str, 'structure': list, 'tokens': list}
    """
    try:
        gemini = GeminiInterface()
        prompt = (
            "Analyze the following song lyrics and extract the intended musical mood, tempo (BPM), key, and structure (intro, verse, chorus, etc.). "
            "Then, suggest a list of control tokens (as integers 0-3071) for a music transformer model.\n"
            f"Lyrics:\n{lyrics}\n"
            "Respond as a JSON object with keys: mood, tempo, key, structure (list), tokens (list of ints)."
        )
        response = gemini.ask(prompt)
        # Try to extract JSON from response
        import json
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            raise ValueError("No JSON found in AI response")
    except Exception as e:
        print(f"AI lyric analysis failed: {e}")
        return None

# --- Rule-based fallback ---
def analyze_lyrics_rule_based(lyrics: str) -> dict:
    """
    Simple keyword-based extraction of mood, tempo, key, and structure.
    Returns a dict as above.
    """
    mood = "happy" if any(w in lyrics.lower() for w in ["happy", "joy", "sun", "bright"]) else "sad" if any(w in lyrics.lower() for w in ["sad", "cry", "dark", "blue"]) else "neutral"
    tempo = 120
    if any(w in lyrics.lower() for w in ["fast", "quick", "run", "dance"]):
        tempo = 140
    elif any(w in lyrics.lower() for w in ["slow", "chill", "relax", "calm"]):
        tempo = 90
    key = "C major" if mood == "happy" else "A minor" if mood == "sad" else "G major"
    structure = ["intro", "verse", "chorus", "verse", "chorus", "outro"]
    # Simple tokenization: hash mood, tempo, key, structure to ints
    tokens = [sum(ord(c) for c in mood) % 128, tempo % 128, sum(ord(c) for c in key) % 128]
    tokens += [random.randint(0, 127) for _ in range(16)]
    return {"mood": mood, "tempo": tempo, "key": key, "structure": structure, "tokens": tokens}

# --- Main pipeline ---
def get_music_prompt_from_lyrics(lyrics: str) -> dict:
    """
    Try AI-powered analysis first, fall back to rule-based if needed.
    Returns a dict as above.
    """
    result = analyze_lyrics_with_ai(lyrics)
    if result and "tokens" in result:
        return result
    return analyze_lyrics_rule_based(lyrics) 