#!/usr/bin/env python3
"""
Setup wizard entry point for Advanced TTS Batch Processor
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the setup wizard"""
    from src.cli.setup_wizard import SetupWizard
    
    # Run the setup wizard
    wizard = SetupWizard()
    wizard.run()

if __name__ == "__main__":
    main()
