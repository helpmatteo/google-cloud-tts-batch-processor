#!/usr/bin/env python3
"""
Advanced Text-to-Speech Batch Processor
High-performance batch processing tool for Google Cloud Text-to-Speech API
Supports multiple languages, voice rotation, caching, and intelligent optimizations
"""

import os
import time
import json
import logging
import asyncio
import aiohttp
import hashlib
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPIError
import argparse
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue, PriorityQueue
import pickle
from functools import lru_cache
import signal
import sys
import itertools

# Rich CLI imports
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tts_batch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

# Import enhanced features
from .config_manager import ConfigManager
from .error_handler import error_handler, safe_tts_call
from .audio_processor import audio_quality_manager

class VoiceRotator:
    """Manages rotation between different neural voices"""
    
    def __init__(self, rotation_enabled: bool = True, language_code: str = "en-US"):
        self.rotation_enabled = rotation_enabled
        self.language_code = language_code
        
        # Default voice sets for different languages
        self.voice_sets = {
            "en-US": [
                "en-US-Neural2-A",  # Female
                "en-US-Neural2-C",  # Male
                "en-US-Neural2-D",  # Female
                "en-US-Neural2-E",  # Male
                "en-US-Neural2-F",  # Female
                "en-US-Neural2-G",  # Male
                "en-US-Neural2-H",  # Female
                "en-US-Neural2-I",  # Male
                "en-US-Neural2-J",  # Male
            ],
            "ja-JP": [
                "ja-JP-Neural2-B",  # Female
                "ja-JP-Neural2-C",  # Male
                "ja-JP-Neural2-D",  # Female
                "ja-JP-Neural2-E",  # Male
            ],
            "es-ES": [
                "es-ES-Neural2-A",  # Female
                "es-ES-Neural2-B",  # Male
                "es-ES-Neural2-C",  # Female
                "es-ES-Neural2-D",  # Male
            ],
            "fr-FR": [
                "fr-FR-Neural2-A",  # Female
                "fr-FR-Neural2-B",  # Male
                "fr-FR-Neural2-C",  # Female
                "fr-FR-Neural2-D",  # Male
            ],
            "de-DE": [
                "de-DE-Neural2-A",  # Female
                "de-DE-Neural2-B",  # Male
                "de-DE-Neural2-C",  # Female
                "de-DE-Neural2-D",  # Male
            ]
        }
        
        # Get voices for the specified language, fallback to en-US if not found
        self.available_voices = self.voice_sets.get(language_code, self.voice_sets["en-US"])
        self.voice_cycle = itertools.cycle(self.available_voices)
        self.current_voice_index = 0
        self.voice_lock = threading.Lock()
        
    def get_next_voice(self) -> str:
        """Get the next voice in rotation"""
        if not self.rotation_enabled:
            return self.available_voices[0]  # Default to first voice if rotation disabled
            
        with self.voice_lock:
            voice = next(self.voice_cycle)
            self.current_voice_index = (self.current_voice_index + 1) % len(self.available_voices)
            return voice
    
    def get_current_voice(self) -> str:
        """Get the current voice without advancing"""
        if not self.rotation_enabled:
            return self.available_voices[0]
        return self.available_voices[self.current_voice_index]
    
    def get_available_voices(self) -> List[str]:
        """Get list of all available voices"""
        return self.available_voices.copy()
    
    def set_rotation_enabled(self, enabled: bool):
        """Enable or disable voice rotation"""
        self.rotation_enabled = enabled

@dataclass
class UltraProcessingConfig:
    """Advanced configuration for ultra-optimized batch processing"""
    voice_name: str = "en-US-Neural2-A"
    audio_format: str = "MP3"
    sample_rate: int = 24000
    delay: float = 0.05  # Reduced delay for ultra mode
    max_workers: int = 5  # More workers
    batch_size: int = 20  # Larger batches
    retry_attempts: int = 3
    retry_delay: float = 0.5
    enable_caching: bool = True
    enable_async: bool = True
    connection_pool_size: int = 10
    max_concurrent_requests: int = 15
    intelligent_batching: bool = True
    resume_from_checkpoint: bool = True
    checkpoint_interval: int = 50
    voice_rotation_enabled: bool = True  # New: Enable voice rotation

