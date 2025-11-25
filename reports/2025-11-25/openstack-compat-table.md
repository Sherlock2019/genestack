# OpenStack Compatibility Analysis

Generated: 2025-11-25 03:07:58

**Detected OpenStack Release**: 2024.2 (Dalmatian)

| Component | Detected Version | Required Compatible Version | Source | Status | Notes |
|-----------|------------------|----------------------------|--------|--------|-------|
| barbican | 2024.2.208+13651f45-628a320c | 16.x | helm-chart-versions.yaml | WARNING | Version 2024.2.208+13651f45-628a320c may not match expected range 16.x for 2024.2 release. |
| blazar | 2025.1.3+95bf0bf6e | 6.x | helm-chart-versions.yaml | ERROR | Component version belongs to 2025.1 release, but deployment targets 2024.2 (Dalmatian). |
| ceilometer | 2024.2.115+13651f45-628a320c | 19.x | helm-chart-versions.yaml | WARNING | Version 2024.2.115+13651f45-628a320c may not match expected range 19.x for 2024.2 release. |
| cinder | 2024.2.409+13651f45-628a320c | 26.x | helm-chart-versions.yaml | WARNING | Version 2024.2.409+13651f45-628a320c may not match expected range 26.x for 2024.2 release. |
| cloudkitty | 2025.1.2+ebb1488dc | 13.x | helm-chart-versions.yaml | ERROR | Component version belongs to 2025.1 release, but deployment targets 2024.2 (Dalmatian). |
| freezer | 2025.1.2+cdd5c6c55 | 5.x | helm-chart-versions.yaml | ERROR | Component version belongs to 2025.1 release, but deployment targets 2024.2 (Dalmatian). |
| glance | 2024.2.396+13651f45-628a320c | 31.x | helm-chart-versions.yaml | WARNING | Version 2024.2.396+13651f45-628a320c may not match expected range 31.x for 2024.2 release. |
| gnocchi | 2024.2.52+22.15d38 | 5.x | helm-chart-versions.yaml | WARNING | Version 2024.2.52+22.15d38 may not match expected range 5.x for 2024.2 release. |
| heat | 2024.2.294+13651f45-628a320c | 22.x | helm-chart-versions.yaml | WARNING | Version 2024.2.294+13651f45-628a320c may not match expected range 22.x for 2024.2 release. |
| horizon | 2024.2.264+13651f45-628a320c | 26.x | helm-chart-versions.yaml | WARNING | Version 2024.2.264+13651f45-628a320c may not match expected range 26.x for 2024.2 release. |
| ironic | 2024.2.121+13651f45-628a320c | 23.x | helm-chart-versions.yaml | WARNING | Version 2024.2.121+13651f45-628a320c may not match expected range 23.x for 2024.2 release. |
| keystone | 2024.2.386+13651f45-628a320c | 26.x | helm-chart-versions.yaml | WARNING | Version 2024.2.386+13651f45-628a320c may not match expected range 26.x for 2024.2 release. |
| magnum | 2024.2.157+13651f45-628a320c | 12.x | helm-chart-versions.yaml | WARNING | Version 2024.2.157+13651f45-628a320c may not match expected range 12.x for 2024.2 release. |
| masakari | 2024.2.17+13651f45-628a320c | 7.x | helm-chart-versions.yaml | WARNING | Version 2024.2.17+13651f45-628a320c may not match expected range 7.x for 2024.2 release. |
| neutron | 2024.2.529+13651f45-628a320c | 25.x | helm-chart-versions.yaml | WARNING | Version 2024.2.529+13651f45-628a320c may not match expected range 25.x for 2024.2 release. |
| nova | 2024.2.555+13651f45-628a320c | 30.x | helm-chart-versions.yaml | WARNING | Version 2024.2.555+13651f45-628a320c may not match expected range 30.x for 2024.2 release. |
| octavia | 2025.1.15+b1e463122 | 13.x | helm-chart-versions.yaml | ERROR | Component version belongs to 2025.1 release, but deployment targets 2024.2 (Dalmatian). |
| placement | 2024.2.62+13651f45-628a320c | 10.x | helm-chart-versions.yaml | WARNING | Version 2024.2.62+13651f45-628a320c may not match expected range 10.x for 2024.2 release. |
| zaqar | 2025.2.0+2d37d445c | 11.x | helm-chart-versions.yaml | ERROR | Component version belongs to 2025.2 release, but deployment targets 2024.2 (Dalmatian). |
