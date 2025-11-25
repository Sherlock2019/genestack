# OpenStack GitHub Version Resolution

Resolves actual OpenStack component versions by querying GitHub API to find tags and release trains from commit SHAs.

## Overview

The GitHub Version Resolver:

1. **Extracts commit SHAs** from version strings in your repository
2. **Queries GitHub API** to get commit information
3. **Finds nearest tags** that match or are ancestors of the commit
4. **Determines release trains** from official OpenStack releases
5. **Compares compatibility** across all services
6. **Recommends versions** for incompatible components

## How It Works

### Step 1: SHA Extraction

Extracts commit SHAs from version patterns:
- `2024.2.208+13651f45-628a320c` → SHA: `13651f45`
- `2025.1.3+95bf0bf6e` → SHA: `95bf0bf6e`
- `2024.1-latest` → No SHA (uses version as-is)

### Step 2: GitHub API Queries

For each component with a SHA:

1. **Query commit**: `GET /repos/openstack/{component}/commits/{sha}`
2. **Query tags**: `GET /repos/openstack/{component}/tags`
3. **Find nearest tag**: Matches commit SHA or finds ancestor tag

### Step 3: Release Train Determination

Maps versions to OpenStack release trains:
- `2025.1.x` → `epoxy`
- `2024.2.x` → `dalmatian`
- `2024.1.x` → `caracal`
- `2023.2.x` → `bobcat`
- etc.

### Step 4: Compatibility Analysis

- **All same train** → ✔ Compatible
- **Mixed trains** → ❌ Incompatible
- **Recommendation**: Use majority release train

## Usage

### Command Line

```bash
# Uses public API (no authentication required)
/opt/genestack/bin/resolve-openstack-github-versions.sh
```

Or use Python directly:

```bash
python3 /opt/genestack/genestack-intelligence/openstack_github_version_resolver.py \
    --repo-path /opt/genestack
```

**Note**: No GitHub token required! The resolver uses GitHub's public API which works without authentication.

### Streamlit Dashboard

1. Navigate to "GitHub Version Resolution" section
2. Click "🔗 Resolve from GitHub" (no authentication required)
3. Wait for API queries to complete (may take a few minutes due to rate limits)
4. Review resolved versions and compatibility

## Output Format

| Component | Repo Version | Upstream SHA | Real Version | Release Train | Compatibility Status | Recommended Version | Source Links |

### Example Output

```
| Component | Repo Version | Upstream SHA | Real Version | Release Train | Compatibility Status | Recommended Version | Source Links |
|-----------|--------------|--------------|--------------|---------------|---------------------|-------------------|-------------|
| keystone | 2024.2.386+... | 13651f45 | 2024.2.0 | dalmatian | ✔ Compatible | - | Commit: https://github.com/openstack/keystone/commit/... |
| nova | 2024.2.555+... | 13651f45 | 2024.2.0 | dalmatian | ✔ Compatible | - | Commit: https://github.com/openstack/nova/commit/... |
| blazar | 2025.1.3+... | 95bf0bf6e | 2025.1.0 | epoxy | ❌ Incompatible | Use dalmatian release train | Commit: https://github.com/openstack/blazar/commit/... |
```

## GitHub API Rate Limits

The resolver uses GitHub's public API which **does not require authentication**.

### Public API (No Token Required)
- **60 requests/hour**
- Works without any authentication
- Automatically handles rate limiting with delays
- May take a few minutes for many components (but works reliably)

### Optional: With Token (Faster)
If you have a GitHub token, you can optionally use it for faster resolution:
- **5,000 requests/hour** (much faster)
- Set as environment variable: `export GITHUB_TOKEN=your_token`
- Not required - the resolver works fine without it

## Output Files

All reports saved to `reports/YYYY-MM-DD/`:

1. **openstack_github_resolved_versions.csv** - CSV table
2. **openstack_github_resolved_versions.md** - Markdown table
3. **openstack_github_resolved_versions.json** - Complete JSON data

## Component Mapping

The resolver maps component names to GitHub repositories:

- `keystone` → `openstack/keystone`
- `nova` → `openstack/nova`
- `neutron` → `openstack/neutron`
- `glance` → `openstack/glance`
- `cinder` → `openstack/cinder`
- etc.

## Release Train Compatibility

### Compatible (✔)
All components use the same release train:
- All `caracal` (2024.1)
- All `dalmatian` (2024.2)
- All `epoxy` (2025.1)

### Incompatible (❌)
Mixed release trains detected:
- Some `caracal`, some `dalmatian`
- Some `epoxy`, some `caracal`

**Resolution**: Unify to majority release train.

## Limitations

1. **Rate Limits**: Public API limited to 60 requests/hour (automatically handled with delays)
2. **Partial SHAs**: Short SHAs may not resolve correctly
3. **Tag Matching**: May not find exact tag if commit is between tags
4. **Network Required**: Must have internet access to GitHub API
5. **Processing Time**: May take a few minutes for many components due to rate limiting

## Troubleshooting

### Rate Limit Exceeded

The resolver automatically handles rate limits by waiting and retrying. If you see rate limit messages, the resolver will automatically wait and continue. This is normal behavior for the public API.

### SHA Not Found

```
Upstream SHA: 13651f45
Real Version: 2024.2.208+13651f45 (fallback)
```

**Cause**: Commit SHA not found in repository
**Solution**: Verify SHA is correct, may be from different branch

### Component Not Mapped

```
Component: unknown-service
Upstream SHA: N/A
```

**Cause**: Component name not in `COMPONENT_REPOS` mapping
**Solution**: Add component to mapping in resolver code

## Integration

### CI/CD Pipeline

```yaml
name: Resolve OpenStack Versions
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  resolve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Resolve Versions
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 genestack-intelligence/openstack_github_version_resolver.py
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: github-resolved-versions
          path: reports/**/openstack_github_resolved_*
```

## Related Documentation

- [Repository Scanner](openstack-repo-scanner.md) - Initial repository scanning
- [Compatibility Analysis](openstack-compatibility-analysis.md) - Detailed compatibility checks
- [Version Inventory](version-inventory.md) - Complete component tracking
