"""BeatAdvisor – converts lyric analysis metrics into concrete beat suggestions.

This module is intentionally heuristic-based and dependency-free so it can run
instantly inside the GUI.  It complements *lyric_analysis.py* and produces a
suggestion-dict that the Beat Studio UI can apply directly.
"""
from __future__ import annotations

from typing import Dict, Any

from lyric_analysis import analyze_lyrics

__all__ = ["suggest_beat"]


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def suggest_beat(lyrics: str) -> Dict[str, Any]:
    """Return a dictionary of beat suggestions for the given *lyrics*.

    Keys:
        recommended_bpm   – integer BPM that should fit the vocal flow
        drum_pattern      – either template-name or algorithmic dict
        instrument_preset – name of a preset in PresetManager (if available)
        mix_preset        – simple dict with reverb / compression advice
        analysis          – the raw analysis metrics for downstream use
    """
    metrics = analyze_lyrics(lyrics)

    bpm = _predict_bpm(metrics)
    drum_pattern = _choose_drum_pattern(metrics)
    instr_preset = _choose_instrument(metrics)
    mix_preset = _choose_mix(metrics)
    chord_mode = _choose_chord_mode(metrics)
    swing = _choose_swing(metrics)

    return {
        "recommended_bpm": bpm,
        "drum_pattern": drum_pattern,
        "instrument_preset": instr_preset,
        "mix_preset": mix_preset,
        "chord_mode": chord_mode,
        "swing": swing,
        "analysis": metrics,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _predict_bpm(m: Dict[str, float]) -> int:
    """Map average syllables + variance to a tempo suggestion."""
    avg = m["avg_syllables"]
    std = m["syllable_stddev"]

    # Base tempo tiers by density
    if avg <= 6:
        bpm = 80
    elif avg <= 8:
        bpm = 90
    elif avg <= 10:
        bpm = 100
    elif avg <= 12:
        bpm = 115
    else:
        bpm = 130

    # If flow is highly irregular, reduce tempo a bit for clarity
    if std > 3:
        bpm = int(bpm * 0.9)

    # Clamp to sensible range
    return max(60, min(180, bpm))


def _choose_drum_pattern(m: Dict[str, float]):
    """Pick drum template based on rhyme density and syllable variance."""
    rhyme = m["rhyme_density"]
    std = m["syllable_stddev"]

    if rhyme > 0.6 and std < 2:
        return "trap"  # dense rhymes + steady flow → modern trap hats
    elif rhyme > 0.4:
        return "hiphop"
    else:
        return "basic"


def _choose_instrument(m: Dict[str, float]):
    """Pick an instrument preset influenced by sentiment and flow."""
    sentiment = m.get("sentiment", "neutral")
    if sentiment == "positive":
        return "Chill Keys"
    elif sentiment == "negative":
        return "Dark 808"
    # Fall back to flow heuristics
    if m["avg_syllables"] > 10:
        return "Aggressive 808"
    elif m["rhyme_density"] > 0.5:
        return "BoomBap Classic"
    return "LoFi Chill"


def _choose_mix(m: Dict[str, float]):
    """Suggest reverb & compression levels."""
    density = m["avg_syllables"]
    if density > 10:
        return {"reverb": 0.25, "compression": True}
    else:
        return {"reverb": 0.4, "compression": False}


def _choose_chord_mode(m: Dict[str, float]):
    """Select chord mode based on sentiment analysis."""
    sentiment = m.get("sentiment", "neutral")
    if sentiment == "positive":
        return "major"
    if sentiment == "negative":
        return "minor"
    return "dorian"


def _choose_swing(m: Dict[str, float]):
    """Return swing percentage (0–60) based on flow irregularity and alliteration."""
    irregularity = m["syllable_stddev"]
    allit = m.get("alliteration_density", 0.0)
    base = min(60, irregularity * 10)  # 0–60 based on stddev up to 6
    bonus = allit * 15  # up to +15 from playful alliteration
    return int(min(60, base + bonus))
