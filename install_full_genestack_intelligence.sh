#!/usr/bin/env bash
set -e

echo "🧬=========================================================="
echo "     Installing FULL Genestack Intelligence Suite"
echo "==========================================================🧬"

ROOT="$(pwd)"
INTEL="$ROOT/genestack-intelligence"

echo "📁 Repo: $ROOT"
echo "📁 Intelligence folder: $INTEL"
echo ""

echo "📦 Installing dependencies..."
apt update -y
apt install -y python3 python3-pip python3-venv graphviz curl git

echo "🐍 Creating venv..."
python3 -m venv "$INTEL/.venv"
source "$INTEL/.venv/bin/activate"
pip install --upgrade pip
pip install streamlit matplotlib seaborn pandas requests pyyaml python-dateutil slack_sdk msal

echo "📁 Creating directory structure..."
mkdir -p "$INTEL/drift" \
         "$INTEL/heatmap" \
         "$INTEL/dashboard" \
         "$INTEL/notify" \
         "$ROOT/reports"

##############################################
# DRIFT MODULE
##############################################
cat << 'PYEOF' > "$INTEL/drift/detect_drift.py"
#!/usr/bin/env python3
import subprocess, os, datetime, json

today = datetime.datetime.now().strftime("%Y-%m-%d")
report_dir = f"reports/{today}"
os.makedirs(report_dir, exist_ok=True)

def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True)

def write(path, content):
    with open(path, "w") as f: f.write(content)

# Helm Drift
helm_expected = run("helm template . || true")
live_helm = run("kubectl get all -o yaml || true")
write(f"{report_dir}/helm_expected.yaml", helm_expected)
write(f"{report_dir}/helm_live.yaml", live_helm)

# Kustomize Drift
kustom_expected = run("kubectl kustomize base-kustomize/overlays/production || true")
live_kustom = run("kubectl get all -o yaml || true")

write(f"{report_dir}/kustom_expected.yaml", kustom_expected)
write(f"{report_dir}/kustom_live.yaml", live_kustom)

summary = f"""
# Drift Report ({today})

## Helm Drift:
Expected vs Live rendered into:
- helm_expected.yaml
- helm_live.yaml

## Kustomize Drift:
Expected vs Live:
- kustom_expected.yaml
- kustom_live.yaml
"""

write(f"{report_dir}/drift-report.md", summary)
print("✅ Drift detection complete.")
PYEOF

##############################################
# HEATMAP MODULE
##############################################
cat << 'PYEOF' > "$INTEL/heatmap/contributor_heatmap.py"
#!/usr/bin/env python3
import subprocess, os, datetime, matplotlib.pyplot as plt
import pandas as pd

today = datetime.datetime.now().strftime("%Y-%m-%d")
outdir = f"reports/{today}"
os.makedirs(outdir, exist_ok=True)

def run(cmd): return subprocess.check_output(cmd, shell=True, text=True)

log = run("git shortlog -sn")

data = []
for line in log.splitlines():
    count, name = line.strip().split("\t")
    data.append((name, int(count)))

df = pd.DataFrame(data, columns=["name", "commits"])

plt.figure(figsize=(10,6))
plt.barh(df["name"], df["commits"])
plt.title("Genestack Contributor Heatmap")
plt.tight_layout()
plt.savefig(f"{outdir}/heatmap.png")

with open(f"{outdir}/heatmap.md", "w") as f:
    f.write(df.to_markdown())

print("✅ Heatmap generated.")
PYEOF

##############################################
# STREAMLIT DASHBOARD
##############################################
cat << 'PYEOF' > "$INTEL/dashboard/app.py"
import streamlit as st
import os, glob
from datetime import datetime

st.title("🧬 Genestack Intelligence Dashboard")

reports = sorted(glob.glob("reports/*"), reverse=True)

if not reports:
    st.warning("No reports yet. Run './local_run_all.sh'")
    st.stop()

latest = reports[0]
st.subheader(f"Latest Report: {os.path.basename(latest)}")

if os.path.exists(f"{latest}/drift-report.md"):
    st.markdown("## Drift Report")
    st.code(open(f"{latest}/drift-report.md").read())

if os.path.exists(f"{latest}/heatmap.md"):
    st.markdown("## Contributor Heatmap")
    st.image(f"{latest}/heatmap.png")
PYEOF

##############################################
# NOTIFICATION MODULE
##############################################
cat << 'PYEOF' > "$INTEL/notify/slack_notify.py"
from slack_sdk.webhook import WebhookClient
import os, datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")
hook = os.getenv("SLACK_WEBHOOK_URL")

if not hook:
    print("⚠️ No Slack webhook set. Skipping...")
    exit(0)

webhook = WebhookClient(hook)
webhook.send(text=f"Genestack Intelligence update for {today} is ready.")

print("✅ Slack notification sent.")
PYEOF

##############################################
# LOCAL RUN-ALL SCRIPT
##############################################
cat << 'EOF2' > "$ROOT/local_run_all.sh"
#!/usr/bin/env bash
set -e
echo "🧠 Running full Genestack Intelligence Suite..."

source genestack-intelligence/.venv/bin/activate

python3 genestack-intelligence/drift/detect_drift.py
python3 genestack-intelligence/heatmap/contributor_heatmap.py
python3 genestack-intelligence/notify/slack_notify.py || true

echo "✅ Reports generated in reports/"
EOF2

chmod +x "$ROOT/local_run_all.sh"

##############################################
# GITHUB ACTION
##############################################
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
        run: pip install matplotlib pandas streamlit slack_sdk
      - name: Run intelligence suite
        run: |
          python3 genestack-intelligence/drift/detect_drift.py
          python3 genestack-intelligence/heatmap/contributor_heatmap.py
YEOF

echo "🎉 Installation complete!"
echo "➡ Run manually: ./local_run_all.sh"
echo "➡ Dashboard: streamlit run genestack-intelligence/dashboard/app.py"
