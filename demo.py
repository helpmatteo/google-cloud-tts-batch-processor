#!/usr/bin/env python3
"""
Demo Script for Advanced TTS Batch Processor
Showcases all the new features and improvements
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import time

console = Console()

def demo_config_manager():
    """Demo the configuration management system"""
    console.print(Panel.fit("[bold blue]⚙️ Configuration Management Demo[/bold blue]", border_style="blue"))
    
    try:
        from config_manager import ConfigManager
        
        # Create config manager
        config_manager = ConfigManager()
        
        # Display configuration
        table = Table(title="Current Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Section", style="cyan")
        table.add_column("Key", style="yellow")
        table.add_column("Value", style="green")
        
        config = config_manager.config
        
        # Audio settings
        audio_config = config.get('audio', {})
        table.add_row("Audio", "Default Format", audio_config.get('default_format', 'MP3'))
        table.add_row("Audio", "Sample Rate", str(audio_config.get('default_sample_rate', 24000)))
        table.add_row("Audio", "Enhancement", audio_config.get('enhancement', 'normalize'))
        
        # Processing settings
        processing_config = config.get('processing', {})
        table.add_row("Processing", "Max Workers", str(processing_config.get('max_workers', 5)))
        table.add_row("Processing", "Batch Size", str(processing_config.get('batch_size', 20)))
        table.add_row("Processing", "Retry Attempts", str(processing_config.get('retry_attempts', 3)))
        
        # Voice settings
        voice_config = config.get('voice', {})
        table.add_row("Voice", "Rotation Enabled", "✅" if voice_config.get('rotation_enabled', True) else "❌")
        table.add_row("Voice", "Default Voice", voice_config.get('default_voice', 'en-US-Neural2-A'))
        
        console.print(table)
        
        # Show available languages
        languages = config.get('languages', {})
        lang_table = Table(title="Available Languages", show_header=True, header_style="bold magenta")
        lang_table.add_column("Language Code", style="cyan")
        lang_table.add_column("Name", style="yellow")
        lang_table.add_column("Voices", style="green")
        
        for code, lang_info in languages.items():
            voice_count = len(lang_info.get('voices', []))
            lang_table.add_row(code, lang_info.get('name', ''), str(voice_count))
        
        console.print(lang_table)
        
        console.print("✅ Configuration management demo completed\n")
        
    except Exception as e:
        console.print(f"❌ Configuration demo failed: {e}\n")

def demo_error_handler():
    """Demo the error handling system"""
    console.print(Panel.fit("[bold blue]🛡️ Error Handling Demo[/bold blue]", border_style="blue"))
    
    try:
        from error_handler import error_handler, CircuitBreakerConfig, RetryConfig, retry_with_backoff
        
        # Create circuit breaker
        cb_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30)
        circuit_breaker = error_handler.get_circuit_breaker('demo', cb_config)
        
        # Demo retry mechanism
        @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=0.1))
        def demo_function(should_fail=False):
            if should_fail:
                raise ValueError("Demo error")
            return "Success!"
        
        # Test successful call
        result = demo_function(should_fail=False)
        console.print(f"✅ Successful call: {result}")
        
        # Test retry mechanism
        try:
            demo_function(should_fail=True)
        except Exception as e:
            console.print(f"✅ Retry mechanism caught error: {e}")
        
        # Show circuit breaker status
        cb_stats = error_handler.get_circuit_breaker_stats()
        if cb_stats:
            table = Table(title="Circuit Breaker Status", show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("State", style="yellow")
            table.add_column("Failures", style="green")
            
            for name, stats in cb_stats.items():
                state_emoji = "🟢" if stats['state'] == 'CLOSED' else "🔴" if stats['state'] == 'OPEN' else "🟡"
                table.add_row(name, f"{state_emoji} {stats['state']}", str(stats['failure_count']))
            
            console.print(table)
        
        console.print("✅ Error handling demo completed\n")
        
    except Exception as e:
        console.print(f"❌ Error handling demo failed: {e}\n")

def demo_audio_processor():
    """Demo the audio processing system"""
    console.print(Panel.fit("[bold blue]🎵 Audio Processing Demo[/bold blue]", border_style="blue"))
    
    try:
        from audio_processor import AudioProcessor, AudioEnhancementConfig
        
        # Create audio processor with custom config
        enhancement_config = AudioEnhancementConfig(
            normalize=True,
            noise_reduction=False,
            compression=False,
            equalizer=False,
            target_loudness=-18.0
        )
        
        processor = AudioProcessor(enhancement_config)
        
        # Show configuration
        table = Table(title="Audio Enhancement Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Setting", style="green")
        
        table.add_row("Normalization", "✅ Enabled" if enhancement_config.normalize else "❌ Disabled", 
                     f"Target: {enhancement_config.target_loudness}dB")
        table.add_row("Noise Reduction", "✅ Enabled" if enhancement_config.noise_reduction else "❌ Disabled", "-")
        table.add_row("Compression", "✅ Enabled" if enhancement_config.compression else "❌ Disabled", "-")
        table.add_row("Equalizer", "✅ Enabled" if enhancement_config.equalizer else "❌ Disabled", "-")
        
        console.print(table)
        
        console.print("✅ Audio processing demo completed\n")
        
    except Exception as e:
        console.print(f"❌ Audio processing demo failed: {e}\n")

def demo_rich_cli():
    """Demo the rich CLI interface"""
    console.print(Panel.fit("[bold blue]🎨 Rich CLI Interface Demo[/bold blue]", border_style="blue"))
    
    # Create a sample progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        task = progress.add_task("Processing demo sentences...", total=10)
        
        for i in range(10):
            time.sleep(0.2)  # Simulate processing
            progress.update(task, advance=1)
    
    # Create sample results table
    table = Table(title="Sample Processing Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    table.add_row("Total Sentences", "10")
    table.add_row("Successful", "9 (90.0%)")
    table.add_row("Failed", "1")
    table.add_row("Processing Time", "2.0s")
    table.add_row("Avg Time/Sentence", "0.2s")
    table.add_row("Language", "en-US")
    table.add_row("Voice Rotation", "✅ Enabled")
    table.add_row("Caching", "✅ Enabled")
    
    console.print(table)
    
    console.print("✅ Rich CLI demo completed\n")

def demo_web_interface():
    """Demo the web interface"""
    console.print(Panel.fit("[bold blue]🌐 Web Interface Demo[/bold blue]", border_style="blue"))
    
    try:
        import flask
        import flask_cors
        
        table = Table(title="Web Interface Features", show_header=True, header_style="bold magenta")
        table.add_column("Feature", style="cyan")
        table.add_column("Description", style="green")
        
        table.add_row("Modern UI", "Beautiful, responsive web interface")
        table.add_row("Real-time Progress", "Live progress tracking with WebSocket")
        table.add_row("Multi-language Support", "Support for 5 languages")
        table.add_row("Voice Rotation", "Automatic voice cycling")
        table.add_row("File Download", "Direct download of generated audio")
        table.add_row("Configuration", "Dynamic configuration management")
        table.add_row("Error Handling", "Comprehensive error reporting")
        
        console.print(table)
        
        console.print("To start the web interface, run:")
        console.print("[bold yellow]python start_web_interface.py[/bold yellow]")
        console.print("Then open: [bold blue]http://localhost:5000[/bold blue]\n")
        
        console.print("✅ Web interface demo completed\n")
        
    except ImportError:
        console.print("❌ Flask not installed. Install with: pip install flask flask-cors\n")

def main():
    """Main demo function"""
    console.print(Panel.fit(
        "[bold green]🎤 Advanced TTS Batch Processor - Feature Demo[/bold green]",
        border_style="green"
    ))
    
    console.print("This demo showcases all the new features and improvements:\n")
    
    # Run demos
    demo_config_manager()
    demo_error_handler()
    demo_audio_processor()
    demo_rich_cli()
    demo_web_interface()
    
    # Final summary
    console.print(Panel.fit(
        "[bold green]✨ Demo Complete![/bold green]\n"
        "The Advanced TTS Batch Processor now includes:\n"
        "• 🎨 Beautiful Rich CLI interface\n"
        "• ⚙️ Advanced configuration management\n"
        "• 🛡️ Robust error handling with circuit breakers\n"
        "• 🎵 Audio quality enhancement\n"
        "• 🌐 Modern web interface\n"
        "• 📊 Real-time progress tracking\n"
        "• 🔄 Voice rotation across languages\n"
        "• 💾 Smart caching and resume functionality",
        border_style="green"
    ))
    
    console.print("\n[bold yellow]Next Steps:[/bold yellow]")
    console.print("1. Install dependencies: pip install -r requirements.txt")
    console.print("2. Set up Google Cloud credentials")
    console.print("3. Try the CLI: python tts_batch_processor.py examples_en.txt --credentials google-credentials.json")
    console.print("4. Launch web interface: python start_web_interface.py")
    console.print("5. Check the documentation in README.md")

if __name__ == "__main__":
    main()
