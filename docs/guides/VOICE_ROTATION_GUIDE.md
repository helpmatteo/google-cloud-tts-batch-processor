# Voice Rotation Guide

## Overview

The voice rotation feature automatically cycles through different neural voices when generating audio files, providing variety in your TTS output without affecting processing efficiency. This feature supports multiple languages including English, Japanese, Spanish, French, and German.

## How It Works

### Voice Rotation Enabled (Default)
- Each sentence gets a different voice automatically
- Cycles through available neural voices for the selected language
- Thread-safe implementation ensures proper rotation
- Maintains all existing caching and optimization features

### Voice Rotation Disabled
- Uses a single fixed voice for all sentences
- Same behavior as before the feature was added
- Useful for consistent voice output

## Available Voices by Language

### English (en-US)
| Voice Name | Type | Gender | Description |
|------------|------|--------|-------------|
| `en-US-Neural2-A` | Neural2 | Female | Primary female voice |
| `en-US-Neural2-C` | Neural2 | Male | Primary male voice |
| `en-US-Neural2-D` | Neural2 | Female | Alternative female voice |
| `en-US-Neural2-E` | Neural2 | Male | Alternative male voice |
| `en-US-Neural2-F` | Neural2 | Female | Additional female voice |
| `en-US-Neural2-G` | Neural2 | Male | Additional male voice |
| `en-US-Neural2-H` | Neural2 | Female | Additional female voice |
| `en-US-Neural2-I` | Neural2 | Male | Additional male voice |
| `en-US-Neural2-J` | Neural2 | Male | Additional male voice |

### Japanese (ja-JP)
| Voice Name | Type | Gender | Description |
|------------|------|--------|-------------|
| `ja-JP-Neural2-B` | Neural2 | Female | Primary female voice |
| `ja-JP-Neural2-C` | Neural2 | Male | Primary male voice |
| `ja-JP-Neural2-D` | Neural2 | Female | Alternative female voice |
| `ja-JP-Neural2-E` | Neural2 | Male | Alternative male voice |

### Spanish (es-ES)
| Voice Name | Type | Gender | Description |
|------------|------|--------|-------------|
| `es-ES-Neural2-A` | Neural2 | Female | Primary female voice |
| `es-ES-Neural2-B` | Neural2 | Male | Primary male voice |
| `es-ES-Neural2-C` | Neural2 | Female | Alternative female voice |
| `es-ES-Neural2-D` | Neural2 | Male | Alternative male voice |

### French (fr-FR)
| Voice Name | Type | Gender | Description |
|------------|------|--------|-------------|
| `fr-FR-Neural2-A` | Neural2 | Female | Primary female voice |
| `fr-FR-Neural2-B` | Neural2 | Male | Primary male voice |
| `fr-FR-Neural2-C` | Neural2 | Female | Alternative female voice |
| `fr-FR-Neural2-D` | Neural2 | Male | Alternative male voice |

### German (de-DE)
| Voice Name | Type | Gender | Description |
|------------|------|--------|-------------|
| `de-DE-Neural2-A` | Neural2 | Female | Primary female voice |
| `de-DE-Neural2-B` | Neural2 | Male | Primary male voice |
| `de-DE-Neural2-C` | Neural2 | Female | Alternative female voice |
| `de-DE-Neural2-D` | Neural2 | Male | Alternative male voice |

## Usage Examples

### Command Line Usage

```bash
# Enable voice rotation (default)
python tts_batch_processor.py sentences.txt --enable-voice-rotation

# Disable voice rotation and use specific voice
python tts_batch_processor.py sentences.txt --disable-voice-rotation --voice en-US-Neural2-A

# Full example with all options
python tts_batch_processor.py sentences.txt \
    --credentials google-credentials.json \
    --language en-US \
    --enable-voice-rotation \
    --format MP3 \
    --sample-rate 24000 \
    --max-workers 5 \
    --batch-size 20
```

### Configuration File Usage

```json
{
  "voice_name": "en-US-Neural2-A",
  "voice_rotation_enabled": true,
  "audio_format": "MP3",
  "sample_rate": 24000,
  "max_workers": 5,
  "batch_size": 20
}
```

## Benefits

### 1. Audio Variety
- Each sentence has a different voice character
- Creates more engaging and diverse audio content
- Reduces listener fatigue in long audio sequences

### 2. Load Distribution
- Spreads requests across different voice models
- May help avoid rate limiting on specific voices
- Better resource utilization

### 3. Processing Efficiency
- No performance impact on processing speed
- Maintains all existing optimizations
- Thread-safe implementation

