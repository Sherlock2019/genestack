# 🎯 Simple Usage Guide - Analyze ANY Git Repository

## Quick Start (3 Steps)

### Step 1: Start the Dashboard
```bash
cd /home/dzoan/genestack
./start.sh
```

### Step 2: Open in Browser
```
http://localhost:8600
```

### Step 3: Enter Any Repo URL
At the top of the page, you'll see:

```
🔗 Git Repository URL
[Enter Git Repository URL to analyze]  [🔍 Analyze This Repo]
```

**Try these examples:**
- `https://github.com/kubernetes/kubernetes`
- `https://github.com/facebook/react`
- `https://github.com/openstack/nova`
- Any public or private repo you have access to!

Click **"🔍 Analyze This Repo"** and wait for it to clone and analyze!

## What You'll See

The dashboard will show you:

### 📊 KPI Metrics
- Total Contributors
- Active Branches  
- Updated Files
- Recent PRs/MRs

### 🏆 Top Contributors
- Gold, Silver, Bronze medals for top 3
- Detailed contribution breakdown
- Branch and file statistics per contributor

### 📈 Branch Analysis
- Commit counts per branch
- Files updated per branch
- Top modified files
- Recent updates and diffs

### 📁 File Change Tracking
- Most modified files
- Risk analysis
- Suggestions for improvements

### 🎨 Visualizations
- Contribution pie charts
- Activity heatmaps
- Drift detection
- Timeline graphs

## That's It!

No configuration needed. Just:
1. Start the app
2. Enter a repo URL
3. Get instant insights!

## Need Help?

- The app works with any Git repository
- It clones repos to a temp directory automatically
- First-time clone may take a minute for large repos
- All analysis happens in real-time

## Advanced Features

Once you've analyzed a repo, explore these tabs:
- **📊 Repository Health** - Health gauges and metrics
- **🔍 Version Inventory** - Scan for versions and dependencies
- **🔄 OpenStack Compatibility** - OpenStack-specific analysis
- **📈 Drift Detection** - Configuration drift analysis
- **🗺️ Contributor Heatmap** - Visual activity patterns
