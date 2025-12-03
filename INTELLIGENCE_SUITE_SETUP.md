# 🧬 Genestack Intelligence Suite - Complete Setup Guide

## 🎉 Server-Agnostic Deployment Ready!

Your Genestack Intelligence Suite has been successfully converted to work on **any server** with Python 3.8+. No more hard-coded paths or server-specific configurations!

---

## 📦 What's New

### 10 New Files Created

| File | Size | Purpose |
|------|------|---------|
| `genestack-intelligence/requirements.txt` | 521 B | Python dependencies |
| `genestack-intelligence/setup.sh` | 3.1 KB | Automated setup script |
| `genestack-intelligence/config.sh` | 2.7 KB | Configuration file |
| `genestack-intelligence/quickstart.sh` | 762 B | One-command launcher |
| `genestack-intelligence/install-remote.sh` | 7.2 KB | Remote server installer |
| `genestack-intelligence/DEPLOYMENT.md` | 8.6 KB | Complete deployment guide |
| `genestack-intelligence/README.md` | 5.1 KB | Suite overview |
| `genestack-intelligence/MIGRATION.md` | 8.1 KB | What changed and why |
| `genestack-intelligence/QUICKREF.md` | 6.3 KB | Quick reference card |
| `genestack-intelligence/.env.example` | 1.7 KB | Environment variable template |
| `genestack-intelligence/genestack-dashboard.service.example` | 1.5 KB | systemd service template |

### 1 File Updated

| File | Size | Changes |
|------|------|---------|
| `start.sh` | 10.9 KB | Completely rewritten - server-agnostic |

---

## 🚀 Quick Start (3 Commands)

### Option 1: Quickstart (Recommended for First Time)

```bash
cd genestack-intelligence
./quickstart.sh
```

This will automatically:
1. Check Python version
2. Create virtual environment
3. Install all dependencies
4. Start the dashboard

### Option 2: Manual Setup

```bash
# 1. Setup
cd genestack-intelligence
./setup.sh

# 2. Start
cd ..
./start.sh
```

### Option 3: Remote Server Installation (Interactive)

```bash
cd genestack-intelligence
./install-remote.sh
```

This interactive script will:
- Check and install Python if needed
- Run setup automatically
- Configure firewall (optional)
- Choose deployment method (manual/background/systemd)
- Display all access URLs

---

## 📍 Access Your Dashboard

Once running, you'll see:

```
🌐 Launching dashboard...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Dashboard Access URLs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📍 Localhost:
     http://localhost:8600

  🌐 Network Access:
     http://192.168.1.100:8600
     http://10.0.0.5:8600

  🖥️  Hostname:
     http://your-server:8600

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The script **auto-detects** all available network interfaces and displays them!

---

## ⚙️ Configuration

### Quick Config

Edit `genestack-intelligence/config.sh`:

```bash
# Server settings
PORT=8600                        # Change port
SERVER_ADDRESS="0.0.0.0"        # Bind to all interfaces

# Features
ENABLE_SCREENSHOTS="false"       # Disable screenshots for servers
ENABLE_DRIFT_DETECTION="true"    # Enable drift detection
ENABLE_HEATMAP="true"           # Enable heatmap generation

# Notifications
ENABLE_SLACK="false"            # Enable Slack notifications
ENABLE_TEAMS="false"            # Enable Teams notifications

# Git integration
ENABLE_GIT_COMMITS="false"      # Disable for servers
```

### Environment Variables

```bash
export GENESTACK_PORT=9000
export GENESTACK_SCREENSHOTS="false"
export GENESTACK_ENABLE_SLACK="true"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"
./start.sh
```

---

## 🏭 Production Deployment

### Method 1: Background Process

```bash
nohup ./start.sh > dashboard.log 2>&1 &

# View logs
tail -f dashboard.log

# Stop
pkill -f "streamlit run"
```

### Method 2: systemd Service (Recommended)

```bash
# 1. Copy service file
sudo cp genestack-intelligence/genestack-dashboard.service.example \
        /etc/systemd/system/genestack-dashboard.service

# 2. Edit paths (replace <USERNAME> and <PATH_TO_GENESTACK>)
sudo nano /etc/systemd/system/genestack-dashboard.service

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable genestack-dashboard
sudo systemctl start genestack-dashboard

# 4. Check status
sudo systemctl status genestack-dashboard

