#!/usr/bin/env python3
"""
Debug version of the analyzer to help diagnose bundling issues.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

def debug_environment():
    """Print detailed debug information about the current environment."""
    print("=" * 50)
    print("ENVIRONMENT DEBUG INFORMATION")
    print("=" * 50)
    
    # Check if running from bundle
    is_bundled = hasattr(sys, '_MEIPASS')
    print(f"Running from PyInstaller bundle: {is_bundled}")
    
    if is_bundled:
        print(f"Bundle directory (sys._MEIPASS): {sys._MEIPASS}")
        print(f"Executable directory: {os.path.dirname(sys.executable)}")
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries
    
    # Check environment variables
    print("\nENVIRONMENT VARIABLES:")
    github_token = os.environ.get('GITHUB_MODELS_TOKEN', 'NOT_SET')
    print(f"GITHUB_MODELS_TOKEN: {'***SET***' if github_token != 'NOT_SET' else 'NOT_SET'}")
    
    # Check for .env files
    print("\n.ENV FILE LOCATIONS:")
    possible_env_locations = [
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.path.dirname(sys.executable), '.env') if is_bundled else None,
        os.path.join(sys._MEIPASS, '.env') if is_bundled else None,
        os.path.expanduser('~/.env')
    ]
    
    for location in possible_env_locations:
        if location:
            exists = os.path.exists(location)
            print(f"  {location}: {'EXISTS' if exists else 'NOT FOUND'}")
            if exists:
                try:
                    with open(location, 'r') as f:
                        content = f.read()
                    has_token = 'GITHUB_MODELS_TOKEN' in content
                    print(f"    Contains GITHUB_MODELS_TOKEN: {has_token}")
                except Exception as e:
                    print(f"    Error reading: {e}")
    
    # Check dotenv availability
    print("\nDOTENV MODULE:")
    try:
        import dotenv
        print(f"  dotenv available: YES (version: {dotenv.__version__})")
    except ImportError:
        print("  dotenv available: NO")
    
    # Check if GUI works
    print("\nGUI TEST:")
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
        print("  tkinter GUI: WORKING")
        root.destroy()
    except Exception as e:
        print(f"  tkinter GUI: ERROR - {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    debug_environment()
    
    # Show debug info in a GUI window too
    root = tk.Tk()
    root.title("Debug Information")
    
    # Create debug text
    is_bundled = hasattr(sys, '_MEIPASS')
    github_token = os.environ.get('GITHUB_MODELS_TOKEN', '')
    
    debug_text = f"""
RUNNING FROM BUNDLE: {is_bundled}
WORKING DIRECTORY: {os.getcwd()[:50]}...
GITHUB_TOKEN SET: {'YES' if github_token else 'NO'}

Check the console window for detailed debug information.

Click OK to continue with normal analyzer...
    """
    
    messagebox.showinfo("Debug Info", debug_text)
    root.destroy()
    
    # Now try to import and run the normal analyzer
    try:
        print("\nTrying to import github_models_analyzer...")
        import github_models_analyzer as gma
        print("Successfully imported github_models_analyzer")
        
        # Check what the analyzer sees
        print(f"Analyzer GITHUB_TOKEN: {'SET' if gma.GITHUB_TOKEN else 'NOT SET'}")
        print(f"Analyzer IMAGES_FOLDER: {gma.IMAGES_FOLDER}")
        print(f"Analyzer OUTPUT_EXCEL: {gma.OUTPUT_EXCEL}")
        
        # Start the analyzer
        print("Starting analyzer...")
        analyzer = gma.ImageAnalyzer()
        analyzer.run()
        
    except Exception as e:
        print(f"Error importing or running analyzer: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error in GUI too
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start analyzer:\n{str(e)[:200]}...")
        root.destroy()
