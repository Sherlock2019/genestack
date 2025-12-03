#!/usr/bin/env bash
# Genestack Intelligence Suite - Quick Start Script
# One-command setup and launch

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🧬=========================================================="
echo "       Genestack Intelligence Suite - Quick Start"
echo "==========================================================🧬"
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "📦 Virtual environment not found. Running setup..."
    echo ""
    "$SCRIPT_DIR/setup.sh"
    echo ""
else
    echo "✅ Virtual environment found"
    echo ""
fi

# Start the dashboard
echo "🚀 Starting dashboard..."
echo ""
cd "$ROOT_DIR"
exec "$ROOT_DIR/start.sh"
