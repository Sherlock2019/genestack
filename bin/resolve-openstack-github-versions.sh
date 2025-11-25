#!/bin/bash
# Resolve OpenStack component versions from GitHub API

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESOLVER_SCRIPT="$REPO_ROOT/genestack-intelligence/openstack_github_version_resolver.py"

if [ ! -f "$RESOLVER_SCRIPT" ]; then
    echo "Error: openstack_github_version_resolver.py not found at $RESOLVER_SCRIPT"
    exit 1
fi

echo "🔗 Resolving OpenStack Component Versions from GitHub..."
echo "Repository: $REPO_ROOT"
echo ""
echo "ℹ️  Using public GitHub API (no authentication required)"
echo "   Rate limit: 60 requests/hour. This may take a few minutes for many components."
echo ""

cd "$REPO_ROOT"

# Run the resolver (no token - uses public API)
python3 "$RESOLVER_SCRIPT" --repo-path "$REPO_ROOT"

echo ""
echo "✅ GitHub version resolution complete!"
echo "📊 View the reports in: reports/$(date +%Y-%m-%d)/"
