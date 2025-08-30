#!/usr/bin/env python3
"""
Distribution packager for Kamerafallen Tools
Creates release packages for Linux and Windows
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime

def create_release_package():
    """Create a release package with documentation"""
    print("📦 Creating release package...")
    
    # Create release directory
    release_dir = f"KamerafallenTools-v2.0-{datetime.now().strftime('%Y%m%d')}"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Copy executable
    if os.path.exists('dist/KamerafallenTools'):
        shutil.copy('dist/KamerafallenTools', release_dir)
        os.chmod(os.path.join(release_dir, 'KamerafallenTools'), 0o755)
        print("✅ Copied Linux executable")
    
    # Copy documentation
    docs_to_copy = [
        'README.md',
        'ANLEITUNG.md',
        '.env.example',
        'requirements.txt'
    ]
    
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy(doc, release_dir)
            print(f"✅ Copied {doc}")
    
    # Create startup script
    startup_script = f"""#!/bin/bash
# Kamerafallen Tools Startup Script
# Automatically sets up the environment and runs the application

echo "🚀 Starting Kamerafallen Tools..."

# Set working directory to script location
cd "$(dirname "$0")"

# Check if .env file exists, if not create from example
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your GitHub token before using AI features"
fi

# Run the application
./KamerafallenTools

echo "👋 Kamerafallen Tools closed."
"""
    
    with open(f'{release_dir}/start.sh', 'w') as f:
        f.write(startup_script)
    os.chmod(f'{release_dir}/start.sh', 0o755)
    print("✅ Created startup script")
    
    # Create user guide
    user_guide = """# Kamerafallen Tools - Benutzerhandbuch

## Schnellstart

1. **Erste Verwendung:**
   - Führen Sie `./start.sh` aus (empfohlen) oder `./KamerafallenTools`
   - Bei erstem Start wird eine .env-Datei erstellt

2. **GitHub Token konfigurieren (optional für KI-Features):**
   - Öffnen Sie die .env-Datei in einem Texteditor
   - Fügen Sie Ihren GitHub Models Token ein: `GITHUB_MODELS_TOKEN=ihr_token_hier`

3. **Tools verwenden:**
   - **E-Mail Extraktor**: Bilder aus .msg-Dateien extrahieren
   - **Analyzer**: KI-gestützte Bildanalyse für Kamerafallen
   - **Renamer**: Bilder basierend auf Excel-Daten umbenennen

## Systemanforderungen

- Linux x86_64
- Mindestens 2GB RAM
- 200MB freier Speicherplatz

## Unterstützte Dateiformate

- **Eingabe**: .msg (E-Mail), .jpg/.jpeg (Bilder), .xlsx (Excel)
- **Ausgabe**: .jpg/.jpeg (Bilder), .xlsx (Excel-Berichte)

## Fehlerbehebung

- **Executable startet nicht**: Prüfen Sie Dateiberechtigungen (`chmod +x KamerafallenTools`)
- **KI-Features funktionieren nicht**: Überprüfen Sie den GitHub Token in der .env-Datei
- **Speicher-Probleme**: Schließen Sie andere Anwendungen für mehr RAM

## Support

Bei Problemen oder Fragen wenden Sie sich an den Entwickler oder erstellen Sie ein Issue im Repository.
"""
    
    with open(f'{release_dir}/BENUTZERHANDBUCH.md', 'w') as f:
        f.write(user_guide)
    print("✅ Created user guide")
    
    # Create zip package
    zip_name = f'{release_dir}-linux.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_name)
    
    print(f"✅ Created zip package: {zip_name}")
    
    # Show package info
    print(f"\n📦 Release Package Created:")
    print(f"   📁 Directory: {release_dir}/")
    print(f"   📦 Zip: {zip_name}")
    print(f"   📊 Contents:")
    
    for item in os.listdir(release_dir):
        item_path = os.path.join(release_dir, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path) / (1024 * 1024)
            print(f"      📄 {item} ({size:.1f} MB)")
    
    return release_dir, zip_name

def main():
    """Main distribution function"""
    print("🚀 Kamerafallen Tools - Distribution Packager")
    print("=" * 60)
    
    # Check if executable exists
    if not os.path.exists('dist/KamerafallenTools'):
        print("❌ Executable not found! Run build_final.py first.")
        return False
    
    # Create release package
    release_dir, zip_file = create_release_package()
    
    print(f"\n🎉 Distribution package ready!")
    print(f"\n📋 Summary:")
    print(f"   🖥️  Platform: Linux x86_64")
    print(f"   📁 Package: {release_dir}/")
    print(f"   📦 Archive: {zip_file}")
    print(f"   🚀 Ready to distribute!")
    
    print(f"\n💡 Usage Instructions:")
    print(f"   1. Extract {zip_file} on target Linux system")
    print(f"   2. Run ./start.sh or ./KamerafallenTools")
    print(f"   3. Configure .env file for AI features (optional)")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
