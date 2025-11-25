# OpenStack Compatibility Analysis

The OpenStack Compatibility Analyzer detects and flags incompatibilities between OpenStack components in your Genestack deployment.

## Overview

The compatibility analyzer performs comprehensive checks to ensure all OpenStack components work together correctly:

- **Release Alignment**: Verifies all components belong to the same OpenStack release
- **API Microversion Compatibility**: Checks service API version compatibility
- **Container Image Alignment**: Ensures container images use the same release
- **Python Library Compatibility**: Validates oslo.* library versions
- **Kubernetes API Compatibility**: Detects deprecated Kubernetes APIs
- **RPC Schema Compatibility**: Checks message queue compatibility (when available)

## Usage

### Command Line

Run the compatibility analysis:

```bash
/opt/genestack/bin/analyze-openstack-compatibility.sh
```

Or use the Python script directly:

```bash
python3 /opt/genestack/genestack-intelligence/openstack_compatibility.py --repo-path /opt/genestack
```

### Streamlit Dashboard

1. Navigate to the Genestack Intelligence Dashboard
2. Scroll to the "OpenStack Compatibility Analysis" section
3. Click "🔄 Run Compatibility Analysis"
4. Review the color-coded compatibility table
5. Export results as CSV if needed

## Output Format

The compatibility table includes:

| Column | Description |
|--------|-------------|
| Component | OpenStack component name |
| Detected Version | Version found in repository |
| Required Compatible Version | Expected version for compatibility |
| Source | File path where version was detected |
| Status | OK, WARNING, or ERROR |
| Notes | Detailed compatibility information |

## Status Meanings

### ✅ OK (Green)
- Component is compatible with the detected OpenStack release
- No issues found

### ⚠️ WARNING (Yellow)
- Potential compatibility issue detected
- May work but not recommended
- Review recommended before deployment

### ❌ ERROR (Red)
- Critical compatibility issue
- Component will likely fail or cause issues
- Must be fixed before deployment

## Compatibility Checks

### 1. Release Alignment

All OpenStack components must belong to the same release family:

**Example:**
- Nova 29.x (Caracal) ✅
- Neutron 24.x (Caracal) ✅
- Placement 9.x (Caracal) ✅
- Keystone 25.x (Caracal) ✅

**Error Example:**
- Nova 29.x (Caracal) ✅
- Neutron 25.x (Dalmatian) ❌

**Resolution:**
Upgrade or downgrade components to match the target release.

### 2. API Microversion Compatibility

Services must support compatible API microversion ranges:

- Nova requires Placement to support specific microversions
- Cinder attachment API must match Nova's requirements
- Services query each other's APIs and must be compatible

**Resolution:**
Ensure all services are on the same release, which guarantees API compatibility.

### 3. Container Image Alignment

All container images should use the same OpenStack release tag:

**Error Example:**
```
Nova image: ghcr.io/.../nova:2024.1-latest
Keystone image: ghcr.io/.../keystone:2025.1-latest  ❌
```

**Resolution:**
Update all image tags to use the same release (e.g., all 2024.1 or all 2025.1).

### 4. Python Library Compatibility

oslo.* libraries must match OpenStack release constraints:

**Check:**
- `oslo.messaging` version
- `oslo.config` version
- `oslo.db` version
- Other oslo.* packages

**Resolution:**
Use the official OpenStack release constraints:
https://releases.openstack.org/constraints/

### 5. Kubernetes API Compatibility

Detects deprecated Kubernetes API versions:

**Deprecated APIs:**
- `apps/v1beta1` (removed in Kubernetes 1.16+)
- `apps/v1beta2` (removed in Kubernetes 1.16+)
- `extensions/v1beta1` (removed in Kubernetes 1.16+)
- `networking.k8s.io/v1beta1` (removed in Kubernetes 1.19+)

**Resolution:**
Update manifests to use current API versions.

## Report Locations

Reports are automatically saved to:

```
reports/YYYY-MM-DD/
├── openstack-compat-table.md    # Markdown table format
└── openstack-compat-table.csv   # CSV format for spreadsheet tools
```

## Example Output

```
| Component | Detected Version | Required Compatible Version | Source | Status | Notes |
|-----------|------------------|----------------------------|--------|--------|-------|
| nova | 2024.2.555+... | 30.x | helm-chart-versions.yaml | WARNING | Version may not match expected range |
| blazar | 2025.1.3+... | 6.x | helm-chart-versions.yaml | ERROR | Component belongs to 2025.1 release, but deployment targets 2024.2 |
| Container Images | 2024.1, 2025.1 | Single release | Helm configs | ERROR | Service images belong to different releases |
```

## Integration with CI/CD

Add to your CI/CD pipeline:

```yaml
# .github/workflows/compatibility-check.yml
name: OpenStack Compatibility Check
on:
  pull_request:
    paths:
      - 'base-helm-configs/**'
      - 'helm-chart-versions.yaml'
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check Compatibility
        run: |
          python3 genestack-intelligence/openstack_compatibility.py
      - name: Check for Errors
        run: |
          if grep -q "ERROR" reports/*/openstack-compat-table.csv; then
            echo "Compatibility errors found!"
            exit 1
          fi
```

## Troubleshooting

### No components detected

- Ensure `helm-chart-versions.yaml` exists
- Check that Helm config files are in `base-helm-configs/`
- Verify file permissions

### False positives

- Version format may not match expected patterns
- Review the Notes column for details
- Some warnings may be acceptable (e.g., patch versions)

### Missing release detection

- Ensure at least one component has a clear release version
- Check image tags in Helm configs
- Verify version format matches OpenStack release patterns

## OpenStack Release Reference

For official release information:

- **Release Matrix**: https://releases.openstack.org/
- **Constraints**: https://releases.openstack.org/constraints/
- **API Versions**: https://docs.openstack.org/api/

## Best Practices

1. **Run before deployment**: Always check compatibility before deploying
2. **Regular checks**: Run analysis after updating component versions
3. **Fix errors first**: Address ERROR status items before WARNING items
4. **Document exceptions**: If warnings are acceptable, document why
5. **Version lock**: Use explicit version pins in `helm-chart-versions.yaml`

## Related Documentation

- [Version Inventory](version-inventory.md) - Complete component version tracking
- [OpenStack Component Versions](openstack-component-versions.md) - How to check actual software versions
- [Genestack Upgrade Guide](genestack-upgrade.md) - Upgrade procedures
