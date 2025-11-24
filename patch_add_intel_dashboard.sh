#!/usr/bin/env bash
set -e

echo "🛠 Patching README.md with Genestack Intelligence Dashboard section..."

README="README.md"
ASSETS="docs/assets"
PREVIEW="$ASSETS/intel_dashboard_preview.png"

# --- Ensure assets directory exists ---
mkdir -p "$ASSETS"

# --- Create a placeholder preview image if ImageMagick exists ---
if command -v convert >/dev/null 2>&1; then
    convert -size 1200x600 xc:"#0E1117" \
        -gravity center \
        -fill "#01C3FF" \
        -pointsize 48 \
        -annotate 0 "Genestack Intelligence Dashboard\nPreview Placeholder" \
        "$PREVIEW"
else
    echo "⚠️ ImageMagick not installed — skipping preview image generation."
    # Create simple text placeholder instead
    echo "[Dashboard Preview Placeholder]" > "$PREVIEW"
fi

# Temporary file for insertion block
TMPBLOCK="$(mktemp)"

cat << 'EOF' > "$TMPBLOCK"
## 🧬 Genestack Intelligence Dashboard — Repository Analytics (NEW)

The **Genestack Intelligence Dashboard** provides real-time engineering analytics,
repository health metrics, drift detection, release-cycle insights, and developer
productivity patterns.

![Genestack Intelligence Dashboard](docs/assets/intel_dashboard_preview.png)

### 🔥 What It Provides
- Contributor heatmaps
- Branch intelligence
- PR insights
- File volatility
- Helm/Kustomize drift detection
- AI risk recommendations
- Slack + Teams notifications
- One-click Streamlit UI

Run:
