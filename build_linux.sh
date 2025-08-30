#!/bin/bash
# Simple packaging script for Linux

echo "🚀 Building Kamerafallen-Tools for Linux..."

# Install PyInstaller if needed
python3 -m pip install pyinstaller

# Create the executable
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name="KamerafallenTools" \
    --add-data="*.py:." \
    --hidden-import="PIL._tkinter_finder" \
    --hidden-import="extract_msg" \
    --hidden-import="pandas" \
    --hidden-import="openpyxl" \
    --hidden-import="PIL" \
    --hidden-import="requests" \
    --hidden-import="dotenv" \
    --hidden-import="tkinter.ttk" \
    --hidden-import="tkinter.filedialog" \
    --hidden-import="tkinter.messagebox" \
    main_gui.py

if [ -f "dist/KamerafallenTools" ]; then
    echo "✅ Executable created successfully!"
    echo "📁 Location: dist/KamerafallenTools"
    echo "📏 Size: $(du -h dist/KamerafallenTools | cut -f1)"
    
    # Make executable
    chmod +x dist/KamerafallenTools
    
    # Create portable package
    mkdir -p dist/KamerafallenTools-linux-portable
    cp dist/KamerafallenTools dist/KamerafallenTools-linux-portable/
    cp .env.example dist/KamerafallenTools-linux-portable/
    cp README.md dist/KamerafallenTools-linux-portable/
    cp ANLEITUNG.md dist/KamerafallenTools-linux-portable/ 2>/dev/null || true
    
    # Create startup script
    cat > dist/KamerafallenTools-linux-portable/start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./KamerafallenTools
EOF
    chmod +x dist/KamerafallenTools-linux-portable/start.sh
    
    # Create archive
    cd dist
    tar -czf KamerafallenTools-linux-v1.0.tar.gz KamerafallenTools-linux-portable/
    cd ..
    
    echo "📦 Portable package created: dist/KamerafallenTools-linux-v1.0.tar.gz"
else
    echo "❌ Build failed!"
    exit 1
fi
