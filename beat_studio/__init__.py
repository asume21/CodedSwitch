"""Beat Studio package wrapper.
This lightweight wrapper makes the existing `Beat_Studio.py` module importable
as a standard package called `beat_studio`, so other code can simply
`import beat_studio`.
"""

# Re-export everything from the original module
from importlib import import_module

_bs = import_module('beat_studio_professional')

globals().update(_bs.__dict__)

__all__ = [name for name in globals() if not name.startswith('_')]
