#!/usr/bin/env python3
"""
Audio Quality Enhancement for TTS Batch Processor
Provides audio processing, enhancement, and quality improvement features
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class AudioEnhancementConfig:
    """Configuration for audio enhancement"""
    normalize: bool = True
    noise_reduction: bool = False
    compression: bool = False
    equalizer: bool = False
    target_loudness: float = -20.0  # dB
    compression_threshold: float = -20.0  # dB
    compression_ratio: float = 4.0
    eq_bands: List[Tuple[float, float]] = None  # (frequency, gain) pairs

class AudioProcessor:
    """Advanced audio processing and enhancement"""
    
    def __init__(self, config: AudioEnhancementConfig = None):
        self.config = config or AudioEnhancementConfig()
        self._setup_eq_bands()
    
    def _setup_eq_bands(self):
        """Setup default equalizer bands if not provided"""
        if self.config.eq_bands is None:
            self.config.eq_bands = [
                (60, 0.0),      # Bass
                (250, 0.0),     # Low mid
                (1000, 0.0),    # Mid
                (4000, 0.0),    # High mid
                (8000, 0.0),    # High
                (16000, 0.0)    # Very high
            ]
    
    def enhance_audio(self, audio_file: str, output_file: str = None) -> str:
        """Enhance audio file with various processing techniques"""
        try:
            logger.info(f"Enhancing audio: {audio_file}")
            
            # Load audio
            audio, sr = librosa.load(audio_file, sr=None)
            
            # Apply enhancements
            if self.config.normalize:
                audio = self._normalize_audio(audio)
            
            if self.config.noise_reduction:
                audio = self._reduce_noise(audio, sr)
            
            if self.config.compression:
                audio = self._apply_compression(audio)
            
            if self.config.equalizer:
                audio = self._apply_equalizer(audio, sr)
            
            # Save enhanced audio
            output_file = output_file or self._get_enhanced_filename(audio_file)
            sf.write(output_file, audio, sr)
            
            logger.info(f"Audio enhanced and saved: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error enhancing audio {audio_file}: {e}")
            raise
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to target loudness"""
        try:
            # Calculate current loudness
            current_loudness = librosa.feature.rms(y=audio)[0].mean()
            current_loudness_db = 20 * np.log10(current_loudness + 1e-10)
            
            # Calculate gain needed
            gain_db = self.config.target_loudness - current_loudness_db
            gain_linear = 10 ** (gain_db / 20)
            
            # Apply gain
            normalized_audio = audio * gain_linear
            
            # Prevent clipping
            max_val = np.max(np.abs(normalized_audio))
            if max_val > 0.95:
                normalized_audio = normalized_audio * (0.95 / max_val)
            
            logger.debug(f"Normalized audio: {current_loudness_db:.1f}dB -> {self.config.target_loudness:.1f}dB")
            return normalized_audio
            
        except Exception as e:
            logger.warning(f"Normalization failed: {e}")
            return audio
    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply spectral gating noise reduction"""
        try:
            # Apply spectral gating
            noise_reduced = librosa.effects.preemphasis(audio, coef=0.95)
            
            # Additional noise reduction using spectral subtraction
            stft = librosa.stft(noise_reduced)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from first 0.5 seconds
            noise_frames = int(0.5 * sr / 512)  # Assuming 512 hop length
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # Spectral subtraction
            alpha = 2.0  # Subtraction factor
            beta = 0.01  # Floor factor
            cleaned_magnitude = magnitude - alpha * noise_spectrum
            cleaned_magnitude = np.maximum(cleaned_magnitude, beta * magnitude)
            
            # Reconstruct signal
            cleaned_stft = cleaned_magnitude * np.exp(1j * phase)
            cleaned_audio = librosa.istft(cleaned_stft)
            
            logger.debug("Applied noise reduction")
            return cleaned_audio
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return audio
    
    def _apply_compression(self, audio: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Calculate RMS envelope
            rms = librosa.feature.rms(y=audio)[0]
            rms_db = 20 * np.log10(rms + 1e-10)
            
            # Apply compression
            threshold_db = self.config.compression_threshold
            ratio = self.config.compression_ratio
            
            compressed_db = np.where(
                rms_db > threshold_db,
                threshold_db + (rms_db - threshold_db) / ratio,
                rms_db
            )
            
            # Calculate gain
            gain_db = compressed_db - rms_db
            gain_linear = 10 ** (gain_db / 20)
            
            # Apply gain (interpolate to match audio length)
            gain_linear = np.interp(
                np.linspace(0, 1, len(audio)),
                np.linspace(0, 1, len(gain_linear)),
                gain_linear
            )
            
            compressed_audio = audio * gain_linear
            
            logger.debug(f"Applied compression: threshold={threshold_db}dB, ratio={ratio}:1")
            return compressed_audio
            
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return audio
    
    def _apply_equalizer(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply multi-band equalizer"""
        try:
            equalized_audio = audio.copy()
            
            for frequency, gain_db in self.config.eq_bands:
                if gain_db != 0:
                    # Create filter
                    b, a = self._create_peaking_filter(frequency, gain_db, sr)
                    equalized_audio = self._apply_filter(equalized_audio, b, a)
            
            logger.debug(f"Applied equalizer with {len(self.config.eq_bands)} bands")
            return equalized_audio
            
        except Exception as e:
            logger.warning(f"Equalizer failed: {e}")
            return audio
    
    def _create_peaking_filter(self, frequency: float, gain_db: float, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create a peaking filter for equalization"""
        from scipy import signal
        
        # Filter parameters
        Q = 1.0  # Quality factor
        w0 = 2 * np.pi * frequency / sr
        
        # Convert gain to linear scale
        gain_linear = 10 ** (gain_db / 20)
        
        # Create filter coefficients
        b, a = signal.iirpeak(w0, Q, gain_linear)
        return b, a
    
    def _apply_filter(self, audio: np.ndarray, b: np.ndarray, a: np.ndarray) -> np.ndarray:
        """Apply IIR filter to audio"""
        from scipy import signal
        return signal.filtfilt(b, a, audio)
    
    def _get_enhanced_filename(self, original_file: str) -> str:
        """Generate filename for enhanced audio"""
        path = Path(original_file)
        return str(path.parent / f"{path.stem}_enhanced{path.suffix}")
    
    def batch_enhance(self, audio_files: List[str], output_dir: str = None) -> List[str]:
        """Enhance multiple audio files"""
        enhanced_files = []
        
        for audio_file in audio_files:
            try:
                if output_dir:
                    output_path = Path(output_dir) / Path(audio_file).name
                    enhanced_file = self.enhance_audio(audio_file, str(output_path))
                else:
                    enhanced_file = self.enhance_audio(audio_file)
                
                enhanced_files.append(enhanced_file)
                
            except Exception as e:
                logger.error(f"Failed to enhance {audio_file}: {e}")
                enhanced_files.append(audio_file)  # Keep original if enhancement fails
        
        return enhanced_files
    
    def analyze_audio(self, audio_file: str) -> Dict[str, Any]:
        """Analyze audio file and return statistics"""
        try:
            audio, sr = librosa.load(audio_file, sr=None)
            
            # Calculate various metrics
            duration = len(audio) / sr
            rms = librosa.feature.rms(y=audio)[0].mean()
            loudness_db = 20 * np.log10(rms + 1e-10)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0].mean()
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0].mean()
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)[0].mean()
            
            # Dynamic range
            dynamic_range = 20 * np.log10(np.max(np.abs(audio)) / (np.std(audio) + 1e-10))
            
            return {
                'duration': duration,
                'sample_rate': sr,
                'loudness_db': loudness_db,
                'spectral_centroid': spectral_centroid,
                'spectral_bandwidth': spectral_bandwidth,
                'zero_crossing_rate': zcr,
                'dynamic_range_db': dynamic_range,
                'peak_amplitude': np.max(np.abs(audio)),
                'rms_amplitude': rms
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio {audio_file}: {e}")
            return {}
    
    def compare_audio(self, original_file: str, enhanced_file: str) -> Dict[str, Any]:
        """Compare original and enhanced audio files"""
        original_stats = self.analyze_audio(original_file)
        enhanced_stats = self.analyze_audio(enhanced_file)
        
        if not original_stats or not enhanced_stats:
            return {}
        
        # Calculate differences
        differences = {}
        for key in original_stats:
            if key in enhanced_stats:
                if isinstance(original_stats[key], (int, float)):
                    diff = enhanced_stats[key] - original_stats[key]
                    differences[f"{key}_difference"] = diff
                    differences[f"{key}_improvement"] = diff > 0
        
        return {
            'original': original_stats,
            'enhanced': enhanced_stats,
            'differences': differences
        }

class AudioQualityManager:
    """Manages audio quality across the TTS processor"""
    
    def __init__(self, enhancement_config: AudioEnhancementConfig = None):
        self.processor = AudioProcessor(enhancement_config)
        self.quality_log = []
    
    def enhance_tts_output(self, audio_file: str, metadata: Dict = None) -> str:
        """Enhance TTS output audio"""
        try:
            # Log original quality
            original_stats = self.processor.analyze_audio(audio_file)
            
            # Enhance audio
            enhanced_file = self.processor.enhance_audio(audio_file)
            
            # Compare quality
            comparison = self.processor.compare_audio(audio_file, enhanced_file)
            
            # Log quality improvement
            quality_entry = {
                'timestamp': time.time(),
                'original_file': audio_file,
                'enhanced_file': enhanced_file,
                'original_stats': original_stats,
                'comparison': comparison,
                'metadata': metadata or {}
            }
            self.quality_log.append(quality_entry)
            
            logger.info(f"Enhanced TTS output: {audio_file} -> {enhanced_file}")
            return enhanced_file
            
        except Exception as e:
            logger.error(f"Failed to enhance TTS output {audio_file}: {e}")
            return audio_file  # Return original if enhancement fails
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Generate quality improvement report"""
        if not self.quality_log:
            return {'message': 'No audio enhancements performed'}
        
        total_files = len(self.quality_log)
        successful_enhancements = sum(1 for entry in self.quality_log 
                                    if entry['enhanced_file'] != entry['original_file'])
        
        # Calculate average improvements
        improvements = []
        for entry in self.quality_log:
            if 'comparison' in entry and 'differences' in entry['comparison']:
                differences = entry['comparison']['differences']
                if 'loudness_db_difference' in differences:
                    improvements.append(differences['loudness_db_difference'])
        
        avg_loudness_improvement = np.mean(improvements) if improvements else 0
        
        return {
            'total_files_processed': total_files,
            'successful_enhancements': successful_enhancements,
            'enhancement_success_rate': successful_enhancements / total_files * 100,
            'average_loudness_improvement_db': avg_loudness_improvement,
            'recent_enhancements': self.quality_log[-10:]  # Last 10 enhancements
        }
    
    def save_quality_log(self, filename: str):
        """Save quality log to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.quality_log, f, indent=2, default=str)
            logger.info(f"Quality log saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save quality log: {e}")

# Global audio quality manager
audio_quality_manager = AudioQualityManager()