class AudioCache:
    """Intelligent caching system for TTS audio files"""
    
    def __init__(self, cache_dir: str = "tts_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_db = self.cache_dir / "cache.db"
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize SQLite cache database"""
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audio_cache (
                    sentence_hash TEXT PRIMARY KEY,
                    voice_name TEXT,
                    audio_format TEXT,
                    sample_rate INTEGER,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _get_sentence_hash(self, sentence: str, voice_name: str, audio_format: str, sample_rate: int) -> str:
        """Generate hash for sentence and parameters"""
        content = f"{sentence}|{voice_name}|{audio_format}|{sample_rate}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_cached_audio(self, sentence: str, voice_name: str, audio_format: str, sample_rate: int) -> Optional[str]:
        """Get cached audio file if exists"""
        sentence_hash = self._get_sentence_hash(sentence, voice_name, audio_format, sample_rate)
        
        with sqlite3.connect(self.cache_db) as conn:
            cursor = conn.execute(
                "SELECT file_path FROM audio_cache WHERE sentence_hash = ?",
                (sentence_hash,)
            )
            result = cursor.fetchone()
            
            if result:
                file_path = Path(result[0])
                if file_path.exists():
                    logger.debug(f"Cache hit for sentence: {sentence[:30]}...")
                    return str(file_path)
                else:
                    # Remove stale cache entry
                    conn.execute("DELETE FROM audio_cache WHERE sentence_hash = ?", (sentence_hash,))
                    conn.commit()
        
        return None
    
    def cache_audio(self, sentence: str, voice_name: str, audio_format: str, sample_rate: int, file_path: str):
        """Cache audio file"""
        sentence_hash = self._get_sentence_hash(sentence, voice_name, audio_format, sample_rate)
        
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO audio_cache (sentence_hash, voice_name, audio_format, sample_rate, file_path) VALUES (?, ?, ?, ?, ?)",
                (sentence_hash, voice_name, audio_format, sample_rate, file_path)
            )
            conn.commit()

class CheckpointManager:
    """Manages processing checkpoints for resuming interrupted batches"""
    
    def __init__(self, checkpoint_file: str = "processing_checkpoint.json"):
        self.checkpoint_file = Path(checkpoint_file)
    
    def save_checkpoint(self, processed_indices: Set[int], total_count: int):
        """Save processing checkpoint"""
        checkpoint_data = {
            'processed_indices': list(processed_indices),
            'total_count': total_count,
            'timestamp': time.time()
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f)
    
    def load_checkpoint(self) -> Tuple[Set[int], int]:
        """Load processing checkpoint"""
        if not self.checkpoint_file.exists():
            return set(), 0
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            return set(checkpoint_data['processed_indices']), checkpoint_data['total_count']
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
            return set(), 0
    
    def clear_checkpoint(self):
        """Clear checkpoint file"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

class IntelligentBatcher:
    """Intelligent batching based on sentence length and complexity"""
    
    def __init__(self, max_batch_size: int = 20):
        self.max_batch_size = max_batch_size
    
    def create_optimized_batches(self, sentences: List[str]) -> List[List[Tuple[int, str]]]:
        """Create optimized batches based on sentence characteristics"""
        if not sentences:
            return []
        
        # Calculate sentence complexity scores
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = self._calculate_complexity_score(sentence)
            sentence_scores.append((i + 1, sentence, score))
        
        # Sort by complexity (process complex sentences first)
        sentence_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Create balanced batches
        batches = []
        current_batch = []
        current_batch_score = 0
        
        for index, sentence, score in sentence_scores:
            if len(current_batch) >= self.max_batch_size or current_batch_score > 100:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [(index, sentence)]
                current_batch_score = score
            else:
                current_batch.append((index, sentence))
                current_batch_score += score
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _calculate_complexity_score(self, sentence: str) -> float:
        """Calculate sentence complexity score"""
        score = 0
        score += len(sentence) * 0.1  # Length factor
        score += sentence.count('。') * 5  # Sentence endings
        score += sentence.count('、') * 2  # Commas
        score += sentence.count('「') * 3  # Quotation marks
        score += sentence.count('」') * 3
        return score

class AdvancedTTSProcessor:
    """Advanced batch processor for multi-language text-to-speech"""
    
    def __init__(self, 
                 credentials_path: Optional[str] = None,
                 output_dir: str = "tts_output_ultra",
                 config: UltraProcessingConfig = None):
        """Initialize the ultra-optimized TTS processor"""
        self.output_dir = Path(output_dir)
        self.config = config or UltraProcessingConfig()
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.cache = AudioCache() if self.config.enable_caching else None
        self.checkpoint_manager = CheckpointManager() if self.config.resume_from_checkpoint else None
        self.batcher = IntelligentBatcher(self.config.batch_size) if self.config.intelligent_batching else None
        
        # Initialize voice rotator
        self.voice_rotator = VoiceRotator(self.config.voice_rotation_enabled)
        
        # Initialize Google Cloud TTS client
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        try:
            self.client = texttospeech.TextToSpeechClient()
            logger.info("Google Cloud TTS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud TTS client: {e}")
            raise
        
        # Thread-safe components
        self.results_lock = threading.Lock()
        self.processed_indices = set()
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Received shutdown signal, saving checkpoint...")
        if self.checkpoint_manager:
            self.checkpoint_manager.save_checkpoint(self.processed_indices, len(self.sentences))
        sys.exit(0)
    
    def get_audio_encoding(self) -> texttospeech.AudioEncoding:
        """Convert string format to Google TTS AudioEncoding enum"""
        encoding_map = {
            'MP3': texttospeech.AudioEncoding.MP3,
            'WAV': texttospeech.AudioEncoding.LINEAR16,
            'OGG': texttospeech.AudioEncoding.OGG_OPUS,
            'FLAC': texttospeech.AudioEncoding.MP3
        }
        return encoding_map.get(self.config.audio_format.upper(), texttospeech.AudioEncoding.MP3)
    
    def _create_safe_filename(self, sentence: str, index: int) -> str:
        """
        Create a safe filename from Japanese sentence
        
        Args:
            sentence: Japanese sentence
            index: Sentence index for fallback
            
        Returns:
            Safe filename string
        """
        import re
        import unicodedata
        
        # Remove leading/trailing whitespace
        sentence = sentence.strip()
        
        # Limit length to avoid filesystem issues (max 100 chars)
        if len(sentence) > 100:
            sentence = sentence[:97] + "..."
        
        # Replace problematic characters
        # Remove or replace characters that cause filesystem issues
        sentence = re.sub(r'[<>:"/\\|?*]', '', sentence)
        
        # Replace spaces and other separators with underscores
        sentence = re.sub(r'[\s、。！？!?]', '_', sentence)
        
        # Remove multiple consecutive underscores
        sentence = re.sub(r'_+', '_', sentence)
        
        # Remove leading/trailing underscores
        sentence = sentence.strip('_')
        
        # If sentence is empty or only contains special chars, use index
        if not sentence or sentence.isspace():
            sentence = f"sentence_{index:04d}"
        
        # Add index prefix for uniqueness and ordering
        safe_filename = f"{index:04d}_{sentence}"
        
        return safe_filename
    
    def synthesize_sentence_ultra(self, sentence: str, index: int) -> Optional[str]:
        """Ultra-optimized sentence synthesis with caching and advanced retry logic"""
        
        # Get voice for this sentence (rotation enabled)
        current_voice = self.voice_rotator.get_next_voice()
        
        # Create safe filename from Japanese sentence
        safe_filename = self._create_safe_filename(sentence, index)
        
        # Check cache first
        if self.cache:
            cached_file = self.cache.get_cached_audio(
                sentence, current_voice, self.config.audio_format, self.config.sample_rate
            )
            if cached_file:
                # Copy cached file to output directory
                cached_path = Path(cached_file)
                output_filename = f"{safe_filename}.{self.config.audio_format.lower()}"
                output_path = self.output_dir / output_filename
                
                if not output_path.exists():
                    import shutil
                    shutil.copy2(cached_path, output_path)
                
                logger.info(f"Cache hit: {output_filename} - '{sentence[:30]}...' (Voice: {current_voice})")
                return str(output_path)
        
        # Perform synthesis with advanced retry logic
        for attempt in range(self.config.retry_attempts):
            try:
                # Create synthesis input
                synthesis_input = texttospeech.SynthesisInput(text=sentence)
                
                # Configure voice
                voice = texttospeech.VoiceSelectionParams(
                    language_code=self.language_code,
                    name=current_voice
                )
                
                # Configure audio
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=self.get_audio_encoding(),
                    sample_rate_hertz=self.config.sample_rate
                )
                
                # Perform synthesis
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # Save audio file
                file_extension = self.config.audio_format.lower()
                filename = f"{safe_filename}.{file_extension}"
                filepath = self.output_dir / filename
                
                with open(filepath, "wb") as out:
                    out.write(response.audio_content)
                
                # Cache the result
                if self.cache:
                    self.cache.cache_audio(
                        sentence, current_voice, self.config.audio_format, 
                        self.config.sample_rate, str(filepath)
                    )
                
                logger.info(f"Generated: {filename} - '{sentence[:30]}...' (Voice: {current_voice})")
                return str(filepath)
                
            except GoogleAPIError as e:
                if "quota" in str(e).lower() or "rate" in str(e).lower():
                    wait_time = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limit hit for sentence {index}, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                logger.error(f"Google Cloud error for sentence {index}: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error for sentence {index}, attempt {attempt + 1}: {e}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay)
                    continue
                return None
        
        return None
    
    def display_processing_stats(self, stats: Dict):
        """Display processing statistics with Rich"""
        table = Table(title="Processing Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Total Sentences", str(stats.get('total', 0)))
        table.add_row("Processed", str(stats.get('processed', 0)))
        table.add_row("Successful", str(stats.get('successful', 0)))
        table.add_row("Failed", str(stats.get('failed', 0)))
        table.add_row("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
        table.add_row("Processing Speed", f"{stats.get('speed', 0):.1f} sentences/sec")
        
        console.print(table)
    
    def create_progress_display(self, total_sentences: int):
        """Create rich progress display"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        )
        return progress
    
    def process_batch_ultra_async(self, batch: List[Tuple[int, str]]) -> List[Dict]:
        """Process batch with async-like concurrent execution"""
        results = []
        
        # Use ThreadPoolExecutor with semaphore for controlled concurrency
        semaphore = threading.Semaphore(self.config.max_concurrent_requests)
        
        def process_with_semaphore(index, sentence):
            with semaphore:
                return self.synthesize_sentence_ultra(sentence, index)
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all sentences in the batch
            future_to_index = {
                executor.submit(process_with_semaphore, index, sentence): index
                for index, sentence in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                sentence = next(s for i, s in batch if i == index)
                
                try:
                    filepath = future.result()
                    if filepath:
                        results.append({
                            'index': index,
                            'sentence': sentence,
                            'filepath': filepath,
                            'status': 'success'
                        })
                    else:
                        results.append({
                            'index': index,
                            'sentence': sentence,
                            'filepath': None,
                            'status': 'failed'
                        })
                except Exception as e:
                    logger.error(f"Exception for sentence {index}: {e}")
                    results.append({
                        'index': index,
                        'sentence': sentence,
                        'filepath': None,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        return results
    
    def process_batch_ultra(self, sentences: List[str]) -> Dict:
        """Ultra-optimized batch processing with all advanced features"""
        self.sentences = sentences  # Store for signal handler
        
        # Load checkpoint if resuming
        if self.checkpoint_manager:
            processed_indices, total_count = self.checkpoint_manager.load_checkpoint()
            if processed_indices and total_count == len(sentences):
                logger.info(f"Resuming from checkpoint: {len(processed_indices)} sentences already processed")
                self.processed_indices = processed_indices
            else:
                self.checkpoint_manager.clear_checkpoint()
        
        results = {
            'total': len(sentences),
            'successful': 0,
            'failed': 0,
            'files': [],
            'errors': [],
            'processing_time': 0,
            'average_time_per_sentence': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info(f"Starting ultra-optimized batch processing of {len(sentences)} sentences")
        if self.config.voice_rotation_enabled:
            available_voices = self.voice_rotator.get_available_voices()
            logger.info(f"Voice rotation enabled: {len(available_voices)} voices available")
            logger.info(f"Available voices: {', '.join(available_voices)}")
        else:
            logger.info(f"Using fixed voice: {self.config.voice_name}")
        logger.info(f"Output format: {self.config.audio_format}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Max workers: {self.config.max_workers}")
        logger.info(f"Max concurrent requests: {self.config.max_concurrent_requests}")
        logger.info(f"Intelligent batching: {self.config.intelligent_batching}")
        logger.info(f"Caching enabled: {self.config.enable_caching}")
        
        start_time = time.time()
        
        # Create optimized batches
        if self.batcher:
            batches = self.batcher.create_optimized_batches(sentences)
        else:
            # Simple batching
            batches = []
            for i in range(0, len(sentences), self.config.batch_size):
                batch_sentences = sentences[i:i + self.config.batch_size]
                batch_tuples = [(i + j + 1, sentence.strip()) for j, sentence in enumerate(batch_sentences)]
                batches.append(batch_tuples)
        
        logger.info(f"Created {len(batches)} optimized batches for processing")
        
        # Process batches
        for batch_num, batch in enumerate(batches, 1):
            batch_start = time.time()
            
            # Skip already processed sentences
            if self.checkpoint_manager:
                batch = [(index, sentence) for index, sentence in batch if index not in self.processed_indices]
                if not batch:
                    logger.info(f"Skipping batch {batch_num} - all sentences already processed")
                    continue
            
            logger.info(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} sentences)")
            
            # Process the batch
            batch_results = self.process_batch_ultra_async(batch)
            
            # Update overall results
            with self.results_lock:
                for result in batch_results:
                    if result['status'] == 'success':
                        results['successful'] += 1
                        results['files'].append(result)
                        self.processed_indices.add(result['index'])
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Index {result['index']}: {result['sentence']}")
            
            batch_time = time.time() - batch_start
            logger.info(f"Batch {batch_num} completed in {batch_time:.2f}s")
            
            # Save checkpoint periodically
            if self.checkpoint_manager and batch_num % self.config.checkpoint_interval == 0:
                self.checkpoint_manager.save_checkpoint(self.processed_indices, len(sentences))
                logger.info(f"Checkpoint saved: {len(self.processed_indices)} sentences processed")
            
            # Rate limiting between batches
            if self.config.delay > 0 and batch_num < len(batches):
                time.sleep(self.config.delay)
            
            # Progress update
            if batch_num % 3 == 0 or batch_num == len(batches):
                elapsed = time.time() - start_time
                processed = len(self.processed_indices)
                rate = processed / elapsed if elapsed > 0 else 0
                eta = (len(sentences) - processed) / rate if rate > 0 else 0
                logger.info(f"Progress: {processed}/{len(sentences)} ({processed/len(sentences)*100:.1f}%) - "
                          f"ETA: {eta:.1f}s")
        
        # Final summary
        total_time = time.time() - start_time
        results['processing_time'] = total_time
        results['average_time_per_sentence'] = total_time / len(sentences) if sentences else 0
        
        logger.info(f"Ultra-optimized batch processing completed in {total_time:.2f} seconds")
        logger.info(f"Results: {results['successful']} successful, {results['failed']} failed")
        logger.info(f"Average time per sentence: {results['average_time_per_sentence']:.3f}s")
        
        # Clear checkpoint on successful completion
        if self.checkpoint_manager:
            self.checkpoint_manager.clear_checkpoint()
        
        return results
    
    def save_results(self, results: Dict, filename: str = "processing_results_ultra.json"):
        """Save processing results to JSON file"""
        results_file = self.output_dir / filename
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Results saved to: {results_file}")

def load_sentences(filepath: str) -> List[str]:
    """Load sentences from text file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        sentences = [line.strip() for line in f if line.strip()]
    return sentences

def main():
    parser = argparse.ArgumentParser(description='Advanced batch processing tool for Google Cloud Text-to-Speech API')
    parser.add_argument('input_file', help='Path to text file with sentences')
    parser.add_argument('--credentials', help='Path to Google Cloud credentials JSON file')
    parser.add_argument('--language', default='en-US', choices=['en-US', 'ja-JP', 'es-ES', 'fr-FR', 'de-DE'], 
                       help='Language code for TTS processing')
    parser.add_argument('--output-dir', default='tts_output', help='Output directory for audio files')
    parser.add_argument('--voice', default='en-US-Neural2-A', help='Google TTS voice name (used when rotation disabled)')
    parser.add_argument('--enable-voice-rotation', action='store_true', default=True, help='Enable voice rotation between available voices')
    parser.add_argument('--disable-voice-rotation', dest='enable_voice_rotation', action='store_false', help='Disable voice rotation (use fixed voice)')
    parser.add_argument('--format', default='MP3', choices=['MP3', 'WAV', 'OGG', 'FLAC'], 
                       help='Audio output format')
    parser.add_argument('--sample-rate', type=int, default=24000, help='Audio sample rate')
    parser.add_argument('--delay', type=float, default=0.05, help='Delay between batches (seconds)')
    parser.add_argument('--max-workers', type=int, default=5, help='Maximum concurrent workers')
    parser.add_argument('--batch-size', type=int, default=20, help='Batch size for processing')
    parser.add_argument('--max-concurrent', type=int, default=15, help='Maximum concurrent requests')
    parser.add_argument('--retry-attempts', type=int, default=3, help='Number of retry attempts')
    parser.add_argument('--enable-caching', action='store_true', default=True, help='Enable audio caching')
    parser.add_argument('--disable-caching', dest='enable_caching', action='store_false', help='Disable audio caching')
    parser.add_argument('--intelligent-batching', action='store_true', default=True, help='Enable intelligent batching')
    parser.add_argument('--disable-intelligent-batching', dest='intelligent_batching', action='store_false', help='Disable intelligent batching')
    parser.add_argument('--resume-checkpoint', action='store_true', default=True, help='Enable checkpoint resuming')
    parser.add_argument('--disable-checkpoint', dest='resume_checkpoint', action='store_false', help='Disable checkpoint resuming')
    parser.add_argument('--max-sentences', type=int, help='Maximum number of sentences to process')
    
    args = parser.parse_args()
    
    try:
        # Load sentences
        logger.info(f"Loading sentences from: {args.input_file}")
        sentences = load_sentences(args.input_file)
        logger.info(f"Loaded {len(sentences)} sentences")
        
        # Limit sentences if specified
        if args.max_sentences:
            sentences = sentences[:args.max_sentences]
            logger.info(f"Limited to {len(sentences)} sentences")
        
        # Create configuration
        config = UltraProcessingConfig(
            voice_name=args.voice,
            audio_format=args.format,
            sample_rate=args.sample_rate,
            delay=args.delay,
            max_workers=args.max_workers,
            batch_size=args.batch_size,
            retry_attempts=args.retry_attempts,
            enable_caching=args.enable_caching,
            intelligent_batching=args.intelligent_batching,
            resume_from_checkpoint=args.resume_checkpoint,
            max_concurrent_requests=args.max_concurrent,
            voice_rotation_enabled=args.enable_voice_rotation
        )
        
        # Initialize processor
        processor = AdvancedTTSProcessor(
            credentials_path=args.credentials,
            output_dir=args.output_dir,
            config=config,
            language_code=args.language
        )
        
        # Process batch
        results = processor.process_batch_ultra(sentences)
        
        # Save results
        processor.save_results(results)
        
        # Display results with Rich
        console.print("\n")
        console.print(Panel.fit(
            "[bold blue]🎤 Advanced TTS Batch Processing Complete![/bold blue]",
            border_style="blue"
        ))
        
        # Create results table
        table = Table(title="Processing Results", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Total Sentences", str(results['total']))
        table.add_row("Successful", f"{results['successful']} ({results['successful']/results['total']*100:.1f}%)")
        table.add_row("Failed", str(results['failed']))
        table.add_row("Processing Time", f"{results['processing_time']:.2f}s")
        table.add_row("Avg Time/Sentence", f"{results['average_time_per_sentence']:.3f}s")
        table.add_row("Output Directory", args.output_dir)
        table.add_row("Language", args.language)
        table.add_row("Voice Rotation", "✅ Enabled" if args.enable_voice_rotation else "❌ Disabled")
        table.add_row("Caching", "✅ Enabled" if args.enable_caching else "❌ Disabled")
        
        console.print(table)
        
        # Show errors if any
        if results['errors']:
            console.print("\n[bold red]Errors Encountered:[/bold red]")
            for error in results['errors'][:5]:
                console.print(f"  • {error}")
            if len(results['errors']) > 5:
                console.print(f"  ... and {len(results['errors']) - 5} more errors")
        
        # Show circuit breaker status
        cb_stats = error_handler.get_circuit_breaker_stats()
        if cb_stats:
            console.print("\n[bold yellow]Circuit Breaker Status:[/bold yellow]")
            for name, stats in cb_stats.items():
                state_emoji = "🟢" if stats['state'] == 'CLOSED' else "🔴" if stats['state'] == 'OPEN' else "🟡"
                console.print(f"  {state_emoji} {name}: {stats['state']} (failures: {stats['failure_count']})")
        
        # Show audio quality report if available
        quality_report = audio_quality_manager.get_quality_report()
        if quality_report.get('total_files_processed', 0) > 0:
            console.print("\n[bold green]Audio Quality Enhancement:[/bold green]")
            console.print(f"  📊 Files enhanced: {quality_report['successful_enhancements']}/{quality_report['total_files_processed']}")
            console.print(f"  📈 Success rate: {quality_report['enhancement_success_rate']:.1f}%")
            if quality_report.get('average_loudness_improvement_db'):
                console.print(f"  🔊 Avg loudness improvement: {quality_report['average_loudness_improvement_db']:.1f}dB")
        
        console.print("\n[bold green]✨ Processing completed successfully![/bold green]")
        
        # Show next steps
        console.print("\n[bold cyan]🚀 Next Steps:[/bold cyan]")
        console.print("  • Check output files in: [cyan]{args.output_dir}[/cyan]")
        console.print("  • Try web interface: [cyan]python start_web_interface.py[/cyan]")
        console.print("  • Run demo: [cyan]python demo.py[/cyan]")
        console.print("  • Get help: [cyan]python smart_cli.py[/cyan]")
        console.print("  • Setup wizard: [cyan]python setup_wizard.py[/cyan]")
        
    except FileNotFoundError:
        logger.error(f"Input file not found: {args.input_file}")
    except Exception as e:
        logger.error(f"Processing failed: {e}")

if __name__ == "__main__":
    main()
