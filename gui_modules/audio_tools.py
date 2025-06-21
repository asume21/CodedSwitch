"""
Audio Tools Module for CodedSwitch
Provides professional audio processing capabilities including:
- Audio file loading and playback
- Advanced editing (trim, normalize, fade, reverse, effects, multi-track)
- Waveform visualization
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import sounddevice as sd
import soundfile as sf
class AudioTools:
   
    """Main Audio Tools class that provides audio processing capabilities."""
    
    def __init__(self, parent):
        """Initialize Audio Tools with parent window reference."""
        self.parent = parent
        self.audio_data = None
        self.sample_rate = 44100
        self.audio_stream = None
        self.is_playing = False
        self.volume = 0.8
    
    # Add this method to your AudioTools class in audio_tools.py
    def show_audio_tools(self):
        """Show the Audio Tools window interface."""
        try:
            # Create main audio tools window
            self.window = tk.Toplevel(self.parent.gui.root)
            self.window.title("🎧 CodedSwitch Audio Tools")
            self.window.geometry("900x700")
        
        # Store reference to status var if available
            self.status_var = getattr(self.parent.gui, 'status_var', tk.StringVar())
        
        # Setup the complete UI
            self.setup_ui()
        
        # Window close protocol
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
            logger.info("Audio Tools window opened successfully")
        
        except Exception as e:
            logger.error(f"Failed to show audio tools: {e}")
            messagebox.showerror("Audio Tools Error", f"Could not open Audio Tools: {str(e)}")
    
    def setup_ui(self):
        """Set up the complete Audio Tools interface."""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
    
        ttk.Label(header_frame, text="🎧 Audio Tools", 
             font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
    
        # Audio status
        audio_status = "✅ Audio Available" if self.audio_data is not None else "❌ No Audio Loaded"
        ttk.Label(header_frame, text=audio_status, 
             font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
    
        # Create all the UI sections
        self._create_file_controls(main_frame)
        self._create_waveform_display(main_frame)
        self._create_tool_buttons(main_frame)
        self._create_playback_controls(main_frame)
    
        # Status bar
        self.status_var.set("Audio Tools ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var,
                           relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, pady=(5, 0))
    
    def on_close(self):
        """Handle window closing."""
        try:
            self._stop_playback()
        except:
            pass
        self.window.destroy()
    
    def _create_file_controls(self, parent):
        """Create file loading controls."""
        frame = ttk.LabelFrame(parent, text="📁 Audio File", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # File path entry
        file_row = ttk.Frame(frame)
        file_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_row, text="File:").pack(side=tk.LEFT, padx=(0, 5))
        self.file_path = tk.StringVar()
        entry = ttk.Entry(file_row, textvariable=self.file_path, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(file_row, text="Browse...", command=self._browse_audio)
        browse_btn.pack(side=tk.LEFT)
        
        # Audio info
        self.audio_info = ttk.Label(frame, text="No file loaded")
        self.audio_info.pack(fill=tk.X, pady=5)
    
    def _create_waveform_display(self, parent):
        """Create the waveform display canvas."""
        frame = ttk.LabelFrame(parent, text="📊 Waveform", padding=5)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(frame, bg='white', height=150)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_tool_buttons(self, parent):
        """Create audio processing tool buttons."""
        frame = ttk.LabelFrame(parent, text="⚙️ Tools", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tool buttons
        tools = [
            ("✂️ Trim", self._trim_audio),
            ("🔊 Normalize", self._normalize_audio),
            ("🎚️ Fade", self._fade_audio),
            ("🔄 Reverse", self._reverse_audio)
        ]
        
        for i, (text, cmd) in enumerate(tools):
            btn = ttk.Button(frame, text=text, command=cmd, width=12)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
        
        # Configure grid
        for i in range(len(tools)):
            frame.columnconfigure(i, weight=1)
    
    def _create_playback_controls(self, parent):
        """Create audio playback controls."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Play/Pause/Stop
        ttk.Button(frame, text="⏯️ Play/Pause", 
                  command=self._toggle_playback).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="⏹ Stop", 
                  command=self._stop_playback).pack(side=tk.LEFT, padx=2)
        
        # Volume
        ttk.Label(frame, text="Volume:").pack(side=tk.LEFT, padx=(15, 5))
        self.volume_var = tk.DoubleVar(value=self.volume)
        ttk.Scale(frame, from_=0.0, to=1.0, variable=self.volume_var, 
                 length=100, command=self._set_volume).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(frame, variable=self.progress_var, maximum=100, 
                      mode='determinate').pack(side=tk.LEFT, fill=tk.X, 
                                             expand=True, padx=10)
    
    def _browse_audio(self):
        """Open file dialog to select an audio file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac"), 
                      ("All Files", "*.*")]
        )
        if file_path:
            self.file_path.set(file_path)
            self._load_audio_file(file_path)
    
    def _load_audio_file(self, file_path):
        """Load an audio file for processing."""
        try:
            # Stop any current playback
            self._stop_playback()
            
            # Load audio file
            self.audio_data, self.sample_rate = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(self.audio_data.shape) > 1:
                self.audio_data = np.mean(self.audio_data, axis=1)
            
            # Update UI
            duration = len(self.audio_data) / self.sample_rate
            self.audio_info.config(
                text=f"Duration: {duration:.2f}s | "
                     f"Sample Rate: {self.sample_rate}Hz | Mono"
            )
            
            # Draw waveform
            self._draw_waveform()
            self.status_var.set(f"Loaded: {file_path.split('/')[-1]}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audio: {e}")
    
    def _draw_waveform(self):
        """Draw the audio waveform on the canvas."""
        if self.audio_data is None:
            return
            
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Downsample for display
        num_samples = min(1000, len(self.audio_data))
        step = max(1, len(self.audio_data) // num_samples)
        samples = self.audio_data[::step]
        
        # Normalize
        max_sample = max(abs(samples.max()), abs(samples.min()))
        if max_sample > 0:
            samples = samples / max_sample
        
        # Draw center line
        center = height // 2
        self.canvas.create_line(0, center, width, center, fill="lightgray")
        
        # Draw waveform
        x_scale = width / len(samples)
        for i in range(1, len(samples)):
            x1 = (i-1) * x_scale
            x2 = i * x_scale
            y1 = center - int(samples[i-1] * (center - 5))
            y2 = center - int(samples[i] * (center - 5))
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
    
    def _toggle_playback(self):
        """Toggle audio playback."""
        if self.audio_data is None:
            messagebox.showwarning("Error", "No audio loaded")
            return
            
        if not self.is_playing:
            self._start_playback()
        else:
            self._pause_playback()
    
    def _start_playback(self):
        """Start audio playback."""
        try:
            if not hasattr(self, 'audio_stream') or self.audio_stream is None:
                self.audio_stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32',
                    callback=self._audio_callback
                )
                self.playback_position = 0
                
            self.audio_stream.start()
            self.is_playing = True
            self.status_var.set("Playing...")
            self._update_progress()
            
        except Exception as e:
            messagebox.showerror("Playback Error", f"Failed to play audio: {e}")
    
    def _pause_playback(self):
        """Pause audio playback."""
        if hasattr(self, 'audio_stream') and self.audio_stream is not None:
            self.audio_stream.stop()
            self.is_playing = False
            self.status_var.set("Paused")
    
    def _stop_playback(self):
        """Stop audio playback and reset position."""
        if hasattr(self, 'audio_stream') and self.audio_stream is not None:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
            self.playback_position = 0
            self.progress_var.set(0)
            self.is_playing = False
            self.status_var.set("Stopped")
    
    def _set_volume(self, volume):
        """Set playback volume."""
        self.volume = float(volume)
    
    def _update_progress(self):
        """Update the progress bar during playback."""
        if hasattr(self, 'audio_stream') and self.audio_stream is not None and self.is_playing:
            if hasattr(self, 'playback_position') and hasattr(self, 'audio_data'):
                progress = (self.playback_position / len(self.audio_data)) * 100
                self.progress_var.set(progress)
                
                # Schedule next update
                self.window.after(100, self._update_progress)
    
    def _audio_callback(self, outdata, frames, time, status):
        """Audio callback for playback."""
        if status:
            print(status, file=sys.stderr)
            
        if not hasattr(self, 'playback_position'):
            self.playback_position = 0
            
        if self.audio_data is None:
            outdata.fill(0)
            return
            
        # Calculate remaining samples
        remaining = len(self.audio_data) - self.playback_position
        
        if remaining == 0:
            # End of audio
            self._stop_playback()
            outdata.fill(0)
            return
            
        # Get the next chunk of audio
        chunk_size = min(frames, remaining)
        chunk = self.audio_data[self.playback_position:self.playback_position + chunk_size]
        
        # Apply volume
        chunk = chunk * self.volume
        
        # Handle stereo output if needed
        if len(chunk.shape) == 1 and outdata.shape[1] > 1:
            outdata[:, 0] = chunk
            for i in range(1, outdata.shape[1]):
                outdata[:, i] = chunk
        else:
            outdata[:chunk_size] = chunk.reshape(-1, 1)
        
        # Zero-fill if needed
        if chunk_size < frames:
            outdata[chunk_size:] = 0
        
        # Update position
        self.playback_position += chunk_size
    
    # ===== Audio Processing Methods =====
    
    def _trim_audio(self):
        """Trim the start and end of the audio."""
        if not hasattr(self, 'window') or not self.window.winfo_exists():
            return
            
        # Create trim dialog
        trim_window = tk.Toplevel(self.window)
        trim_window.title("Trim Audio")
        trim_window.geometry("400x300")
        
        duration = len(self.audio_data) / self.sample_rate
        
        ttk.Label(trim_window, text=f"Duration: {duration:.2f} seconds").pack(pady=5)
        
        # Start time control
        ttk.Label(trim_window, text="Start Time (seconds):").pack()
        start_var = tk.DoubleVar(value=0.0)
        ttk.Scale(trim_window, from_=0, to=duration, variable=start_var, 
                 length=350).pack()
        
        # End time control
        ttk.Label(trim_window, text="End Time (seconds):").pack()
        end_var = tk.DoubleVar(value=duration)
        ttk.Scale(trim_window, from_=0, to=duration, variable=end_var, 
                 length=350).pack()
        
        def apply_trim():
            try:
                start_sample = int(start_var.get() * self.sample_rate)
                end_sample = int(end_var.get() * self.sample_rate)
                
                if start_sample >= end_sample:
                    messagebox.showerror("Error", "Start time must be before end time")
                    return
                
                # Trim the audio
                self.audio_data = self.audio_data[start_sample:end_sample]
                
                # Update UI
                self._draw_waveform()
                self.status_var.set(
                    f"Trimmed audio to {start_var.get():.2f}s - {end_var.get():.2f}s"
                )
                trim_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to trim audio: {e}")
        
        ttk.Button(trim_window, text="Apply Trim", command=apply_trim).pack(pady=20)
    
    def _normalize_audio(self):
        """Normalize audio to maximum level."""
        try:
            # Find maximum absolute value
            max_val = np.max(np.abs(self.audio_data))
            
            if max_val > 0:
                # Normalize to 0.9 to avoid potential clipping
                self.audio_data = (self.audio_data / max_val) * 0.9
                
                # Update UI
                self._draw_waveform()
                self.status_var.set("Audio normalized")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to normalize audio: {e}")
    
    def _fade_audio(self):
        """Apply fade in/out to audio."""
        if not hasattr(self, 'window') or not self.window.winfo_exists():
            return
            
        # Create fade dialog
        fade_window = tk.Toplevel(self.window)
        fade_window.title("Fade Audio")
        fade_window.geometry("300x250")
        
        # Fade in control
        ttk.Label(fade_window, text="Fade In (seconds):").pack()
        fade_in_var = tk.DoubleVar(value=0.5)
        ttk.Scale(fade_window, from_=0, to=5, variable=fade_in_var, 
                 length=250).pack()
        
        # Fade out control
        ttk.Label(fade_window, text="Fade Out (seconds):").pack()
        fade_out_var = tk.DoubleVar(value=0.5)
        ttk.Scale(fade_window, from_=0, to=5, variable=fade_out_var, 
                 length=250).pack()
        
        def apply_fade():
            try:
                fade_in_samples = int(fade_in_var.get() * self.sample_rate)
                fade_out_samples = int(fade_out_var.get() * self.sample_rate)
                
                # Apply fade in
                if fade_in_samples > 0:
                    fade_in = np.linspace(0, 1, fade_in_samples)
                    self.audio_data[:fade_in_samples] *= fade_in
                
                # Apply fade out
                if fade_out_samples > 0:
                    fade_out = np.linspace(1, 0, fade_out_samples)
                    self.audio_data[-fade_out_samples:] *= fade_out
                
                # Update UI
                self._draw_waveform()
                self.status_var.set("Applied fade in/out")
                fade_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply fade: {e}")
        
        ttk.Button(fade_window, text="Apply Fade", command=apply_fade).pack(pady=20)
    
    def _reverse_audio(self):
        """Reverse the audio."""
        try:
            self.audio_data = np.flip(self.audio_data)
            self._draw_waveform()
            self.status_var.set("Audio reversed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reverse audio: {e}")
    
    def save_audio(self):
        """Save the processed audio to a file."""
        if self.audio_data is None:
            messagebox.showwarning("Error", "No audio to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                sf.write(file_path, self.audio_data, self.sample_rate)
                self.status_var.set(f"Saved: {file_path.split('/')[-1]}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {e}")
