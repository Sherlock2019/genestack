# OpenStack Repository Scanner - Quick Reference

## What It Does

Scans your Git repository (NO CLI required) to find ALL OpenStack component versions and analyzes compatibility.

## Quick Start

### Command Line
```bash
# Basic scan
/opt/genestack/bin/scan-openstack-repo.sh

# With web scraping
/opt/genestack/bin/scan-openstack-repo.sh --scrape
```

### Dashboard
1. Open Streamlit dashboard
2. Go to "OpenStack Repository Component Scanner"
3. Check "Scrape OpenStack Releases" (optional)
4. Click "🔄 Run Repository Scan"

## Output

Generates 4 files in `reports/YYYY-MM-DD/`:

1. **openstack_repo_inventory.json** - Complete raw data
2. **openstack_repo_inventory.md** - Markdown table
3. **openstack_repo_compatibility.csv** - CSV for Excel/Sheets
4. **openstack_recommended_stack.json** - Recommended release

## Table Columns

| Column | Description |
|--------|-------------|
| Component | OpenStack service name |
| Version Detected | Version found in repo |
| File | Source file path |
| Mapped Release | OpenStack release (Caracal, Dalmatian, etc.) |
| Compatibility Issues | OK, WARNING, or ERROR details |
| Recommended Stack | Unified release recommendation |

## Compatibility Status

- 🟢 **OK** - No issues
- 🟡 **WARNING** - Mixed releases, review needed
- 🔴 **ERROR** - Major mismatch, must fix

## What Gets Scanned

- `helm-chart-versions.yaml`
- All `Chart.yaml` files
- All `values.yaml` and `*-helm-overrides.yaml`
- `kustomization.yaml` files
- `Dockerfile` and `Containerfile`
- `requirements.txt`
- `.github/workflows/*.yml`
- Any YAML with version/image/tag fields

## Web Scraping

When enabled, fetches data from:
- https://releases.openstack.org/
- Individual release pages for component versions
- Updates compatibility matrix with latest info

## Example Output

```
Recommended Release: Caracal (2024.1)
Components: 41
Issues Found: 41
Release Series: 3 (Caracal, Dalmatian, Epoxy)

Recommendation: Mixed releases detected. 
Unify all components to Caracal (2024.1) for compatibility.
```

## Integration

Add to CI/CD to check compatibility on every PR:

```yaml
- name: Check OpenStack Compatibility
  run: /opt/genestack/bin/scan-openstack-repo.sh
```

Full documentation: [docs/openstack-repo-scanner.md](../docs/openstack-repo-scanner.md)
