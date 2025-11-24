#!/usr/bin/env bash
set -euo pipefail

echo "📦 Installing Genestack Intelligence Agent (minimal)..."

REPO_ROOT="$(pwd)"
mkdir -p "$REPO_ROOT/genestack-intelligence/scripts"
mkdir -p "$REPO_ROOT/reports"
mkdir -p "$REPO_ROOT/docs"

cat << 'EOF' > "$REPO_ROOT/genestack-intelligence/scripts/genestack_insights.py"
#!/usr/bin/env python3
import json, datetime, requests
from pathlib import Path

REPO="rackerlabs/genestack"
OUT=Path("reports")/datetime.datetime.now().strftime("%Y-%m-%d")
OUT.mkdir(parents=True, exist_ok=True)

def fetch(endpoint):
    return requests.get(f"https://api.github.com/repos/{REPO}/{endpoint}").json()

def main():
    c = fetch("contributors")
    b = fetch("branches")
    md = "# Genestack Insights\n\n"
    md += "## Contributors\n" + "\n".join([f"- {x['login']}" for x in c[:10]])
    md += "\n\n## Branches\n" + "\n".join([f"- {x['name']}" for x in b[:10]])

    (OUT/"insights.md").write_text(md)
    Path("docs/community-insights.md").write_text(md)

if __name__ == "__main__":
    main()
EOF

chmod +x "$REPO_ROOT/genestack-intelligence/scripts/genestack_insights.py"

echo "⚙️ Running once..."
python3 genestack-intelligence/scripts/genestack_insights.py

echo "✅ Done!"
