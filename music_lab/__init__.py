'''
Music Lab package – combines AI audio generation (MusicGen) with a Tkinter piano-roll
widget.  Heavy dependencies (torch, audiocraft) are imported lazily so the rest of
CodedSwitch can run without them.  Down-stream GUI code should first call
`music_lab.is_available()` to decide whether to enable generation features.
'''
from __future__ import annotations

from importlib import import_module
from typing import Any, Dict

from .generator import MusicGenerator, DependencyError  # noqa: F401 re-export
from .piano_roll import PianoRoll  # noqa: F401 re-export

__all__ = [
    "MusicGenerator",
    "DependencyError",
    "PianoRoll",
    "is_available",
]


_DEF_CACHE: Dict[str, Any] = {}


def is_available() -> bool:
    """Return *True* if heavy MusicGen + torch deps are importable."""
    if "_avail" not in _DEF_CACHE:
        try:
            import_module("audiocraft")
            import_module("torch")
            _DEF_CACHE["_avail"] = True
        except ModuleNotFoundError:
            _DEF_CACHE["_avail"] = False
    return _DEF_CACHE["_avail"]
