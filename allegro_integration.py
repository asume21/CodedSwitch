import os
import torch
from Allegro_Music_Transformer.x_transformer import TransformerWrapper, Decoder, AutoregressiveWrapper
from Allegro_Music_Transformer import TMIDIX

MODEL_PATH = os.path.join('backups', 'slim_backup')
SEQ_LEN = 2048

def load_allegro_model(model_path=MODEL_PATH, device='cuda' if torch.cuda.is_available() else 'cpu'):
    model = TransformerWrapper(
        num_tokens=3088,
        max_seq_len=SEQ_LEN,
        attn_layers=Decoder(dim=1024, depth=16, heads=8, attn_flash=True)
    )
    model = AutoregressiveWrapper(model)
    model = torch.nn.DataParallel(model)
    model.to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

# Singleton pattern for model loading
_allegro_model = None

def get_allegro_model():
    global _allegro_model
    if _allegro_model is None:
        _allegro_model = load_allegro_model()
    return _allegro_model

def generate_midi_from_prompt(prompt_tokens, max_length=SEQ_LEN):
    """
    Generate a MIDI file from control tokens using Allegro Music Transformer.
    prompt_tokens: list of int (control tokens, e.g. from lyric analysis)
    Returns: MIDI bytes
    """
    model = get_allegro_model()
    device = next(model.parameters()).device
    x = torch.tensor([prompt_tokens], dtype=torch.long, device=device)
    with torch.no_grad():
        y = model.generate(x, max_seq_len=max_length)
    # Convert generated tokens to MIDI
    midi_data = TMIDIX.Tegridy_MIDI_Converter(y[0].tolist())
    return midi_data 