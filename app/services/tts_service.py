"""Text-to-speech service using Piper TTS."""
import subprocess
import tempfile
import logging
import re
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool

logger = logging.getLogger(__name__)


class TTSWorker(QRunnable):
    """Background worker for TTS generation and playback."""
    
    class Signals(QObject):
        started = Signal()
        finished = Signal()
        error = Signal(str)
    
    def __init__(self, text: str, model_path: str, config_path: str, volume: float):
        super().__init__()
        self.text = text
        self.model_path = model_path
        self.config_path = config_path
        self.volume = volume
        self.length_scale = 0.90  # Slightly faster for Indian English rhythm
        self.noise_scale = 0.75   # More expressive
        self.signals = self.Signals()
        self.setAutoDelete(True)
    
    def run(self):
        """Execute TTS in background thread."""
        try:
            self.signals.started.emit()
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                output_path = tmp.name
            
            # Build Piper command
            cmd = [
                'piper-tts',
                '-m', self.model_path,
                '-c', self.config_path,
                '-f', output_path,
                '--length-scale', str(self.length_scale),
                '--noise-scale', str(self.noise_scale)
            ]
            
            # Run Piper TTS
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=self.text, timeout=30)
            
            if process.returncode != 0:
                raise RuntimeError(f"Piper failed: {stderr}")
            
            # Play audio with volume control
            play_cmd = ['aplay', '-D', 'default', output_path]
            
            # Set volume using amixer
            subprocess.run(['amixer', 'set', 'Master', f'{int(self.volume * 100)}%'], 
                         check=False, capture_output=True)
            
            subprocess.run(play_cmd, check=True, capture_output=True, timeout=60)
            
            # Cleanup
            Path(output_path).unlink(missing_ok=True)
            
            self.signals.finished.emit()
            
        except subprocess.TimeoutExpired:
            self.signals.error.emit("TTS timeout")
        except FileNotFoundError:
            self.signals.error.emit("Piper not installed")
        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.signals.error.emit(str(e))


class TTSService(QObject):
    """Text-to-speech service with Piper TTS."""
    
    speaking_started = Signal()
    speaking_finished = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, model_path: str, config_path: str, enabled: bool = True):
        super().__init__()
        self.model_path = model_path
        self.config_path = config_path
        self.enabled = enabled
        self.volume = 1.0
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(1)  # Only one TTS at a time
        
        # Validate Piper installation
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate Piper and model files exist."""
        try:
            subprocess.run(['piper-tts', '--help'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Piper TTS not found in PATH")
        
        if not Path(self.model_path).exists():
            logger.warning(f"Piper model not found: {self.model_path}")
        
        if not Path(self.config_path).exists():
            logger.warning(f"Piper config not found: {self.config_path}")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable TTS."""
        self.enabled = enabled
        logger.info(f"TTS {'enabled' if enabled else 'disabled'}")
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
    
    def speak(self, text: str):
        """Speak text using Piper TTS (non-blocking)."""
        if not self.enabled:
            logger.info("TTS disabled, not speaking")
            return
        
        if not text.strip():
            logger.info("Empty text, not speaking")
            return
        
        # Clean text for speech
        clean_text = self._clean_text_for_speech(text)
        if not clean_text:
            logger.info("No text after cleaning, not speaking")
            return
        
        logger.info(f"Speaking: {clean_text[:50]}...")
        
        # Create and start worker
        worker = TTSWorker(clean_text, self.model_path, self.config_path, self.volume)
        worker.signals.started.connect(self._on_started)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        
        self.thread_pool.start(worker)
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Remove code blocks, URLs, emojis, and formatting for natural speech."""
        # Remove tool results section
        text = re.sub(r'---\s*TOOL RESULTS\s*---[\s\S]*$', '', text)
        
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        
        # Remove ALL emojis using ASCII encoding
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Remove markdown bold/italic but keep text
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # Remove markdown headers but keep text
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove sources section
        text = re.sub(r'Sources:.*$', '', text, flags=re.DOTALL)
        
        # Remove numbered lists but keep text
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove bullet points but keep text
        text = re.sub(r'^[•\-\*]\s+', '', text, flags=re.MULTILINE)
        
        # Replace colons with commas for better speech flow
        text = text.replace(':', ',')
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _on_started(self):
        """Handle TTS started."""
        self.speaking_started.emit()
    
    def _on_finished(self):
        """Handle TTS finished."""
        self.speaking_finished.emit()
    
    def _on_error(self, error: str):
        """Handle TTS error."""
        logger.error(f"TTS error: {error}")
        self.error_occurred.emit(error)
        self.speaking_finished.emit()  # Ensure UI updates
    
    def stop(self):
        """Stop all TTS playback."""
        # Kill any running aplay processes
        try:
            subprocess.run(['pkill', 'aplay'], check=False, capture_output=True)
        except Exception:
            pass
