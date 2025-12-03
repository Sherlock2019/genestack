#!/usr/bin/env bash
# Genestack Intelligence Suite - Start Script
# Server-agnostic launcher for the dashboard

set -e

echo "🧬=========================================================="
echo "       Starting Genestack Intelligence Suite Dashboard"
echo "==========================================================🧬"

# ============================================================
# Path Detection
# ============================================================

ROOT="$(cd "$(dirname "$0")" && pwd)"
INTEL="$ROOT/genestack-intelligence"
VENV="$INTEL/.venv"
CONFIG_FILE="$INTEL/config.sh"

# ============================================================
# Load Configuration
# ============================================================

# Load default configuration if exists
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "⚠️  Warning: config.sh not found, using defaults"
    PORT="${GENESTACK_PORT:-8600}"
    SERVER_ADDRESS="${GENESTACK_ADDRESS:-0.0.0.0}"
    ENABLE_SCREENSHOTS="${GENESTACK_SCREENSHOTS:-false}"
    ENABLE_SLACK="${GENESTACK_ENABLE_SLACK:-false}"
    ENABLE_TEAMS="${GENESTACK_ENABLE_TEAMS:-false}"
    ENABLE_GIT_COMMITS="${GENESTACK_GIT_COMMITS:-false}"
    ENABLE_DRIFT_DETECTION="${GENESTACK_DRIFT:-true}"
    ENABLE_HEATMAP="${GENESTACK_HEATMAP:-true}"
    PYTHON_CMD="${GENESTACK_PYTHON:-python3}"
    STREAMLIT_ARGS="${GENESTACK_STREAMLIT_ARGS:-}"
fi

# ============================================================
# Environment Check
# ============================================================

echo "📁 Working directory: $ROOT"

# Check if virtual environment exists
if [ ! -d "$VENV" ]; then
    echo ""
    echo "❌ Virtual environment not found at: $VENV"
    echo ""
    echo "Please run the setup script first:"
    echo "   cd $INTEL"
    echo "   ./setup.sh"
    echo ""
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$VENV/bin/activate"

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found in virtual environment"
    exit 1
fi

# ============================================================
# Server Detection
# ============================================================

echo "🔍 Detecting server configuration..."

# Get primary IP address
PRIMARY_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "unknown")

# Get hostname
HOSTNAME=$(hostname 2>/dev/null || echo "unknown")

# Get all network interfaces (for display)
ALL_IPS=$(hostname -I 2>/dev/null | tr ' ' '\n' | grep -v '^$' || echo "")

echo "   Hostname: $HOSTNAME"
echo "   Primary IP: $PRIMARY_IP"

# ============================================================
# Report Generation
# ============================================================

if [ "$ENABLE_DRIFT_DETECTION" = "true" ]; then
    echo ""
    echo "🔍 Generating drift detection report..."
    if [ -f "$INTEL/drift/detect_drift.py" ]; then
        python3 "$INTEL/drift/detect_drift.py" || echo "⚠️  Drift detection failed"
    else
        echo "⚠️  Drift detection script not found"
    fi
fi

if [ "$ENABLE_HEATMAP" = "true" ]; then
    echo ""
    echo "🗺️  Generating contributor heatmap..."
    if [ -f "$INTEL/heatmap/contributor_heatmap.py" ]; then
        python3 "$INTEL/heatmap/contributor_heatmap.py" || echo "⚠️  Heatmap generation failed"
    else
        echo "⚠️  Heatmap script not found"
    fi
fi

# ============================================================
# Notifications
# ============================================================

if [ "$ENABLE_SLACK" = "true" ]; then
    echo ""
    echo "📨 Sending Slack notification..."
    if [ -f "$INTEL/notify/slack_notify.py" ]; then
        python3 "$INTEL/notify/slack_notify.py" || echo "⚠️  Slack notification failed"
    else
        echo "⚠️  Slack notification script not found"
    fi
fi

if [ "$ENABLE_TEAMS" = "true" ]; then
    echo ""
    echo "📨 Sending Teams notification..."
    if [ -f "$INTEL/notify/teams_notify.py" ]; then
        python3 "$INTEL/notify/teams_notify.py" || echo "⚠️  Teams notification failed"
    else
        echo "⚠️  Teams notification script not found"
    fi
fi

# ============================================================
# Screenshot Capture (Background)
# ============================================================

