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
