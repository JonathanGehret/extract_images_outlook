#!/bin/bash
# Lean packaging script for Linux (excludes ML libraries)

echo "🚀 Building Kamerafallen-Tools for Linux (lean build)..."

# Install PyInstaller if needed
python3 -m pip install pyinstaller

# Create the executable with exclusions
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name="KamerafallenTools" \
    --add-data="github_models_analyzer.py:." \
    --add-data="github_models_io.py:." \
    --add-data="github_models_api.py:." \
    --add-data="extract_img_email.py:." \
    --add-data="rename_images_from_excel.py:." \
    --hidden-import="PIL._tkinter_finder" \
    --hidden-import="extract_msg" \
    --hidden-import="pandas" \
    --hidden-import="openpyxl" \
    --hidden-import="openpyxl.styles" \
    --hidden-import="PIL" \
    --hidden-import="requests" \
    --hidden-import="dotenv" \
    --hidden-import="tkinter.ttk" \
    --hidden-import="tkinter.filedialog" \
    --hidden-import="tkinter.messagebox" \
    --hidden-import="github_models_analyzer" \
    --hidden-import="github_models_io" \
    --hidden-import="github_models_api" \
    --hidden-import="extract_img_email" \
    --hidden-import="rename_images_from_excel" \
    --exclude-module="torch" \
    --exclude-module="tensorflow" \
    --exclude-module="torchvision" \
    --exclude-module="numpy.distutils" \
    --exclude-module="matplotlib" \
    --exclude-module="scipy" \
    --exclude-module="sklearn" \
    --exclude-module="cv2" \
    --exclude-module="jupyterlab" \
    --exclude-module="notebook" \
    main_gui.py

if [ -f "dist/KamerafallenTools" ]; then
    echo "✅ Executable created successfully!"
    echo "📁 Location: dist/KamerafallenTools"
    echo "📏 Size: $(du -h dist/KamerafallenTools | cut -f1)"
    
    # Make executable
    chmod +x dist/KamerafallenTools
    
    # Test the executable quickly
    echo "🧪 Testing executable..."
    timeout 5s dist/KamerafallenTools --help 2>/dev/null || echo "Quick test completed"
    
    # Create portable package
    mkdir -p dist/KamerafallenTools-linux-portable
    cp dist/KamerafallenTools dist/KamerafallenTools-linux-portable/
    cp .env.example dist/KamerafallenTools-linux-portable/ 2>/dev/null || true
    cp README.md dist/KamerafallenTools-linux-portable/ 2>/dev/null || true
    
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
    echo "🎯 Final size: $(du -h dist/KamerafallenTools-linux-v1.0.tar.gz | cut -f1)"
else
    echo "❌ Build failed!"
    exit 1
fi
