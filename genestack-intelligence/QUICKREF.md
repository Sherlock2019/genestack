# 🧬 Genestack Intelligence Suite - Quick Reference

## 🚀 Quick Start

```bash
# First time setup
cd genestack-intelligence
./setup.sh

# Start dashboard
cd ..
./start.sh

# Or use quickstart (does both)
cd genestack-intelligence
./quickstart.sh
```

## 📍 Access URLs

Once running, access at:
- `http://localhost:8600`
- `http://<your-server-ip>:8600`
- `http://<hostname>:8600`

## ⚙️ Configuration

### Quick Config

Edit `genestack-intelligence/config.sh`:

```bash
PORT=8600                        # Change port
SERVER_ADDRESS="0.0.0.0"        # Bind address
ENABLE_SCREENSHOTS="false"       # Disable screenshots
ENABLE_SLACK="true"             # Enable Slack
ENABLE_TEAMS="true"             # Enable Teams
```

### Environment Variables

```bash
export GENESTACK_PORT=9000
export GENESTACK_SCREENSHOTS="false"
./start.sh
```

## 🔧 Common Tasks

### Change Port

```bash
# Option 1: Edit config
nano genestack-intelligence/config.sh
# Change: PORT=8601

# Option 2: Environment variable
export GENESTACK_PORT=8601
./start.sh
```

### Run in Background

```bash
nohup ./start.sh > dashboard.log 2>&1 &

# Check if running
ps aux | grep streamlit

# Stop
pkill -f "streamlit run"
```

### Setup systemd Service

```bash
# 1. Copy and edit service file
sudo cp genestack-intelligence/genestack-dashboard.service.example \
        /etc/systemd/system/genestack-dashboard.service

# 2. Edit paths
sudo nano /etc/systemd/system/genestack-dashboard.service
# Replace <USERNAME> and <PATH_TO_GENESTACK>

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable genestack-dashboard
sudo systemctl start genestack-dashboard

# 4. Check status
sudo systemctl status genestack-dashboard

# 5. View logs
sudo journalctl -u genestack-dashboard -f
```

### Disable Screenshots

```bash
# Edit config
nano genestack-intelligence/config.sh
# Set: ENABLE_SCREENSHOTS="false"

# Or use environment variable
export GENESTACK_SCREENSHOTS="false"
./start.sh
```

### Enable Notifications

```bash
# Slack
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"
export GENESTACK_ENABLE_SLACK="true"

# Teams
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/YOUR/WEBHOOK"
export GENESTACK_ENABLE_TEAMS="true"

./start.sh
```

## 🐛 Troubleshooting

### Virtual Environment Not Found

```bash
cd genestack-intelligence
./setup.sh
```

### Port Already in Use

```bash
# Find process
sudo lsof -i :8600

# Kill process
sudo kill -9 <PID>

# Or change port
export GENESTACK_PORT=8601
./start.sh
```

### Can't Access from Network

```bash
# 1. Check config
nano genestack-intelligence/config.sh
# Ensure: SERVER_ADDRESS="0.0.0.0"

# 2. Check firewall
sudo ufw allow 8600/tcp          # Ubuntu
sudo firewall-cmd --add-port=8600/tcp --permanent  # RHEL/Rocky
sudo firewall-cmd --reload
```

### Python Version Too Old

```bash
# Check version
python3 --version

# Need Python 3.8+
# Install newer version or use pyenv
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/genestack
```

## 📁 File Structure

```
genestack/
├── start.sh                          # Main launcher
└── genestack-intelligence/
    ├── setup.sh                      # Setup script
    ├── quickstart.sh                 # One-command start
    ├── config.sh                     # Configuration
    ├── requirements.txt              # Dependencies
    ├── DEPLOYMENT.md                 # Full guide
    ├── MIGRATION.md                  # Migration guide
    ├── README.md                     # Overview
    ├── QUICKREF.md                   # This file
    ├── .env.example                  # Env var template
    ├── genestack-dashboard.service.example  # systemd template
    ├── dashboard/                    # Dashboard app
    ├── drift/                        # Drift detection
    ├── heatmap/                      # Heatmap generation
    └── notify/                       # Notifications
```

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[MIGRATION.md](MIGRATION.md)** - What changed and why
- **[README.md](README.md)** - Intelligence suite overview
- **[config.sh](config.sh)** - All configuration options

## 🎯 Common Scenarios

### Development

```bash
cd genestack-intelligence
./quickstart.sh
# Access at http://localhost:8600
```

### Remote Server

```bash
# Setup once
cd genestack-intelligence
./setup.sh

# Configure
nano config.sh
# Set: ENABLE_SCREENSHOTS="false"
# Set: ENABLE_GIT_COMMITS="false"

# Run in background
cd ..
nohup ./start.sh > dashboard.log 2>&1 &
```

### Production

```bash
# Setup
cd genestack-intelligence
./setup.sh

# Configure
nano config.sh

# Install systemd service
sudo cp genestack-dashboard.service.example \
        /etc/systemd/system/genestack-dashboard.service
sudo nano /etc/systemd/system/genestack-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable genestack-dashboard
sudo systemctl start genestack-dashboard

# Setup reverse proxy (nginx)
# See DEPLOYMENT.md for details
```

## 🔍 Monitoring

```bash
# Check if running
ps aux | grep streamlit

# Check port
sudo netstat -tlnp | grep 8600

# View logs (systemd)
sudo journalctl -u genestack-dashboard -f

# View logs (background)
tail -f dashboard.log

# Check memory
ps aux | grep streamlit | awk '{print $6}'
```

## 🛑 Stopping

```bash
# Interactive mode
Ctrl+C

# Background mode
pkill -f "streamlit run"

# systemd
sudo systemctl stop genestack-dashboard
```

## 🔄 Updating

```bash
# Pull latest changes
git pull

# Reinstall dependencies (if requirements.txt changed)
cd genestack-intelligence
source .venv/bin/activate
pip install -r requirements.txt

# Restart
cd ..
./start.sh
```

## 📞 Getting Help

1. Check this quick reference
2. Read [DEPLOYMENT.md](DEPLOYMENT.md)
3. Check error messages (they include solutions!)
4. Review logs
5. Open an issue

## 💡 Tips

- **First time?** Use `./quickstart.sh`
- **Production?** Use systemd service
- **Remote access?** Set `SERVER_ADDRESS="0.0.0.0"`
- **Slow server?** Disable screenshots
- **Multiple instances?** Change port per instance
- **Security?** Use reverse proxy with SSL

---

**Quick Reference v1.0** | For detailed info, see [DEPLOYMENT.md](DEPLOYMENT.md)
