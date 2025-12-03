#!/usr/bin/env bash
# Genestack Intelligence Suite - Remote Server Installation Script
# Use this script to quickly set up the dashboard on a remote server

set -e

echo "🧬=========================================================="
echo "   Genestack Intelligence Suite - Remote Installation"
echo "==========================================================🧬"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.sh" ] || [ ! -f "config.sh" ]; then
    echo "❌ Error: This script must be run from the genestack-intelligence directory"
    echo ""
    echo "Usage:"
    echo "  1. Clone the repository:"
    echo "     git clone <repo-url> genestack"
    echo "  2. Navigate to intelligence directory:"
    echo "     cd genestack/genestack-intelligence"
    echo "  3. Run this script:"
    echo "     ./install-remote.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📍 Installation directory: $ROOT_DIR"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$NAME
    OS_VERSION=$VERSION_ID
    echo "🖥️  Detected OS: $OS_NAME $OS_VERSION"
else
    OS_NAME="Unknown"
    echo "⚠️  Could not detect OS"
fi

echo ""

# Check and install Python if needed
echo "🔍 Checking for Python 3.8+..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo ""
    echo "Would you like to install Python 3? (requires sudo)"
    read -p "Install Python 3? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OS_NAME" == *"Ubuntu"* ]] || [[ "$OS_NAME" == *"Debian"* ]]; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-venv python3-pip
        elif [[ "$OS_NAME" == *"Red Hat"* ]] || [[ "$OS_NAME" == *"CentOS"* ]] || [[ "$OS_NAME" == *"Rocky"* ]]; then
            sudo yum install -y python3 python3-venv python3-pip
        elif [[ "$OS_NAME" == *"Fedora"* ]]; then
            sudo dnf install -y python3 python3-venv python3-pip
        else
            echo "❌ Automatic installation not supported for $OS_NAME"
            echo "   Please install Python 3.8+ manually"
            exit 1
        fi
    else
        echo "❌ Python 3 is required. Please install it manually."
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Check for git
echo "🔍 Checking for git..."
if ! command -v git &> /dev/null; then
    echo "⚠️  Git not found (optional but recommended)"
    echo ""
    read -p "Install git? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OS_NAME" == *"Ubuntu"* ]] || [[ "$OS_NAME" == *"Debian"* ]]; then
            sudo apt-get install -y git
        elif [[ "$OS_NAME" == *"Red Hat"* ]] || [[ "$OS_NAME" == *"CentOS"* ]] || [[ "$OS_NAME" == *"Rocky"* ]]; then
            sudo yum install -y git
        elif [[ "$OS_NAME" == *"Fedora"* ]]; then
            sudo dnf install -y git
        fi
    fi
else
    echo "✅ Git is installed"
fi

echo ""

# Run setup
echo "📦 Running setup script..."
echo ""
./setup.sh

echo ""
echo "⚙️  Configuration"
echo ""
echo "The dashboard is configured with defaults. You can customize:"
echo ""
echo "1. Edit config.sh:"
echo "   nano config.sh"
echo ""
echo "2. Or set environment variables:"
echo "   export GENESTACK_PORT=9000"
echo "   export GENESTACK_SCREENSHOTS=false"
echo ""

# Ask about firewall
echo "🔥 Firewall Configuration"
echo ""
echo "The dashboard runs on port 8600 by default."
echo "Would you like to open this port in the firewall?"
echo ""
read -p "Configure firewall? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PORT=8600
    if command -v ufw &> /dev/null; then
        echo "Configuring UFW..."
        sudo ufw allow $PORT/tcp
        echo "✅ Port $PORT opened in UFW"
    elif command -v firewall-cmd &> /dev/null; then
        echo "Configuring firewalld..."
        sudo firewall-cmd --permanent --add-port=$PORT/tcp
        sudo firewall-cmd --reload
        echo "✅ Port $PORT opened in firewalld"
    else
        echo "⚠️  No supported firewall found (ufw or firewalld)"
        echo "   You may need to configure your firewall manually"
    fi
fi

echo ""
echo "🎯 Installation Options"
echo ""
echo "Choose how you want to run the dashboard:"
echo ""
echo "1. Manual (run once, stop with Ctrl+C)"
echo "2. Background (run in background, manual management)"
echo "3. systemd Service (auto-start on boot, recommended for production)"
echo "4. Just setup (I'll configure it myself)"
echo ""
read -p "Choose option (1-4): " -n 1 -r
echo
echo ""

case $REPLY in
    1)
        echo "🚀 Starting dashboard in manual mode..."
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        cd "$ROOT_DIR"
        ./start.sh
        ;;
    2)
        echo "🚀 Starting dashboard in background mode..."
        cd "$ROOT_DIR"
        nohup ./start.sh > dashboard.log 2>&1 &
        PID=$!
        echo ""
        echo "✅ Dashboard started in background (PID: $PID)"
        echo ""
        echo "To view logs:"
        echo "   tail -f $ROOT_DIR/dashboard.log"
        echo ""
        echo "To stop:"
        echo "   pkill -f 'streamlit run'"
        echo ""
        ;;
    3)
        echo "⚙️  Setting up systemd service..."
        echo ""
        
        SERVICE_FILE="/etc/systemd/system/genestack-dashboard.service"
        
        # Create service file
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Genestack Intelligence Dashboard
Documentation=https://github.com/rackerlabs/genestack
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$ROOT_DIR
ExecStart=$ROOT_DIR/start.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        echo "✅ Service file created: $SERVICE_FILE"
        echo ""
        
        # Enable and start service
        sudo systemctl daemon-reload
        sudo systemctl enable genestack-dashboard
        sudo systemctl start genestack-dashboard
        
        echo "✅ Service enabled and started"
        echo ""
        echo "Service commands:"
        echo "   Status:  sudo systemctl status genestack-dashboard"
        echo "   Stop:    sudo systemctl stop genestack-dashboard"
        echo "   Restart: sudo systemctl restart genestack-dashboard"
        echo "   Logs:    sudo journalctl -u genestack-dashboard -f"
        echo ""
        
        # Wait a moment and show status
        sleep 2
        sudo systemctl status genestack-dashboard --no-pager
        ;;
    4)
        echo "✅ Setup complete!"
        echo ""
        echo "To start the dashboard manually:"
        echo "   cd $ROOT_DIR"
        echo "   ./start.sh"
        echo ""
        ;;
    *)
        echo "Invalid option. Setup complete."
        echo ""
        echo "To start the dashboard:"
        echo "   cd $ROOT_DIR"
        echo "   ./start.sh"
        echo ""
        ;;
esac

# Show access information
if [[ $REPLY =~ ^[123]$ ]]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Dashboard Access URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  📍 Localhost:"
    echo "     http://localhost:8600"
    echo ""
    
    PRIMARY_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
    if [ -n "$PRIMARY_IP" ]; then
        echo "  🌐 Network:"
        echo "     http://$PRIMARY_IP:8600"
        echo ""
    fi
    
    HOSTNAME=$(hostname 2>/dev/null || echo "")
    if [ -n "$HOSTNAME" ]; then
        echo "  🖥️  Hostname:"
        echo "     http://$HOSTNAME:8600"
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "📚 Documentation:"
echo "   - Quick Reference: $SCRIPT_DIR/QUICKREF.md"
echo "   - Deployment Guide: $SCRIPT_DIR/DEPLOYMENT.md"
echo "   - Configuration: $SCRIPT_DIR/config.sh"
echo ""
echo "🎉 Installation complete!"
echo "==========================================================🧬"
