"""Advanced Lyric Analyzer

Derives detailed musical parameters (tempo, scale, energy, etc.) from raw lyrics
text.  This helper is deliberately dependency-light so it works in an offline
installation while still giving better results than the previous keyword check.

If heavy NLP libraries (spaCy, nltk, textblob) are present in the environment
it can be extended easily, but for now we rely on heuristic statistics that are
fast and deterministic.
"""
from __future__ import annotations

import re
from typing import Dict, Any, List

# Importing from the main audio module causes no circular issues because Scale
# is defined before BeatStudioEngine tries to import this helper.
try:
    from beat_studio_professional import Scale  # type: ignore
except Exception:  # pragma: no cover – fallback if module name changes
    Scale = None  # type: ignore


class LyricAnalyzer:
    """Generate a *music DNA* dict from a lyrics block."""

    # Very small but effective word lists – tweak as desired.
    _POSITIVE: List[str] = [
        "love", "happy", "joy", "bright", "smile", "dance", "light", "shine",
        "good", "sun", "party", "fun", "free", "alive",
    ]
    _NEGATIVE: List[str] = [
        "sad", "cry", "tears", "lonely", "dark", "pain", "gone", "miss",
        "die", "cold", "hurt", "fear",
    ]
    # Words that suggest high physical energy / movement
    _ENERGY: List[str] = [
        "run", "jump", "move", "dance", "party", "wild", "fire", "high",
        "burn", "rush", "fast", "speed",
    ]

    # Regex for syllables (very rough – counts vowels groups)
    _RE_VOWEL = re.compile(r"[aeiouy]+", re.I)

    def analyze(self, lyrics: str) -> Dict[str, Any]:
        text = lyrics.lower()

        # Sentiment score
        pos = sum(text.count(w) for w in self._POSITIVE)
        neg = sum(text.count(w) for w in self._NEGATIVE)
        sentiment = pos - neg  # >0 positive, <0 negative

        # Energy / arousal
        energy_hits = sum(text.count(w) for w in self._ENERGY)
        exclamations = lyrics.count("!")
        energy_score = energy_hits + exclamations * 2  # emphasise "!!!"
        energy_norm = max(0.0, min(1.0, energy_score / 12.0))  # clamp 0-1

        # Syllable density: syllables per word gives hint of complexity
        words = re.findall(r"[a-zA-Z']+", lyrics)
        syllables = sum(len(self._RE_VOWEL.findall(w)) for w in words)
        syll_per_word = syllables / len(words) if words else 1.0

        # Map to parameters -------------------------------------------------
        is_major = sentiment >= 0
        scale = Scale.MAJOR if (Scale and is_major) else (Scale.MINOR if Scale else None)

        # Tempo: base 90, add up to +60 with energy, tweak down for complex words
        tempo = 90 + int(energy_norm * 60) - int((syll_per_word - 1.3) * 10)
        tempo = max(Scale and 60 or 60, min(tempo, 180))  # keep reasonable

        # Drum pattern choice
        if tempo >= 140:
            drum_pattern = "trap"
        elif tempo >= 110:
            drum_pattern = "hiphop"
        else:
            drum_pattern = "basic"

        # Synth choice
        synth_type = "saw" if tempo >= 130 else ("square" if tempo >= 100 else "sine")

        return {
            "tempo": tempo,
            "scale": scale if scale is not None else "minor" if sentiment < 0 else "major",
            "drum_pattern": drum_pattern,
            "synth_type": synth_type,
            "energy": energy_norm,
            "sentiment": sentiment,
            "syllables_per_word": syll_per_word,
        }


# Mini test
if __name__ == "__main__":
    sample = "I feel so happy and alive, we dance all night under the bright lights!"
    print(LyricAnalyzer().analyze(sample))
