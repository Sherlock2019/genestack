#!/bin/bash
# Script to get actual software versions of all OpenStack components
# This script queries running pods to get the actual package versions

set -e

NAMESPACE=${NAMESPACE:-openstack}

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
echo "Namespace: $NAMESPACE"
echo ""

declare -A versions

for service_info in "${services[@]}"; do
    IFS=':' read -r service pod_label <<< "$service_info"
    
    # Try to find pod with app label
    pod=$(kubectl -n $NAMESPACE get pods -l app=$pod_label --no-headers 2>/dev/null | head -1 | awk '{print $1}')
    
    if [ -z "$pod" ]; then
        # Try alternative: look for pod name containing service name
        pod=$(kubectl -n $NAMESPACE get pods --no-headers 2>/dev/null | grep -i "$service" | head -1 | awk '{print $1}')
    fi
    
    if [ -z "$pod" ]; then
        versions[$service]="N/A (pod not found)"
        printf "%-20s %s\n" "$service:" "N/A (pod not found)"
        continue
    fi
    
    # Try pip show first (most reliable)
    version=$(kubectl -n $NAMESPACE exec $pod -- pip show $service 2>/dev/null | grep "^Version:" | awk '{print $2}' | head -1 | tr -d '\r\n')
    
    # If that fails, try Python import
    if [ -z "$version" ] || [ "$version" == "" ]; then
        version=$(kubectl -n $NAMESPACE exec $pod -- python3 -c "import $service; print($service.__version__)" 2>/dev/null | head -1 | tr -d '\r\n')
    fi
    
    # Handle special cases for services with different module names
    if [ -z "$version" ] || [ "$version" == "" ]; then
        case $service in
            "placement")
                version=$(kubectl -n $NAMESPACE exec $pod -- python3 -c "import openstack.placement; print(openstack.placement.__version__)" 2>/dev/null | head -1 | tr -d '\r\n')
                if [ -z "$version" ]; then
                    version=$(kubectl -n $NAMESPACE exec $pod -- pip show openstack-placement 2>/dev/null | grep "^Version:" | awk '{print $2}' | head -1 | tr -d '\r\n')
                fi
                ;;
            "horizon")
                version=$(kubectl -n $NAMESPACE exec $pod -- pip show openstack-dashboard 2>/dev/null | grep "^Version:" | awk '{print $2}' | head -1 | tr -d '\r\n')
                if [ -z "$version" ]; then
                    version=$(kubectl -n $NAMESPACE exec $pod -- python3 -c "import horizon; print(horizon.__version__)" 2>/dev/null | head -1 | tr -d '\r\n')
                fi
                ;;
            "ceilometer")
                version=$(kubectl -n $NAMESPACE exec $pod -- pip show python-ceilometer 2>/dev/null | grep "^Version:" | awk '{print $2}' | head -1 | tr -d '\r\n')
                ;;
            "gnocchi")
                version=$(kubectl -n $NAMESPACE exec $pod -- pip show gnocchi 2>/dev/null | grep "^Version:" | awk '{print $2}' | head -1 | tr -d '\r\n')
                ;;
        esac
    fi
    
    if [ -z "$version" ] || [ "$version" == "" ]; then
        versions[$service]="N/A (version not found)"
        printf "%-20s %s\n" "$service:" "N/A (version not found)"
    else
        versions[$service]="$version"
        printf "%-20s %s\n" "$service:" "$version"
    fi
done

echo ""
echo "=================================================="
echo "Summary (for documentation):"
echo ""
echo "| Component | Software Version | Release Name | Notes |"
echo "|-----------|-----------------|--------------|-------|"

# Map release names based on version patterns
declare -A release_map
release_map["2024.1"]="Caracal"
release_map["2024.2"]="Dalmatian"
release_map["2025.1"]="Epoxy"

for service_info in "${services[@]}"; do
    IFS=':' read -r service pod_label <<< "$service_info"
    version="${versions[$service]}"
    
    # Try to determine release name from image tag
    config_file="base-helm-configs/${service}/${service}-helm-overrides.yaml"
    if [ -f "$config_file" ]; then
        if [ "$service" == "ironic" ]; then
            release_tag=$(grep "ironic_api:" "$config_file" 2>/dev/null | grep -oE "202[0-9].[0-9]" | head -1)
        elif [ "$service" == "ceilometer" ]; then
            release_tag=$(grep "ceilometer_central:" "$config_file" 2>/dev/null | grep -oE "202[0-9].[0-9]" | head -1)
        elif [ "$service" == "gnocchi" ]; then
            release_tag=$(grep "gnocchi_api:" "$config_file" 2>/dev/null | grep -oE "202[0-9].[0-9]" | head -1)
        else
            release_tag=$(grep "${service}_api:" "$config_file" 2>/dev/null | grep -oE "202[0-9].[0-9]" | head -1)
        fi
    fi
    
    release_name="${release_map[$release_tag]:-Unknown}"
    
    # Get service description
    case $service in
        "keystone") desc="Identity service" ;;
        "glance") desc="Image service" ;;
        "nova") desc="Compute service" ;;
        "cinder") desc="Block storage service" ;;
        "neutron") desc="Networking service" ;;
        "heat") desc="Orchestration service" ;;
        "barbican") desc="Key management service" ;;
        "placement") desc="Resource placement service" ;;
        "octavia") desc="Load balancing service" ;;
        "magnum") desc="Container orchestration service" ;;
        "masakari") desc="Instance high availability service" ;;
        "ceilometer") desc="Telemetry service" ;;
        "gnocchi") desc="Metric storage service" ;;
        "cloudkitty") desc="Rating service" ;;
        "ironic") desc="Bare metal provisioning service" ;;
        "designate") desc="DNS service" ;;
        "zaqar") desc="Messaging service" ;;
        "blazar") desc="Resource reservation service" ;;
        "freezer") desc="Backup and restore service" ;;
        "horizon") desc="Web dashboard" ;;
        *) desc="OpenStack service" ;;
    esac
    
    printf "| %-9s | %-16s | %-12s | %s |\n" "$service" "$version" "$release_name" "$desc"
done
