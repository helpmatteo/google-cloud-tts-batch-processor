#!/usr/bin/env python3
"""
Interactive Setup Wizard for Advanced TTS Batch Processor
Guides users through initial setup and configuration
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess
import shutil

console = Console()

class SetupWizard:
    """Interactive setup wizard for TTS processor"""
    
    def __init__(self):
        self.config = {}
        self.credentials_path = None
        
    def welcome(self):
        """Display welcome message"""
        console.print(Panel.fit(
            "[bold blue]🎤 Welcome to Advanced TTS Batch Processor Setup![/bold blue]\n\n"
            "This wizard will help you set up your TTS processor in just a few minutes.\n"
            "We'll configure your Google Cloud credentials, language preferences, and processing settings.",
            border_style="blue"
        ))
        
        if not Confirm.ask("Ready to begin setup?", default=True):
            console.print("[yellow]Setup cancelled. You can run this wizard anytime with: python setup_wizard.py[/yellow]")
            sys.exit(0)
    
    def check_python_version(self):
        """Check Python version compatibility"""
        console.print("\n[bold cyan]🔍 Checking Python version...[/bold cyan]")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            console.print("[red]❌ Python 3.7+ is required. Current version: {}.{}[/red]".format(
                version.major, version.minor))
            return False
        
        console.print(f"[green]✅ Python {version.major}.{version.minor}.{version.micro} detected[/green]")
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        console.print("\n[bold cyan]📦 Installing dependencies...[/bold cyan]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Installing packages...", total=None)
                
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    console.print("[green]✅ Dependencies installed successfully[/green]")
                    return True
                else:
                    console.print(f"[red]❌ Installation failed: {result.stderr}[/red]")
                    return False
                    
        except Exception as e:
            console.print(f"[red]❌ Error installing dependencies: {e}[/red]")
            return False
    
    def setup_credentials(self):
        """Guide user through credential setup - PRIORITY FIRST"""
        console.print("\n[bold cyan]🔑 Google Cloud Credentials Setup (Required)[/bold cyan]")
        console.print("This is the most important step! You need Google Cloud credentials to use the TTS service.")
        
        # Check for existing credentials
        existing_paths = [
            "google-credentials.json",
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            os.getenv("GOOGLE_CREDENTIALS_PATH")
        ]
        
        for path in existing_paths:
            if path and Path(path).exists():
                console.print(f"[green]✅ Found existing credentials: {path}[/green]")
                if Confirm.ask("Use existing credentials?", default=True):
                    self.credentials_path = path
                    return True
        
        console.print("\n[bold red]⚠️ No Google Cloud credentials found![/bold red]")
        console.print("You MUST set up Google Cloud credentials to use the TTS service.")
        
        # Force credential setup
        console.print("\n[bold yellow]Let's set up your Google Cloud credentials now:[/bold yellow]")
        
        # Provide step-by-step instructions
        steps = [
            "1. Go to [link=https://console.cloud.google.com]Google Cloud Console[/link]",
            "2. Create a new project or select existing one",
            "3. Enable the Text-to-Speech API",
            "4. Create a service account",
            "5. Download the JSON key file"
        ]
        
        for step in steps:
            console.print(f"   {step}")
        
        console.print("\n[bold yellow]Options:[/bold yellow]")
        console.print("1. I have credentials file (recommended)")
        console.print("2. I need detailed help setting up Google Cloud")
        console.print("3. Skip for now (demo mode only - limited functionality)")
        
        choice = Prompt.ask("Choose option", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            return self._handle_existing_credentials()
        elif choice == "2":
            return self._show_google_cloud_help()
        else:
            console.print("\n[bold yellow]⚠️ Demo mode selected[/bold yellow]")
            console.print("You'll only be able to explore the interface without real TTS processing.")
            console.print("To use full functionality, you'll need to set up credentials later.")
            return self._setup_demo_mode()
    
    def _handle_existing_credentials(self):
        """Handle existing credentials file"""
        console.print("\n[bold yellow]Please provide the path to your credentials file:[/bold yellow]")
        
        while True:
            path = Prompt.ask("Credentials file path", default="google-credentials.json")
            
            if Path(path).exists():
                # Validate the credentials file
                if self._validate_credentials_file(path):
                    # Copy to project directory
                    target_path = "google-credentials.json"
                    shutil.copy2(path, target_path)
                    self.credentials_path = target_path
                    console.print(f"[green]✅ Credentials validated and copied to: {target_path}[/green]")
                    return True
                else:
                    console.print("[red]❌ Invalid credentials file format[/red]")
                    console.print("Please ensure you have a valid Google Cloud service account JSON file.")
                    if not Confirm.ask("Try again?", default=True):
                        return self._setup_demo_mode()
            else:
                console.print(f"[red]❌ File not found: {path}[/red]")
                console.print("Please check the file path and try again.")
                if not Confirm.ask("Try again?", default=True):
                    return self._setup_demo_mode()
    
    def _validate_credentials_file(self, file_path: str) -> bool:
        """Validate Google Cloud credentials file"""
        try:
            with open(file_path, 'r') as f:
                creds = json.load(f)
            
            # Check for required fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            for field in required_fields:
                if field not in creds:
                    console.print(f"[red]Missing required field: {field}[/red]")
                    return False
            
            # Check if it's a service account
            if creds.get('type') != 'service_account':
                console.print("[red]Not a service account credentials file[/red]")
                return False
            
            console.print(f"[green]✅ Valid service account for project: {creds.get('project_id', 'Unknown')}[/green]")
            return True
            
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON format[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Error reading credentials file: {e}[/red]")
            return False
    
    def _show_google_cloud_help(self):
        """Show detailed Google Cloud setup help"""
        console.print(Panel.fit(
            "[bold blue]🔧 Complete Google Cloud Setup Guide[/bold blue]\n\n"
            "[bold yellow]Step 1: Create a Google Cloud Project[/bold yellow]\n"
            "1. Go to https://console.cloud.google.com\n"
            "2. Sign in with your Google account\n"
            "3. Click 'Select a project' → 'New Project'\n"
            "4. Enter a project name (e.g., 'my-tts-project')\n"
            "5. Click 'Create'\n\n"
            
            "[bold yellow]Step 2: Enable the Text-to-Speech API[/bold yellow]\n"
            "1. In your project, go to 'APIs & Services' → 'Library'\n"
            "2. Search for 'Cloud Text-to-Speech API'\n"
            "3. Click on it and press 'Enable'\n"
            "4. Wait for the API to be enabled\n\n"
            
            "[bold yellow]Step 3: Create a Service Account[/bold yellow]\n"
            "1. Go to 'APIs & Services' → 'Credentials'\n"
            "2. Click 'Create Credentials' → 'Service Account'\n"
            "3. Enter service account name (e.g., 'tts-service')\n"
            "4. Click 'Create and Continue'\n"
            "5. Skip role assignment, click 'Continue'\n"
            "6. Click 'Done'\n\n"
            
            "[bold yellow]Step 4: Create and Download API Key[/bold yellow]\n"
            "1. Click on your newly created service account\n"
            "2. Go to 'Keys' tab\n"
            "3. Click 'Add Key' → 'Create New Key'\n"
            "4. Choose 'JSON' format\n"
            "5. Click 'Create' - this will download the key file\n\n"
            
            "[bold yellow]Step 5: Save the Credentials[/bold yellow]\n"
            "1. Rename the downloaded file to 'google-credentials.json'\n"
            "2. Move it to this project directory\n"
            "3. Run this setup wizard again\n\n"
            
            "[bold red]Important Security Notes:[/bold red]\n"
            "• Keep your credentials file secure and private\n"
            "• Don't share or commit it to version control\n"
            "• The file contains sensitive access keys\n\n"
            
            "[bold green]Cost Information:[/bold green]\n"
            "• Google Cloud TTS has a free tier\n"
            "• First 4 million characters per month are free\n"
            "• After that, ~$4 per 1 million characters\n"
            "• You can set up billing alerts to control costs",
            border_style="blue"
        ))
        
        console.print("\n[bold yellow]Would you like to:[/bold yellow]")
        console.print("1. Continue with demo mode (explore interface only)")
        console.print("2. Exit and complete Google Cloud setup first")
        
        choice = Prompt.ask("Choose option", choices=["1", "2"], default="2")
        
        if choice == "1":
            return self._setup_demo_mode()
        else:
            console.print("\n[bold blue]📋 Next Steps:[/bold blue]")
            console.print("1. Follow the guide above to set up Google Cloud")
            console.print("2. Download your credentials file")
            console.print("3. Run this wizard again: python setup_wizard.py")
            console.print("4. Select 'I have credentials file' when prompted")
            return False
    
    def _setup_demo_mode(self):
        """Setup demo mode without credentials"""
        console.print("\n[bold yellow]🎭 Setting up demo mode...[/bold yellow]")
        console.print("Demo mode allows you to explore the interface without Google Cloud credentials.")
        console.print("You can add credentials later and restart the wizard.")
        
        self.config['demo_mode'] = True
        return True
    
    def configure_language_preferences(self):
        """Configure language and voice preferences"""
        console.print("\n[bold cyan]🌍 Configuring language preferences...[/bold cyan]")
        
        # Show available languages
        languages = {
            "en-US": "English (US)",
            "ja-JP": "Japanese",
            "es-ES": "Spanish (Spain)",
            "fr-FR": "French",
            "de-DE": "German"
        }
        
        table = Table(title="Available Languages", show_header=True, header_style="bold magenta")
        table.add_column("Code", style="cyan")
        table.add_column("Language", style="yellow")
        
        for code, name in languages.items():
            table.add_row(code, name)
        
        console.print(table)
        
        # Select primary language
        primary_lang = Prompt.ask(
            "Select your primary language",
            choices=list(languages.keys()),
            default="en-US"
        )
        
        self.config['primary_language'] = primary_lang
        
        # Select additional languages
        additional_langs = []
        for code, name in languages.items():
            if code != primary_lang:
                if Confirm.ask(f"Add {name} support?", default=False):
                    additional_langs.append(code)
        
        self.config['additional_languages'] = additional_langs
        
        # Voice preferences
        console.print("\n[bold yellow]Voice Preferences:[/bold yellow]")
        self.config['voice_rotation'] = Confirm.ask(
            "Enable voice rotation (different voice for each sentence)?",
            default=True
        )
        
        if not self.config['voice_rotation']:
            voice_options = ["Female", "Male", "Mixed"]
            voice_pref = Prompt.ask(
                "Preferred voice type",
                choices=voice_options,
                default="Female"
            )
            self.config['voice_preference'] = voice_pref
    
    def configure_processing_settings(self):
        """Configure processing settings"""
        console.print("\n[bold cyan]⚙️ Configuring processing settings...[/bold cyan]")
        
        # Audio quality
        console.print("\n[bold yellow]Audio Quality Settings:[/bold yellow]")
        quality_options = {
            "fast": "Fast (16kHz, smaller files)",
            "standard": "Standard (24kHz, recommended)",
            "high": "High (48kHz, larger files)"
        }
        
        for key, desc in quality_options.items():
            console.print(f"  {key}: {desc}")
        
        quality = Prompt.ask(
            "Select audio quality",
            choices=list(quality_options.keys()),
            default="standard"
        )
        
        self.config['audio_quality'] = quality
        
        # Processing speed
        console.print("\n[bold yellow]Processing Speed:[/bold yellow]")
        speed_options = {
            "conservative": "Conservative (fewer concurrent requests)",
            "balanced": "Balanced (recommended)",
            "aggressive": "Aggressive (more concurrent requests)"
        }
        
        for key, desc in speed_options.items():
            console.print(f"  {key}: {desc}")
        
        speed = Prompt.ask(
            "Select processing speed",
            choices=list(speed_options.keys()),
            default="balanced"
        )
        
        self.config['processing_speed'] = speed
        
        # Output format
        format_options = {
            "MP3": "MP3 (compressed, recommended)",
            "WAV": "WAV (uncompressed, larger)",
            "OGG": "OGG (open format)",
            "FLAC": "FLAC (lossless)"
        }
        
        console.print("\n[bold yellow]Output Format:[/bold yellow]")
        for key, desc in format_options.items():
            console.print(f"  {key}: {desc}")
        
        output_format = Prompt.ask(
            "Select output format",
            choices=list(format_options.keys()),
            default="MP3"
        )
        
        self.config['output_format'] = output_format
    
    def configure_advanced_features(self):
        """Configure advanced features"""
        console.print("\n[bold cyan]🔧 Configuring advanced features...[/bold cyan]")
        
        # Audio enhancement
        self.config['audio_enhancement'] = Confirm.ask(
            "Enable audio quality enhancement (normalization, etc.)?",
            default=True
        )
        
        # Caching
        self.config['enable_caching'] = Confirm.ask(
            "Enable caching (faster subsequent runs)?",
            default=True
        )
        
        # Resume functionality
        self.config['enable_resume'] = Confirm.ask(
            "Enable resume functionality (continue interrupted processing)?",
            default=True
        )
        
        # Web interface
        self.config['enable_web_interface'] = Confirm.ask(
            "Enable web interface (modern browser UI)?",
            default=True
        )
    
    def create_configuration(self):
        """Create configuration files"""
        console.print("\n[bold cyan]📝 Creating configuration files...[/bold cyan]")
        
        try:
            # Create YAML configuration
            from ..core.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            # Update configuration based on wizard choices
            config = config_manager.config
            
            # Audio settings
            quality_settings = {
                "fast": {"sample_rate": 16000, "enhancement": "minimal"},
                "standard": {"sample_rate": 24000, "enhancement": "normalize"},
                "high": {"sample_rate": 48000, "enhancement": "full"}
            }
            
            audio_settings = quality_settings.get(self.config.get('audio_quality', 'standard'), {})
            config['audio']['default_sample_rate'] = audio_settings.get('sample_rate', 24000)
            config['audio']['enhancement'] = audio_settings.get('enhancement', 'normalize')
            config['audio']['default_format'] = self.config.get('output_format', 'MP3')
            
            # Processing settings
            speed_settings = {
                "conservative": {"max_workers": 3, "max_concurrent": 10, "delay": 0.1},
                "balanced": {"max_workers": 5, "max_concurrent": 15, "delay": 0.05},
                "aggressive": {"max_workers": 8, "max_concurrent": 20, "delay": 0.02}
            }
            
            proc_settings = speed_settings.get(self.config.get('processing_speed', 'balanced'), {})
            config['processing']['max_workers'] = proc_settings.get('max_workers', 5)
            config['processing']['max_concurrent'] = proc_settings.get('max_concurrent', 15)
            config['processing']['delay'] = proc_settings.get('delay', 0.05)
            config['processing']['enable_caching'] = self.config.get('enable_caching', True)
            config['processing']['resume_checkpoint'] = self.config.get('enable_resume', True)
            
            # Voice settings
            config['voice']['rotation_enabled'] = self.config.get('voice_rotation', True)
            config['voice']['default_language'] = self.config.get('primary_language', 'en-US')
            
            # Save configuration
            config_manager.save_config(config)
            
            # Create demo credentials if in demo mode
            if self.config.get('demo_mode', False):
                self._create_demo_credentials()
            
            console.print("[green]✅ Configuration files created successfully[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error creating configuration: {e}[/red]")
            return False
    
    def _create_demo_credentials(self):
        """Create demo credentials file"""
        demo_creds = {
            "type": "service_account",
            "project_id": "demo-project",
            "private_key_id": "demo-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nDEMO_KEY\n-----END PRIVATE KEY-----\n",
            "client_email": "demo@demo-project.iam.gserviceaccount.com",
            "client_id": "demo-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/demo%40demo-project.iam.gserviceaccount.com"
        }
        
        with open("google-credentials-demo.json", "w") as f:
            json.dump(demo_creds, f, indent=2)
        
        console.print("[yellow]⚠️ Demo credentials created (google-credentials-demo.json)[/yellow]")
        console.print("[yellow]Replace with real credentials when ready for production use[/yellow]")
    
    def show_summary(self):
        """Show setup summary"""
        console.print("\n[bold cyan]📋 Setup Summary[/bold cyan]")
        
        table = Table(title="Configuration Summary", show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        # Credentials
        if self.config.get('demo_mode', False):
            table.add_row("Credentials", "Demo mode (google-credentials-demo.json)")
        else:
            table.add_row("Credentials", f"✅ {self.credentials_path}")
        
        # Language
        primary_lang = self.config.get('primary_language', 'en-US')
        additional_langs = self.config.get('additional_languages', [])
        langs = [primary_lang] + additional_langs
        table.add_row("Languages", ", ".join(langs))
        
        # Voice rotation
        voice_rotation = "✅ Enabled" if self.config.get('voice_rotation', True) else "❌ Disabled"
        table.add_row("Voice Rotation", voice_rotation)
        
        # Audio quality
        quality = self.config.get('audio_quality', 'standard').title()
        table.add_row("Audio Quality", quality)
        
        # Processing speed
        speed = self.config.get('processing_speed', 'balanced').title()
        table.add_row("Processing Speed", speed)
        
        # Output format
        format_type = self.config.get('output_format', 'MP3')
        table.add_row("Output Format", format_type)
        
        # Features
        features = []
        if self.config.get('audio_enhancement', True):
            features.append("Audio Enhancement")
        if self.config.get('enable_caching', True):
            features.append("Caching")
        if self.config.get('enable_resume', True):
            features.append("Resume")
        if self.config.get('enable_web_interface', True):
            features.append("Web Interface")
        
        table.add_row("Enabled Features", ", ".join(features))
        
        console.print(table)
    
    def show_next_steps(self):
        """Show next steps"""
        console.print("\n[bold green]🎉 Setup Complete![/bold green]")
        
        console.print("\n[bold yellow]Next Steps:[/bold yellow]")
        
        if self.config.get('demo_mode', False):
            console.print("1. 🎭 Try demo mode: python demo.py")
            console.print("2. 🌐 Launch web interface: python start_web_interface.py")
            console.print("3. 🔑 Add real Google Cloud credentials when ready")
            console.print("4. 🚀 Run: python tts_batch_processor.py examples_en.txt --credentials google-credentials.json")
        else:
            console.print("1. 🚀 Process your first sentences:")
            console.print("   python tts_batch_processor.py examples_en.txt --credentials google-credentials.json")
            console.print("2. 🌐 Launch web interface: python start_web_interface.py")
            console.print("3. 🎭 Try the demo: python demo.py")
        
        console.print("\n[bold blue]Documentation:[/bold blue]")
        console.print("• README.md - Complete user guide")
        console.print("• QUICK_START.md - Quick start guide")
        console.print("• ENHANCEMENT_SUMMARY.md - Feature overview")
        
        console.print("\n[bold green]Happy Text-to-Speech Processing! 🎤✨[/bold green]")
    
    def run(self):
        """Run the complete setup wizard"""
        try:
            self.welcome()
            
            if not self.check_python_version():
                return False
            
            if not self.install_dependencies():
                return False
            
            if not self.setup_credentials():
                return False
            
            self.configure_language_preferences()
            self.configure_processing_settings()
            self.configure_advanced_features()
            
            if not self.create_configuration():
                return False
            
            self.show_summary()
            self.show_next_steps()
            
            return True
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Setup cancelled by user[/yellow]")
            return False
        except Exception as e:
            console.print(f"\n[red]Setup failed: {e}[/red]")
            return False

def main():
    """Main function"""
    wizard = SetupWizard()
    success = wizard.run()
    
    if success:
        console.print("\n[bold green]✅ Setup completed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Setup failed. Please try again.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
