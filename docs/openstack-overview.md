# Building the cloud

![Genestack Logo](assets/images/genestack-logo.png){ align=right }

## The DNA of our services

The DNA of the OpenStack services has been built to scale, and be managed in a pseudo light-outs environment. We're aiming to empower operators to do more, simply and easily. The high level tenets we started our project from are simple and were written with intention. We're building Genestack not to show off how complex our platform is or how smart our engineers are, we're building systems to show how simple cloud deployment, operations, and maintenance can be.

## Core Tenets
* All services make use of our core infrastructure which is all managed by operators.
    * Rollback and versioning is present and a normal feature of our operations.
* Backups, rollbacks, and package management all built into our applications delivery.
* Databases, users, and grants are all run against a cluster which is setup for OpenStack to use a single right, and read from many.
    * The primary node is part of application service discovery and will be automatically promoted / demoted within the cluster as needed.
* Queues, permissions, vhosts, and users are all backed by a cluster with automatic failover. All of the queues deployed in the environment are done with Quorum queues, giving us a best of bread queing platform which gracefully recovers from faults while maintaining performance.
* Horizontal scaling groups have been applied to all of our services. This means we'll be able to auto scale API applications up and down based on the needs of the environment.

## Deployment choices

When you're building the cloud, you have a couple of deployment choices, the most fundamental of which is `base` or `aio`.

* `base` creates a production-ready environment that ensures an HA system is deployed across the hardware available in your cloud.
* `aio` creates a minimal cloud environment which is suitable for test, which may have low resources.

The following examples all assume the use of a production environment, however, if you change `base` to `aio`, the deployment footprint will be changed for a given service.

!!! info

    From this point forward we're building our OpenStack cloud. The following commands will leverage `helm` as the package manager and `kustomize` as our configuration management backend.

## OpenStack Component Versions

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
