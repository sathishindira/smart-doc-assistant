#!/usr/bin/env python3
"""
Main runner script for the AI Document Assistant
This script sets up the environment and runs the Streamlit app
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_environment():
    """Setup the environment and install required packages if needed"""
    print("Setting up AI Document Assistant...")
    
    # Create necessary directories
    os.makedirs('./vector_store/', exist_ok=True)
    os.makedirs('./temp/', exist_ok=True)
    
    print("Environment setup complete!")

def main():
    """Main entry point"""
    setup_environment()
    
    # Import and run the Streamlit app
    print("Starting Streamlit application...")
    print("Access the app at: http://localhost:8501")
    
    # Run streamlit
    os.system("streamlit run 06_streamlit_app_complete.py")

if __name__ == "__main__":
    main()