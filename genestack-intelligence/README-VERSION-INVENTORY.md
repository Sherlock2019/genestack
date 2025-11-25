# Genestack Version Inventory System

## Quick Start

### Generate Inventory Report

```bash
# Using the convenience script
/opt/genestack/bin/generate-version-inventory.sh

# Or directly with Python
python3 /opt/genestack/genestack-intelligence/version_inventory.py
```

### View in Dashboard

1. Start the Streamlit dashboard:
   ```bash
   cd /opt/genestack/genestack-intelligence
   streamlit run dashboard/app.py
   ```

2. Navigate to "Complete Component Version Inventory" section
3. Click "🔄 Scan Repository for All Component Versions"

## What Gets Scanned

The version inventory system scans **all** repository artifacts:

### ✅ Component Types Detected

1. **Helm Charts** (`helm-chart`)
   - Chart versions from `Chart.yaml`
   - App versions
   - Image tags from values files

2. **Kustomize Overlays** (`kustomize-image`)
   - Image overrides in `kustomization.yaml`
   - Resource versions

3. **Container Images** (`container-image`, `container-base-image`)
   - Base images from Containerfiles/Dockerfiles
   - Image tags from Helm values
   - Generic image references in YAML

4. **OpenStack Services** (`openstack-service`, `openstack-service-image`)
   - Helm chart versions
   - Container image tags
   - Service versions from `helm-chart-versions.yaml`

5. **Kubernetes Manifests** (`kubernetes-api`)
   - API versions used
   - Detects deprecated APIs

6. **Operators/CRDs** (`operator-crd`)
   - Custom Resource Definition versions
   - Operator API versions

7. **Python Packages** (`python-package`)
   - Versions from `requirements.txt`
   - Queries PyPI for latest versions

8. **Ansible Roles** (`ansible-role-var`)
   - Version variables in defaults/vars
   - Role-specific version pins

9. **CI/CD Workflows** (`github-action`, `ci-cd-tool`)
   - GitHub Actions versions
   - Tool versions (Python, Helm, kubectl, etc.)

10. **Generic Images** (`generic-image`)
    - Any image references found in YAML files
    - Pattern matching for common image fields

## Output Format

### Table Structure

| Component | Type | Version in Repo | Latest Upstream Version | Source Path | Notes |
|-----------|------|-----------------|------------------------|-------------|-------|

### Report Locations

```
reports/YYYY-MM-DD/
├── component-inventory.md    # Markdown table
└── component-inventory.csv   # CSV for Excel/Sheets
```

## Features

### ✅ Automatic Detection
- Scans entire repository recursively
- Detects versions from multiple file types
- Handles various version formats

### ✅ Upstream Comparison
- Queries PyPI for Python packages
- Can query Helm chart repositories
- Kubernetes API version checking
- Extensible for other sources

### ✅ Interactive Dashboard
- Filter by component type
- Search by name or path
- Color-coded version status
- Export to CSV
- Statistics and metrics

### ✅ Export Options
- Markdown tables
- CSV format
- Download from dashboard
- Automatic report generation

## Version Status Colors

- 🟢 **Green**: Up to date
- 🟡 **Yellow**: Minor version outdated
- 🔴 **Red**: Major version outdated
- ⚪ **Gray**: Latest version unknown

## Statistics Provided

- Total components found
- Number of component types
- Count of potentially outdated components
- Components with latest version info

## Integration

### CI/CD Pipeline

Add to your GitHub Actions workflow:

```yaml
- name: Generate Version Inventory
  run: |
    python3 genestack-intelligence/version_inventory.py
  continue-on-error: true

- name: Upload Inventory Report
  uses: actions/upload-artifact@v3
  with:
    name: version-inventory
    path: reports/**/component-inventory.*
```

### Scheduled Scans

Run weekly to track version drift:

```bash
# Add to crontab
0 0 * * 0 cd /opt/genestack && /opt/genestack/bin/generate-version-inventory.sh
```

## Extending the Scanner

To add support for new component types:

1. Add `scan_*` method to `VersionInventory` class
2. Call from `scan_all()`
3. Implement `_get_latest_version()` for the type
4. Update documentation

Example:

```python
def scan_new_component_type(self):
    """Scan for new component type"""
    for config_file in self.repo_path.rglob("new-config-pattern.*"):
        # Extract version
        version = extract_version(config_file)
        self.inventory.append({
            "Component": component_name,
            "Type": "new-component-type",
            "Version in Repo": version,
            "Latest Upstream Version": None,
            "Source Path": str(config_file.relative_to(self.repo_path)),
            "Notes": "Description"
        })
```

## Troubleshooting

### Scan takes too long
- First scan processes all files
- Consider filtering by type in dashboard
- Future: Add caching mechanism

### No upstream versions
- Some types require API access
- Network connectivity needed
- Registry authentication may be required

### Missing components
- Check file paths match expected structure
- Verify file permissions
- Review scan methods for your component type

## Performance

- **Initial Scan**: ~30-60 seconds for full repository
- **Subsequent Scans**: Similar (no caching yet)
- **Upstream Queries**: Adds 10-30 seconds depending on network

## Future Enhancements

- [ ] Caching mechanism for faster rescans
- [ ] Registry API integration for container images
- [ ] Helm chart repository queries
- [ ] Version diff tracking over time
- [ ] Automated update recommendations
- [ ] Integration with dependency update tools
- [ ] Slack/Teams notifications for outdated components

## Documentation

Full documentation: [docs/version-inventory.md](../docs/version-inventory.md)
