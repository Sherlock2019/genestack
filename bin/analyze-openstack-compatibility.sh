#!/bin/bash
# Analyze OpenStack component compatibility

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPAT_SCRIPT="$REPO_ROOT/genestack-intelligence/openstack_compatibility.py"

if [ ! -f "$COMPAT_SCRIPT" ]; then
    echo "Error: openstack_compatibility.py not found at $COMPAT_SCRIPT"
    exit 1
fi

echo "🔍 Analyzing OpenStack Component Compatibility..."
echo "Repository: $REPO_ROOT"
echo ""

cd "$REPO_ROOT"

# Run the compatibility analyzer
python3 "$COMPAT_SCRIPT" --repo-path "$REPO_ROOT"

echo ""
echo "✅ Compatibility analysis complete!"
echo "📊 View the reports in: reports/$(date +%Y-%m-%d)/"
