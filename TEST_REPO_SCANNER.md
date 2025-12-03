# Repository Scanner - Testing Guide

## What Changed

The Genestack Intelligence Dashboard can now analyze **ANY** Git repository URL you provide!

## How It Works

1. **Enter Repo URL**: At the top of the dashboard, there's a text input field
2. **Click "Analyze This Repo"**: The app will:
   - Clone the repo to a temp directory (if it's not the current repo)
   - Run all Git analysis on that repository
   - Display all metrics, contributors, branches, files, etc.

## Features

- ✅ Analyzes any public Git repository
- ✅ Works with GitHub, GitLab, Bitbucket, etc.
- ✅ Clones repos to temp directory automatically
- ✅ Caches cloned repos during session
- ✅ All existing features work on the new repo:
  - Contributors analysis
  - Branch statistics
  - File change tracking
  - PR/MR history
  - Drift detection
  - Heatmaps
  - Version inventory
  - OpenStack compatibility

## Usage Examples

### Example 1: Analyze Kubernetes
```
https://github.com/kubernetes/kubernetes
```

### Example 2: Analyze React
```
https://github.com/facebook/react
```

### Example 3: Analyze any private repo (if you have access)
```
git@github.com:your-org/your-private-repo.git
```

## How to Test

1. Start the dashboard:
   ```bash
   ./start.sh
   ```

2. Open the dashboard in your browser (usually http://localhost:8600)

3. At the top, you'll see "🔗 Git Repository URL"

4. Enter any Git repository URL, for example:
   ```
   https://github.com/torvalds/linux
   ```

5. Click "🔍 Analyze This Repo"

6. Wait for the repo to clone (shows spinner)

7. The dashboard will refresh and show analysis for that repo!

## Technical Details

### New Files
- `genestack-intelligence/dashboard/repo_manager.py` - Handles repo cloning and management

### Modified Files
- `genestack-intelligence/dashboard/app.py` - Updated to use repo_manager

### Key Changes
1. Added `RepoManager` class to handle cloning
2. Modified `git()` function to accept `repo_path` parameter
3. All git commands now run in the specified repo directory
4. Session state tracks current repo path
5. Temp repos are cleaned up automatically

## Limitations

- Shallow clone (depth=1) for speed - full history not available
- 5-minute timeout for cloning large repos
- Requires Git to be installed on the system
- Private repos require SSH key or credentials configured

## Future Enhancements

- [ ] Support for full clone (not just shallow)
- [ ] Progress bar for large clones
- [ ] Multiple repo comparison
- [ ] Save/load analyzed repos
- [ ] Export analysis reports
