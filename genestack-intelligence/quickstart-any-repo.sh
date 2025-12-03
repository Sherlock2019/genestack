#!/usr/bin/env bash
# Quick start script to analyze any Git repository

set -e

echo "🧬 Genestack Intelligence - Universal Repo Analyzer"
echo "===================================================="
echo ""
echo "This dashboard can analyze ANY Git repository!"
echo ""
echo "Examples you can try:"
echo "  • https://github.com/kubernetes/kubernetes"
echo "  • https://github.com/facebook/react"
echo "  • https://github.com/torvalds/linux"
echo "  • https://github.com/openstack/nova"
echo ""
echo "Starting dashboard..."
echo ""

# Get to the right directory
cd "$(dirname "$0")/.."

# Run the start script
./start.sh