### 4. Flexibility
- Easy to enable/disable via command line or config
- Can switch between rotation and fixed voice modes
- Backward compatible with existing workflows

## Technical Implementation

### VoiceRotator Class
```python
class VoiceRotator:
    def __init__(self, rotation_enabled: bool = True, language_code: str = "en-US"):
        self.rotation_enabled = rotation_enabled
        self.language_code = language_code
        
        # Default voice sets for different languages
        self.voice_sets = {
            "en-US": ["en-US-Neural2-A", "en-US-Neural2-C", "en-US-Neural2-D", ...],
            "ja-JP": ["ja-JP-Neural2-B", "ja-JP-Neural2-C", "ja-JP-Neural2-D", ...],
            "es-ES": ["es-ES-Neural2-A", "es-ES-Neural2-B", "es-ES-Neural2-C", ...],
            # ... more languages
        }
        
        self.available_voices = self.voice_sets.get(language_code, self.voice_sets["en-US"])
        self.voice_cycle = itertools.cycle(self.available_voices)
        self.voice_lock = threading.Lock()
    
    def get_next_voice(self) -> str:
        """Get the next voice in rotation"""
        if not self.rotation_enabled:
            return self.available_voices[0]
        
        with self.voice_lock:
            return next(self.voice_cycle)
```

### Integration Points
- **Caching**: Voice is included in cache key for proper cache management
- **Logging**: Voice information is logged for each processed sentence
- **Configuration**: Can be controlled via config file or command line
- **Thread Safety**: Uses locks to ensure proper rotation in concurrent processing

## Testing

### Test Scripts
```bash
# Test voice rotation functionality
python test_voice_rotation.py

# Demonstrate voice rotation in action
python demo_voice_rotation.py
```

### Expected Output
With voice rotation enabled, you should see different voices being used:
```
1. Voice: ja-JP-Neural2-B | Sentence: こんにちは、元気ですか？
2. Voice: ja-JP-Neural2-C | Sentence: 今日は良い天気ですね。
3. Voice: ja-JP-Neural2-D | Sentence: 日本語の勉強を頑張っています。
...
```

## Configuration Options

### Command Line Arguments
- `--enable-voice-rotation`: Enable voice rotation (default: True)
- `--disable-voice-rotation`: Disable voice rotation
- `--voice`: Specify voice when rotation is disabled

### Configuration File
- `voice_rotation_enabled`: Boolean flag to enable/disable rotation
- `voice_name`: Fallback voice when rotation is disabled

## Migration Guide

### From Previous Versions
1. **No Breaking Changes**: Existing configurations continue to work
2. **Default Behavior**: Voice rotation is enabled by default
3. **Backward Compatibility**: All existing command line options still work
4. **Optional Feature**: Can be disabled if not needed

### Updating Existing Scripts
```bash
# Old way (still works)
python batch_tts_processor_ultra.py sentences.txt --voice ja-JP-Neural2-B

# New way with voice rotation
python batch_tts_processor_ultra.py sentences.txt --enable-voice-rotation

# New way with fixed voice
python batch_tts_processor_ultra.py sentences.txt --disable-voice-rotation --voice ja-JP-Neural2-B
```

## Troubleshooting

### Common Issues

1. **All sentences using same voice**
   - Check if voice rotation is disabled
   - Verify `--enable-voice-rotation` flag is set

2. **Cache conflicts**
   - Voice is included in cache key, so different voices won't conflict
   - Cache is voice-specific for proper management

3. **Performance concerns**
   - Voice rotation has no performance impact
   - All optimizations remain active

### Log Messages
Look for these log messages to verify voice rotation:
```
Voice rotation enabled: 6 voices available
Available voices: ja-JP-Neural2-B, ja-JP-Neural2-C, ...
Generated: 0001_こんにちは.mp3 - 'こんにちは、元気ですか？...' (Voice: ja-JP-Neural2-B)
Generated: 0002_今日は.mp3 - '今日は良い天気ですね。...' (Voice: ja-JP-Neural2-C)
```

## Best Practices

1. **Use voice rotation for variety**: Enable for diverse audio content
2. **Use fixed voice for consistency**: Disable for uniform voice output
3. **Monitor logs**: Check voice usage in log files
4. **Test with small batches**: Verify rotation behavior before large processing
5. **Consider audience**: Choose appropriate voice mix for your content

## Future Enhancements

Potential improvements for future versions:
- Custom voice selection patterns
- Voice-specific configuration options
- Voice quality preferences
- Dynamic voice availability checking
