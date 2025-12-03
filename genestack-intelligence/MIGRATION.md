# Migration Guide - Server-Agnostic Deployment

This document explains the changes made to make the Genestack Intelligence Suite server-agnostic and easy to deploy on any server.

## 🎯 What Changed

The suite has been refactored to eliminate hard-coded paths and server-specific configurations, making it portable and easy to deploy anywhere.

## 📝 Changes Summary

### New Files Created

1. **`requirements.txt`** - Python dependencies for the intelligence suite
   - Previously missing, dependencies were unclear
   - Now contains all required packages with versions

2. **`setup.sh`** - Automated setup script
   - Creates virtual environment
   - Installs all dependencies
   - Sets up Playwright for screenshots
   - Validates Python version

3. **`config.sh`** - Configuration file
   - Centralized configuration management
   - All settings in one place
   - Environment variable support
   - Easy to customize per server

4. **`DEPLOYMENT.md`** - Comprehensive deployment guide
   - Step-by-step setup instructions
   - Troubleshooting section
   - Production deployment guide
   - systemd service setup

5. **`README.md`** - Intelligence suite documentation
   - Quick start guide
   - Component overview
   - Configuration examples

6. **`quickstart.sh`** - One-command setup and launch
   - Combines setup and start in one script
   - Perfect for first-time users

7. **`.env.example`** - Environment variable template
   - Example configuration
   - All available options documented

8. **`genestack-dashboard.service.example`** - systemd service template
   - Production deployment
   - Auto-start on boot
   - Log management

### Modified Files

1. **`start.sh`** - Completely rewritten
   - **Before:** Hard-coded server IP, assumed virtual environment exists
   - **After:** 
     - Auto-detects server IP and hostname
     - Checks for virtual environment before starting
     - Loads configuration from `config.sh`
     - Better error messages
     - Displays all available access URLs
     - Configurable features (screenshots, notifications, reports)

## 🔄 Migration Steps

### If You Have an Existing Installation

1. **Backup your current setup:**
   ```bash
   cd /home/dzoan/genestack
   cp start.sh start.sh.backup
   ```

2. **The new files are already in place**, but you need to run setup:
   ```bash
   cd genestack-intelligence
   ./setup.sh
   ```

3. **Configure for your environment:**
   ```bash
   nano config.sh
   # Adjust PORT, ENABLE_SCREENSHOTS, etc.
   ```

4. **Start the dashboard:**
   ```bash
   cd ..
   ./start.sh
   ```

### For New Installations

Simply run:
```bash
cd genestack-intelligence
./quickstart.sh
```

## 🎨 Key Improvements

### 1. No More Hard-Coded Paths

**Before:**
```bash
source "$INTEL/.venv/bin/activate"  # Would fail if .venv doesn't exist
```

**After:**
```bash
if [ ! -d "$VENV" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run: ./setup.sh"
    exit 1
fi
source "$VENV/bin/activate"
```

### 2. Server Auto-Detection

**Before:**
```bash
SERVER_IP="203.60.1.117"  # Hard-coded!
```

**After:**
```bash
PRIMARY_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "unknown")
ALL_IPS=$(hostname -I 2>/dev/null | tr ' ' '\n' | grep -v '^$' || echo "")
# Displays all available IPs automatically
```

### 3. Configurable Features

**Before:** Everything always ran, no way to disable features

**After:** Control everything via `config.sh`:
```bash
ENABLE_SCREENSHOTS="false"      # Disable if not needed
ENABLE_SLACK="true"             # Enable notifications
ENABLE_GIT_COMMITS="false"      # Disable for servers
ENABLE_DRIFT_DETECTION="true"   # Control report generation
```

### 4. Better Error Messages

**Before:**
```bash
source "$INTEL/.venv/bin/activate"
# Error: No such file or directory (cryptic)
```

**After:**
```bash
if [ ! -d "$VENV" ]; then
    echo "❌ Virtual environment not found at: $VENV"
    echo ""
    echo "Please run the setup script first:"
    echo "   cd $INTEL"
    echo "   ./setup.sh"
    exit 1
fi
```

### 5. Flexible Deployment Options

Now supports:
- **Manual execution:** `./start.sh`
- **Background mode:** `nohup ./start.sh &`
- **systemd service:** Auto-start on boot
- **Docker:** (Coming soon)

