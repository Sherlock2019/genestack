#!/usr/bin/env bash
# Genestack Intelligence Suite - Configuration
# Edit this file to customize settings for your server

# ============================================================
# Server Configuration
# ============================================================

# Port to run the dashboard on
# Default: 8600
PORT="${GENESTACK_PORT:-8600}"

# Server address to bind to
# Use 0.0.0.0 to allow external connections
# Use 127.0.0.1 for localhost only
# Default: 0.0.0.0
SERVER_ADDRESS="${GENESTACK_ADDRESS:-0.0.0.0}"

# ============================================================
# Screenshot Configuration
# ============================================================

# Enable automatic dashboard screenshot capture
# Set to "true" to enable, "false" to disable
# Default: true
ENABLE_SCREENSHOTS="${GENESTACK_SCREENSHOTS:-true}"

# Timeout for dashboard to become ready (seconds)
# Default: 60
PREVIEW_TIMEOUT_SECONDS="${GENESTACK_PREVIEW_TIMEOUT:-60}"

# Wait time for UI to stabilize before capture (seconds)
# Default: 15
PREVIEW_STABILIZE_SECONDS="${GENESTACK_PREVIEW_STABILIZE:-15}"

# ============================================================
# Notification Configuration
# ============================================================

# Enable Slack notifications
# Set to "true" to enable, "false" to disable
# Requires SLACK_WEBHOOK_URL environment variable
# Default: false
ENABLE_SLACK="${GENESTACK_ENABLE_SLACK:-false}"

# Enable Microsoft Teams notifications
# Set to "true" to enable, "false" to disable
# Requires TEAMS_WEBHOOK_URL environment variable
# Default: false
ENABLE_TEAMS="${GENESTACK_ENABLE_TEAMS:-false}"

# ============================================================
# Git Configuration
# ============================================================

# Enable automatic git commits for screenshots
# Set to "true" to enable, "false" to disable
# Default: false (disabled for server deployments)
ENABLE_GIT_COMMITS="${GENESTACK_GIT_COMMITS:-false}"

# ============================================================
# Report Generation
# ============================================================

# Enable drift detection report generation
# Default: true
ENABLE_DRIFT_DETECTION="${GENESTACK_DRIFT:-true}"

# Enable contributor heatmap generation
# Default: true
ENABLE_HEATMAP="${GENESTACK_HEATMAP:-true}"

# ============================================================
# Advanced Configuration
# ============================================================

# Python executable to use
# Default: python3
PYTHON_CMD="${GENESTACK_PYTHON:-python3}"

# Additional Streamlit arguments
# Example: "--server.enableCORS=false --server.enableXsrfProtection=false"
STREAMLIT_ARGS="${GENESTACK_STREAMLIT_ARGS:-}"
