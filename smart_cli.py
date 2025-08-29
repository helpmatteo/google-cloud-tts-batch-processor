#!/usr/bin/env python3
"""
Smart CLI for Advanced TTS Batch Processor
Provides intelligent command suggestions and auto-completion
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.syntax import Syntax
import subprocess
import argparse
from typing import List, Dict, Any, Optional

console = Console()

class SmartCLI:
    """Smart CLI with command suggestions and auto-completion"""
    
    def __init__(self):
        self.command_history = []
        self.suggestions_cache = {}
        
    def show_welcome(self):
        """Show welcome message with quick actions"""
        console.print(Panel.fit(
            "[bold blue]🎤 Advanced TTS Batch Processor - Smart CLI[/bold blue]\n\n"
            "What would you like to do?",
            border_style="blue"
        ))
        
        actions = [
            ("🚀", "Process text to speech", "process"),
            ("🌐", "Launch web interface", "web"),
            ("⚙️", "Configure settings", "config"),
            ("🎭", "Run demo", "demo"),
            ("📖", "Show help", "help"),
            ("❌", "Exit", "exit")
        ]
        
        table = Table(show_header=False, box=None)
        table.add_column("Icon", style="cyan", width=3)
        table.add_column("Action", style="yellow")
        table.add_column("Command", style="green")
        
        for icon, action, command in actions:
            table.add_row(icon, action, command)
        
        console.print(table)
    
    def get_user_choice(self) -> str:
        """Get user choice with suggestions"""
        while True:
            choice = Prompt.ask("\nEnter your choice", default="help")
            
            if choice in ["exit", "quit", "q"]:
                return "exit"
            elif choice in ["process", "p"]:
                return "process"
            elif choice in ["web", "w"]:
                return "web"
            elif choice in ["config", "c", "setup"]:
                return "config"
            elif choice in ["demo", "d"]:
                return "demo"
            elif choice in ["help", "h", "?"]:
                return "help"
            else:
                console.print(f"[yellow]Unknown choice: {choice}[/yellow]")
                console.print("Try: process, web, config, demo, help, or exit")
    
    def show_help(self):
        """Show comprehensive help"""
        console.print(Panel.fit(
            "[bold blue]📖 Help - Advanced TTS Batch Processor[/bold blue]",
            border_style="blue"
        ))
        
        # Quick commands
        console.print("\n[bold yellow]Quick Commands:[/bold yellow]")
        quick_commands = [
            ("python tts_batch_processor.py examples_en.txt --credentials google-credentials.json", "Process English sentences"),
            ("python start_web_interface.py", "Launch web interface"),
            ("python setup_wizard.py", "Interactive setup wizard"),
            ("python demo.py", "Run feature demo"),
            ("python smart_cli.py", "Launch this smart CLI")
        ]
        
        for cmd, desc in quick_commands:
            console.print(f"  [cyan]{cmd}[/cyan] - {desc}")
        
        # Common options
        console.print("\n[bold yellow]Common Options:[/bold yellow]")
        options = [
            ("--language en-US", "Set language (en-US, ja-JP, es-ES, fr-FR, de-DE)"),
            ("--voice en-US-Neural2-A", "Set specific voice"),
            ("--enable-voice-rotation", "Enable voice rotation"),
            ("--format MP3", "Set output format (MP3, WAV, OGG, FLAC)"),
            ("--sample-rate 24000", "Set sample rate (16000, 24000, 48000)"),
            ("--max-sentences 10", "Limit number of sentences to process"),
            ("--output-dir my_output", "Set output directory")
        ]
        
        for opt, desc in options:
            console.print(f"  [cyan]{opt}[/cyan] - {desc}")
        
        # Examples
        console.print("\n[bold yellow]Examples:[/bold yellow]")
        examples = [
            ("Basic processing", "python tts_batch_processor.py input.txt --credentials google-credentials.json"),
            ("Japanese with voice rotation", "python tts_batch_processor.py input.txt --language ja-JP --enable-voice-rotation"),
            ("High quality output", "python tts_batch_processor.py input.txt --format WAV --sample-rate 48000"),
            ("Test run", "python tts_batch_processor.py input.txt --max-sentences 5")
        ]
        
        for title, cmd in examples:
            console.print(f"  [bold]{title}:[/bold]")
            console.print(f"    [cyan]{cmd}[/cyan]")
    
    def interactive_process(self):
        """Interactive text processing"""
        console.print(Panel.fit(
            "[bold blue]🚀 Interactive Text Processing[/bold blue]",
            border_style="blue"
        ))
        
        # Get input file
        input_file = self._get_input_file()
        if not input_file:
            return
        
        # Get credentials
        credentials = self._get_credentials()
        if not credentials:
            return
        
        # Get language
        language = self._get_language()
        
        # Get voice settings
        voice_rotation = self._get_voice_rotation()
        
        # Get output settings
        output_format = self._get_output_format()
        sample_rate = self._get_sample_rate()
        
        # Build command
        command = self._build_command(
            input_file, credentials, language, voice_rotation, 
            output_format, sample_rate
        )
        
        # Show command and execute
        self._show_and_execute_command(command)
    
    def _get_input_file(self) -> Optional[str]:
        """Get input file with suggestions"""
        console.print("\n[bold yellow]Input File:[/bold yellow]")
        
        # Check for existing text files
        text_files = list(Path(".").glob("*.txt"))
        example_files = [f for f in text_files if "example" in f.name.lower()]
        
        if example_files:
            console.print("Found example files:")
            for i, file in enumerate(example_files, 1):
                console.print(f"  {i}. {file.name}")
            
            choice = Prompt.ask("Select file number or enter path", default="1")
            
            try:
                file_num = int(choice) - 1
                if 0 <= file_num < len(example_files):
                    return str(example_files[file_num])
            except ValueError:
                pass
            
            # User entered a path
            if Path(choice).exists():
                return choice
        
        # Manual input
        while True:
            path = Prompt.ask("Enter input file path")
            if Path(path).exists():
                return path
            else:
                console.print(f"[red]File not found: {path}[/red]")
                if not Prompt.ask("Try again?", choices=["y", "n"], default="y") == "y":
                    return None
    
    def _get_credentials(self) -> Optional[str]:
        """Get credentials file with suggestions"""
        console.print("\n[bold yellow]Credentials:[/bold yellow]")
        
        # Check for existing credentials
        cred_files = [
            "google-credentials.json",
            "google-credentials-demo.json",
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            os.getenv("GOOGLE_CREDENTIALS_PATH")
        ]
        
        existing_creds = [f for f in cred_files if f and Path(f).exists()]
        
        if existing_creds:
            console.print("Found credentials:")
            for i, cred in enumerate(existing_creds, 1):
                console.print(f"  {i}. {cred}")
            
            choice = Prompt.ask("Select credentials or enter path", default="1")
            
            try:
                cred_num = int(choice) - 1
                if 0 <= cred_num < len(existing_creds):
                    return existing_creds[cred_num]
            except ValueError:
                pass
            
            # User entered a path
            if Path(choice).exists():
                return choice
        
        # Manual input
        while True:
            path = Prompt.ask("Enter credentials file path")
            if Path(path).exists():
                return path
            else:
                console.print(f"[red]File not found: {path}[/red]")
                if Prompt.ask("Setup credentials now?", choices=["y", "n"], default="y") == "y":
                    self._setup_credentials()
                    return "google-credentials.json"
                elif not Prompt.ask("Try again?", choices=["y", "n"], default="y") == "y":
                    return None
    
    def _setup_credentials(self):
        """Setup credentials"""
        console.print("\n[bold yellow]Setting up credentials...[/bold yellow]")
        console.print("Please run the setup wizard:")
        console.print("  python setup_wizard.py")
        
        if Prompt.ask("Run setup wizard now?", choices=["y", "n"], default="y") == "y":
            subprocess.run([sys.executable, "setup_wizard.py"])
    
    def _get_language(self) -> str:
        """Get language selection"""
        console.print("\n[bold yellow]Language:[/bold yellow]")
        
        languages = {
            "1": "en-US (English)",
            "2": "ja-JP (Japanese)",
            "3": "es-ES (Spanish)",
            "4": "fr-FR (French)",
            "5": "de-DE (German)"
        }
        
        for key, lang in languages.items():
            console.print(f"  {key}. {lang}")
        
        choice = Prompt.ask("Select language", choices=list(languages.keys()), default="1")
        
        lang_map = {
            "1": "en-US",
            "2": "ja-JP", 
            "3": "es-ES",
            "4": "fr-FR",
            "5": "de-DE"
        }
        
        return lang_map.get(choice, "en-US")
    
    def _get_voice_rotation(self) -> bool:
        """Get voice rotation preference"""
        console.print("\n[bold yellow]Voice Rotation:[/bold yellow]")
        return Prompt.ask(
            "Enable voice rotation (different voice for each sentence)?",
            choices=["y", "n"],
            default="y"
        ) == "y"
    
    def _get_output_format(self) -> str:
        """Get output format"""
        console.print("\n[bold yellow]Output Format:[/bold yellow]")
        
        formats = {
            "1": "MP3 (compressed, recommended)",
            "2": "WAV (uncompressed, larger)",
            "3": "OGG (open format)",
            "4": "FLAC (lossless)"
        }
        
        for key, fmt in formats.items():
            console.print(f"  {key}. {fmt}")
        
        choice = Prompt.ask("Select format", choices=list(formats.keys()), default="1")
        
        format_map = {
            "1": "MP3",
            "2": "WAV",
            "3": "OGG", 
            "4": "FLAC"
        }
        
        return format_map.get(choice, "MP3")
    
    def _get_sample_rate(self) -> int:
        """Get sample rate"""
        console.print("\n[bold yellow]Sample Rate:[/bold yellow]")
        
        rates = {
            "1": "16000 Hz (fast, smaller files)",
            "2": "24000 Hz (standard, recommended)",
            "3": "48000 Hz (high quality, larger files)"
        }
        
        for key, rate in rates.items():
            console.print(f"  {key}. {rate}")
        
        choice = Prompt.ask("Select sample rate", choices=list(rates.keys()), default="2")
        
        rate_map = {
            "1": 16000,
            "2": 24000,
            "3": 48000
        }
        
        return rate_map.get(choice, 24000)
    
    def _build_command(self, input_file: str, credentials: str, language: str, 
                      voice_rotation: bool, output_format: str, sample_rate: int) -> str:
        """Build the command string"""
        cmd_parts = [
            "python", "tts_batch_processor.py",
            input_file,
            "--credentials", credentials,
            "--language", language,
            "--format", output_format,
            "--sample-rate", str(sample_rate)
        ]
        
        if voice_rotation:
            cmd_parts.append("--enable-voice-rotation")
        else:
            cmd_parts.append("--disable-voice-rotation")
        
        return " ".join(cmd_parts)
    
    def _show_and_execute_command(self, command: str):
        """Show command and execute"""
        console.print(f"\n[bold cyan]Command:[/bold cyan]")
        console.print(f"[cyan]{command}[/cyan]")
        
        if Prompt.ask("\nExecute this command?", choices=["y", "n"], default="y") == "y":
            console.print("\n[bold yellow]Executing command...[/bold yellow]")
            subprocess.run(command.split())
        else:
            console.print("[yellow]Command cancelled[/yellow]")
    
    def launch_web_interface(self):
        """Launch web interface"""
        console.print(Panel.fit(
            "[bold blue]🌐 Launching Web Interface[/bold blue]",
            border_style="blue"
        ))
        
        console.print("Starting web interface...")
        console.print("URL: http://localhost:5000")
        console.print("Press Ctrl+C to stop")
        
        try:
            subprocess.run([sys.executable, "start_web_interface.py"])
        except KeyboardInterrupt:
            console.print("\n[yellow]Web interface stopped[/yellow]")
    
    def run_config_wizard(self):
        """Run configuration wizard"""
        console.print(Panel.fit(
            "[bold blue]⚙️ Configuration Wizard[/bold blue]",
            border_style="blue"
        ))
        
        console.print("Launching setup wizard...")
        subprocess.run([sys.executable, "setup_wizard.py"])
    
    def run_demo(self):
        """Run demo"""
        console.print(Panel.fit(
            "[bold blue]🎭 Feature Demo[/bold blue]",
            border_style="blue"
        ))
        
        console.print("Running feature demonstration...")
        subprocess.run([sys.executable, "demo.py"])
    
    def run(self):
        """Run the smart CLI"""
        try:
            while True:
                self.show_welcome()
                choice = self.get_user_choice()
                
                if choice == "exit":
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                elif choice == "process":
                    self.interactive_process()
                elif choice == "web":
                    self.launch_web_interface()
                elif choice == "config":
                    self.run_config_wizard()
                elif choice == "demo":
                    self.run_demo()
                elif choice == "help":
                    self.show_help()
                    Prompt.ask("\nPress Enter to continue")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye! 👋[/yellow]")

def main():
    """Main function"""
    cli = SmartCLI()
    cli.run()

if __name__ == "__main__":
    main()
