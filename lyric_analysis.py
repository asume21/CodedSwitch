"""Lyric analysis utilities for CodedSwitch

Provides lightweight, dependency-free helpers to extract metrics that
inform beat suggestions and lyric-improvement tools.  Designed to run
quickly with no external packages so it can execute inside the GUI
thread if needed.
"""
from __future__ import annotations

import re
from typing import Dict, List


__all__ = [
    "count_syllables",
    "analyze_lyrics",
]

# ---------------------------------------------------------------------------
# Simple lexicons for additional metrics
# ---------------------------------------------------------------------------

_POSITIVE_WORDS = {
    "love", "happy", "joy", "bright", "winner", "shine", "peace", "smile", "good", "great", "awesome",
}
_NEGATIVE_WORDS = {
    "hate", "sad", "dark", "pain", "lose", "lost", "fear", "cry", "bad", "fail", "tears",
}
_PROFANE_WORDS = {
    "shit", "fuck", "bitch", "damn", "ass", "fucker", "bastard",
}

# Very small english stop-word sample to surface keywords
_STOP_WORDS = {
    "the", "and", "a", "an", "is", "in", "on", "for", "to", "of", "with", "that", "this", "it", "at", "by",
}


# ---------------------------------------------------------------------------
# Basic syllable counter
# ---------------------------------------------------------------------------

_VOWELS = "aeiouy"


def _strip_nonalpha(word: str) -> str:
    """Keep only alphabetic characters to simplify subsequent logic."""
    return re.sub(r"[^a-z]", "", word.lower())


def count_syllables(word: str) -> int:
    """Very small heuristic syllable estimator.

    This is *not* perfect, but is accurate enough for musical phrasing
    guidance (<±1 syllable in practice for most English words).
    """
    word = _strip_nonalpha(word)
    if not word:
        return 0

    syllables = 0
    prev_is_vowel = False

    for ch in word:
        is_vowel = ch in _VOWELS
        if is_vowel and not prev_is_vowel:
            syllables += 1
        prev_is_vowel = is_vowel

    # Silent "e" at the end of words like "make", "love"
    if word.endswith("e") and syllables > 1:
        syllables -= 1

    # Every word has at least one syllable
    return max(syllables, 1)


# ---------------------------------------------------------------------------
# Rhyme + flow metrics
# ---------------------------------------------------------------------------

def _rhyme_key(word: str, depth: int = 3) -> str:
    """Very naive rhyme key based on the last *depth* alphabetic characters."""
    word = _strip_nonalpha(word)
    return word[-depth:] if len(word) >= depth else word


def analyze_lyrics(text: str) -> Dict[str, float]:
    """Return aggregate statistics about the supplied *text* lyrics.

    The calculation is intentionally simple so it can run in real-time.
    Results:
        line_count          – total non-blank lines
        total_words         – all words (alpha tokens)
        total_syllables     – total syllables across lyrics
        avg_syllables       – average syllables per line
        syllable_stddev     – stdev of syllables per line (flow regularity)
        rhyme_density       – proportion of lines that rhyme with another line
    """
    lines: List[str] = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return {
            "line_count": 0,
            "total_words": 0,
            "total_syllables": 0,
            "avg_syllables": 0.0,
            "syllable_stddev": 0.0,
            "rhyme_density": 0.0,
        }

    total_syllables = 0
    all_words: List[str] = []
    syllables_per_line: List[int] = []
    total_words = 0

    for ln in lines:
        words_in_line = re.findall(r"[A-Za-z']+", ln)
        all_words.extend(words_in_line)
        total_words += len(words_in_line)
        line_syll = sum(count_syllables(w) for w in words_in_line)
        syllables_per_line.append(line_syll)
        total_syllables += line_syll

    # Flow regularity (standard deviation)
    avg = total_syllables / len(lines)
    variance = sum((s - avg) ** 2 for s in syllables_per_line) / len(syllables_per_line)
    stddev = variance ** 0.5

    # Rhyme density – count how many lines share the same rhyme key
    endings = [_rhyme_key(ln.split()[-1]) for ln in lines]
    rhyme_pairs = 0
    for idx, end in enumerate(endings):
        if any(end == earlier for earlier in endings[:idx]):
            rhyme_pairs += 1
    rhyme_density = rhyme_pairs / len(lines)

    # -------------------------------------------------------------------
    # New metrics
    # -------------------------------------------------------------------

    # Sentiment (very naive word-list scoring)
    pos_hits = sum(1 for w in all_words if w.lower() in _POSITIVE_WORDS)
    neg_hits = sum(1 for w in all_words if w.lower() in _NEGATIVE_WORDS)
    sentiment_score = (pos_hits - neg_hits) / max(1, total_words)
    if sentiment_score > 0.05:
        sentiment = "positive"
    elif sentiment_score < -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # Energy score: words per line (0–20 typical)
    energy = total_words / max(1, len(lines))

    # Lexical richness
    unique_words = len(set(w.lower() for w in all_words))
    lexical_richness = unique_words / max(1, total_words)

    # Keywords – top 5 non-stop words by frequency
    freq: Dict[str, int] = {}
    for w in all_words:
        wl = w.lower()
        if wl in _STOP_WORDS:
            continue
        freq[wl] = freq.get(wl, 0) + 1
    keywords = [kw for kw, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:5]]

    # Alliteration density – consecutive lines sharing starting consonant
    initials = [re.sub(r"[^a-z]", "", ln.lower()).strip()[:1] or "" for ln in lines]
    allit = sum(1 for i in range(1, len(initials)) if initials[i] and initials[i] == initials[i-1])
    alliteration_density = allit / max(1, len(lines)-1)

    # Profanity flag
    profanity_flag = any(w.lower() in _PROFANE_WORDS for w in all_words)

    return {
        "line_count": len(lines),
        "total_words": total_words,
        "total_syllables": total_syllables,
        "avg_syllables": avg,
        "syllable_stddev": stddev,
        "rhyme_density": rhyme_density,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "energy": energy,
        "keywords": keywords,
        "alliteration_density": alliteration_density,
        "lexical_richness": lexical_richness,
        "profanity": profanity_flag,
    }
