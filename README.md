# Advanced Text-to-Speech Batch Processor

A high-performance Python toolkit for batch processing text-to-speech conversion using Google Cloud Text-to-Speech API. This tool supports multiple languages, voice rotation, intelligent caching, and optimized processing for large-scale audio generation.

## 🌟 Features

- ✅ **Multi-language Support** - English, Japanese, Spanish, French, German, and more
- ✅ **Voice Rotation** - Automatically cycle through different neural voices
- ✅ **High Performance** - Async processing with connection pooling and intelligent batching
- ✅ **Smart Caching** - Prevents duplicate API calls and enables resume functionality
- ✅ **Multiple Audio Formats** - MP3, WAV, OGG, FLAC
- ✅ **Configurable Quality** - Adjustable sample rates and voice selection
- ✅ **Progress Tracking** - Real-time progress monitoring and detailed logging
- ✅ **Error Handling** - Robust retry mechanisms and error recovery
- ✅ **Rate Limiting** - Built-in API quota management
- ✅ **🎨 Beautiful CLI** - Rich terminal interface with progress bars and tables
- ✅ **🌐 Web Interface** - Modern web UI for easy TTS processing
- ✅ **⚙️ Configuration Management** - YAML-based configuration system
- ✅ **🛡️ Circuit Breaker** - Advanced error handling and resilience
- ✅ **🎵 Audio Enhancement** - Quality improvement and normalization
- ✅ **📊 Real-time Monitoring** - Live progress tracking and statistics

## 🚀 Quick Start

### Option 1: One-Click Launcher (Recommended)
```bash
python launch.py
```
This will automatically check your system and recommend the best interface for you!

### Option 2: Interactive Setup Wizard
```bash
python setup_wizard.py
```
Guided setup with credential configuration and preferences.

### Option 3: Manual Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Set Up Google Cloud
1. **Create a Google Cloud Project** and enable the Text-to-Speech API
2. **Create a Service Account** and download the JSON credentials file
3. **Save the credentials** as `google-credentials.json` in your project directory

#### 3. Basic Usage

#### Command Line Interface
```bash
# Process English sentences
python tts_batch_processor.py examples_en.txt --credentials google-credentials.json

# Process Japanese sentences with voice rotation
python tts_batch_processor.py examples_ja.txt \
    --credentials google-credentials.json \
    --language ja-JP \
    --enable-voice-rotation

# Process Spanish sentences with specific voice
python tts_batch_processor.py examples_es.txt \
    --credentials google-credentials.json \
    --language es-ES \
    --voice es-ES-Neural2-A
```

#### Web Interface
```bash
# Start the web interface
python start_web_interface.py

# Then open http://localhost:5000 in your browser
```

#### Smart CLI Interface
```bash
# Launch interactive command-line interface
python smart_cli.py
```

#### Demo Mode
```bash
# See all features in action
python demo.py
```

## 📖 Detailed Usage

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_file` | Path to text file with sentences | Required |
| `--credentials` | Path to Google Cloud credentials JSON | Required |
| `--language` | Language code (en-US, ja-JP, es-ES, fr-FR, de-DE) | `en-US` |
| `--output-dir` | Output directory for audio files | `tts_output` |
| `--voice` | Specific voice name (used when rotation disabled) | Auto-selected |
| `--enable-voice-rotation` | Enable voice rotation between available voices | `True` |
| `--disable-voice-rotation` | Disable voice rotation (use fixed voice) | `False` |
| `--format` | Audio format (MP3, WAV, OGG, FLAC) | `MP3` |
| `--sample-rate` | Audio sample rate in Hz | `24000` |
| `--delay` | Delay between batches (seconds) | `0.05` |
| `--max-workers` | Maximum concurrent workers | `5` |
| `--batch-size` | Batch size for processing | `20` |
| `--max-concurrent` | Maximum concurrent requests | `15` |
| `--retry-attempts` | Number of retry attempts | `3` |
| `--max-sentences` | Maximum number of sentences to process | All |

### Supported Languages

| Language | Code | Available Voices |
|----------|------|------------------|
| English (US) | `en-US` | 9 Neural2 voices |
| Japanese | `ja-JP` | 4 Neural2 voices |
| Spanish (Spain) | `es-ES` | 4 Neural2 voices |
| French | `fr-FR` | 4 Neural2 voices |
| German | `de-DE` | 4 Neural2 voices |

### Voice Rotation

When enabled, the processor automatically cycles through available voices for each sentence:

```bash
# Enable voice rotation (default)
python tts_batch_processor.py input.txt \
    --credentials google-credentials.json \
    --enable-voice-rotation