# 5. View logs
sudo journalctl -u genestack-dashboard -f
```

### Method 3: Interactive Installation

```bash
cd genestack-intelligence
./install-remote.sh
# Follow the prompts to choose deployment method
```

---

## 🎯 Key Improvements

### Before ❌

- Hard-coded server IP: `203.60.1.117`
- Assumed virtual environment exists → cryptic errors
- No dependency documentation
- No configuration options
- Single deployment method
- Manual setup required

### After ✅

- **Auto-detects** server IP, hostname, and all network interfaces
- **Checks** for virtual environment, provides clear setup instructions
- **Documents** all dependencies in `requirements.txt`
- **Fully configurable** via `config.sh` or environment variables
- **Multiple deployment options**: manual, background, systemd
- **Automated setup** with `setup.sh` and `quickstart.sh`
- **Interactive installer** for remote servers
- **Comprehensive documentation** (4 guides, 45+ KB)

---

## 📚 Documentation

All documentation is in `genestack-intelligence/`:

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[QUICKREF.md](genestack-intelligence/QUICKREF.md)** | Quick reference card | Need a quick command |
| **[README.md](genestack-intelligence/README.md)** | Suite overview | First time learning |
| **[DEPLOYMENT.md](genestack-intelligence/DEPLOYMENT.md)** | Complete deployment guide | Setting up production |
| **[MIGRATION.md](genestack-intelligence/MIGRATION.md)** | What changed and why | Understanding changes |

### Quick Links

- **Troubleshooting**: [DEPLOYMENT.md#troubleshooting](genestack-intelligence/DEPLOYMENT.md#troubleshooting)
- **Configuration**: [DEPLOYMENT.md#configuration](genestack-intelligence/DEPLOYMENT.md#configuration)
- **Production Setup**: [DEPLOYMENT.md#production-deployment](genestack-intelligence/DEPLOYMENT.md#production-deployment)
- **Common Tasks**: [QUICKREF.md#common-tasks](genestack-intelligence/QUICKREF.md#common-tasks)

---

## 🐛 Common Issues & Solutions

### Issue: Virtual Environment Not Found

```bash
❌ Virtual environment not found at: /path/to/.venv
```

**Solution:**
```bash
cd genestack-intelligence
./setup.sh
```

### Issue: Port Already in Use

```bash
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Option 1: Change port
export GENESTACK_PORT=8601
./start.sh

# Option 2: Kill existing process
sudo lsof -i :8600
sudo kill -9 <PID>
```

### Issue: Can't Access from Network

**Solution:**
```bash
# 1. Check config
nano genestack-intelligence/config.sh
# Ensure: SERVER_ADDRESS="0.0.0.0"

# 2. Check firewall
sudo ufw allow 8600/tcp                              # Ubuntu/Debian
sudo firewall-cmd --add-port=8600/tcp --permanent    # RHEL/Rocky/Fedora
sudo firewall-cmd --reload
```

### Issue: Python Version Too Old

```bash
❌ Error: Python 3.8 or higher is required
```

**Solution:**
```bash
# Check version
python3 --version

