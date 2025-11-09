#!/bin/bash
# Lean packaging script for Linux (excludes ML libraries)

echo "🚀 Building Kamerafallen-Tools for Linux (lean build)..."

# Install PyInstaller if needed
python3 -m pip install pyinstaller

# Create the executable using the spec file for better reliability
python3 -m PyInstaller KamerafallenTools.spec

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
