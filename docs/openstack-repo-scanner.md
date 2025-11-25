# OpenStack Repository Scanner

Comprehensive repository-only scanner for OpenStack component versions and compatibility analysis.

## Overview

The OpenStack Repository Scanner performs a complete analysis of your Git repository to:

- **Extract ALL OpenStack component versions** from any file in the repository
- **Map versions to official OpenStack releases** (Caracal, Dalmatian, Epoxy, etc.)
- **Detect compatibility issues** between components
- **Recommend unified release stack** for deployment
- **Scrape official OpenStack release data** from releases.openstack.org

## Key Features

### ✅ Repository-Only Analysis
- **NO CLI commands required** - works entirely from Git repository
- Scans all file types: YAML, Dockerfiles, requirements.txt, workflows, etc.
- Recursive directory scanning
- Pattern matching for version strings

### ✅ Comprehensive Version Detection
Scans for versions in:
- `helm-chart-versions.yaml`
- `Chart.yaml` files (appVersion, version)
- `values.yaml` and `*-helm-overrides.yaml`
- `kustomization.yaml` (image tags)
- `Dockerfile` and `Containerfile` (FROM images)
- `requirements.txt` (Python packages)
- `.github/workflows/*.yml` (CI/CD versions)
- Any YAML file with version/image/tag fields

### ✅ Official Release Mapping
Maps detected versions to official OpenStack releases:
- 2025.1 → Epoxy
- 2024.2 → Dalmatian
- 2024.1 → Caracal
- 2023.2 → Bobcat
- 2023.1 → Antelope
- 2022.0 → Zed

### ✅ Compatibility Analysis
Detects:
- **MAJOR_RELEASE_MISMATCH** - Components from different release series
- **MIXED_RELEASES** - Multiple release series detected
- **CORE_SERVICE_MISMATCH** - Core services (Nova, Neutron, Keystone) mismatched
- **PLACEMENT/NOVA_MISMATCH** - Placement and Nova version incompatibility
- **UNSUPPORTED (EOL)** - End-of-life releases
- **VERSION_UNMAPPABLE** - Cannot determine release from version

### ✅ Web Scraping
Optional scraping from releases.openstack.org:
- Fetches latest release information
- Extracts component versions per release
- Updates compatibility matrix

## Usage

### Command Line

```bash
# Basic scan (repository only)
/opt/genestack/bin/scan-openstack-repo.sh

# With OpenStack release scraping
/opt/genestack/bin/scan-openstack-repo.sh --scrape
```

Or use Python directly:

```bash
python3 /opt/genestack/genestack-intelligence/openstack_repo_scanner.py --repo-path /opt/genestack
python3 /opt/genestack/genestack-intelligence/openstack_repo_scanner.py --repo-path /opt/genestack --scrape
```

### Streamlit Dashboard

1. Navigate to "OpenStack Repository Component Scanner" section
2. Check "Scrape OpenStack Releases" if you want latest data from website
3. Click "🔄 Run Repository Scan"
4. Review the compatibility table with color-coded status
5. Check the "Recommended Stack" section for unified release recommendation

## Output Files

All reports are saved to `reports/YYYY-MM-DD/`:

### 1. openstack_repo_inventory.json
Complete inventory with:
- All detected components
- Version sources and line numbers
- Version context (surrounding lines)
- Release mapping
- Release distribution

### 2. openstack_repo_inventory.md
Markdown table format:
- Component inventory table
- Release distribution summary
- Compatibility issues
- Recommended stack

### 3. openstack_repo_compatibility.csv
CSV format for spreadsheet tools:
- Component
- Version Detected
- File
- Mapped Release
- Compatibility Issues
- Recommended Stack

### 4. openstack_recommended_stack.json
Recommended stack analysis:
- Dominant release
- Release distribution
- Component count
- Issues found
- Overall recommendation

## Table Format

| Component | Version Detected | File | Mapped Release | Compatibility Issues | Recommended Stack |
|-----------|------------------|------|----------------|---------------------|-------------------|

### Example Output

```
| Component | Version Detected | File | Mapped Release | Compatibility Issues | Recommended Stack |
|-----------|------------------|------|----------------|---------------------|-------------------|
| keystone | 2024.1-latest | base-helm-configs/keystone/keystone-helm-overrides.yaml | Caracal | MIXED_RELEASES | Caracal (2024.1) — Fully compatible |
| nova | 2024.2.555+... | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH; MIXED_RELEASES | Unify to Caracal (2024.1) |
| blazar | 2025.1.3+... | helm-chart-versions.yaml | Epoxy | MAJOR_RELEASE_MISMATCH; MIXED_RELEASES | Unify to Caracal (2024.1) |
```

## Compatibility Status

### ✅ OK (Green)
- Component aligned with recommended release
- No compatibility issues

### ⚠️ WARNING (Yellow)
- Mixed releases detected
- Potential compatibility concerns
- Review recommended

### ❌ ERROR (Red)
- Major release mismatch
- Core service incompatibility
- EOL/unsupported release
- Must fix before deployment

## Recommended Stack

The scanner determines the dominant release (most components) and recommends:

**If all components aligned:**
```
"Caracal (2024.1) — Fully compatible"
```

**If mixed releases:**
```
"Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1)"
```

Includes link to official release documentation:
```
https://releases.openstack.org/2024.1/
```

## Version Detection Patterns

The scanner recognizes these version formats:

- `2025.1.2`
- `2024.2.186+cdd5e6c55`
- `"2024.1"`
- `v2024.2`
- `2024.1-latest`
- `image: ghcr.io/...:2024.2`
- `appVersion: "2025.1.0"`
- `keystone_version: "2024.1"`
- `openstack_version: "2025.1"`

## Integration

### CI/CD Pipeline

```yaml
name: OpenStack Compatibility Check
on:
  pull_request:
    paths:
      - 'base-helm-configs/**'
      - 'helm-chart-versions.yaml'
      - '**/*.yaml'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check Compatibility
        run: |
          python3 genestack-intelligence/openstack_repo_scanner.py
      - name: Check for Errors
        run: |
          if grep -q "MAJOR_RELEASE_MISMATCH\|CORE_SERVICE_MISMATCH\|EOL" reports/*/openstack_repo_compatibility.csv; then
            echo "Compatibility errors found!"
            exit 1
          fi
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: compatibility-reports
          path: reports/**/openstack_repo_*
```

## Troubleshooting

### No components detected
- Check file paths match repository structure
- Verify files contain OpenStack component names
- Review version format patterns

### Version unmappable
- Version format may not match expected patterns
- Check if version string contains release identifier (e.g., 2024.1)
- Review source file for context

### False compatibility warnings
- Some version formats may trigger false positives
- Review the "File" column to verify source
- Check version context in JSON inventory

## Best Practices

1. **Run before major deployments** - Catch compatibility issues early
2. **Use --scrape flag** - Get latest release data from official sources
3. **Review recommended stack** - Follow unified release recommendation
4. **Fix errors first** - Address ERROR status before WARNING
5. **Document exceptions** - If warnings are acceptable, document why

## Related Documentation

- [Version Inventory](version-inventory.md) - Complete component tracking
- [Compatibility Analysis](openstack-compatibility-analysis.md) - Detailed compatibility checks
- [OpenStack Component Versions](openstack-component-versions.md) - How to check actual software versions
