# Genestack Component Version Inventory

Generated: 2025-11-24 23:55:40

| Component | Type | Version in Repo | Latest Upstream Version | OpenStack Version (Numeric) | OpenStack Release Name | Compatibility | Recommended Upstream | Source Path | Notes |
|---|---|---|---|---|---|---|---|---|---|
| memcached (image) | container-image | 1.6.39-debian-12-r1 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/memcached/memcached-helm-overrides.yaml | Image tag from Helm values |
| memcached (image) | container-image | 12-debian-12-r34 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/memcached/memcached-helm-overrides.yaml | Image tag from Helm values |
| memcached (image) | container-image | 0.15.0-debian-12-r3 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/memcached/memcached-helm-overrides.yaml | Image tag from Helm values |
| grafana (image) | container-image | 10.3.3 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/grafana/grafana-helm-overrides.yaml | Image tag from Helm values |
| redis-sentinel (image) | container-image | v8.2.2 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/redis-sentinel/redis-sentinel-helm-overrides.yaml | Image tag from Helm values |
| redis-sentinel (image) | container-image | v1.44.0 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/redis-sentinel/redis-sentinel-helm-overrides.yaml | Image tag from Helm values |
| openstack-api-exporter-chart | helm-chart | 0.1.0 | N/A | Unknown | Unknown | Unknown | Unknown | base-helm-configs/openstack-api-exporter-chart/Chart.yaml | appVersion: 1.0 |
| kube-prometheus-stack (image) | container-image | v0.26.0 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-prometheus-stack/kube-prometheus-stack-helm-overrides.yaml | Image tag from Helm values |
| kube-prometheus-stack (image) | container-image | v0.34.0 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-prometheus-stack/kube-prometheus-stack-helm-overrides.yaml | Image tag from Helm values |
| kube-prometheus-stack (image) | container-image | v2.49.1 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-prometheus-stack/kube-prometheus-stack-helm-overrides.yaml | Image tag from Helm values |
| kube-prometheus-stack (image) | container-image | v0.34.0 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-prometheus-stack/kube-prometheus-stack-helm-overrides.yaml | Image tag from Helm values |
| kube-ovn (image) | container-image | v1.14.10 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-ovn/kube-ovn-helm-overrides.yaml | Image tag from Helm values |
| postgres-operator (image) | container-image | v1.12.2 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/postgres-operator/postgres-operator-helm-overrides.yaml | Image tag from Helm values |
| cinder | container-base-image | $VERSION | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | Containerfiles/Cinder-volume-netapp-Containerfile | Base image: openstackhelm/cinder |
| ubuntu | container-base-image | 22.04 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | Containerfiles/GnocchiRXT-Containerfile | Base image: ubuntu |
| ubuntu | container-base-image | 22.04 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | Containerfiles/CeilometerRXT-Containerfile | Base image: ubuntu |
| barbican | openstack-service | 2024.2.208+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| blazar | openstack-service | 2025.1.3+95bf0bf6e | N/A | 2025.1 | Epoxy | ❌ Mismatch | 2025.1 (Epoxy) | helm-chart-versions.yaml | OpenStack Helm chart version |
| ceilometer | openstack-service | 2024.2.115+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| cinder | openstack-service | 2024.2.409+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| cloudkitty | openstack-service | 2025.1.2+ebb1488dc | N/A | 2025.1 | Epoxy | ❌ Mismatch | 2025.1 (Epoxy) | helm-chart-versions.yaml | OpenStack Helm chart version |
| freezer | openstack-service | 2025.1.2+cdd5c6c55 | N/A | 2025.1 | Epoxy | ❌ Mismatch | 2025.1 (Epoxy) | helm-chart-versions.yaml | OpenStack Helm chart version |
| glance | openstack-service | 2024.2.396+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| gnocchi | openstack-service | 2024.2.52+22.15d38 | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| heat | openstack-service | 2024.2.294+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| horizon | openstack-service | 2024.2.264+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| ironic | openstack-service | 2024.2.121+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| keystone | openstack-service | 2024.2.386+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| magnum | openstack-service | 2024.2.157+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| masakari | openstack-service | 2024.2.17+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| neutron | openstack-service | 2024.2.529+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| nova | openstack-service | 2024.2.555+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| octavia | openstack-service | 2025.1.15+b1e463122 | N/A | 2025.1 | Epoxy | ❌ Mismatch | 2025.1 (Epoxy) | helm-chart-versions.yaml | OpenStack Helm chart version |
| placement | openstack-service | 2024.2.62+13651f45-628a320c | N/A | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | helm-chart-versions.yaml | OpenStack Helm chart version |
| zaqar | openstack-service | 2025.2.0+2d37d445c | N/A | Unknown | Unknown | Unknown | Unknown | helm-chart-versions.yaml | OpenStack Helm chart version |
| masakari (image) | openstack-service-image | ghcr.io/rackerlabs/genestack-images/masakari:2024.1-latest | N/A | Unknown | Unknown | Unknown | Unknown | base-helm-configs/masakari/masakari-helm-overrides.yaml | OpenStack masakari container image tag |
| cloudkitty (image) | openstack-service-image | ghcr.io/rackerlabs/genestack-images/cloudkitty:2024.1-latest | N/A | Unknown | Unknown | Unknown | Unknown | base-helm-configs/cloudkitty/cloudkitty-helm-overrides.yaml | OpenStack cloudkitty container image tag |
| rabbitmq.com | kubernetes-api | rabbitmq.com/v1beta1 | v1.30+ (check K8s docs) | Unknown | Unknown | Unknown | Unknown | manifests/ | Kubernetes API version used in manifests |
| storage.k8s.io | kubernetes-api | storage.k8s.io/v1 | v1.30+ (check K8s docs) | Unknown | Unknown | Unknown | Unknown | manifests/ | Kubernetes API version used in manifests |
| v1 | kubernetes-api | v1 | v1.30+ (check K8s docs) | Unknown | Unknown | Unknown | Unknown | manifests/ | Kubernetes API version used in manifests |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| ceph.rook.io | operator-crd | v1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1 |
| objectbucket.io | operator-crd | v1alpha1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1alpha1 |
| objectbucket.io | operator-crd | v1alpha1 | N/A | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | CRD version: v1alpha1 |
| ansible | python-package | 9.0,<10.0 | 13.0.0 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| ansible-core | python-package | 2.17.0 | 2.20.0 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| cryptography | python-package | 43.0.1 | 46.0.3 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| jinja2 | python-package | 3.1.5 | 3.1.6 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| jmespath | python-package | 1.0.1 | 1.0.1 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| jsonschema | python-package | 4.23.0 | 4.25.1 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| MarkupSafe | python-package | 2.1.3 | 3.0.3 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| netaddr | python-package | 0.9.0 | 1.3.0 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| pbr | python-package | 5.11.1 | 7.0.3 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| kubernetes | python-package | 24.2.0 | 34.1.0 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| openstacksdk | python-package | 1.0.0 | 4.8.0 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| python-openstackclient | python-package | 7.4.0 | 8.2.0 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| dictdiffer | python-package | 0.9.0 | 0.9.0 | Unknown | Unknown | Unknown | Unknown | requirements.txt |  |
| ansible-compat | python-package | 4.1.11 | 25.11.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| ansible-lint | python-package | 24.2.0 | 25.11.1 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| attrs | python-package | 23.2.0 | 25.4.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| black | python-package | 24.3.0 | 25.11.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| bracex | python-package | 2.4 | 2.6 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| click | python-package | 8.1.7 | 8.3.1 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| filelock | python-package | 3.13.1 | 3.20.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| jsonschema | python-package | 4.21.1 | 4.25.1 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| jsonschema-specifications | python-package | 2023.12.1 | 2025.9.1 | 2023.1 | Antelope | ❌ Mismatch | 2023.1 (Antelope) | dev-requirements.txt |  |
| markdown-it-py | python-package | 3.0.0 | 4.0.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| mdurl | python-package | 0.1.2 | 0.1.2 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| mypy-extensions | python-package | 1.0.0 | 1.1.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| pathspec | python-package | 0.12.1 | 0.12.1 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| platformdirs | python-package | 4.2.0 | 4.5.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| pygments | python-package | 2.17.2 | 2.19.2 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| referencing | python-package | 0.33.0 | 0.37.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| reno | python-package | 4.0.0 | 4.1.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| rich | python-package | 13.7.0 | 14.2.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| rpds-py | python-package | 0.17.1 | 0.29.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| subprocess-tee | python-package | 0.4.1 | 0.4.2 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| tomli | python-package | 2.0.1 | 2.3.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| typing-extensions | python-package | 4.9.0 | 4.15.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| wcmatch | python-package | 8.5 | 10.1 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| yamllint | python-package | 1.35.1 | 1.37.1 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| pre_commit | python-package | 4.1.0 | 4.5.0 | Unknown | Unknown | Unknown | Unknown | dev-requirements.txt |  |
| octavia_preconf.amphora_image_version | ansible-role-var | focal | N/A | Unknown | Unknown | Unknown | Unknown | ansible/roles/octavia_preconf/defaults/main.yml | Ansible role variable |
| actions/checkout | github-action | v3 | N/A | Unknown | Unknown | Unknown | Unknown | .github/workflows/genestack-intel.yml | GitHub Action |
| actions/setup-python | github-action | v4 | N/A | Unknown | Unknown | Unknown | Unknown | .github/workflows/genestack-intel.yml | GitHub Action |
| python-version | ci-cd-tool | 3.x | N/A | Unknown | Unknown | Unknown | Unknown | .github/workflows/genestack-intel.yml | CI/CD tool version |
| actions/checkout | github-action | v3 | N/A | Unknown | Unknown | Unknown | Unknown | .github/workflows/genestack-intel-suite.yml | GitHub Action |
| actions/setup-python | github-action | v4 | N/A | Unknown | Unknown | Unknown | Unknown | .github/workflows/genestack-intel-suite.yml | GitHub Action |
| python-version | ci-cd-tool | 3.x | N/A | Unknown | Unknown | Unknown | Unknown | .github/workflows/genestack-intel-suite.yml | CI/CD tool version |
| mariadb | generic-image | 11.4.3 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/mariadb-cluster/base/mariadb-replication.yaml | Image: docker-registry1.mariadb.com/library/mariadb |
| ceph | generic-image | master | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/operator.yaml | Image: rook/ceph |
| description | generic-image |  Image | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | Image: description |
| description | generic-image |  Image | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | Image: description |
| type | generic-image |  string | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | Image: type |
| description | generic-image |  Image | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | Image: description |
| description | generic-image |  Image | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-operator/base/crds.yaml | Image: description |
| mariadb | generic-image | 11.4.3 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/grafana/base/grafana-database.yaml | Image: docker-registry1.mariadb.com/library/mariadb |
| repository | generic-image |  "hashicorp/vault-k8s" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/vault/base/values.yaml | Image: repository |
| repository | generic-image |  "hashicorp/vault" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/vault/base/values.yaml | Image: repository |
| repository | generic-image |  "hashicorp/vault-csi-provider" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/vault/base/values.yaml | Image: repository |
| repository | generic-image |  "hashicorp/vault" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/vault/base/values.yaml | Image: repository |
| kubernetes-entrypoint | generic-image | latest" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/ovn/base/ovn-setup.yaml | Image: "ghcr.io/rackerlabs/genestack-images/kubernetes-entrypoint |
| k8s | generic-image | 1.26.11 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/ovn/base/ovn-setup.yaml | Image: alpine/k8s |
| ovs | generic-image | v3.5.1-latest" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/ovn/base/ovn-setup.yaml | Image: "ghcr.io/rackerlabs/genestack-images/ovs |
| k8s | generic-image | 1.26.11 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/ovn/base/ovn-setup.yaml | Image: alpine/k8s |
| kube-ovn | generic-image | v1.13.13 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/ovn-backup/base/ovn-backup.yaml | Image: docker.io/kubeovn/kube-ovn |
| ceph | generic-image | v18.2.1 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-cluster/base/toolbox.yaml | Image: quay.io/ceph/ceph |
| ceph | generic-image | v18.2.2 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-cluster/base/rook-cluster.yaml | Image: quay.io/ceph/ceph |
| pullPolicy | generic-image |  IfNotPresent | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/vault-secrets-operator/base/values.yaml | Image: pullPolicy |
| pullPolicy | generic-image |  IfNotPresent | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/vault-secrets-operator/base/values.yaml | Image: pullPolicy |
| etcd-backup | generic-image | v0.0.5 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/backups/base/etcd/etcd-backup.yaml | Image: csengteam/etcd-backup |
| etcd-backup | generic-image | v0.0.5 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/backups/base/etcd/etcd-backup.yaml | Image: csengteam/etcd-backup |
| ceph | generic-image | v18.2.2 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-cluster-external-pvc/base/cluster-on-pvc.yaml | Image: quay.io/ceph/ceph |
| ceph | generic-image | v18.2.1 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/rook-cluster-external-pvc/base/toolbox.yaml | Image: quay.io/ceph/ceph |
| kubernetes-entrypoint | generic-image | latest" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/skyline/base/deployment-apiserver.yaml | Image: "ghcr.io/rackerlabs/genestack-images/kubernetes-entrypoint |
| heat | generic-image | 2024.1-latest" | N/A (requires registry access) | 2024.1 | Caracal | ❌ Mismatch | 2024.1 (Caracal) | base-kustomize/skyline/base/deployment-apiserver.yaml | Image: "ghcr.io/rackerlabs/genestack-images/heat |
| yq | generic-image | latest" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-kustomize/skyline/base/deployment-apiserver.yaml | Image: "ghcr.io/linuxserver/yq |
| skyline | generic-image | 2024.2-latest" | N/A (requires registry access) | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | base-kustomize/skyline/base/deployment-apiserver.yaml | Image: "ghcr.io/rackerlabs/genestack-images/skyline |
| skyline | generic-image | 2024.2-latest" | N/A (requires registry access) | 2024.2 | Dalmatian | OK | 2024.2 (Dalmatian) | base-kustomize/skyline/base/deployment-apiserver.yaml | Image: "ghcr.io/rackerlabs/genestack-images/skyline |
| {get_param | generic-image |  image_name | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | testing/build.yaml | Image: {get_param |
| {get_param | generic-image |  image_name | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | testing/build.yaml | Image: {get_param |
| {get_param | generic-image |  image_name | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | testing/build.yaml | Image: {get_param |
| type | generic-image |  string | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | testing/single.yaml | Image: type |
| { get_param | generic-image |  image | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | testing/single.yaml | Image: { get_param |
| enabled | generic-image |  true | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/ironic/ironic-helm-overrides.yaml | Image: enabled |
| registry | generic-image |  docker.io | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/memcached/memcached-helm-overrides.yaml | Image: registry |
| registry | generic-image |  docker.io | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/memcached/memcached-helm-overrides.yaml | Image: registry |
| registry | generic-image |  docker.io | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/memcached/memcached-helm-overrides.yaml | Image: registry |
| tag | generic-image |  "10.3.3" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/grafana/grafana-helm-overrides.yaml | Image: tag |
| ## @param image.registry [default | generic-image |  REGISTRY_NAME] | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/prometheus-kube-event-exporter/values.yaml | Image: ## @param image.registry [default |
| registry | generic-image |  quay.io | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/prometheus-postgres-exporter/values.yaml | Image: registry |
| repository | generic-image |  ghcr.io/openstack-exporter/openstack-exporter | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/monitoring/openstack-metrics-exporter/openstack-metrics-exporter-helm-overrides.yaml | Image: repository |
| repository | generic-image |  ghcr.io/rackerlabs/genestack-images/openstack-exporter | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/openstack-api-exporter-chart/values.yaml | Image: repository |
| "{{ .Values.image.repository }} | generic-image | {{ | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/openstack-api-exporter-chart/templates/all.yaml | Image: "{{ .Values.image.repository }} |
| repository | generic-image |  ghcr.io/mariadb-operator/mariadb-operator | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/mariadb-operator/mariadb-operator-helm-overrides.yaml | Image: repository |
| repository | generic-image |  ghcr.io/mariadb-operator/mariadb-operator | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/mariadb-operator/mariadb-operator-helm-overrides.yaml | Image: repository |
| repository | generic-image |  ghcr.io/mariadb-operator/mariadb-operator | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/mariadb-operator/mariadb-operator-helm-overrides.yaml | Image: repository |
| tag | generic-image |  v0.26.0 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-prometheus-stack/kube-prometheus-stack-helm-overrides.yaml | Image: tag |
| tag | generic-image |  v2.49.1 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-prometheus-stack/kube-prometheus-stack-helm-overrides.yaml | Image: tag |
| tag | generic-image |  v0.34.0 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-prometheus-stack/kube-prometheus-stack-helm-overrides.yaml | Image: tag |
| pullPolicy | generic-image |  IfNotPresent | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/kube-ovn/kube-ovn-helm-overrides.yaml | Image: pullPolicy |
| registry | generic-image |  quay.io | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/prometheus-mysql-exporter/values.yaml | Image: registry |
| repo | generic-image |  "gcr.io/cloud-sql-connectors/cloud-sql-proxy" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/prometheus-mysql-exporter/values.yaml | Image: repo |
| registry | generic-image |  ghcr.io | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/postgres-operator/postgres-operator-helm-overrides.yaml | Image: registry |
| spilo-16 | generic-image | 3.2-p3 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/postgres-operator/postgres-operator-helm-overrides.yaml | Image: ghcr.io/zalando/spilo-16 |
| logical-backup | generic-image | v1.12.2" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/postgres-operator/postgres-operator-helm-overrides.yaml | Image: "ghcr.io/zalando/postgres-operator/logical-backup |
| pgbouncer | generic-image | master-32" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/postgres-operator/postgres-operator-helm-overrides.yaml | Image: "registry.opensource.zalan.do/acid/pgbouncer |
| spilo-16 | generic-image | 3.2-p3 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/postgres-operator/postgres-operator-helm-overrides.yaml | Image: ghcr.io/zalando/spilo-16 |
| logical-backup | generic-image | v1.12.2" | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/postgres-operator/postgres-operator-helm-overrides.yaml | Image: "ghcr.io/zalando/postgres-operator/logical-backup |
| repository | generic-image |  quay.io/prometheus/pushgateway | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/prometheus-pushgateway/values.yaml | Image: repository |
| oauth-proxy | generic-image | v1.1.0 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | base-helm-configs/prometheus-pushgateway/values.yaml | Image: openshift/oauth-proxy |
| k8s | generic-image | 1.26.11 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | manifests/utils/utils-kubectl.yaml | Image: alpine/k8s |
| jessie-dnsutils | generic-image | 1.3 | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | manifests/utils/utils-dnsutils.yaml | Image: registry.k8s.io/e2e-test-images/jessie-dnsutils |
| openstack-client | generic-image | latest | N/A (requires registry access) | Unknown | Unknown | Unknown | Unknown | manifests/utils/utils-openstack-client-admin.yaml | Image: ghcr.io/rackerlabs/genestack-images/openstack-client |
