#!/usr/bin/env python3
"""
Genestack Version Inventory Scanner
Scans the entire repository for component versions and compares with upstream.
"""

import os
import re
import json
import yaml
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import requests
from collections import defaultdict

try:
    from openstack_version_resolver import extract_version_from_chart_tag, get_release_status
    OPENSTACK_RESOLVER_AVAILABLE = True
except ImportError:
    OPENSTACK_RESOLVER_AVAILABLE = False
    print("Warning: openstack_version_resolver not available. OpenStack version resolution will be skipped.")

class VersionInventory:
    def __init__(self, repo_path: str = "/root/genestack"):
        self.repo_path = Path(repo_path)
        self.inventory = []
        self.version_cache = {}
        
    def scan_all(self) -> List[Dict]:
        """Scan entire repository for versions"""
        print("Starting comprehensive version inventory scan...")
        
        # 1. Helm Charts
        print("Scanning Helm charts...")
        self.scan_helm_charts()
        
        # 2. Kustomize
        print("Scanning Kustomize overlays...")
        self.scan_kustomize()
        
        # 3. Container Images
        print("Scanning container images...")
        self.scan_container_images()
        
        # 4. OpenStack Components
        print("Scanning OpenStack components...")
        self.scan_openstack_components()
        
        # 5. Kubernetes Manifests
        print("Scanning Kubernetes manifests...")
        self.scan_kubernetes_manifests()
        
        # 6. Operators/CRDs
        print("Scanning Operators/CRDs...")
        self.scan_operators_crds()
        
        # 7. Python Packages
        print("Scanning Python packages...")
        self.scan_python_packages()
        
        # 8. Ansible Roles
        print("Scanning Ansible roles...")
        self.scan_ansible_roles()
        
        # 9. CI/CD Workflows
        print("Scanning CI/CD workflows...")
        self.scan_cicd_workflows()
        
        # 10. Generic Image Scanner
        print("Scanning for generic image references...")
        self.scan_generic_images()
        
        # 11. Get latest versions
        print("Querying latest upstream versions...")
        self.enrich_with_latest_versions()
        
        # 12. Enrich with OpenStack version information
        if OPENSTACK_RESOLVER_AVAILABLE:
            print("Enriching with OpenStack release information...")
            self.enrich_with_openstack_versions()
        
        return self.inventory
    
    def scan_helm_charts(self):
        """Scan Helm charts for versions"""
        helm_configs = self.repo_path / "base-helm-configs"
        if not helm_configs.exists():
            return
        
        for chart_dir in helm_configs.iterdir():
            if not chart_dir.is_dir():
                continue
            
            chart_yaml = chart_dir / "Chart.yaml"
            values_yaml = chart_dir / f"{chart_dir.name}-helm-overrides.yaml"
            
            version = None
            app_version = None
            
            # Read Chart.yaml
            if chart_yaml.exists():
                try:
                    with open(chart_yaml, 'r') as f:
                        chart_data = yaml.safe_load(f)
                        version = chart_data.get('version')
                        app_version = chart_data.get('appVersion')
                except Exception as e:
                    pass
            
            # Read values.yaml for image tags
            image_tags = []
            if values_yaml.exists():
                try:
                    with open(values_yaml, 'r') as f:
                        values_data = yaml.safe_load(f)
                        image_tags = self._extract_image_tags_from_yaml(values_data)
                except Exception as e:
                    pass
            
            if version:
                self.inventory.append({
                    "Component": chart_dir.name,
                    "Type": "helm-chart",
                    "Version in Repo": version,
                    "Latest Upstream Version": None,
                    "Source Path": str(chart_yaml.relative_to(self.repo_path)),
                    "Notes": f"appVersion: {app_version}" if app_version else "",
                    "Comments": ""  # Editable comments column
                })
            
            # Add image tags as separate entries
            for tag in image_tags:
                if tag:
                    self.inventory.append({
                        "Component": f"{chart_dir.name} (image)",
                        "Type": "container-image",
                        "Version in Repo": tag,
                        "Latest Upstream Version": None,
                        "Source Path": str(values_yaml.relative_to(self.repo_path)),
                        "Notes": "Image tag from Helm values",
                        "Comments": ""
                    })
    
    def scan_kustomize(self):
        """Scan Kustomize overlays for versions"""
        kustomize_base = self.repo_path / "base-kustomize"
        if not kustomize_base.exists():
            return
        
        for kustomization_file in kustomize_base.rglob("kustomization.yaml"):
            try:
                with open(kustomization_file, 'r') as f:
                    kust_data = yaml.safe_load(f)
                    
                    # Extract images
                    images = kust_data.get('images', [])
                    for img in images:
                        name = img.get('name', 'unknown')
                        new_tag = img.get('newTag') or img.get('newName', '').split(':')[-1] if ':' in img.get('newName', '') else None
                        
                        if new_tag:
                            self.inventory.append({
                                "Component": name,
                                "Type": "kustomize-image",
                                "Version in Repo": new_tag,
                                "Latest Upstream Version": None,
                                "Source Path": str(kustomization_file.relative_to(self.repo_path)),
                                "Notes": "Kustomize image override",
                                "Comments": ""
                            })
            except Exception as e:
                pass
    
    def scan_container_images(self):
        """Scan Containerfiles/Dockerfiles for base images"""
        containerfiles_dir = self.repo_path / "Containerfiles"
        if containerfiles_dir.exists():
            for containerfile in containerfiles_dir.glob("*"):
                if containerfile.is_file():
                    try:
                        with open(containerfile, 'r') as f:
                            for line in f:
                                if line.strip().startswith('FROM'):
                                    match = re.search(r'FROM\s+(.+?):(.+?)(?:\s|$)', line)
                                    if match:
                                        image = match.group(1)
                                        tag = match.group(2)
                                        self.inventory.append({
                                            "Component": image.split('/')[-1],
                                            "Type": "container-base-image",
                                            "Version in Repo": tag,
                                            "Latest Upstream Version": None,
                                            "Source Path": str(containerfile.relative_to(self.repo_path)),
                                            "Notes": f"Base image: {image}",
                                            "Comments": ""
                                        })
                    except Exception as e:
                        pass
    
    def scan_openstack_components(self):
        """Scan OpenStack component versions"""
        # Check helm-chart-versions.yaml
        versions_file = self.repo_path / "helm-chart-versions.yaml"
        if versions_file.exists():
            try:
                with open(versions_file, 'r') as f:
                    versions_data = yaml.safe_load(f)
                    charts = versions_data.get('charts', {})
                    for component, version in charts.items():
                        if any(x in component.lower() for x in ['keystone', 'nova', 'neutron', 'glance', 'cinder', 
                                                                 'heat', 'barbican', 'placement', 'octavia', 'magnum',
                                                                 'masakari', 'ceilometer', 'gnocchi', 'cloudkitty',
                                                                 'ironic', 'designate', 'zaqar', 'blazar', 'freezer',
                                                                 'horizon', 'skyline']):
                            self.inventory.append({
                                "Component": component,
                                "Type": "openstack-service",
                                "Version in Repo": version,
                                "Latest Upstream Version": None,
                                "Source Path": str(versions_file.relative_to(self.repo_path)),
                                "Notes": "OpenStack Helm chart version",
                                "Comments": ""
                            })
            except Exception as e:
                pass
        
        # Scan helm configs for OpenStack image tags
        helm_configs = self.repo_path / "base-helm-configs"
        if helm_configs.exists():
            openstack_services = ['keystone', 'glance', 'nova', 'cinder', 'neutron', 'heat', 
                                 'barbican', 'placement', 'octavia', 'magnum', 'masakari',
                                 'ceilometer', 'gnocchi', 'cloudkitty', 'ironic', 'designate',
                                 'zaqar', 'blazar', 'freezer', 'horizon']
            
            for service in openstack_services:
                config_file = helm_configs / service / f"{service}-helm-overrides.yaml"
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            content = f.read()
                            # Extract version patterns like :2024.1-latest
                            matches = re.findall(rf'{service}_api.*?:(.+?)(?:["\s]|$)', content)
                            for match in matches:
                                if match and match.strip():
                                    self.inventory.append({
                                        "Component": f"{service} (image)",
                                        "Type": "openstack-service-image",
                                        "Version in Repo": match.strip(),
                                        "Latest Upstream Version": None,
                                        "Source Path": str(config_file.relative_to(self.repo_path)),
                                        "Notes": f"OpenStack {service} container image tag",
                                        "Comments": ""
                                    })
                                    break
                    except Exception as e:
                        pass
    
    def scan_kubernetes_manifests(self):
        """Scan Kubernetes manifests for API versions"""
        manifests_dir = self.repo_path / "manifests"
        if manifests_dir.exists():
            api_versions = set()
            for yaml_file in manifests_dir.rglob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        for doc in yaml.safe_load_all(f):
                            if doc and 'apiVersion' in doc:
                                api_versions.add(doc['apiVersion'])
                except Exception as e:
                    pass
            
            for api_version in sorted(api_versions):
                self.inventory.append({
                    "Component": api_version.split('/')[0] if '/' in api_version else api_version,
                    "Type": "kubernetes-api",
                    "Version in Repo": api_version,
                    "Latest Upstream Version": None,
                    "Source Path": "manifests/",
                    "Notes": f"Kubernetes API version used in manifests",
                    "Comments": ""
                })
    
    def scan_operators_crds(self):
        """Scan for Operator CRDs"""
        for crd_file in self.repo_path.rglob("*.yaml"):
            if 'crd' in crd_file.name.lower() or 'crd' in str(crd_file.parent).lower():
                try:
                    with open(crd_file, 'r') as f:
                        for doc in yaml.safe_load_all(f):
                            if doc and doc.get('kind') == 'CustomResourceDefinition':
                                spec = doc.get('spec', {})
                                versions = spec.get('versions', [])
                                for version in versions:
                                    self.inventory.append({
                                        "Component": spec.get('group', 'unknown'),
                                        "Type": "operator-crd",
                                        "Version in Repo": version.get('name', 'unknown'),
                                        "Latest Upstream Version": None,
                                        "Source Path": str(crd_file.relative_to(self.repo_path)),
                                        "Notes": f"CRD version: {version.get('name')}",
                                        "Comments": ""
                                    })
                except Exception as e:
                    pass
    
    def scan_python_packages(self):
        """Scan Python requirements files"""
        req_files = [
            self.repo_path / "requirements.txt",
            self.repo_path / "dev-requirements.txt",
            self.repo_path / "doc-requirements.txt",
        ]
        
        for req_file in req_files:
            if req_file.exists():
                try:
                    with open(req_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Parse package==version
                                match = re.match(r'^([a-zA-Z0-9_-]+(?:\[.*?\])?)(?:==|>=|<=|>|<|~=)(.+?)(?:\s|$)', line)
                                if match:
                                    package = match.group(1).split('[')[0]
                                    version = match.group(2).split()[0] if match.group(2) else None
                                    if version:
                                        self.inventory.append({
                                            "Component": package,
                                            "Type": "python-package",
                                            "Version in Repo": version,
                                            "Latest Upstream Version": None,
                                            "Source Path": str(req_file.relative_to(self.repo_path)),
                                            "Notes": "",
                                            "Comments": ""
                                        })
                except Exception as e:
                    pass
    
    def scan_ansible_roles(self):
        """Scan Ansible roles for versions"""
        roles_dir = self.repo_path / "ansible" / "roles"
        if roles_dir.exists():
            for role_dir in roles_dir.iterdir():
                if role_dir.is_dir():
                    defaults_file = role_dir / "defaults" / "main.yml"
                    vars_file = role_dir / "vars" / "main.yml"
                    
                    for config_file in [defaults_file, vars_file]:
                        if config_file.exists():
                            try:
                                with open(config_file, 'r') as f:
                                    data = yaml.safe_load(f)
                                    if data:
                                        for key, value in data.items():
                                            if 'version' in key.lower() or 'tag' in key.lower():
                                                if isinstance(value, str) and value:
                                                    self.inventory.append({
                                                        "Component": f"{role_dir.name}.{key}",
                                                        "Type": "ansible-role-var",
                                                        "Version in Repo": value,
                                                        "Latest Upstream Version": None,
                                                        "Source Path": str(config_file.relative_to(self.repo_path)),
                                                        "Notes": f"Ansible role variable",
                                                        "Comments": ""
                                                    })
                            except Exception as e:
                                pass
    
    def scan_cicd_workflows(self):
        """Scan GitHub Actions workflows"""
        workflows_dir = self.repo_path / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                try:
                    with open(workflow_file, 'r') as f:
                        workflow_data = yaml.safe_load(f)
                        # Extract versions from workflow
                        self._extract_workflow_versions(workflow_data, workflow_file)
                except Exception as e:
                    pass
    
    def _extract_workflow_versions(self, data: dict, file_path: Path):
        """Extract versions from GitHub Actions workflow"""
        if not isinstance(data, dict):
            return
        
        for key, value in data.items():
            if key == 'uses' and isinstance(value, str):
                # Extract action version
                if '@' in value:
                    action, version = value.rsplit('@', 1)
                    self.inventory.append({
                        "Component": action,
                        "Type": "github-action",
                        "Version in Repo": version,
                        "Latest Upstream Version": None,
                        "Source Path": str(file_path.relative_to(self.repo_path)),
                        "Notes": "GitHub Action",
                        "Comments": ""
                    })
            elif key in ['python-version', 'helm-version', 'kubectl-version', 'kube-version']:
                self.inventory.append({
                    "Component": key,
                    "Type": "ci-cd-tool",
                    "Version in Repo": str(value),
                    "Latest Upstream Version": None,
                    "Source Path": str(file_path.relative_to(self.repo_path)),
                    "Notes": f"CI/CD tool version",
                    "Comments": ""
                })
            elif isinstance(value, dict):
                self._extract_workflow_versions(value, file_path)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._extract_workflow_versions(item, file_path)
    
    def scan_generic_images(self):
        """Scan for generic image references in YAML files"""
        image_patterns = [
            r'image:\s*(.+?):(.+?)(?:\s|$)',
            r'imageTag:\s*(.+?)(?:\s|$)',
            r'docker_image:\s*(.+?):(.+?)(?:\s|$)',
            r'containerImage:\s*(.+?):(.+?)(?:\s|$)',
        ]
        
        for yaml_file in self.repo_path.rglob("*.yaml"):
            if '.git' in str(yaml_file):
                continue
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                    for pattern in image_patterns:
                        matches = re.finditer(pattern, content, re.MULTILINE)
                        for match in matches:
                            if len(match.groups()) >= 2:
                                image = match.group(1)
                                tag = match.group(2)
                                if tag and tag not in ['null', 'None', '']:
                                    self.inventory.append({
                                        "Component": image.split('/')[-1].split(':')[0],
                                        "Type": "generic-image",
                                        "Version in Repo": tag,
                                        "Latest Upstream Version": None,
                                        "Source Path": str(yaml_file.relative_to(self.repo_path)),
                                        "Notes": f"Image: {image}",
                                        "Comments": ""
                                    })
            except Exception as e:
                pass
    
    def _extract_image_tags_from_yaml(self, data: dict, path: str = "") -> List[str]:
        """Recursively extract image tags from YAML structure"""
        tags = []
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['tag', 'imageTag', 'version'] and isinstance(value, str):
                    tags.append(value)
                elif key == 'image' and isinstance(value, str) and ':' in value:
                    tags.append(value.split(':')[-1])
                else:
                    tags.extend(self._extract_image_tags_from_yaml(value, f"{path}.{key}"))
        elif isinstance(data, list):
            for item in data:
                tags.extend(self._extract_image_tags_from_yaml(item, path))
        return tags
    
    def enrich_with_latest_versions(self):
        """Query upstream sources for latest versions"""
        print("Enriching with latest versions (this may take a while)...")
        
        for item in self.inventory:
            component = item["Component"]
            comp_type = item["Type"]
            current_version = item["Version in Repo"]
            
            # Skip if already has latest version
            if item["Latest Upstream Version"]:
                continue
            
            latest = self._get_latest_version(component, comp_type, current_version)
            item["Latest Upstream Version"] = latest
    
    def _get_latest_version(self, component: str, comp_type: str, current_version: str) -> Optional[str]:
        """Get latest version from upstream source"""
        cache_key = f"{component}:{comp_type}"
        if cache_key in self.version_cache:
            return self.version_cache[cache_key]
        
        latest = None
        
        try:
            if comp_type == "python-package":
                latest = self._get_pypi_latest(component)
            elif comp_type in ["helm-chart", "openstack-service"]:
                latest = self._get_helm_chart_latest(component)
            elif comp_type in ["container-image", "container-base-image", "generic-image"]:
                # For images, we'd need to query registries - skip for now
                latest = "N/A (requires registry access)"
            elif comp_type == "kubernetes-api":
                latest = "v1.30+ (check K8s docs)"
            else:
                latest = "N/A"
        except Exception as e:
            latest = f"Error: {str(e)[:50]}"
        
        self.version_cache[cache_key] = latest
        return latest
    
    def _get_pypi_latest(self, package: str) -> Optional[str]:
        """Query PyPI for latest version"""
        try:
            url = f"https://pypi.org/pypi/{package}/json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('info', {}).get('version')
        except:
            pass
        return None
    
    def _get_helm_chart_latest(self, chart: str) -> Optional[str]:
        """Query Helm chart repository for latest version"""
        # This would require access to chart repositories
        # For now, return None
        return None
    
    def enrich_with_openstack_versions(self):
        """Enrich inventory with OpenStack version and compatibility information"""
        if not OPENSTACK_RESOLVER_AVAILABLE:
            return
        
        # Track global release for compatibility checking
        global_release = None
        global_numeric = None
        release_counts = defaultdict(int)
        
        # First pass: extract versions and determine majority release
        for item in self.inventory:
            version_in_repo = item.get("Version in Repo", "")
            if not version_in_repo:
                continue
            
            # Extract OpenStack version from chart tag
            full_version, numeric, release, formatted = extract_version_from_chart_tag(version_in_repo)
            
            if full_version and numeric and release:
                item["OpenStack Software Version"] = formatted or full_version  # Use formatted version if available
                item["OpenStack Version (Numeric)"] = numeric
                item["OpenStack Release Name"] = release
                release_counts[release] += 1
            else:
                item["OpenStack Software Version"] = "Unknown"
                item["OpenStack Version (Numeric)"] = "Unknown"
                item["OpenStack Release Name"] = "Unknown"
        
        # Determine global (majority) release and its numeric version
        if release_counts:
            global_release = max(release_counts.items(), key=lambda x: x[1])[0]
            # Find the numeric version for the majority release
            for item in self.inventory:
                if item.get("OpenStack Release Name") == global_release:
                    global_numeric = item.get("OpenStack Version (Numeric)")
                    break
        
        # Second pass: set compatibility and recommended versions
        for item in self.inventory:
            release = item.get("OpenStack Release Name", "Unknown")
            numeric = item.get("OpenStack Version (Numeric)", "Unknown")
            
            # Compatibility check
            if release == "Unknown":
                item["Compatibility"] = "Unknown"
                item["Recommended Upstream"] = "Unknown"
            elif release == global_release:
                item["Compatibility"] = "OK"
                # For compatible components, recommend their current formatted version
                formatted_version = item.get("OpenStack Software Version", "Unknown")
                if formatted_version != "Unknown" and release != "Unknown":
                    item["Recommended Upstream"] = formatted_version
                elif numeric != "Unknown" and release != "Unknown":
                    item["Recommended Upstream"] = f"{release.lower()} v{numeric.split('.')[1]}"
                else:
                    item["Recommended Upstream"] = "Unknown"
            else:
                item["Compatibility"] = "❌ Mismatch"
                # For mismatched components, recommend the majority release formatted version
                # Find the formatted version for the majority release
                global_formatted_version = None
                for inv_item in self.inventory:
                    if inv_item.get("OpenStack Release Name") == global_release:
                        global_formatted_version = inv_item.get("OpenStack Software Version")
                        if global_formatted_version and global_formatted_version != "Unknown":
                            break
                
                if global_formatted_version and global_formatted_version != "Unknown":
                    item["Recommended Upstream"] = global_formatted_version
                elif global_numeric and global_release:
                    # Fallback: construct formatted version from numeric
                    minor_version = global_numeric.split('.')[1]
                    item["Recommended Upstream"] = f"{global_release.lower()} v{minor_version}"
                else:
                    item["Recommended Upstream"] = "Unknown"
    
    def export_to_markdown(self, output_path: Path):
        """Export inventory to Markdown table"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("# Genestack Component Version Inventory\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Build header with optional OpenStack columns
            # Order: Component, Type, Version in Repo, OpenStack Software Version (if available), Latest Upstream Version, then rest
            headers = ["Component", "Type", "Version in Repo"]
            if OPENSTACK_RESOLVER_AVAILABLE and any("OpenStack Software Version" in item for item in self.inventory):
                headers.append("OpenStack Software Version")
            headers.append("Latest Upstream Version")
            if OPENSTACK_RESOLVER_AVAILABLE and any("OpenStack Software Version" in item for item in self.inventory):
                headers.extend(["OpenStack Release Name", "Compatibility", "Recommended Upstream"])
            headers.extend(["Source Path", "Notes", "Comments"])
            
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("|" + "|".join(["---" for _ in headers]) + "|\n")
            
            for item in self.inventory:
                row = [
                    item.get('Component', ''),
                    item.get('Type', ''),
                    item.get('Version in Repo', ''),
                ]
                # Add OpenStack Software Version right after Version in Repo
                if OPENSTACK_RESOLVER_AVAILABLE and "OpenStack Software Version" in item:
                    row.append(item.get('OpenStack Software Version', 'Unknown'))
                # Add Latest Upstream Version
                row.append(item.get('Latest Upstream Version') or 'N/A')
                # Add remaining OpenStack fields
                if OPENSTACK_RESOLVER_AVAILABLE and "OpenStack Software Version" in item:
                    row.extend([
                        item.get('OpenStack Release Name', 'Unknown'),
                        item.get('Compatibility', 'Unknown'),
                        item.get('Recommended Upstream', 'Unknown')
                    ])
                # Add Source Path, Notes, and Comments
                row.extend([
                    item.get('Source Path', ''),
                    item.get('Notes', ''),
                    item.get('Comments', '')
                ])
                f.write("| " + " | ".join(str(x) for x in row) + " |\n")
    
    def export_to_csv(self, output_path: Path):
        """Export inventory to CSV"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build fieldnames - collect all possible fields from inventory items
        # Order: Component, Type, Version in Repo, OpenStack Software Version (if available), Latest Upstream Version, then rest
        base_fieldnames = ['Component', 'Type', 'Version in Repo']
        
        # Check if any items have OpenStack fields
        has_openstack_fields = any("OpenStack Software Version" in item or "OpenStack Version (Numeric)" in item for item in self.inventory)
        
        if has_openstack_fields:
            # Build ordered fieldnames list
            fieldnames = base_fieldnames.copy()
            # Add OpenStack Software Version right after Version in Repo
            if any("OpenStack Software Version" in item for item in self.inventory):
                fieldnames.append('OpenStack Software Version')
            # Add Latest Upstream Version
            fieldnames.append('Latest Upstream Version')
            # Add remaining OpenStack fields
            openstack_fields = ['OpenStack Release Name', 'Compatibility', 'Recommended Upstream']
            for field in openstack_fields:
                if any(field in item for item in self.inventory):
                    fieldnames.append(field)
            # Add Source Path, Notes, and Comments
            fieldnames.extend(['Source Path', 'Notes', 'Comments'])
            # Add any other OpenStack fields that might exist (like OpenStack Version (Numeric))
            all_fields = set()
            for item in self.inventory:
                all_fields.update(item.keys())
            for field in sorted(all_fields):
                if field not in fieldnames:
                    fieldnames.append(field)
        else:
            fieldnames = base_fieldnames + ['Latest Upstream Version', 'Source Path', 'Notes', 'Comments']
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.inventory)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan Genestack repository for component versions")
    parser.add_argument("--repo-path", default="/root/genestack", help="Path to Genestack repository")
    parser.add_argument("--output-dir", help="Output directory for reports (default: reports/YYYY-MM-DD)")
    args = parser.parse_args()
    
    # Determine repo path
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent.parent
        repo_path = script_dir.resolve()
    
    scanner = VersionInventory(repo_path=str(repo_path))
    inventory = scanner.scan_all()
    
    # Export results
    if args.output_dir:
        report_dir = Path(args.output_dir)
    else:
        report_dir = repo_path / "reports" / datetime.now().strftime("%Y-%m-%d")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    scanner.export_to_markdown(report_dir / "component-inventory.md")
    scanner.export_to_csv(report_dir / "component-inventory.csv")
    
    print(f"\n✅ Scan complete! Found {len(inventory)} components.")
    print(f"📄 Reports exported to: {report_dir}")
    print(f"   - component-inventory.md")
    print(f"   - component-inventory.csv")
