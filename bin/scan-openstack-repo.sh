#!/bin/bash
# Scan repository for OpenStack component versions (repository-only, no CLI)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCANNER_SCRIPT="$REPO_ROOT/genestack-intelligence/openstack_repo_scanner.py"

if [ ! -f "$SCANNER_SCRIPT" ]; then
    echo "Error: openstack_repo_scanner.py not found at $SCANNER_SCRIPT"
    exit 1
fi

echo "🔍 Scanning Repository for OpenStack Component Versions..."
echo "Repository: $REPO_ROOT"
echo "Mode: Repository-only (NO CLI commands)"
echo ""

cd "$REPO_ROOT"

# Run the scanner
if [ "$1" == "--scrape" ]; then
    echo "Including OpenStack release data scraping..."
    python3 "$SCANNER_SCRIPT" --repo-path "$REPO_ROOT" --scrape
else
    python3 "$SCANNER_SCRIPT" --repo-path "$REPO_ROOT"
fi

echo ""
echo "✅ Repository scan complete!"
echo "📊 View the reports in: reports/$(date +%Y-%m-%d)/"
echo ""
echo "Generated files:"
echo "  - openstack_repo_inventory.json"
echo "  - openstack_repo_inventory.md"
echo "  - openstack_repo_compatibility.csv"
echo "  - openstack_recommended_stack.json"
