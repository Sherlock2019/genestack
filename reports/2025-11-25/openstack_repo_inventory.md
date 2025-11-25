# OpenStack Repository Component Inventory

Generated: 2025-11-25 00:06:58

Repository: /root/genestack

## Release Distribution

- **Caracal (2024.1)**: 16 components
- **Dalmatian (2024.2)**: 15 components
- **Epoxy (2025.1)**: 8 components

## Component Inventory

| Component | Version Detected | Real Version | File | Mapped Release | Compatibility Issues | Recommended Stack |
|-----------|------------------|--------------|------|----------------|---------------------|-------------------|
| barbican | 2024.2.208+13651f45 | dalmatian v2.208 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| blazar | 2025.1.3+95bf0bf6e | epoxy v1.3 | helm-chart-versions.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| ceilometer | 2024.2.115+13651f45 | dalmatian v2.115 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| cinder | 2024.2.409+13651f45 | dalmatian v2.409 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal); CORE_SERVICE_MISMATCH | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| cloudkitty | 2025.1.2+ebb1488dc | epoxy v1.2 | helm-chart-versions.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| freezer | 2025.1.2+cdd5c6c55 | epoxy v1.2 | helm-chart-versions.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| glance | 2024.2.396+13651f45 | dalmatian v2.396 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal); CORE_SERVICE_MISMATCH | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| gnocchi | 2024.2.52+22 | dalmatian v2.52 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| heat | 2024.2.294+13651f45 | dalmatian v2.294 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| horizon | 2024.2.264+13651f45 | dalmatian v2.264 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| ironic | 2024.2.121+13651f45 | dalmatian v2.121 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| keystone | 2024.2.386+13651f45 | dalmatian v2.386 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal); CORE_SERVICE_MISMATCH | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| magnum | 2024.2.157+13651f45 | dalmatian v2.157 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| masakari | 2024.2.17+13651f45 | dalmatian v2.17 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| neutron | 2024.2.529+13651f45 | dalmatian v2.529 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal); CORE_SERVICE_MISMATCH | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| nova | 2024.2.555+13651f45 | dalmatian v2.555 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal); CORE_SERVICE_MISMATCH | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| octavia | 2025.1.15+b1e463122 | epoxy v1.15 | helm-chart-versions.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| placement | 2024.2.62+13651f45 | dalmatian v2.62 | helm-chart-versions.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal); CORE_SERVICE_MISMATCH | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| zaqar | 2025.2.0+2d37d445c | Unknown | helm-chart-versions.yaml | None | VERSION_UNMAPPABLE | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| heat | 2024.1-latest | caracal v1 | base-helm-configs/ironic/ironic-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| glance | 2024.1-latest | caracal v1 | base-helm-configs/glance/glance-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy); CORE_SERVICE_MISMATCH | Caracal (2024.1) — Fully compatible |
| masakari | 2024.1-latest | caracal v1 | base-helm-configs/masakari/masakari-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| gnocchi | 2024.1-ubuntu_jammy | caracal v1 | base-helm-configs/gnocchi/gnocchi-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| cinder | 2024.1-latest | caracal v1 | base-helm-configs/cinder/cinder-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy); CORE_SERVICE_MISMATCH | Caracal (2024.1) — Fully compatible |
| cloudkitty | 2024.1-latest | caracal v1 | base-helm-configs/cloudkitty/cloudkitty-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| heat | 2025.1-latest | epoxy v1 | base-helm-configs/zaqar/zaqar-helm-overrides.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| zaqar | 2025.1-latest | epoxy v1 | base-helm-configs/zaqar/zaqar-helm-overrides.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| horizon | 2024.1-latest | caracal v1 | base-helm-configs/horizon/horizon-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| designate | 2024.1-latest | caracal v1 | base-helm-configs/designate/designate-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| ceilometer | 2024.1-ubuntu_jammy | caracal v1 | base-helm-configs/ceilometer/ceilometer-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| blazar | 2025.1-latest | epoxy v1 | base-helm-configs/blazar/blazar-helm-overrides.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| magnum | 2024.1-latest | caracal v1 | base-helm-configs/magnum/magnum-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| placement | 2024.1-latest | caracal v1 | base-helm-configs/placement/placement-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy); CORE_SERVICE_MISMATCH; PLACEMENT/NOVA_MISMATCH | Caracal (2024.1) — Fully compatible |
| neutron | 2024.1-latest | caracal v1 | base-helm-configs/neutron/neutron-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy); CORE_SERVICE_MISMATCH | Caracal (2024.1) — Fully compatible |
| barbican | 2024.1-latest | caracal v1 | base-helm-configs/barbican/barbican-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| nova | 2024.1-latest | caracal v1 | base-helm-configs/nova/nova-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy); CORE_SERVICE_MISMATCH | Caracal (2024.1) — Fully compatible |
| freezer | 2025.1-latest | epoxy v1 | base-helm-configs/freezer/freezer-helm-overrides.yaml | Epoxy | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Dalmatian, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| keystone | 2024.1-latest | caracal v1 | base-helm-configs/keystone/keystone-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy); CORE_SERVICE_MISMATCH | Caracal (2024.1) — Fully compatible |
| octavia | 2024.1-latest | caracal v1 | base-helm-configs/octavia/octavia-helm-overrides.yaml | Caracal | MIXED_RELEASES (Dalmatian, Epoxy) | Caracal (2024.1) — Fully compatible |
| skyline | 2024.2-latest | dalmatian v2 | base-kustomize/skyline/base/deployment-apiserver.yaml | Dalmatian | MAJOR_RELEASE_MISMATCH (target: Caracal); MIXED_RELEASES (Epoxy, Caracal) | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
| octavia | 3 | Unknown | ansible/playbooks/octavia-preconf-main.yaml | None | VERSION_UNMAPPABLE | Unify to Caracal (2024.1). Mixed releases detected: Dalmatian (2024.2), Epoxy (2025.1), Caracal (2024.1) |
