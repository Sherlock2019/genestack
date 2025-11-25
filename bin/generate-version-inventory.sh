#!/bin/bash
# Generate complete version inventory for Genestack

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INVENTORY_SCRIPT="$REPO_ROOT/genestack-intelligence/version_inventory.py"

if [ ! -f "$INVENTORY_SCRIPT" ]; then
    echo "Error: version_inventory.py not found at $INVENTORY_SCRIPT"
    exit 1
fi

echo "🔍 Generating Genestack Component Version Inventory..."
echo "Repository: $REPO_ROOT"
echo ""

cd "$REPO_ROOT"

# Run the inventory scanner
python3 "$INVENTORY_SCRIPT" --repo-path "$REPO_ROOT"

echo ""
echo "✅ Inventory generation complete!"
echo "📊 View the reports in: reports/$(date +%Y-%m-%d)/"
