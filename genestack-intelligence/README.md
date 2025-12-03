# 🧬 Genestack Intelligence Suite

A comprehensive dashboard and analytics suite for monitoring **ANY Git repository** - analyze contributors, track drift, and visualize repository health.

## 🎯 NEW: Universal Repository Scanner

**Analyze ANY Git repository in seconds!** Just enter a URL and get instant insights:
- `https://github.com/kubernetes/kubernetes`
- `https://github.com/facebook/react`
- `https://github.com/openstack/nova`
- Or any public/private repo you have access to!

## ✨ Features

- **🔗 Universal Repo Scanner** - Analyze ANY Git repository by URL
- **📊 Interactive Dashboard** - Real-time visualization of contributors and metrics
- **🏆 Top Contributors** - Gold, Silver, Bronze medals with detailed breakdowns
- **🔍 Drift Detection** - Automatically detect configuration drift
- **🗺️ Contributor Heatmap** - Visualize code contribution patterns
- **📈 Repository Health Metrics** - Track activity and health gauges
- **📁 File Change Tracking** - Most modified files with risk analysis
- **🌿 Branch Analysis** - Commit counts, updated files, recent changes
- **🔔 Notifications** - Slack and Microsoft Teams integration
- **📸 Automated Screenshots** - Capture dashboard previews automatically

## 🚀 Quick Start

### 1. Setup (First Time Only)

```bash
cd genestack-intelligence
./setup.sh
```

This creates a virtual environment and installs all dependencies.

### 2. Start the Dashboard

```bash
cd ..
./start.sh
```

The dashboard will be available at `http://localhost:8600`

### 3. Analyze Any Repository

1. Open the dashboard in your browser
2. At the top, enter any Git repository URL:
   ```
   https://github.com/kubernetes/kubernetes
   ```
3. Click **"🔍 Analyze This Repo"**
4. Wait for the repo to clone (10-60 seconds)
5. See instant insights! 🎉

**That's it!** No configuration needed. Works with any public or private Git repository.

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Complete deployment instructions for any server
- **[Configuration Guide](DEPLOYMENT.md#configuration)** - Customize settings
- **[Troubleshooting](DEPLOYMENT.md#troubleshooting)** - Common issues and solutions

## 🔧 Configuration

Edit `config.sh` to customize:

```bash
# Change port
PORT=9000

# Disable screenshots
ENABLE_SCREENSHOTS="false"

# Enable notifications
ENABLE_SLACK="true"
ENABLE_TEAMS="true"
```

Or use environment variables:

```bash
export GENESTACK_PORT=9000
./start.sh
```

## 📦 Components

### Dashboard (`dashboard/`)
- `app.py` - Main Streamlit dashboard application
- `repo_health_metrics.py` - Repository health calculations
- `bmw_repo_health_gauges.py` - Health gauge visualizations
- `capture_dashboard.py` - Screenshot capture utility
- `theme_manager.py` - Theme management

### Drift Detection (`drift/`)
- `detect_drift.py` - Configuration drift detection

### Heatmap (`heatmap/`)
- `contributor_heatmap.py` - Contributor activity heatmap generation

### Notifications (`notify/`)
- `slack_notify.py` - Slack notification integration
- `teams_notify.py` - Microsoft Teams notification integration

### Version Management
- `version_inventory.py` - OpenStack version inventory
- `openstack_version_resolver.py` - Version resolution logic
- `openstack_github_version_resolver.py` - GitHub-based version resolution
- `openstack_compatibility.py` - Compatibility analysis
- `openstack_repo_scanner.py` - Repository scanning

## 🌐 Server Deployment

The suite is fully server-agnostic and can be deployed anywhere:

### Manual Background Mode

```bash
nohup ./start.sh > dashboard.log 2>&1 &
```

### systemd Service (Recommended)

See [DEPLOYMENT.md](DEPLOYMENT.md#using-systemd-recommended-for-production) for complete instructions.

### Docker (Coming Soon)

```bash
docker-compose up -d
```

## 🔐 Security

For production deployments:

1. **Use a reverse proxy** (nginx/Apache) with SSL
2. **Configure firewall** to restrict access
3. **Enable authentication** via reverse proxy
4. **Use VPN or SSH tunneling** for remote access

See [Production Deployment](DEPLOYMENT.md#production-deployment) for details.

## 🐛 Troubleshooting

### Virtual Environment Not Found

```bash
cd genestack-intelligence
./setup.sh
```

### Port Already in Use

Change port in `config.sh` or:

```bash
export GENESTACK_PORT=8601
./start.sh
```

### More Issues?

See the [Troubleshooting Guide](DEPLOYMENT.md#troubleshooting)

## 📊 Dashboard Access

Once running, access the dashboard at:

- **Localhost:** `http://localhost:8600`
- **Network:** `http://<server-ip>:8600`
- **Hostname:** `http://<hostname>:8600`

All available URLs are displayed when starting the dashboard.

## 🔔 Notifications Setup

### Slack

1. Create a Slack webhook URL
2. Set environment variable:
   ```bash
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   ```
3. Enable in `config.sh`:
   ```bash
   ENABLE_SLACK="true"
   ```

### Microsoft Teams

1. Create a Teams webhook URL
2. Set environment variable:
   ```bash
   export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/YOUR/WEBHOOK/URL"
   ```
3. Enable in `config.sh`:
   ```bash
   ENABLE_TEAMS="true"
   ```

## 📝 Requirements

- Python 3.8+
- Git
- Network access for external connections
- Chromium (optional, for screenshots - installed automatically)

## 🛠️ Development

### Install in Development Mode

```bash
cd genestack-intelligence
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Components Individually

```bash
# Drift detection
python3 drift/detect_drift.py

# Heatmap generation
python3 heatmap/contributor_heatmap.py

# Dashboard only
streamlit run dashboard/app.py --server.port=8600
```

## 📄 License

See main repository LICENSE file.

## 🤝 Contributing

Contributions are welcome! Please follow the main repository's contribution guidelines.

## 📞 Support

For issues or questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md)
2. Review logs
3. Open an issue in the repository

---

**Made with ❤️ for the Genestack community**
