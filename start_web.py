#!/usr/bin/env python3
"""
Web interface entry point for Advanced TTS Batch Processor
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Start the web interface"""
    from src.web.start_web_interface import start_web_server
    
    # Start the web server
    start_web_server()

if __name__ == "__main__":
    main()
