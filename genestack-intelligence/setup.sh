#!/usr/bin/env bash
# Genestack Intelligence Suite - Setup Script
# This script sets up the virtual environment and installs dependencies
# Works on any server with Python 3.8+

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "🧬=========================================================="
echo "       Genestack Intelligence Suite - Setup"
echo "==========================================================🧬"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

echo "   Found Python $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
    echo "❌ Error: Python 3.8 or higher is required"
    echo "   Current version: $PYTHON_VERSION"
    exit 1
fi

# Check for venv module
echo ""
echo "🔍 Checking for venv module..."
if ! python3 -c "import venv" &> /dev/null; then
    echo "❌ Error: python3-venv is not installed"
    echo "   Please install it using:"
    echo "   - Ubuntu/Debian: sudo apt-get install python3-venv"
    echo "   - RHEL/CentOS: sudo yum install python3-venv"
    echo "   - Fedora: sudo dnf install python3-venv"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "   Virtual environment already exists at: $VENV_DIR"
    read -p "   Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        echo "   ✅ Virtual environment recreated"
    else
        echo "   Using existing virtual environment"
    fi
else
    python3 -m venv "$VENV_DIR"
    echo "   ✅ Virtual environment created at: $VENV_DIR"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --quiet --upgrade pip

# Install requirements
echo ""
echo "📥 Installing dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install --quiet -r "$SCRIPT_DIR/requirements.txt"
    echo "   ✅ Dependencies installed"
else
    echo "❌ Error: requirements.txt not found at $SCRIPT_DIR/requirements.txt"
    exit 1
fi

# Install Playwright browsers (optional)
echo ""
echo "🎭 Installing Playwright browsers (for screenshot capture)..."
echo "   This may take a few minutes..."
python3 -m playwright install chromium 2>&1 | grep -v "Downloading" || true
echo "   ✅ Playwright setup complete"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the dashboard, run:"
echo "   ./start.sh"
echo ""
echo "==========================================================🧬"
