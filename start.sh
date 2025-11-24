#!/usr/bin/env bash
set -e

echo "🧬=========================================================="
echo "       Starting Genestack Intelligence Suite Dashboard"
echo "==========================================================🧬"

ROOT="$(cd "$(dirname "$0")" && pwd)"
INTEL="$ROOT/genestack-intelligence"
SCREENSHOT="$ROOT/docs/assets/intel_dashboard_preview.png"
SCREENSHOT_TOP_FILES="$ROOT/docs/assets/intel_dashboard_top_files.png"
README_PATH="$ROOT/README.md"

SERVER_IP="203.60.1.117"
PORT=8600

ensure_playwright() {
    if ! python3 -c "import playwright" >/dev/null 2>&1; then
        pip3 install --quiet playwright
    fi
    python3 -m playwright install chromium >/dev/null 2>&1 || true
}

update_readme_preview() {
    local cache_bust
    cache_bust="$(date -u +"%Y%m%dT%H%M%SZ")"
    local rel_overview="docs/assets/intel_dashboard_preview.png?ts=$cache_bust"
    local rel_top_files="docs/assets/intel_dashboard_top_files.png?ts=$cache_bust"
    python3 - "$README_PATH" "$rel_overview" "$rel_top_files" <<'PY'
import sys

readme_path = sys.argv[1]
overview_image = sys.argv[2]
top_files_image = sys.argv[3]
start = "<!-- INTELLIGENCE_DASHBOARD_START -->"
end = "<!-- INTELLIGENCE_DASHBOARD_END -->"

with open(readme_path, encoding="utf-8") as fh:
    content = fh.read()

replacement = (
    f"{start}\n"
    f'<p align="center">\n'
    f'  <strong>Dashboard Overview & KPI Snapshot</strong><br>\n'
    f'  <img src="{overview_image}" alt="Genestack Intelligence Dashboard Overview" width="100%">\n'
    f"</p>\n"
    f'<p align="center">\n'
    f'  <strong>Top 10 Modified Files per Branch</strong><br>\n'
    f'  <img src="{top_files_image}" alt="Top 10 Modified Files per Branch" width="100%">\n'
    f"</p>\n"
    f"{end}"
)

if start not in content or end not in content:
    sys.exit("Marker block missing in README.md")

pre, _, rest = content.partition(start)
_, _, post = rest.partition(end)
updated = pre + replacement + post

with open(readme_path, "w", encoding="utf-8") as fh:
    fh.write(updated)
PY
}

publish_preview_commit() {
    git -C "$ROOT" add "$SCREENSHOT" "$SCREENSHOT_TOP_FILES" "$README_PATH" || true
    if git -C "$ROOT" diff --cached --quiet; then
        echo "🧾 README already up to date with latest screenshot."
        return
    fi
    git -C "$ROOT" commit -m "chore: update intelligence dashboard preview" || true
    git -C "$ROOT" push || true
}

capture_dashboard_preview_async() {
    (
        echo "📸 Scheduling dashboard preview capture after UI launch..."
        ensure_playwright
        local max_wait=${PREVIEW_TIMEOUT_SECONDS:-60}
        local elapsed=0
        until curl -fsS "http://127.0.0.1:$PORT/_stcore/health" >/dev/null 2>&1; do
            if [ "$elapsed" -ge "$max_wait" ]; then
                echo "⚠️ Dashboard did not become ready within ${max_wait}s — skipping capture."
                exit 0
            fi
            sleep 2
            elapsed=$((elapsed + 2))
        done
        sleep "${PREVIEW_STABILIZE_SECONDS:-15}"
        local capture_failed=0
        if ! python3 "$INTEL/dashboard/capture_dashboard.py" \
            --url "http://127.0.0.1:$PORT" \
            --output "$SCREENSHOT" \
            --wait 60 \
            --full-page; then
            capture_failed=1
        fi
        if ! python3 "$INTEL/dashboard/capture_dashboard.py" \
            --url "http://127.0.0.1:$PORT" \
            --output "$SCREENSHOT_TOP_FILES" \
            --wait 60 \
            --scroll-text "Top 10 Modified Files per Branch"; then
            capture_failed=1
        fi
        if [ "$capture_failed" -eq 0 ]; then
            update_readme_preview
            publish_preview_commit
        else
            echo "⚠️ Failed to capture dashboard screenshots."
        fi
    ) &
}

echo "📁 Working directory: $ROOT"
echo "📦 Activating virtual environment..."
source "$INTEL/.venv/bin/activate"

echo "🧠 Generating latest intelligence reports..."
python3 "$INTEL/drift/detect_drift.py"
python3 "$INTEL/heatmap/contributor_heatmap.py"

echo "📨 Sending notifications (Slack + Teams if configured)..."
python3 "$INTEL/notify/slack_notify.py" || true
python3 "$INTEL/notify/teams_notify.py" || true

echo ""
echo "🌐 Launching dashboard..."
echo "You can connect using ANY of these:"
echo "  ▶ http://localhost:$PORT"
echo "  ▶ http://$SERVER_IP:$PORT"
echo "  ▶ http://$(hostname -I | awk '{print $1}'):$PORT"
echo ""

capture_dashboard_preview_async

streamlit run "$INTEL/dashboard/app.py" \
    --server.port=$PORT \
    --server.address=0.0.0.0

echo "==============================================================="
