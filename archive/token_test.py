#!/usr/bin/env python3
"""
Isolated Token Loading Test
Tests GITHUB_MODELS_TOKEN loading in different scenarios to debug bundled executable issues.
"""

import os
import sys
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

def test_token_loading():
    """Test all possible ways of loading the GitHub token"""
    
    print_header("GITHUB TOKEN LOADING TEST")
    
    # Test 1: Direct environment variable
    print("\n1️⃣ Testing direct os.environ access...")
    token_env = os.environ.get('GITHUB_MODELS_TOKEN')
    print(f"   os.environ.get('GITHUB_MODELS_TOKEN'): {token_env[:10] + '...' if token_env else 'None'}")
    
    # Test 2: Test if we're in a bundled executable
    print("\n2️⃣ Testing execution environment...")
    if hasattr(sys, '_MEIPASS'):
        print("   ✅ Running in PyInstaller bundle")
        print(f"   Bundle temp dir: {sys._MEIPASS}")
        bundle_dir = Path(sys._MEIPASS)
    else:
        print("   ⚠️ Running in normal Python")
        bundle_dir = Path(__file__).parent
    
    current_dir = Path.cwd()
    script_dir = Path(__file__).parent if not hasattr(sys, '_MEIPASS') else Path(sys._MEIPASS)
    
    print(f"   Current working dir: {current_dir}")
    print(f"   Script/bundle dir: {script_dir}")
    
    # Test 3: Look for .env files in various locations
    print("\n3️⃣ Searching for .env files...")
    
    env_locations = [
        current_dir / '.env',
        script_dir / '.env', 
        bundle_dir / '.env',
        Path.home() / '.env',
        Path('/tmp') / '.env'  # For testing
    ]
    
    found_env_files = []
    for env_path in env_locations:
        if env_path.exists():
            found_env_files.append(env_path)
            print(f"   ✅ Found: {env_path}")
            
            # Try to read it
            try:
                with open(env_path, 'r') as f:
                    content = f.read().strip()
                    lines = [line for line in content.split('\n') if 'GITHUB' in line and not line.startswith('#')]
                    if lines:
                        print(f"      Content preview: {lines[0][:30]}...")
                    else:
                        print("      No GITHUB_MODELS_TOKEN found in file")
            except Exception as e:
                print(f"      ⚠️ Could not read: {e}")
        else:
            print(f"   ❌ Not found: {env_path}")
    
    # Test 4: Try python-dotenv if available
    print("\n4️⃣ Testing python-dotenv loading...")
    try:
        from dotenv import load_dotenv, find_dotenv
        print("   ✅ dotenv module available")
        
        # Try automatic finding
        env_file = find_dotenv()
        print(f"   find_dotenv() result: {env_file}")
        
        if env_file:
            result = load_dotenv(env_file)
            print(f"   load_dotenv() result: {result}")
            token_after_dotenv = os.environ.get('GITHUB_MODELS_TOKEN')
            print(f"   Token after dotenv: {token_after_dotenv[:10] + '...' if token_after_dotenv else 'None'}")
        
        # Try loading from each found .env file
        for env_path in found_env_files:
            print(f"   Trying to load: {env_path}")
            result = load_dotenv(env_path)
            print(f"   Result: {result}")
            token_test = os.environ.get('GITHUB_MODELS_TOKEN')
            print(f"   Token after loading {env_path}: {token_test[:10] + '...' if token_test else 'None'}")
            
    except ImportError:
        print("   ❌ dotenv module not available")
    except Exception as e:
        print(f"   ⚠️ Error with dotenv: {e}")
    
    # Test 5: Manual .env parsing
    print("\n5️⃣ Testing manual .env parsing...")
    for env_path in found_env_files:
        print(f"   Manually parsing: {env_path}")
        try:
            with open(env_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line.startswith('GITHUB_MODELS_TOKEN=') and not line.startswith('#'):
                        token_value = line.split('=', 1)[1].strip().strip('"\'')
                        if token_value and token_value != 'your_github_token_here':
                            print(f"      ✅ Found valid token on line {line_num}: {token_value[:10]}...")
                            return token_value
                        else:
                            print(f"      ⚠️ Found placeholder token on line {line_num}")
        except Exception as e:
            print(f"      ❌ Error parsing {env_path}: {e}")
    
    # Test 6: Final status
    print_header("FINAL STATUS")
    final_token = os.environ.get('GITHUB_MODELS_TOKEN')
    if final_token and final_token != 'your_github_token_here':
        print(f"✅ SUCCESS: Token is available: {final_token[:10]}...")
        return final_token
    else:
        print("❌ FAILURE: No valid token found")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Create a .env file in the same folder as this executable")
        print("2. Add this line: GITHUB_MODELS_TOKEN=your_actual_token_here")
        print("3. Get a token from: https://github.com/settings/tokens")
        print("4. Make sure the token has 'Models' permission")
        return None

if __name__ == "__main__":
    try:
        test_token_loading()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*50}")
    print("Test completed. Press Enter to exit...")
    input()
