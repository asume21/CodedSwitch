import os
import numpy as np
import onnxruntime as rt
from midi_composer.midi_tokenizer import MIDITokenizer
from midi_composer.app_onnx import generate

# Paths to model and tokenizer (update as needed)
MODEL_DIR = os.path.join('midi-composer', 'example')
MODEL_PATH = os.path.join(MODEL_DIR, 'model.onnx')
TOKENIZER_PATH = os.path.join(MODEL_DIR, 'tokenizer.json')

# Load model and tokenizer once (singleton)
_model = None
_tokenizer = None

def load_midi_composer_model():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        _model = [rt.InferenceSession(MODEL_PATH), rt.InferenceSession(MODEL_PATH), MIDITokenizer(TOKENIZER_PATH)]
        _tokenizer = _model[2]
    return _model, _tokenizer

def generate_midi_with_midi_composer(prompt=None, max_len=512, temp=1.0, top_p=0.98, top_k=20):
    """
    Generate a MIDI sequence using midi-composer's ONNX backend.
    prompt: Optional input sequence (as numpy array or None for random)
    Returns: MIDI tokens (can be converted to MIDI file with midi_tokenizer)
    """
    model, tokenizer = load_midi_composer_model()
    # If prompt is a string, tokenize it (implement as needed)
    if isinstance(prompt, str):
        # TODO: Implement lyric-to-token conversion or use a default prompt
        prompt = None
    midi_tokens = generate(model, prompt=prompt, max_len=max_len, temp=temp, top_p=top_p, top_k=top_k)
    return midi_tokens 