# OpenStack Component Software Versions

This document describes how to check the actual software version of each OpenStack component deployed in Genestack.

## Methods to Check Versions

There are several ways to check the software version of OpenStack components:

### Method 1: Using pip show (Recommended)

Get the version from the Python package installed in the container:

```bash
# Get a pod name for the service
POD=$(kubectl -n openstack get pods -l app=keystone-api --no-headers | head -1 | awk '{print $1}')

# Check version using pip
kubectl -n openstack exec $POD -- pip show keystone | grep Version
```

### Method 2: Using Python import

Check the version using Python's `__version__` attribute:

```bash
kubectl -n openstack exec $POD -- python3 -c "import keystone; print(keystone.__version__)"
```

### Method 3: Using service CLI commands

Some services provide version commands:

```bash
# For services that support --version flag
kubectl -n openstack exec $POD -- keystone --version

# Or using manage commands
kubectl -n openstack exec $POD -- keystone-manage --version
```

### Method 4: Using OpenStack API endpoints

Some services expose version information via their API:

```bash
# Get Keystone version
curl -s http://keystone-api.openstack.svc.cluster.local:5000/v3 | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', {}).get('version', {}).get('id', 'N/A'))"

# Get Nova version
curl -s http://nova-api.openstack.svc.cluster.local:8774/v2.1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', {}).get('version', 'N/A'))"
```

## Commands for Each Component

### Keystone (Identity Service)

```bash
# Get pod
POD=$(kubectl -n openstack get pods -l app=keystone-api --no-headers | head -1 | awk '{print $1}')

# Method 1: pip show
kubectl -n openstack exec $POD -- pip show keystone | grep Version

# Method 2: Python import
kubectl -n openstack exec $POD -- python3 -c "import keystone; print(keystone.__version__)"
```

### Glance (Image Service)

```bash
POD=$(kubectl -n openstack get pods -l app=glance-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show glance | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import glance; print(glance.__version__)"
```

### Nova (Compute Service)

```bash
POD=$(kubectl -n openstack get pods -l app=nova-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show nova | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import nova; print(nova.__version__)"
```

### Cinder (Block Storage Service)

```bash
POD=$(kubectl -n openstack get pods -l app=cinder-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show cinder | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import cinder; print(cinder.__version__)"
```

### Neutron (Networking Service)

```bash
POD=$(kubectl -n openstack get pods -l app=neutron-server --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show neutron | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import neutron; print(neutron.__version__)"
```

### Heat (Orchestration Service)

```bash
POD=$(kubectl -n openstack get pods -l app=heat-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show heat | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import heat; print(heat.__version__)"
```

### Barbican (Key Management Service)

```bash
POD=$(kubectl -n openstack get pods -l app=barbican-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show barbican | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import barbican; print(barbican.__version__)"
```

### Placement (Resource Placement Service)

```bash
POD=$(kubectl -n openstack get pods -l app=placement-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show placement | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import placement; print(placement.__version__)"
```

### Octavia (Load Balancing Service)

```bash
POD=$(kubectl -n openstack get pods -l app=octavia-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show octavia | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import octavia; print(octavia.__version__)"
```

### Magnum (Container Orchestration Service)

```bash
POD=$(kubectl -n openstack get pods -l app=magnum-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show magnum | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import magnum; print(magnum.__version__)"
```

### Masakari (Instance High Availability Service)

```bash
POD=$(kubectl -n openstack get pods -l app=masakari-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show masakari | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import masakari; print(masakari.__version__)"
```

### Ceilometer (Telemetry Service)

```bash
POD=$(kubectl -n openstack get pods -l app=ceilometer-central --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show ceilometer | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import ceilometer; print(ceilometer.__version__)"
```

### Gnocchi (Metric Storage Service)

```bash
POD=$(kubectl -n openstack get pods -l app=gnocchi-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show gnocchi | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import gnocchi; print(gnocchi.__version__)"
```

### Cloudkitty (Rating Service)

```bash
POD=$(kubectl -n openstack get pods -l app=cloudkitty-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show cloudkitty | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import cloudkitty; print(cloudkitty.__version__)"
```

### Ironic (Bare Metal Provisioning Service)

```bash
POD=$(kubectl -n openstack get pods -l app=ironic-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show ironic | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import ironic; print(ironic.__version__)"
```

### Designate (DNS Service)

```bash
POD=$(kubectl -n openstack get pods -l app=designate-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show designate | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import designate; print(designate.__version__)"
```

### Zaqar (Messaging Service)

```bash
POD=$(kubectl -n openstack get pods -l app=zaqar-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show zaqar | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import zaqar; print(zaqar.__version__)"
```

### Blazar (Resource Reservation Service)

```bash
POD=$(kubectl -n openstack get pods -l app=blazar-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show blazar | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import blazar; print(blazar.__version__)"
```

### Freezer (Backup and Restore Service)

```bash
POD=$(kubectl -n openstack get pods -l app=freezer-api --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show freezer | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import freezer; print(freezer.__version__)"
```

### Horizon (Web Dashboard)

```bash
POD=$(kubectl -n openstack get pods -l app=horizon --no-headers | head -1 | awk '{print $1}')
kubectl -n openstack exec $POD -- pip show horizon | grep Version
# or
kubectl -n openstack exec $POD -- python3 -c "import horizon; print(horizon.__version__)"
```

## Automated Script

You can use the following script to check all versions at once:

```bash
#!/bin/bash
# Check all OpenStack component versions

services=(
    "keystone:keystone-api"
    "glance:glance-api"
    "nova:nova-api"
    "cinder:cinder-api"
    "neutron:neutron-server"
    "heat:heat-api"
    "barbican:barbican-api"
    "placement:placement-api"
    "octavia:octavia-api"
    "magnum:magnum-api"
    "masakari:masakari-api"
    "ceilometer:ceilometer-central"
    "gnocchi:gnocchi-api"
    "cloudkitty:cloudkitty-api"
    "ironic:ironic-api"
    "designate:designate-api"
    "zaqar:zaqar-api"
    "blazar:blazar-api"
    "freezer:freezer-api"
    "horizon:horizon"
)

echo "OpenStack Component Software Versions"
echo "====================================="
echo ""

for service_info in "${services[@]}"; do
    IFS=':' read -r service pod_label <<< "$service_info"
    pod=$(kubectl -n openstack get pods -l app=$pod_label --no-headers 2>/dev/null | head -1 | awk '{print $1}')
    
    if [ -z "$pod" ]; then
        printf "%-20s %s\n" "$service:" "N/A (pod not found)"
        continue
    fi
    
    version=$(kubectl -n openstack exec $pod -- pip show $service 2>/dev/null | grep "^Version:" | awk '{print $2}')
    
    if [ -z "$version" ]; then
        version=$(kubectl -n openstack exec $pod -- python3 -c "import $service; print($service.__version__)" 2>/dev/null)
    fi
    
    if [ -z "$version" ]; then
        version="N/A"
    fi
    
    printf "%-20s %s\n" "$service:" "$version"
done
```

## Notes

- The actual software version (e.g., `27.0.0`, `28.0.0`) is different from the release name (e.g., `2024.1 Caracal`, `2025.1 Epoxy`)
- Release names like "Caracal" or "Epoxy" refer to the OpenStack release cycle, not the specific package version
- Software versions follow semantic versioning (major.minor.patch)
- Some services may have different package names or module names, so the import statement may vary
