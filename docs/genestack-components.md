# Product Component Matrix

The following components are part of the initial product release
and largely deployed with Helm+Kustomize against the K8s API (v1.28 and up).

| Group      | Component             | Status   |
|------------|-----------------------|----------|
| Kubernetes | Kubernetes            | Included |
| Kubernetes | Kubernetes Dashboard  | Included |
| Kubernetes | Cert-Manager          | Included |
| Kubernetes | MetaLB (L2/L3)        | Included |
| Kubernetes | Core DNS              | Included |
| Kubernetes | Nginx Gateway API     | Removed  |
| Kubernetes | Kube-Proxy (IPVS)     | Included |
| Kubernetes | Calico                | Optional |
| Kubernetes | Kube-OVN              | Included |
| Kubernetes | Helm                  | Included |
| Kubernetes | Kustomize             | Included |
| Kubernetes | ArgoCD                | Optional |
| OpenStack  | openVswitch (Helm)    | Optional |
| OpenStack  | mariaDB (Operator)    | Included |
| OpenStack  | rabbitMQ (Operator)   | Included |
| OpenStack  | memcacheD (Operator)  | Included |
| OpenStack  | Ceph Rook             | Optional |
| OpenStack  | iscsi/tgtd            | Included |
| OpenStack  | Aodh (Helm)           | Optional |
| OpenStack  | Ceilometer (Helm)     | Optional |
| OpenStack  | Keystone (Helm)       | Included |
| OpenStack  | Glance (Helm)         | Included |
| OpenStack  | Cinder (Helm)         | Included |
| OpenStack  | Nova (Helm)           | Included |
| OpenStack  | Neutron (Helm)        | Included |
| OpenStack  | Placement (Helm)      | Included |
| OpenStack  | Horizon (Helm)        | Included |
| OpenStack  | Skyline (Helm)        | Optional |
| OpenStack  | Heat (Helm)           | Included |
| OpenStack  | Designate (Helm)      | Optional |
| OpenStack  | Barbican (Helm)       | Included |
| OpenStack  | Octavia (Helm)        | Included |
| OpenStack  | Ironic (Helm)         | Optional |
| OpenStack  | Magnum (Helm)         | Optional |
| OpenStack  | Masakari (Helm)       | Optional |
| OpenStack  | Cloudkitty (Helm)     | Optional |
| OpenStack  | Blazar (Helm)         | Optional |
| OpenStack  | Freezer (Helm)        | Optional |
| OpenStack  | metal3.io             | Planned  |
| OpenStack  | PostgreSQL (Operator) | Included |
| OpenStack  | Consul                | Planned  |

Initial monitoring components consists of the following projects

| Group      | Component          | Status   |
|------------|--------------------|----------|
| Kubernetes | Prometheus         | Included |
| Kubernetes | Alertmanager       | Included |
| Kubernetes | Grafana            | Included |
| Kubernetes | Node Exporter      | Included |
| Kubernetes | Kube State Metrics | Included |
| Kubernetes | redfish Exporter   | Included |
| OpenStack  | OpenStack Exporter | Included |
| OpenStack  | RabbitMQ Exporter  | Included |
| OpenStack  | Mysql Exporter     | Included |
| OpenStack  | memcacheD Exporter | Included |
| OpenStack  | Postgres Exporter  | Included |
| Kubernetes | Thanos             | Optional |

## OpenStack Component Software Versions

The following table lists all OpenStack components and their software versions currently being used in Genestack:

| Component | Release Version | Release Name | Notes |
|-----------|-----------------|--------------|-------|
| Keystone | 2024.1 | Caracal | Identity service |
| Glance | 2024.1 | Caracal | Image service |
| Heat | 2024.1 | Caracal | Orchestration service |
| Barbican | 2024.1 | Caracal | Key management service |
| Cinder | 2024.1 | Caracal | Block storage service |
| Placement | 2024.1 | Caracal | Resource placement service |
| Nova | 2024.1 | Caracal | Compute service |
| Neutron | 2024.1 | Caracal | Networking service |
| Horizon | 2024.1 | Caracal | Web dashboard |
| Skyline | 2024.2 | Dalmatian | Next-generation dashboard |
| Octavia | 2024.1 | Caracal | Load balancing service |
| Magnum | 2024.1 | Caracal | Container orchestration service |
| Masakari | 2024.1 | Caracal | Instance high availability service |
| Ceilometer | 2024.1 | Caracal | Telemetry service |
| Gnocchi | 2024.1 | Caracal | Metric storage service |
| Cloudkitty | 2024.1 | Caracal | Rating service |
| Ironic | 2024.1 | Caracal | Bare metal provisioning service |
| Designate | 2024.1 | Caracal | DNS service |
| Zaqar | 2025.1 | Epoxy | Messaging service |
| Blazar | 2025.1 | Epoxy | Resource reservation service |
| Freezer | 2025.1 | Epoxy | Backup and restore service |

!!! note "Version Information"

    **Release Names vs Software Versions**: The values shown in the "Software Version" column (2024.1, 2024.2, 2025.1) are OpenStack release names, not the actual software package versions. The actual software versions (e.g., `27.0.0`, `28.0.0`) can be checked from running pods using the commands documented in [OpenStack Component Versions](openstack-component-versions.md).
    
    To get the actual software versions of all components, run:
    
    ```bash
    /opt/genestack/bin/get-openstack-versions.sh
    ```
    
    This script queries running pods to extract the actual package versions installed in each service container.
    
    Component release names are determined by the image tags specified in the Helm override files located in `/etc/genestack/base-helm-configs/`. Most components are currently on OpenStack 2024.1 (Caracal), with some components upgraded to 2025.1 (Epoxy). Skyline is on 2024.2 (Dalmatian).