# Disable voice rotation and use specific voice
python tts_batch_processor.py input.txt \
    --credentials google-credentials.json \
    --disable-voice-rotation \
    --voice en-US-Neural2-A
```

## 📁 Output Structure

```
tts_output/
├── sentence_0001.mp3
├── sentence_0002.mp3
├── sentence_0003.mp3
├── ...
├── processing_results.json
└── tts_batch.log
```

### Processing Results

The tool generates a detailed JSON report:

```json
{
  "total": 100,
  "successful": 98,
  "failed": 2,
  "processing_time": "00:02:30",
  "files": [
    {
      "index": 1,
      "sentence": "Hello, how are you today?",
      "filepath": "tts_output/sentence_0001.mp3",
      "voice": "en-US-Neural2-A",
      "duration": 2.5
    }
  ],
  "errors": [
    "Index 15: Empty sentence",
    "Index 23: Google Cloud error: Quota exceeded"
  ]
}
```

## ⚙️ Configuration

### Audio Formats

| Format | Extension | Description | Recommended |
|--------|-----------|-------------|-------------|
| MP3 | `.mp3` | Compressed audio format | ✅ Yes |
| WAV | `.wav` | Uncompressed audio format | No |
| OGG | `.ogg` | Open source compressed format | No |
| FLAC | `.flac` | Lossless compressed format | No |

### Sample Rates

| Rate | Description | Recommended |
|------|-------------|-------------|
| 24000 Hz | Standard quality | ✅ Yes |
| 16000 Hz | Lower quality, smaller files | No |
| 48000 Hz | High quality, larger files | No |

## 💰 Cost Estimation

Google Cloud TTS pricing (as of 2024):
- **Neural2 voices**: $16.00 per 1 million characters
- **Wavenet voices**: $4.00 per 1 million characters

**Example**: 1000 sentences (~20,000 characters)
- **Neural2**: ~$0.32
- **Wavenet**: ~$0.08

## 🔧 Advanced Features

### 🎨 Rich CLI Interface
- **Beautiful Progress Bars**: Real-time processing visualization
- **Colorful Tables**: Easy-to-read results and statistics
- **Interactive Elements**: Enhanced user experience
- **Status Indicators**: Clear success/failure feedback

### 🌐 Web Interface
- **Modern UI**: Responsive, user-friendly interface
- **Real-time Progress**: Live updates during processing
- **File Management**: Direct download of generated audio
- **Configuration Panel**: Easy settings management

### ⚙️ Configuration Management
- **YAML Configuration**: Human-readable settings
- **Dynamic Updates**: Runtime configuration changes
- **Validation**: Automatic configuration validation
- **Defaults**: Sensible default values

### 🛡️ Advanced Error Handling
- **Circuit Breaker Pattern**: Prevents cascading failures
- **Exponential Backoff**: Intelligent retry mechanisms
- **Error Recovery**: Graceful failure handling
- **Monitoring**: Real-time error tracking

### 🎵 Audio Quality Enhancement
- **Normalization**: Consistent audio levels
- **Noise Reduction**: Clean audio output
- **Compression**: Dynamic range control
- **Equalization**: Frequency balance adjustment

### 💾 Caching and Resume
- **Intelligent Caching**: Prevents duplicate API calls
- **Resume Functionality**: Continue interrupted processing
- **Cost Reduction**: Minimize API usage
- **Performance Boost**: Faster subsequent runs

### 🚀 One-Click Launcher
- **Smart Recommendations**: Automatically suggests best interface
- **System Detection**: Checks capabilities and dependencies
- **Easy Access**: Single command to get started
- **Browser Integration**: Automatic browser opening

### 🎯 Interactive Setup Wizard
- **Guided Setup**: Step-by-step configuration
- **Credential Management**: Easy Google Cloud setup
- **Preference Selection**: Language and voice preferences
- **Demo Mode**: Try without credentials

### 🧠 Smart CLI
- **Interactive Commands**: Guided command building
- **Auto-completion**: Intelligent suggestions
- **File Detection**: Automatic file and credential detection
- **Help Integration**: Built-in help and examples

### Performance Optimization
- **Async Processing**: Concurrent API requests
- **Connection Pooling**: Reuse HTTP connections
- **Intelligent Batching**: Optimize batch sizes
- **Rate Limiting**: Respect API quotas

## 🛠️ Examples

### Test Run (10 sentences)
```bash
python tts_batch_processor.py examples_en.txt \
    --credentials google-credentials.json \
    --max-sentences 10 \
    --output-dir test_output
