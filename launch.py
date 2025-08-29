#!/usr/bin/env python3
"""
One-Click Launcher for Advanced TTS Batch Processor
Automatically chooses the best interface based on user preferences and system capabilities
"""

import os
import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import webbrowser
import time

console = Console()

class TTSLauncher:
    """One-click launcher for TTS processor"""
    
    def __init__(self):
        self.console = Console()
        
    def show_welcome(self):
        """Show welcome message"""
        console.print(Panel.fit(
            "[bold blue]🎤 Advanced TTS Batch Processor - One-Click Launcher[/bold blue]\n\n"
            "Welcome! This launcher will help you get started quickly.\n"
            "Choose your preferred interface or let us recommend one for you.",
            border_style="blue"
        ))
    
    def check_system_capabilities(self):
        """Check system capabilities and dependencies"""
        console.print("\n[bold cyan]🔍 Checking system capabilities...[/bold cyan]")
        
        capabilities = {
            "python_version": self._check_python_version(),
            "dependencies": self._check_dependencies(),
            "credentials": self._check_credentials(),
            "browser": self._check_browser(),
            "network": self._check_network()
        }
        
        return capabilities
    
    def _check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 7:
            console.print(f"[green]✅ Python {version.major}.{version.minor}.{version.micro}[/green]")
            return True
        else:
            console.print(f"[red]❌ Python 3.7+ required (found {version.major}.{version.minor})[/red]")
            return False
    
    def _check_dependencies(self):
        """Check if dependencies are installed"""
        try:
            import rich
            import flask
            import yaml
            console.print("[green]✅ Core dependencies installed[/green]")
            return True
        except ImportError as e:
            console.print(f"[red]❌ Missing dependencies: {e}[/red]")
            return False
    
    def _check_credentials(self):
        """Check for Google Cloud credentials"""
        cred_paths = [
            "google-credentials.json",
            "google-credentials-demo.json",
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            os.getenv("GOOGLE_CREDENTIALS_PATH")
        ]
        
        for path in cred_paths:
            if path and Path(path).exists():
                console.print(f"[green]✅ Credentials found: {path}[/green]")
                return True
        
        console.print("[yellow]⚠️ No credentials found (demo mode available)[/yellow]")
        return False
    
    def _check_browser(self):
        """Check if browser is available"""
        try:
            webbrowser.get()
            console.print("[green]✅ Browser available[/green]")
            return True
        except:
            console.print("[yellow]⚠️ Browser not available[/yellow]")
            return False
    
    def _check_network(self):
        """Check network connectivity"""
        try:
            import urllib.request
            urllib.request.urlopen('http://www.google.com', timeout=3)
            console.print("[green]✅ Network connectivity[/green]")
            return True
        except:
            console.print("[yellow]⚠️ Network connectivity issues[/yellow]")
            return False
    
    def recommend_interface(self, capabilities):
        """Recommend the best interface based on capabilities"""
        console.print("\n[bold cyan]🎯 Interface Recommendation[/bold cyan]")
        
        if not capabilities["python_version"]:
            console.print("[red]❌ Cannot recommend interface - Python version incompatible[/red]")
            return None
        
        if not capabilities["dependencies"]:
            console.print("[yellow]⚠️ Installing dependencies first...[/yellow]")
            self._install_dependencies()
            capabilities["dependencies"] = True
        
        # Decision logic
        if capabilities["browser"] and capabilities["network"]:
            if capabilities["credentials"]:
                console.print("[green]🎯 Recommended: Web Interface[/green]")
                console.print("   • Modern, user-friendly interface")
                console.print("   • Real-time progress tracking")
                console.print("   • Easy file management")
                return "web"
            else:
                console.print("[green]🎯 Recommended: Setup Wizard[/green]")
                console.print("   • Interactive credential setup")
                console.print("   • Guided configuration")
                console.print("   • Demo mode available")
                return "setup"
        else:
            console.print("[green]🎯 Recommended: Smart CLI[/green]")
            console.print("   • Works without browser")
            console.print("   • Interactive command building")
            console.print("   • Full feature access")
            return "cli"
    
    def _install_dependencies(self):
        """Install missing dependencies"""
        try:
            console.print("Installing dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            console.print("[green]✅ Dependencies installed successfully[/green]")
        except subprocess.CalledProcessError:
            console.print("[red]❌ Failed to install dependencies[/red]")
            console.print("Please run: pip install -r requirements.txt")
    
    def show_interface_options(self):
        """Show all available interface options"""
        console.print("\n[bold cyan]🎛️ Available Interfaces[/bold cyan]")
        
        interfaces = [
            ("🌐", "Web Interface", "Modern browser-based UI", "web"),
            ("🎯", "Smart CLI", "Interactive command-line interface", "cli"),
            ("⚙️", "Setup Wizard", "Guided initial setup", "setup"),
            ("🎭", "Demo Mode", "Feature demonstration", "demo"),
            ("📖", "Help & Documentation", "Show help and examples", "help")
        ]
        
        table = Table(title="Interface Options", show_header=True, header_style="bold magenta")
        table.add_column("Icon", style="cyan", width=3)
        table.add_column("Interface", style="yellow")
        table.add_column("Description", style="green")
        table.add_column("Command", style="blue")
        
        for icon, name, desc, cmd in interfaces:
            table.add_row(icon, name, desc, cmd)
        
        console.print(table)
    
    def get_user_preference(self, recommendation):
        """Get user's interface preference"""
        console.print(f"\n[bold yellow]Your recommendation: {recommendation.upper()}[/bold yellow]")
        
        if Confirm.ask("Use recommended interface?", default=True):
            return recommendation
        
        self.show_interface_options()
        
        while True:
            choice = Prompt.ask("Choose interface", choices=["web", "cli", "setup", "demo", "help"])
            if choice:
                return choice
    
    def launch_interface(self, interface):
        """Launch the selected interface"""
        console.print(f"\n[bold green]🚀 Launching {interface.upper()} interface...[/bold green]")
        
        try:
            if interface == "web":
                self._launch_web_interface()
            elif interface == "cli":
                self._launch_smart_cli()
            elif interface == "setup":
                self._launch_setup_wizard()
            elif interface == "demo":
                self._launch_demo()
            elif interface == "help":
                self._show_help()
            else:
                console.print(f"[red]Unknown interface: {interface}[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Interface stopped by user[/yellow]")
        except Exception as e:
            console.print(f"[red]Error launching interface: {e}[/red]")
    
    def _launch_web_interface(self):
        """Launch web interface"""
        console.print("Starting web interface...")
        console.print("URL: http://localhost:5000")
        console.print("Press Ctrl+C to stop")
        
        # Start web interface in background
        process = subprocess.Popen([sys.executable, "start_web_interface.py"])
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Try to open browser
        try:
            webbrowser.open('http://localhost:5000')
            console.print("[green]✅ Browser opened automatically[/green]")
        except:
            console.print("[yellow]⚠️ Please open http://localhost:5000 in your browser[/yellow]")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            console.print("\n[yellow]Web interface stopped[/yellow]")
    
    def _launch_smart_cli(self):
        """Launch smart CLI"""
        console.print("Starting smart CLI...")
        subprocess.run([sys.executable, "smart_cli.py"])
    
    def _launch_setup_wizard(self):
        """Launch setup wizard"""
        console.print("Starting setup wizard...")
        subprocess.run([sys.executable, "setup_wizard.py"])
    
    def _launch_demo(self):
        """Launch demo"""
        console.print("Starting feature demo...")
        subprocess.run([sys.executable, "demo.py"])
    
    def _show_help(self):
        """Show help and documentation"""
        console.print(Panel.fit(
            "[bold blue]📖 Help & Documentation[/bold blue]\n\n"
            "Quick Start:\n"
            "• python setup_wizard.py - Interactive setup\n"
            "• python smart_cli.py - Smart command-line interface\n"
            "• python start_web_interface.py - Web interface\n"
            "• python demo.py - Feature demonstration\n\n"
            "Documentation:\n"
            "• README.md - Complete user guide\n"
            "• QUICK_START.md - Quick start guide\n"
            "• ENHANCEMENT_SUMMARY.md - Feature overview\n\n"
            "Examples:\n"
            "• examples_en.txt - English sentences\n"
            "• examples_ja.txt - Japanese sentences\n"
            "• examples_es.txt - Spanish sentences",
            border_style="blue"
        ))
    
    def run(self):
        """Run the launcher"""
        try:
            self.show_welcome()
            
            # Check system capabilities
            capabilities = self.check_system_capabilities()
            
            # Get recommendation
            recommendation = self.recommend_interface(capabilities)
            
            if not recommendation:
                console.print("[red]❌ Cannot proceed - system requirements not met[/red]")
                return False
            
            # Get user preference
            interface = self.get_user_preference(recommendation)
            
            # Launch interface
            self.launch_interface(interface)
            
            return True
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Launcher cancelled by user[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Launcher error: {e}[/red]")
            return False

def main():
    """Main function"""
    launcher = TTSLauncher()
    success = launcher.run()
    
    if success:
        console.print("\n[bold green]✅ Launcher completed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Launcher failed. Please try again.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
