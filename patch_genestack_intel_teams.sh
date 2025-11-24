#!/usr/bin/env bash
set -e

echo "🛠 Applying Teams Notification Patch..."
ROOT="$(pwd)"
INTEL="$ROOT/genestack-intelligence"
NOTIFY="$INTEL/notify"

mkdir -p "$NOTIFY"

###############################################
# 1. Install Teams notification module
###############################################
echo "📦 Installing Teams notifier..."
cat << 'PYEOF' > "$NOTIFY/teams_notify.py"
#!/usr/bin/env python3
import os
import datetime
import requests

today = datetime.datetime.now().strftime("%Y-%m-%d")
webhook = os.getenv("TEAMS_WEBHOOK_URL")

if not webhook:
    print("⚠️ No Microsoft Teams webhook set. Skipping...")
    exit(0)

msg = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "Genestack Intelligence Update",
    "themeColor": "0076D7",
    "title": f"🧬 Genestack Intelligence Report — {today}",
    "text": (
        f"✔ Drift report generated\n"
        f"✔ Contributor heatmap updated\n"
        f"✔ All intelligence modules executed\n\n"
        f"📁 Location: `reports/{today}`"
    )
}

response = requests.post(webhook, json=msg)
if response.status_code not in (200, 204):
    print("❌ Error sending Teams notification:", response.text)
else:
    print("📨 Teams notification sent.")
PYEOF

chmod +x "$NOTIFY/teams_notify.py"


###############################################
# 2. Update local_run_all.sh to include Teams
###############################################
echo "🔧 Updating local_run_all.sh..."
cat << 'EOF2' > "$ROOT/local_run_all.sh"
#!/usr/bin/env bash
set -e
echo "🧠 Running full Genestack Intelligence Suite..."

source genestack-intelligence/.venv/bin/activate

python3 genestack-intelligence/drift/detect_drift.py
python3 genestack-intelligence/heatmap/contributor_heatmap.py

# Notifications
python3 genestack-intelligence/notify/slack_notify.py || true
python3 genestack-intelligence/notify/teams_notify.py || true

echo "✅ Reports generated in reports/"
EOF2

chmod +x "$ROOT/local_run_all.sh"


###############################################
# 3. Update GitHub Actions workflow
###############################################
echo "🌀 Updating GitHub Actions workflow..."

mkdir -p "$ROOT/.github/workflows"

cat << 'YEOF' > "$ROOT/.github/workflows/genestack-intel-suite.yml"
name: Genestack Intelligence Suite

on:
  push:
  pull_request:
  schedule:
    - cron: "0 2 * * *"

jobs:
  intel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"

      - name: Install dependencies
        run: pip install matplotlib pandas streamlit slack_sdk requests

      - name: Run intelligence suite
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          TEAMS_WEBHOOK_URL: ${{ secrets.TEAMS_WEBHOOK_URL }}
        run: |
          python3 genestack-intelligence/drift/detect_drift.py
          python3 genestack-intelligence/heatmap/contributor_heatmap.py
          python3 genestack-intelligence/notify/slack_notify.py || true
          python3 genestack-intelligence/notify/teams_notify.py || true
YEOF

echo "🎉 Patch complete!"
echo "➡ Run: ./local_run_all.sh"
echo "➡ GitHub Actions will send Slack + Teams notifications automatically."