```

### High Quality Production Run
```bash
python tts_batch_processor.py input.txt \
    --credentials google-credentials.json \
    --voice en-US-Neural2-A \
    --format MP3 \
    --sample-rate 24000 \
    --delay 0.15 \
    --output-dir production_audio
```

### Multi-language Processing
```bash
# English
python tts_batch_processor.py examples_en.txt \
    --credentials google-credentials.json \
    --language en-US \
    --output-dir english_audio

# Japanese
python tts_batch_processor.py examples_ja.txt \
    --credentials google-credentials.json \
    --language ja-JP \
    --output-dir japanese_audio

# Spanish
python tts_batch_processor.py examples_es.txt \
    --credentials google-credentials.json \
    --language es-ES \
    --output-dir spanish_audio
```

### Web Interface Usage
```bash
# Start the web interface
python start_web_interface.py

# Open http://localhost:5000 in your browser
# Upload text file or paste sentences
# Configure language, voice, and format
# Start processing with real-time progress
```

### Demo All Features
```bash
# Run the comprehensive demo
python demo.py

# This showcases all new features including:
# - Rich CLI interface
# - Configuration management
# - Error handling
# - Audio processing
# - Web interface capabilities
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   Error: Failed to initialize Google Cloud TTS client
   ```
   - Check credentials file path
   - Verify service account has Text-to-Speech API access

2. **Quota Exceeded**
   ```
   Error: Quota exceeded for quota group 'default'
   ```
   - Increase delay: `--delay 0.5`
   - Process smaller batches: `--max-sentences 100`

3. **Invalid Voice**
   ```
   Error: Invalid voice name
   ```
   - Check available voices in `tts_config.json`
   - Use supported language codes

### Performance Tips

- **Large batches**: Use `--delay 0.2` to avoid rate limits
- **Testing**: Use `--max-sentences 10` for quick tests
- **Quality**: Use Neural2 voices with 24kHz sample rate
- **Storage**: Use MP3 format for smaller file sizes

## 📚 Documentation

- [Voice Rotation Guide](VOICE_ROTATION_GUIDE.md) - Detailed voice rotation configuration
- [Testing Guide](TESTING_GUIDE.md) - Testing and validation procedures
- [Performance Comparison](PERFORMANCE_COMPARISON.md) - Performance benchmarks
- [Ultra Optimization Guide](ULTRA_OPTIMIZATION_GUIDE.md) - Advanced optimization techniques

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is provided as-is for educational and personal use. Please respect Google Cloud's terms of service and usage limits. Users are responsible for their own API usage and costs.

## 🆘 Support

If you encounter issues:
1. Check the log file: `tts_batch.log`
2. Verify your Google Cloud setup
3. Test with a small batch first
4. Check your internet connection
5. Review the troubleshooting section above

---

**Happy Text-to-Speech Processing! 🎤✨**
# google-cloud-tts-batch-processor
# google-cloud-tts-batch-processor
