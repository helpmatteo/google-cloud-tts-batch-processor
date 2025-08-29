#!/usr/bin/env python3
"""
Start Web Interface for Advanced TTS Batch Processor
Launches the Flask web interface with proper configuration
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import flask_cors
        import yaml
        import rich
        console.print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        console.print(f"❌ Missing dependency: {e}")
        console.print("Please run: pip install -r requirements.txt")
        return False

def check_credentials():
    """Check if Google Cloud credentials are available"""
    credentials_paths = [
        "google-credentials.json",
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        os.getenv("GOOGLE_CREDENTIALS_PATH")
    ]
    
    for path in credentials_paths:
        if path and Path(path).exists():
            console.print(f"✅ Found credentials: {path}")
            return True
    
    console.print("⚠️  No Google Cloud credentials found")
    console.print("Please set up your credentials before using the web interface")
    console.print("You can:")
    console.print("  1. Create google-credentials.json file")
    console.print("  2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    console.print("  3. Set GOOGLE_CREDENTIALS_PATH environment variable")
    return False

def start_web_interface():
    """Start the web interface"""
    try:
        from web_interface import app
        
        # Display startup information
        console.print(Panel.fit(
            "[bold blue]🎤 Advanced TTS Batch Processor - Web Interface[/bold blue]",
            border_style="blue"
        ))
        
        # Create info table
        table = Table(title="Web Interface Information", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("URL", "http://localhost:8789")
        table.add_row("Host", "0.0.0.0")
        table.add_row("Port", "8789")
        table.add_row("Debug Mode", "Enabled")
        
        console.print(table)
        
        console.print("\n[bold yellow]Starting web interface...[/bold yellow]")
        console.print("Press Ctrl+C to stop the server")
        
        # Start the Flask app
        app.run(debug=True, host='0.0.0.0', port=8789)
        
    except ImportError as e:
        console.print(f"❌ Error importing web interface: {e}")
        console.print("Make sure all dependencies are installed")
    except Exception as e:
        console.print(f"❌ Error starting web interface: {e}")

def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold green]🚀 Advanced TTS Batch Processor - Web Interface Launcher[/bold green]",
        border_style="green"
    ))
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check credentials (warning only)
    check_credentials()
    
    # Start web interface
    start_web_interface()

if __name__ == "__main__":
    main()
