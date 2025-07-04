import os
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import tempfile
import sounddevice as sd
import soundfile as sf

MODEL_NAME = 'facebook/musicgen-small'  # Switched from 'medium' to 'small' for faster generation

# Load the model once at import
musicgen_model = MusicGen.get_pretrained(MODEL_NAME)


def generate_musicgen_audio(prompt: str, duration: int = 15, out_wav: str = None) -> str:
    """
    Generate audio from a text prompt using MusicGen.
    Returns the path to the generated WAV file.
    """
    # The latest audiocraft MusicGen API does not accept 'duration' as a keyword argument.
    # If duration control is needed, set it as a model property or check the latest docs.
    wav = musicgen_model.generate([prompt], progress=True)
    if out_wav is None:
        fd, out_wav = tempfile.mkstemp(suffix='.wav', prefix='musicgen_')
        os.close(fd)
    audio_write(out_wav, wav[0].cpu(), musicgen_model.sample_rate, strategy="loudness")
    return out_wav


def play_audio(wav_path: str):
    """
    Play a WAV file using sounddevice.
    """
    data, samplerate = sf.read(wav_path, dtype='float32')
    sd.play(data, samplerate)
    sd.wait()


def export_audio(wav_path: str, export_path: str):
    """
    Export the generated WAV file to a user-specified location.
    """
    os.replace(wav_path, export_path) 