# Install newer Python (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Or use pyenv
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv local 3.11.0
```

**More solutions**: See [DEPLOYMENT.md#troubleshooting](genestack-intelligence/DEPLOYMENT.md#troubleshooting)

---

## 🌟 Features

- 📊 **Interactive Dashboard** - Real-time OpenStack component monitoring
- 🔍 **Drift Detection** - Automatic configuration drift analysis
- 🗺️ **Contributor Heatmap** - Code contribution visualization
- 📈 **Repository Health** - Health metrics and trends
- 🔔 **Notifications** - Slack and Microsoft Teams integration
- 📸 **Screenshots** - Automatic dashboard capture (optional)
- 🎨 **Themes** - Light and dark mode support
- 📱 **Responsive** - Works on desktop, tablet, and mobile

---

## 🔐 Security Best Practices

### For Production Deployments

1. **Use a Reverse Proxy** (nginx/Apache) with SSL
   ```nginx
   server {
       listen 443 ssl;
       server_name dashboard.example.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8600;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Configure Firewall**
   ```bash
   # Only allow from specific IPs
   sudo ufw allow from 192.168.1.0/24 to any port 8600
   ```

3. **Enable Authentication** (via reverse proxy)
   - Use basic auth
   - Use OAuth2
   - Use VPN or SSH tunnel

4. **Disable Unnecessary Features**
   ```bash
   # In config.sh
   ENABLE_SCREENSHOTS="false"
   ENABLE_GIT_COMMITS="false"
   ```

---

## 📊 File Structure

```
genestack/
├── start.sh                          # Main launcher (updated)
├── INTELLIGENCE_SUITE_SETUP.md       # This file
├── SETUP_SUMMARY.md                  # Setup summary
└── genestack-intelligence/
    ├── setup.sh                      # Setup script
    ├── quickstart.sh                 # One-command launcher
    ├── install-remote.sh             # Interactive installer
    ├── config.sh                     # Configuration
    ├── requirements.txt              # Dependencies
    ├── DEPLOYMENT.md                 # Deployment guide
    ├── README.md                     # Suite overview
    ├── MIGRATION.md                  # What changed
    ├── QUICKREF.md                   # Quick reference
    ├── .env.example                  # Env var template
    ├── genestack-dashboard.service.example  # systemd template
    ├── dashboard/                    # Dashboard app
    │   ├── app.py
    │   ├── repo_health_metrics.py
    │   ├── bmw_repo_health_gauges.py
    │   ├── capture_dashboard.py
    │   └── theme_manager.py
    ├── drift/                        # Drift detection
    │   └── detect_drift.py
    ├── heatmap/                      # Heatmap generation
    │   └── contributor_heatmap.py
    ├── notify/                       # Notifications
    │   ├── slack_notify.py
    │   └── teams_notify.py
    └── [other Python modules]
```

---

## 🎓 Usage Scenarios

### Scenario 1: Local Development

```bash
cd genestack-intelligence
./quickstart.sh
# Access at http://localhost:8600
```

### Scenario 2: Remote Server (Background)

```bash
# Setup
cd genestack-intelligence
./setup.sh

# Configure
nano config.sh
# Set: ENABLE_SCREENSHOTS="false"

# Run in background
cd ..
nohup ./start.sh > dashboard.log 2>&1 &
```

### Scenario 3: Production Server (systemd)

```bash
# Use interactive installer
cd genestack-intelligence
./install-remote.sh
# Choose option 3: systemd Service

# Or manually
./setup.sh
sudo cp genestack-dashboard.service.example /etc/systemd/system/genestack-dashboard.service
sudo nano /etc/systemd/system/genestack-dashboard.service
sudo systemctl enable --now genestack-dashboard
```

### Scenario 4: Multiple Instances

```bash
# Instance 1 (port 8600)
export GENESTACK_PORT=8600
./start.sh &

# Instance 2 (port 8601)
export GENESTACK_PORT=8601
./start.sh &
```

---

## 🔄 Updating

```bash
# Pull latest changes
git pull

# Update dependencies (if requirements.txt changed)
cd genestack-intelligence
source .venv/bin/activate
pip install -r requirements.txt

# Restart
cd ..
./start.sh
```

---

## 📞 Support

### Getting Help

1. **Check Documentation**
   - [QUICKREF.md](genestack-intelligence/QUICKREF.md) - Quick answers
   - [DEPLOYMENT.md](genestack-intelligence/DEPLOYMENT.md) - Detailed guide

2. **Check Error Messages**
   - Error messages now include solutions!

3. **Check Logs**
   ```bash
   # Background mode
   tail -f dashboard.log
   
   # systemd
   sudo journalctl -u genestack-dashboard -f
   ```

4. **Open an Issue**
   - Include error messages
   - Include your OS and Python version
   - Include relevant logs

---

## 🎉 Benefits Summary

| Benefit | Description |
|---------|-------------|
| ✅ **Portable** | Works on any server with Python 3.8+ |
| ✅ **Automated** | One-command setup and launch |
| ✅ **Documented** | 45+ KB of comprehensive documentation |
| ✅ **Configurable** | Easy customization per environment |
| ✅ **Production-Ready** | systemd service support |
| ✅ **User-Friendly** | Clear error messages with solutions |
| ✅ **Maintainable** | Centralized configuration |
| ✅ **Flexible** | Multiple deployment options |
| ✅ **Secure** | Production security best practices |
| ✅ **Interactive** | Interactive installer for remote servers |

---

## 🎯 Next Steps

1. **Run Setup** (if you haven't already):
   ```bash
   cd genestack-intelligence
   ./setup.sh
   ```

2. **Configure** (optional):
   ```bash
   nano config.sh
   ```

3. **Start Dashboard**:
   ```bash
   cd ..
   ./start.sh
   ```

4. **Access Dashboard** at the displayed URLs

5. **For Production**, set up systemd service:
   ```bash
   cd genestack-intelligence
   ./install-remote.sh
   # Choose option 3
   ```

---

## 📝 Changelog

### v2.0 (Server-Agnostic Release)

**Added:**
- ✨ Automated setup script (`setup.sh`)
- ✨ Configuration file (`config.sh`)
- ✨ Quick start script (`quickstart.sh`)
- ✨ Interactive remote installer (`install-remote.sh`)
- ✨ Dependencies documentation (`requirements.txt`)
- ✨ Comprehensive documentation (4 guides)
- ✨ systemd service template
- ✨ Environment variable template

**Changed:**
- 🔄 Completely rewrote `start.sh` for server-agnostic operation
- 🔄 Auto-detects server IP, hostname, and network interfaces
- 🔄 Checks virtual environment before starting
- 🔄 Better error messages with solutions
- 🔄 Configurable features via config file

**Fixed:**
- 🐛 Hard-coded server IP removed
- 🐛 Cryptic error messages replaced with helpful ones
- 🐛 Missing dependency documentation
- 🐛 No configuration options

---

**🚀 Your Genestack Intelligence Suite is now ready to deploy anywhere!**

For questions or issues, see the [Support](#-support) section above.

---

*Generated: $(date)*
*Version: 2.0 (Server-Agnostic Release)*
