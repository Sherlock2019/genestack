# Genestack Intelligence Suite - Deployment Guide

This guide explains how to deploy the Genestack Intelligence Suite Dashboard on any server.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Running the Dashboard](#running-the-dashboard)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Prerequisites

### Required

- **Python 3.8+** - The dashboard requires Python 3.8 or higher
- **Git** - For cloning the repository and version control
- **Network Access** - Ability to bind to a network port (default: 8600)

### Optional

- **Chromium/Chrome** - For automatic screenshot capture (installed via Playwright)
- **Slack Webhook** - For Slack notifications
- **Teams Webhook** - For Microsoft Teams notifications

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd genestack
```

### 2. Run Setup

```bash
cd genestack-intelligence
./setup.sh
```

This will:
- Check Python version compatibility
- Create a virtual environment
- Install all required dependencies
- Set up Playwright for screenshots

### 3. Start the Dashboard

```bash
cd ..
./start.sh
```

The dashboard will be available at:
- `http://localhost:8600`
- `http://<your-server-ip>:8600`

## Detailed Setup

### Step 1: Verify Python Installation

Check your Python version:

```bash
python3 --version
```

You need Python 3.8 or higher. If not installed:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

**RHEL/CentOS/Rocky:**
```bash
sudo yum install python3 python3-venv python3-pip
```

**Fedora:**
```bash
sudo dnf install python3 python3-venv python3-pip
```

### Step 2: Navigate to Intelligence Directory

```bash
cd /path/to/genestack/genestack-intelligence
```

### Step 3: Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Verify Python version (3.8+)
2. Check for `venv` module
3. Create virtual environment at `.venv/`
4. Install all dependencies from `requirements.txt`
5. Install Playwright browsers for screenshot capture

### Step 4: Configure (Optional)

Edit `config.sh` to customize settings:

```bash
nano config.sh
```

See [Configuration](#configuration) section for details.

## Configuration

The `config.sh` file contains all configurable settings. You can also set these via environment variables.

### Server Settings

```bash
# Port to run on (default: 8600)
PORT=8600

# Bind address (0.0.0.0 = all interfaces, 127.0.0.1 = localhost only)
SERVER_ADDRESS="0.0.0.0"
```

### Screenshot Settings

```bash
# Enable automatic screenshot capture
ENABLE_SCREENSHOTS="true"

# Timeout for dashboard to become ready (seconds)
PREVIEW_TIMEOUT_SECONDS=60

# Wait time for UI to stabilize (seconds)
PREVIEW_STABILIZE_SECONDS=15
```

### Notification Settings

```bash
# Enable Slack notifications (requires SLACK_WEBHOOK_URL env var)
ENABLE_SLACK="false"

# Enable Teams notifications (requires TEAMS_WEBHOOK_URL env var)
ENABLE_TEAMS="false"
```

### Report Generation

```bash
# Enable drift detection
ENABLE_DRIFT_DETECTION="true"

# Enable contributor heatmap
ENABLE_HEATMAP="true"
```

### Git Integration

```bash
# Enable automatic git commits for screenshots
# (Disabled by default for server deployments)
ENABLE_GIT_COMMITS="false"
```

### Environment Variables

You can also set configuration via environment variables:

```bash
export GENESTACK_PORT=9000
export GENESTACK_ADDRESS="127.0.0.1"
export GENESTACK_SCREENSHOTS="false"
./start.sh
```

## Running the Dashboard

### Standard Launch

```bash
cd /path/to/genestack
./start.sh
```

### Background Mode (Production)

To run in the background:

```bash
nohup ./start.sh > dashboard.log 2>&1 &
```

To stop:

```bash
pkill -f "streamlit run"
```

### Using systemd (Recommended for Production)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/genestack-dashboard.service
```

Add the following content:

```ini
[Unit]
Description=Genestack Intelligence Dashboard
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/path/to/genestack
ExecStart=/path/to/genestack/start.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable genestack-dashboard
sudo systemctl start genestack-dashboard
```

Check status:

```bash
sudo systemctl status genestack-dashboard
```

View logs:

```bash
sudo journalctl -u genestack-dashboard -f
```

## Troubleshooting

### Virtual Environment Not Found

**Error:**
```
❌ Virtual environment not found at: /path/to/.venv
```

**Solution:**
```bash
cd genestack-intelligence
./setup.sh
```

### Python Version Too Old

**Error:**
```
❌ Error: Python 3.8 or higher is required
```

**Solution:**
Install a newer Python version or use a Python version manager like `pyenv`:

```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0
pyenv local 3.11.0
```

### Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
Change the port in `config.sh`:

```bash
PORT=8601
```

Or find and kill the process using the port:

```bash
# Find process
sudo lsof -i :8600

# Kill process
sudo kill -9 <PID>
```

### Permission Denied

**Error:**
```
Permission denied: '/path/to/genestack-intelligence/.venv'
```

**Solution:**
Ensure you have write permissions:

```bash
sudo chown -R $USER:$USER /path/to/genestack
```

### Screenshot Capture Fails

**Error:**
```
⚠️ Failed to capture dashboard screenshots
```

**Solution:**
1. Disable screenshots in `config.sh`:
   ```bash
   ENABLE_SCREENSHOTS="false"
   ```

2. Or install Playwright browsers manually:
   ```bash
   source genestack-intelligence/.venv/bin/activate
   python3 -m playwright install chromium
   python3 -m playwright install-deps
   ```

### Dashboard Not Accessible from Network

**Issue:** Dashboard works on localhost but not from other machines.

**Solution:**
1. Check `SERVER_ADDRESS` in `config.sh` is set to `0.0.0.0`
2. Check firewall rules:
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 8600/tcp
   
   # RHEL/CentOS/Rocky
   sudo firewall-cmd --permanent --add-port=8600/tcp
   sudo firewall-cmd --reload
   ```

## Production Deployment

### Security Considerations

1. **Firewall Configuration**
   - Only expose the dashboard port to trusted networks
   - Use a reverse proxy (nginx/Apache) with SSL

2. **Authentication**
   - Consider adding authentication via reverse proxy
   - Use VPN or SSH tunneling for remote access

3. **Resource Limits**
   - Monitor memory usage
   - Set up log rotation

### Reverse Proxy Setup (nginx)

Create nginx configuration:

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location / {
        proxy_pass http://localhost:8600;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoring

Monitor the dashboard with:

```bash
# Check if running
ps aux | grep streamlit

# Check port
sudo netstat -tlnp | grep 8600

# View logs (if using systemd)
sudo journalctl -u genestack-dashboard -f
```

### Backup

Backup important files:

```bash
# Configuration
cp genestack-intelligence/config.sh config.sh.backup

# Reports
tar -czf reports-backup.tar.gz reports/

# Documentation
tar -czf docs-backup.tar.gz docs/
```

## Performance Tuning

### For Large Repositories

If working with large repositories, adjust these settings:

```bash
# In config.sh
PREVIEW_TIMEOUT_SECONDS=120
PREVIEW_STABILIZE_SECONDS=30
```

### Memory Usage

Monitor memory usage:

```bash
# Check memory
free -h

# Check process memory
ps aux | grep streamlit | awk '{print $6}'
```

If memory is an issue, consider:
- Disabling screenshot capture
- Running reports less frequently
- Using a machine with more RAM

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `sudo journalctl -u genestack-dashboard -f`
3. Open an issue in the repository

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Playwright Documentation](https://playwright.dev/python/)
- [systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
