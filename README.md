# Advanced TTS Batch Processor

A powerful, feature-rich Text-to-Speech batch processing system with web interface, voice rotation, and advanced audio processing capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Google Cloud account with Text-to-Speech API enabled
- Google Cloud service account credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jpg-tts
   ```

2. **Run the setup wizard**
   ```bash
   python setup.py
   ```
   This will guide you through:
   - Installing dependencies
   - Setting up Google Cloud credentials
   - Configuring language preferences
   - Setting processing options

3. **Start using the system**
   ```bash
   # Process text files
   python main.py docs/examples/examples_en.txt
   
   # Launch web interface
   python start_web.py
   
   # Try the demo
   python demo.py
   ```

## 📁 Project Structure

```
jpg-tts/
├── src/                    # Main source code
│   ├── core/              # Core TTS processing modules
│   │   ├── tts_batch_processor.py
│   │   ├── audio_processor.py
│   │   ├── config_manager.py
│   │   └── error_handler.py
│   ├── web/               # Web interface modules
│   │   ├── web_interface.py
│   │   └── start_web_interface.py
│   ├── cli/               # Command-line interface modules
│   │   ├── smart_cli.py
│   │   ├── setup_wizard.py
│   │   └── demo.py
│   └── utils/             # Utility modules
│       └── launch.py
├── docs/                  # Documentation
│   ├── guides/           # Detailed guides and documentation
│   └── examples/         # Example text files
├── config/               # Configuration files
│   ├── tts_config.yaml
│   └── tts_config.json
├── scripts/              # Installation and setup scripts
├── tests/                # Test files
├── main.py               # Main CLI entry point
├── start_web.py          # Web interface entry point
├── setup.py              # Setup wizard entry point
├── demo.py               # Demo entry point
└── requirements.txt      # Python dependencies
```

## 🎯 Key Features

### Core Features
- **Batch Processing**: Process multiple text files efficiently
- **Voice Rotation**: Automatically rotate between different voices
- **Multi-language Support**: English, Japanese, Spanish, French, German
- **Audio Enhancement**: Quality improvement and normalization
- **Resume Functionality**: Continue interrupted processing
- **Caching**: Faster subsequent runs with result caching

### Web Interface
- **Modern UI**: Clean, responsive web interface
- **Real-time Processing**: Live progress updates
- **File Upload**: Drag-and-drop file processing
- **Settings Management**: Easy configuration changes

### Advanced Features
- **Error Handling**: Robust error recovery and logging
- **Performance Optimization**: Configurable processing speeds
- **Multiple Output Formats**: MP3, WAV, OGG, FLAC
- **Quality Settings**: Fast, Standard, and High quality options

## 📖 Usage

### Command Line Interface

```bash
# Basic usage
python main.py input.txt

# With specific options
python main.py input.txt --language en-US --voice female --output mp3

# Process multiple files
python main.py file1.txt file2.txt file3.txt

# Use specific configuration
python main.py input.txt --config config/custom_config.yaml
```

### Web Interface

```bash
# Start the web server
python start_web.py

# Access at http://localhost:5000
```

### Configuration

The system uses YAML configuration files located in the `config/` directory:

- `tts_config.yaml`: Main configuration
- `tts_config.json`: Alternative JSON format

Key configuration options:
- Audio quality settings
- Processing speed and concurrency
- Voice preferences
- Language settings
- Output format options

## 🔧 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Structure
- **Core Modules**: Main TTS processing logic
- **Web Interface**: Flask-based web application
- **CLI Tools**: Command-line interface and utilities
- **Configuration**: Flexible configuration management

### Adding New Features
1. Add your module to the appropriate `src/` subdirectory
2. Update the corresponding `__init__.py` file
3. Add tests in the `tests/` directory
4. Update documentation in `docs/guides/`

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **Guides**: Detailed setup and usage guides
- **Examples**: Sample text files for testing
- **Configuration**: Configuration file documentation

Key documentation files:
- `docs/QUICK_START.md`: Quick start guide
- `docs/guides/GOOGLE_CLOUD_SETUP.md`: Google Cloud setup
- `docs/guides/ENHANCEMENT_SUMMARY.md`: Feature overview
- `docs/guides/TESTING_GUIDE.md`: Testing instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🆘 Support

For support and questions:
1. Check the documentation in `docs/guides/`
2. Review the example files in `docs/examples/`
3. Run the setup wizard: `python setup.py`
4. Try the demo: `python demo.py`

## 🎉 Acknowledgments

- Google Cloud Text-to-Speech API
- Flask web framework
- Rich terminal library
- All contributors and users
