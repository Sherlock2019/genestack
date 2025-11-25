# Genestack Version Inventory

The Genestack Version Inventory system provides comprehensive scanning and tracking of all component versions across the entire repository.

## Overview

The version inventory scanner automatically detects and catalogs versions for:

- **Helm Charts** - Chart versions and appVersions from `Chart.yaml` and values files
- **Kustomize Overlays** - Image tags and resource versions
- **Container Images** - Base images from Containerfiles/Dockerfiles
- **OpenStack Components** - Service versions from Helm configs and chart versions
- **Kubernetes Manifests** - API versions used across all manifests
- **Operators/CRDs** - Custom Resource Definition versions
- **Python Packages** - Package versions from requirements.txt files
- **Ansible Roles** - Version variables in role defaults and vars
- **CI/CD Workflows** - GitHub Actions versions and tool versions
- **Generic Images** - Any image references found in YAML files

## Usage

### Command Line

Generate a complete inventory report:

```bash
/opt/genestack/bin/generate-version-inventory.sh
```

Or use the Python script directly:

```bash
python3 /opt/genestack/genestack-intelligence/version_inventory.py --repo-path /opt/genestack
```

### Streamlit Dashboard

1. Navigate to the Genestack Intelligence Dashboard
2. Scroll to the "Complete Component Version Inventory" section
3. Click "🔄 Scan Repository for All Component Versions"
4. Wait for the scan to complete (may take a few minutes)
5. Use filters to view specific component types
6. Export results as CSV or view the generated reports

## Output Format

The inventory generates a table with the following columns:

| Column | Description |
|--------|-------------|
| Component | Name of the component |
| Type | Component type (helm-chart, container-image, python-package, etc.) |
| Version in Repo | Current version found in repository |
| Latest Upstream Version | Latest available version from upstream source |
| Source Path | File path where version was detected |
| Notes | Additional context or metadata |

## Report Locations

Reports are automatically saved to:

```
reports/YYYY-MM-DD/
├── component-inventory.md    # Markdown table format
└── component-inventory.csv   # CSV format for spreadsheet tools
```

## Version Comparison

The system attempts to compare repository versions with latest upstream versions:

- **Python Packages**: Queries PyPI API
- **Helm Charts**: Can query chart repositories (requires configuration)
- **Container Images**: Requires registry access (not automatically queried)
- **Kubernetes APIs**: Compares against current Kubernetes version standards

### Color Coding

In the Streamlit dashboard, components are color-coded:

- 🟢 **Green**: Up to date with latest version
- 🟡 **Yellow**: Minor version outdated
- 🔴 **Red**: Major version outdated
- ⚪ **Gray**: Latest version unknown or unavailable

## Filtering and Search

The dashboard provides:

- **Type Filter**: Filter by component type (helm-chart, python-package, etc.)
- **Search**: Search by component name or source path
- **Statistics**: View counts of total components, types, and outdated items

## Integration with CI/CD

You can integrate version inventory scanning into your CI/CD pipeline:

```yaml
# .github/workflows/version-inventory.yml
name: Version Inventory
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Inventory
        run: |
          python3 genestack-intelligence/version_inventory.py
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: version-inventory
          path: reports/
```

## Limitations

- **Upstream Version Detection**: Not all component types have automatic upstream version detection
- **Registry Access**: Container image latest versions require registry API access
- **Rate Limiting**: PyPI and other APIs may have rate limits
- **Version Parsing**: Some version formats may not be automatically parsed

## Extending the Scanner

To add support for new component types:

1. Add a new `scan_*` method to `VersionInventory` class
2. Call it from `scan_all()` method
3. Implement `_get_latest_version()` logic for the new type
4. Update this documentation

## Troubleshooting

### No components found

- Ensure you're running from the repository root
- Check that the repository structure matches expected paths
- Verify file permissions

### Upstream versions show "N/A"

- Some component types don't have automatic upstream detection
- Network access may be required for API queries
- Registry authentication may be needed for container images

### Scan takes too long

- The initial scan processes all files in the repository
- Subsequent scans can be faster with caching (future enhancement)
- Consider filtering by component type in the dashboard

## Examples

### Find all Helm chart versions

```bash
python3 genestack-intelligence/version_inventory.py | grep "helm-chart"
```

### Check for outdated Python packages

```bash
python3 genestack-intelligence/version_inventory.py | \
  grep "python-package" | \
  awk -F',' '$4 != "N/A" && $3 != $4 {print}'
```

### Export specific component type

```python
from version_inventory import VersionInventory
import pandas as pd

scanner = VersionInventory()
inventory = scanner.scan_all()
df = pd.DataFrame(inventory)

# Filter for OpenStack services
openstack_df = df[df['Type'] == 'openstack-service']
openstack_df.to_csv('openstack-versions.csv', index=False)
```
