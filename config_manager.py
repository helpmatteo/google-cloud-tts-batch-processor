#!/usr/bin/env python3
"""
Configuration Manager for Advanced TTS Batch Processor
Handles YAML configuration files and default settings
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json

@dataclass
class AudioConfig:
    """Audio processing configuration"""
    default_format: str = "MP3"
    default_sample_rate: int = 24000
    enhancement: str = "normalize"
    compression_quality: int = 9

@dataclass
class ProcessingConfig:
    """Processing configuration"""
    max_workers: int = 5
    batch_size: int = 20
    retry_attempts: int = 3
    delay: float = 0.05
    max_concurrent: int = 15
    enable_caching: bool = True
    intelligent_batching: bool = True
    resume_checkpoint: bool = True

@dataclass
class VoiceConfig:
    """Voice configuration"""
    rotation_enabled: bool = True
    default_voice: str = "en-US-Neural2-A"
    language_code: str = "en-US"

class ConfigManager:
    """Manages configuration for the TTS processor"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("tts_config.yaml")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return self.validate_config(config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.get_default_config()
        else:
            config = self.get_default_config()
            self.save_config(config)
            return config
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to YAML file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and add missing defaults"""
        default_config = self.get_default_config()
        
        # Ensure all required sections exist
        for section, default_value in default_config.items():
            if section not in config:
                config[section] = default_value
            elif isinstance(default_value, dict):
                for key, value in default_value.items():
                    if key not in config[section]:
                        config[section][key] = value
        
        return config
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'languages': {
                'en-US': {
                    'name': 'English (US)',
                    'voices': [
                        'en-US-Neural2-A', 'en-US-Neural2-C', 'en-US-Neural2-D',
                        'en-US-Neural2-E', 'en-US-Neural2-F', 'en-US-Neural2-G',
                        'en-US-Neural2-H', 'en-US-Neural2-I', 'en-US-Neural2-J'
                    ],
                    'recommended': True
                },
                'ja-JP': {
                    'name': 'Japanese',
                    'voices': [
                        'ja-JP-Neural2-B', 'ja-JP-Neural2-C',
                        'ja-JP-Neural2-D', 'ja-JP-Neural2-E'
                    ],
                    'recommended': True
                },
                'es-ES': {
                    'name': 'Spanish (Spain)',
                    'voices': [
                        'es-ES-Neural2-A', 'es-ES-Neural2-B',
                        'es-ES-Neural2-C', 'es-ES-Neural2-D'
                    ],
                    'recommended': False
                },
                'fr-FR': {
                    'name': 'French',
                    'voices': [
                        'fr-FR-Neural2-A', 'fr-FR-Neural2-B',
                        'fr-FR-Neural2-C', 'fr-FR-Neural2-D'
                    ],
                    'recommended': False
                },
                'de-DE': {
                    'name': 'German',
                    'voices': [
                        'de-DE-Neural2-A', 'de-DE-Neural2-B',
                        'de-DE-Neural2-C', 'de-DE-Neural2-D'
                    ],
                    'recommended': False
                }
            },
            'audio': {
                'default_format': 'MP3',
                'default_sample_rate': 24000,
                'enhancement': 'normalize',
                'compression_quality': 9,
                'formats': {
                    'MP3': {'extension': 'mp3', 'recommended': True},
                    'WAV': {'extension': 'wav', 'recommended': False},
                    'OGG': {'extension': 'ogg', 'recommended': False},
                    'FLAC': {'extension': 'flac', 'recommended': False}
                }
            },
            'processing': {
                'max_workers': 5,
                'batch_size': 20,
                'retry_attempts': 3,
                'delay': 0.05,
                'max_concurrent': 15,
                'enable_caching': True,
                'intelligent_batching': True,
                'resume_checkpoint': True
            },
            'voice': {
                'rotation_enabled': True,
                'default_voice': 'en-US-Neural2-A',
                'default_language': 'en-US'
            },
            'rate_limits': {
                'requests_per_minute': 300,
                'recommended_delay': 0.1,
                'max_concurrent': 1
            }
        }
    
    def get_language_voices(self, language_code: str) -> List[str]:
        """Get available voices for a language"""
        return self.config.get('languages', {}).get(language_code, {}).get('voices', [])
    
    def get_audio_config(self) -> AudioConfig:
        """Get audio configuration"""
        audio_config = self.config.get('audio', {})
        return AudioConfig(
            default_format=audio_config.get('default_format', 'MP3'),
            default_sample_rate=audio_config.get('default_sample_rate', 24000),
            enhancement=audio_config.get('enhancement', 'normalize'),
            compression_quality=audio_config.get('compression_quality', 9)
        )
    
    def get_processing_config(self) -> ProcessingConfig:
        """Get processing configuration"""
        processing_config = self.config.get('processing', {})
        return ProcessingConfig(
            max_workers=processing_config.get('max_workers', 5),
            batch_size=processing_config.get('batch_size', 20),
            retry_attempts=processing_config.get('retry_attempts', 3),
            delay=processing_config.get('delay', 0.05),
            max_concurrent=processing_config.get('max_concurrent', 15),
            enable_caching=processing_config.get('enable_caching', True),
            intelligent_batching=processing_config.get('intelligent_batching', True),
            resume_checkpoint=processing_config.get('resume_checkpoint', True)
        )
    
    def get_voice_config(self) -> VoiceConfig:
        """Get voice configuration"""
        voice_config = self.config.get('voice', {})
        return VoiceConfig(
            rotation_enabled=voice_config.get('rotation_enabled', True),
            default_voice=voice_config.get('default_voice', 'en-US-Neural2-A'),
            language_code=voice_config.get('default_language', 'en-US')
        )
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update a specific configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config(self.config)
    
    def export_config(self, format: str = 'yaml') -> str:
        """Export configuration in specified format"""
        if format.lower() == 'json':
            return json.dumps(self.config, indent=2)
        elif format.lower() == 'yaml':
            return yaml.dump(self.config, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