capture_dashboard_preview_async() {
    (
        echo "📸 Scheduling dashboard preview capture after UI launch..."
        
        # Ensure playwright is installed
        if ! python3 -c "import playwright" >/dev/null 2>&1; then
            echo "⚠️  Playwright not installed, skipping screenshot capture"
            return
        fi
        
        python3 -m playwright install chromium >/dev/null 2>&1 || true
        
        local max_wait=${PREVIEW_TIMEOUT_SECONDS:-60}
        local elapsed=0
        
        # Wait for dashboard to be ready
        until curl -fsS "http://127.0.0.1:$PORT/_stcore/health" >/dev/null 2>&1; do
            if [ "$elapsed" -ge "$max_wait" ]; then
                echo "⚠️  Dashboard did not become ready within ${max_wait}s — skipping capture."
                exit 0
            fi
            sleep 2
            elapsed=$((elapsed + 2))
        done
        
        # Wait for UI to stabilize
        sleep "${PREVIEW_STABILIZE_SECONDS:-15}"
        
        # Capture screenshots
        local capture_failed=0
        local screenshot_dir="$ROOT/docs/assets"
        
        mkdir -p "$screenshot_dir"
        
        if [ -f "$INTEL/dashboard/capture_dashboard.py" ]; then
            # Full page screenshot
            if ! python3 "$INTEL/dashboard/capture_dashboard.py" \
                --url "http://127.0.0.1:$PORT" \
                --output "$screenshot_dir/intel_dashboard_preview.png" \
                --wait 60 \
                --full-page; then
                capture_failed=1
            fi
            
            # Top files screenshot
            if ! python3 "$INTEL/dashboard/capture_dashboard.py" \
                --url "http://127.0.0.1:$PORT" \
                --output "$screenshot_dir/intel_dashboard_top_files.png" \
                --wait 60 \
                --scroll-text "Top 10 Modified Files per Branch"; then
                capture_failed=1
            fi
            
            if [ "$capture_failed" -eq 0 ]; then
                echo "✅ Dashboard screenshots captured successfully"
                
                # Update README if git commits are enabled
                if [ "$ENABLE_GIT_COMMITS" = "true" ]; then
                    echo "📝 Updating README with new screenshots..."
                    update_readme_preview
                    publish_preview_commit
                fi
            else
                echo "⚠️  Failed to capture dashboard screenshots."
            fi
        else
            echo "⚠️  Screenshot capture script not found"
        fi
    ) &
}

update_readme_preview() {
    local cache_bust
    cache_bust="$(date -u +"%Y%m%dT%H%M%SZ")"
    local rel_overview="docs/assets/intel_dashboard_preview.png?ts=$cache_bust"
    local rel_top_files="docs/assets/intel_dashboard_top_files.png?ts=$cache_bust"
    local readme_path="$ROOT/README.md"
    
    if [ ! -f "$readme_path" ]; then
        echo "⚠️  README.md not found, skipping update"
        return
    fi
    
    python3 - "$readme_path" "$rel_overview" "$rel_top_files" <<'PY'
import sys

readme_path = sys.argv[1]
overview_image = sys.argv[2]
top_files_image = sys.argv[3]
start = "<!-- INTELLIGENCE_DASHBOARD_START -->"
end = "<!-- INTELLIGENCE_DASHBOARD_END -->"

try:
    with open(readme_path, encoding="utf-8") as fh:
        content = fh.read()
except FileNotFoundError:
    sys.exit(0)

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
    sys.exit(0)

pre, _, rest = content.partition(start)
_, _, post = rest.partition(end)
updated = pre + replacement + post

with open(readme_path, "w", encoding="utf-8") as fh:
    fh.write(updated)
PY
}

publish_preview_commit() {
    local screenshot_dir="$ROOT/docs/assets"
    local readme_path="$ROOT/README.md"
    
    git -C "$ROOT" add "$screenshot_dir/intel_dashboard_preview.png" \
                        "$screenshot_dir/intel_dashboard_top_files.png" \
                        "$readme_path" 2>/dev/null || true
    
    if git -C "$ROOT" diff --cached --quiet 2>/dev/null; then
        echo "🧾 README already up to date with latest screenshot."
        return
    fi
    
    git -C "$ROOT" commit -m "chore: update intelligence dashboard preview" 2>/dev/null || true
    git -C "$ROOT" push 2>/dev/null || true
}

# Start screenshot capture if enabled
if [ "$ENABLE_SCREENSHOTS" = "true" ]; then
    capture_dashboard_preview_async
fi

# ============================================================
# Kill Processes on Ports
# ============================================================

echo ""
echo "🔍 Checking for processes on port $PORT..."

# Find and kill any process using the port
PORT_PID=$(lsof -ti:$PORT 2>/dev/null || true)

if [ -n "$PORT_PID" ]; then
    echo "🛑 Found process on port $PORT (PID: $PORT_PID)"
    echo "   Killing process..."
    kill -9 $PORT_PID 2>/dev/null || true
    sleep 1
    echo "✅ Port $PORT cleared"
else
    echo "✅ Port $PORT is available"
fi

# ============================================================
# Launch Dashboard
# ============================================================

echo ""
echo "🌐 Launching dashboard..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Dashboard Access URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Display localhost URL
echo "  📍 Localhost:"
echo "     http://localhost:$PORT"
echo ""

# Display all available IPs
if [ -n "$ALL_IPS" ]; then
    echo "  🌐 Network Access:"
    while IFS= read -r ip; do
        [ -n "$ip" ] && echo "     http://$ip:$PORT"
    done <<< "$ALL_IPS"
    echo ""
fi

# Display hostname URL
if [ "$HOSTNAME" != "unknown" ]; then
    echo "  🖥️  Hostname:"
    echo "     http://$HOSTNAME:$PORT"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Launch Streamlit
streamlit run "$INTEL/dashboard/app.py" \
    --server.port="$PORT" \
    --server.address="$SERVER_ADDRESS" \
    $STREAMLIT_ARGS

echo ""
echo "🧬=========================================================="
echo "       Dashboard stopped"
echo "==========================================================🧬"