## 🔧 Configuration Options

### Via config.sh

Edit `genestack-intelligence/config.sh`:
```bash
PORT=9000
SERVER_ADDRESS="127.0.0.1"
ENABLE_SCREENSHOTS="false"
```

### Via Environment Variables

```bash
export GENESTACK_PORT=9000
export GENESTACK_ADDRESS="127.0.0.1"
./start.sh
```

### Via .env File

```bash
cp genestack-intelligence/.env.example genestack-intelligence/.env
nano genestack-intelligence/.env
```

Then modify `start.sh` to load it:
```bash
if [ -f "$INTEL/.env" ]; then
    set -a
    source "$INTEL/.env"
    set +a
fi
```

## 🚀 Deployment Scenarios

### Development Machine

```bash
cd genestack-intelligence
./quickstart.sh
```

### Remote Server (Background)

```bash
cd genestack
nohup ./start.sh > dashboard.log 2>&1 &
```

### Production Server (systemd)

```bash
# Setup
cd genestack-intelligence
./setup.sh

# Configure
nano config.sh

# Install service
sudo cp genestack-dashboard.service.example /etc/systemd/system/genestack-dashboard.service
sudo nano /etc/systemd/system/genestack-dashboard.service
# Edit User, WorkingDirectory, ExecStart paths

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable genestack-dashboard
sudo systemctl start genestack-dashboard
```

### Docker (Future)

```bash
docker-compose up -d
```

## 📊 Comparison

| Feature | Before | After |
|---------|--------|-------|
| Setup Process | Manual, unclear | Automated (`setup.sh`) |
| Configuration | Hard-coded in script | Centralized (`config.sh`) |
| Server IP | Hard-coded | Auto-detected |
| Virtual Environment | Assumed to exist | Checked, helpful error |
| Dependencies | Unclear | Documented (`requirements.txt`) |
| Deployment | Manual only | Multiple options |
| Documentation | Minimal | Comprehensive |
| Error Messages | Cryptic | Clear and actionable |
| Portability | Single server | Any server |

## 🎓 Best Practices

### For Development

```bash
# Use default settings
cd genestack-intelligence
./quickstart.sh
```

### For Staging/Testing

```bash
# Disable screenshots and git commits
nano config.sh
# Set:
# ENABLE_SCREENSHOTS="false"
# ENABLE_GIT_COMMITS="false"

./start.sh
```

### For Production

```bash
# Use systemd service
# Disable screenshots
# Enable notifications
# Set up reverse proxy with SSL
# Configure firewall

# See DEPLOYMENT.md for complete guide
```

## 🐛 Troubleshooting

All common issues are now documented in `DEPLOYMENT.md`:

- Virtual environment not found → Run `setup.sh`
- Port in use → Change in `config.sh`
- Permission denied → Fix ownership
- Can't access from network → Check firewall and `SERVER_ADDRESS`

## 📚 Additional Resources

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[README.md](README.md)** - Intelligence suite overview
- **[config.sh](config.sh)** - Configuration options
- **[.env.example](.env.example)** - Environment variable template

## ✅ Verification

To verify the migration was successful:

1. **Check files exist:**
   ```bash
   ls -la genestack-intelligence/
   # Should see: setup.sh, config.sh, requirements.txt, DEPLOYMENT.md, etc.
   ```

2. **Run setup:**
   ```bash
   cd genestack-intelligence
   ./setup.sh
   ```

3. **Start dashboard:**
   ```bash
   cd ..
   ./start.sh
   ```

4. **Access dashboard:**
   - Open browser to `http://localhost:8600`
   - Should see the dashboard

## 🎉 Benefits

- ✅ **Portable** - Works on any server with Python 3.8+
- ✅ **Documented** - Clear instructions for every scenario
- ✅ **Configurable** - Easy to customize per environment
- ✅ **Maintainable** - Centralized configuration
- ✅ **Production-Ready** - systemd service support
- ✅ **User-Friendly** - Better error messages
- ✅ **Automated** - One-command setup

## 🤝 Support

If you encounter issues:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)
2. Review error messages (they now include solutions!)
3. Check logs
4. Open an issue

---

**The Genestack Intelligence Suite is now ready for deployment anywhere! 🚀**
