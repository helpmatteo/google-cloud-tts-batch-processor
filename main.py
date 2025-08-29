#!/usr/bin/env python3
"""
Main entry point for Advanced TTS Batch Processor
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point"""
    from src.cli.smart_cli import SmartCLI
    
    # Initialize and run the CLI
    cli = SmartCLI()
    cli.run()

if __name__ == "__main__":
    main()
