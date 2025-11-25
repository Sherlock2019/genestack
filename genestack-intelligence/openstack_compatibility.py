#!/usr/bin/env python3
"""
OpenStack Compatibility Analyzer
Detects and flags incompatibilities between OpenStack components.
"""

import os
import re
import json
import yaml
import csv
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

# OpenStack release compatibility matrix
OPENSTACK_RELEASES = {
    "2024.1": {  # Caracal
        "name": "Caracal",
        "components": {
            "nova": "29.x",
            "neutron": "24.x",
            "keystone": "25.x",
            "glance": "30.x",
            "cinder": "25.x",
            "placement": "9.x",
            "heat": "21.x",
            "barbican": "15.x",
            "octavia": "12.x",
            "magnum": "11.x",
            "masakari": "6.x",
            "ceilometer": "18.x",
            "gnocchi": "4.x",
            "cloudkitty": "12.x",
            "ironic": "22.x",
            "designate": "15.x",
            "zaqar": "10.x",
            "blazar": "5.x",
            "freezer": "4.x",
            "horizon": "25.x",
        }
    },
    "2024.2": {  # Dalmatian
        "name": "Dalmatian",
        "components": {
            "nova": "30.x",
            "neutron": "25.x",
            "keystone": "26.x",
            "glance": "31.x",
            "cinder": "26.x",
            "placement": "10.x",
            "heat": "22.x",
            "barbican": "16.x",
            "octavia": "13.x",
            "magnum": "12.x",
            "masakari": "7.x",
            "ceilometer": "19.x",
            "gnocchi": "5.x",
            "cloudkitty": "13.x",
            "ironic": "23.x",
            "designate": "16.x",
            "zaqar": "11.x",
            "blazar": "6.x",
            "freezer": "5.x",
            "horizon": "26.x",
        }
    },
    "2025.1": {  # Epoxy
        "name": "Epoxy",
        "components": {
            "nova": "31.x",
            "neutron": "26.x",
            "keystone": "27.x",
            "glance": "32.x",
            "cinder": "27.x",
            "placement": "11.x",
            "heat": "23.x",
            "barbican": "17.x",
            "octavia": "14.x",
            "magnum": "13.x",
            "masakari": "8.x",
            "ceilometer": "20.x",
            "gnocchi": "6.x",
            "cloudkitty": "14.x",
            "ironic": "24.x",
            "designate": "17.x",
            "zaqar": "12.x",
            "blazar": "7.x",
            "freezer": "6.x",
            "horizon": "27.x",
        }
    }
}

class OpenStackCompatibilityAnalyzer:
    def __init__(self, repo_path: str = "/root/genestack"):
        self.repo_path = Path(repo_path)
        self.compatibility_table = []
        self.component_versions = {}
        self.detected_release = None
        
    def analyze(self) -> List[Dict]:
        """Run complete compatibility analysis"""
        print("Starting OpenStack compatibility analysis...")
        
        # 1. Extract component versions
        print("Extracting component versions...")
        self.extract_component_versions()
        
        # 2. Determine OpenStack release
        print("Determining OpenStack release...")
        self.determine_release()
        
        # 3. Check compatibility
        print("Checking compatibility...")
        self.check_release_alignment()
        self.check_api_microversions()
        self.check_container_image_alignment()
        self.check_python_library_compatibility()
        self.check_kubernetes_api_compatibility()
        
        return self.compatibility_table
    
    def extract_component_versions(self):
        """Extract OpenStack component versions from various sources"""
        
        # From helm-chart-versions.yaml
        versions_file = self.repo_path / "helm-chart-versions.yaml"
        if versions_file.exists():
            try:
                with open(versions_file, 'r') as f:
                    data = yaml.safe_load(f)
                    charts = data.get('charts', {})
                    for component, version in charts.items():
                        if any(x in component.lower() for x in ['keystone', 'nova', 'neutron', 'glance', 
                                                                 'cinder', 'heat', 'barbican', 'placement',
                                                                 'octavia', 'magnum', 'masakari', 'ceilometer',
                                                                 'gnocchi', 'cloudkitty', 'ironic', 'designate',
                                                                 'zaqar', 'blazar', 'freezer', 'horizon']):
                            self.component_versions[component] = {
                                'version': version,
                                'source': str(versions_file.relative_to(self.repo_path)),
                                'type': 'helm-chart'
                            }
            except Exception as e:
                pass
        
        # From Helm configs (image tags)
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
                            # Extract version patterns like :2024.1-latest or :2025.1-latest
                            matches = re.findall(rf'{service}_api.*?:(.+?)(?:["\s\n]|$)', content)
                            for match in matches:
                                if match and match.strip():
                                    version_tag = match.strip()
                                    # Extract release version (e.g., 2024.1 from 2024.1-latest)
                                    release_match = re.search(r'(\d{4}\.\d)', version_tag)
                                    if release_match:
                                        if service not in self.component_versions:
                                            self.component_versions[service] = {
                                                'version': version_tag,
                                                'source': str(config_file.relative_to(self.repo_path)),
                                                'type': 'container-image',
                                                'release': release_match.group(1)
                                            }
                                    break
                    except Exception as e:
                        pass
    
    def determine_release(self):
        """Determine the primary OpenStack release from component versions"""
        release_counts = defaultdict(int)
        
        for component, info in self.component_versions.items():
            release = info.get('release')
            if release:
                release_counts[release] += 1
        
        if release_counts:
            self.detected_release = max(release_counts.items(), key=lambda x: x[1])[0]
        else:
            # Try to infer from version strings
            for component, info in self.component_versions.items():
                version = info.get('version', '')
                # Look for release pattern in version string
                match = re.search(r'(\d{4}\.\d)', str(version))
                if match:
                    release = match.group(1)
                    release_counts[release] += 1
            
            if release_counts:
                self.detected_release = max(release_counts.items(), key=lambda x: x[1])[0]
    
    def check_release_alignment(self):
        """Check if all components belong to the same OpenStack release"""
        if not self.detected_release:
            return
        
        expected_release = self.detected_release
        release_info = OPENSTACK_RELEASES.get(expected_release)
        
        if not release_info:
            return
        
        for component, info in self.component_versions.items():
            component_name = component.lower()
            detected_version = info.get('version', '')
            detected_release = info.get('release')
            
            # Extract release from version if not explicitly set
            if not detected_release:
                match = re.search(r'(\d{4}\.\d)', str(detected_version))
                if match:
                    detected_release = match.group(1)
            
            # Get expected version range for this component
            expected_version_range = release_info['components'].get(component_name)
            
            status = "OK"
            notes = ""
            required_version = expected_version_range or f"{expected_release} release"
            
            if detected_release and detected_release != expected_release:
                status = "ERROR"
                notes = f"Component version belongs to {detected_release} release, but deployment targets {expected_release} ({release_info['name']})."
            elif not detected_release and expected_version_range:
                status = "WARNING"
                notes = f"Unable to determine release from version '{detected_version}'. Expected {expected_version_range} for {expected_release} release."
            elif expected_version_range:
                # Check if version matches expected range
                major_version = self._extract_major_version(detected_version)
                expected_major = expected_version_range.split('.')[0]
                if major_version and expected_major and major_version != expected_major:
                    status = "WARNING"
                    notes = f"Version {detected_version} may not match expected range {expected_version_range} for {expected_release} release."
                else:
                    notes = f"Component aligned with {expected_release} ({release_info['name']}) release."
            
            self.compatibility_table.append({
                "Component": component,
                "Detected Version": detected_version,
                "Required Compatible Version": required_version,
                "Source": info.get('source', 'Unknown'),
                "Status": status,
                "Notes": notes
            })
    
    def check_api_microversions(self):
        """Check API microversion compatibility"""
        # This would require live API access
        # For now, add placeholder checks based on release
        
        if not self.detected_release:
            return
        
        release_info = OPENSTACK_RELEASES.get(self.detected_release)
        if not release_info:
            return
        
        # Check Nova-Placement compatibility
        nova_info = self.component_versions.get('nova')
        placement_info = self.component_versions.get('placement')
        
        if nova_info and placement_info:
            nova_release = nova_info.get('release') or self._extract_release_from_version(nova_info.get('version', ''))
            placement_release = placement_info.get('release') or self._extract_release_from_version(placement_info.get('version', ''))
            
            if nova_release and placement_release and nova_release != placement_release:
                self.compatibility_table.append({
                    "Component": "Nova-Placement API",
                    "Detected Version": f"Nova: {nova_release}, Placement: {placement_release}",
                    "Required Compatible Version": "Same release",
                    "Source": f"{nova_info.get('source')}, {placement_info.get('source')}",
                    "Status": "ERROR",
                    "Notes": "Nova and Placement must be on the same OpenStack release for API microversion compatibility."
                })
    
    def check_container_image_alignment(self):
        """Check if container images are aligned to the same release"""
        image_releases = {}
        
        for component, info in self.component_versions.items():
            if info.get('type') == 'container-image':
                release = info.get('release') or self._extract_release_from_version(info.get('version', ''))
                if release:
                    if release not in image_releases:
                        image_releases[release] = []
                    image_releases[release].append(component)
        
        if len(image_releases) > 1:
            releases_list = ', '.join([f"{r} ({', '.join(comps)})" for r, comps in image_releases.items()])
            self.compatibility_table.append({
                "Component": "Container Images",
                "Detected Version": releases_list,
                "Required Compatible Version": "Single release",
                "Source": "Helm configs",
                "Status": "ERROR",
                "Notes": f"Service container images belong to different OpenStack releases: {releases_list}. All services should use the same release."
            })
    
    def check_python_library_compatibility(self):
        """Check Python library compatibility"""
        req_files = [
            self.repo_path / "requirements.txt",
            self.repo_path / "dev-requirements.txt",
        ]
        
        oslo_packages = {}
        for req_file in req_files:
            if req_file.exists():
                try:
                    with open(req_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Check for oslo packages
                                match = re.match(r'^(oslo[\.\w-]+)(?:==|>=|<=|>|<|~=)(.+?)(?:\s|$)', line)
                                if match:
                                    package = match.group(1)
                                    version = match.group(2).split()[0] if match.group(2) else None
                                    if version:
                                        oslo_packages[package] = {
                                            'version': version,
                                            'source': str(req_file.relative_to(self.repo_path))
                                        }
                except Exception as e:
                    pass
        
        if oslo_packages and self.detected_release:
            # Check if oslo versions are compatible with detected release
            self.compatibility_table.append({
                "Component": "Python Libraries (oslo.*)",
                "Detected Version": f"{len(oslo_packages)} oslo packages found",
                "Required Compatible Version": f"Compatible with {self.detected_release}",
                "Source": ", ".join([pkg['source'] for pkg in oslo_packages.values()]),
                "Status": "WARNING",
                "Notes": f"Verify oslo.* package versions match OpenStack {self.detected_release} release constraints. Check https://releases.openstack.org/constraints/"
            })
    
    def check_kubernetes_api_compatibility(self):
        """Check for deprecated Kubernetes API versions"""
        deprecated_apis = {
            'apps/v1beta1': 'Kubernetes 1.16+',
            'apps/v1beta2': 'Kubernetes 1.16+',
            'extensions/v1beta1': 'Kubernetes 1.16+',
            'networking.k8s.io/v1beta1': 'Kubernetes 1.19+',
        }
        
        found_deprecated = []
        manifests_dir = self.repo_path / "manifests"
        if manifests_dir.exists():
            for yaml_file in manifests_dir.rglob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        for doc in yaml.safe_load_all(f):
                            if doc and 'apiVersion' in doc:
                                api_version = doc['apiVersion']
                                if api_version in deprecated_apis:
                                    found_deprecated.append({
                                        'api': api_version,
                                        'file': str(yaml_file.relative_to(self.repo_path)),
                                        'removed_in': deprecated_apis[api_version]
                                    })
                except Exception as e:
                    pass
        
        if found_deprecated:
            for dep in found_deprecated:
                self.compatibility_table.append({
                    "Component": f"Kubernetes API ({dep['api']})",
                    "Detected Version": dep['api'],
                    "Required Compatible Version": "Current API version",
                    "Source": dep['file'],
                    "Status": "ERROR",
                    "Notes": f"Deprecated API {dep['api']} removed in {dep['removed_in']}. Update to current API version."
                })
    
    def _extract_major_version(self, version_str: str) -> Optional[str]:
        """Extract major version number from version string"""
        if not version_str:
            return None
        match = re.search(r'^(\d+)', str(version_str))
        return match.group(1) if match else None
    
    def _extract_release_from_version(self, version_str: str) -> Optional[str]:
        """Extract OpenStack release (e.g., 2024.1) from version string"""
        if not version_str:
            return None
        match = re.search(r'(\d{4}\.\d)', str(version_str))
        return match.group(1) if match else None
    
    def export_to_markdown(self, output_path: Path):
        """Export compatibility table to Markdown"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("# OpenStack Compatibility Analysis\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            if self.detected_release:
                release_info = OPENSTACK_RELEASES.get(self.detected_release, {})
                f.write(f"**Detected OpenStack Release**: {self.detected_release} ({release_info.get('name', 'Unknown')})\n\n")
            
            f.write("| Component | Detected Version | Required Compatible Version | Source | Status | Notes |\n")
            f.write("|-----------|------------------|----------------------------|--------|--------|-------|\n")
            
            for item in self.compatibility_table:
                f.write(f"| {item['Component']} | {item['Detected Version']} | {item['Required Compatible Version']} | "
                       f"{item['Source']} | {item['Status']} | {item['Notes']} |\n")
    
    def export_to_csv(self, output_path: Path):
        """Export compatibility table to CSV"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Component', 'Detected Version', 'Required Compatible Version',
                                                   'Source', 'Status', 'Notes'])
            writer.writeheader()
            writer.writerows(self.compatibility_table)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze OpenStack component compatibility")
    parser.add_argument("--repo-path", default="/root/genestack", help="Path to Genestack repository")
    parser.add_argument("--output-dir", help="Output directory for reports (default: reports/YYYY-MM-DD)")
    args = parser.parse_args()
    
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        script_dir = Path(__file__).parent.parent
        repo_path = script_dir.resolve()
    
    analyzer = OpenStackCompatibilityAnalyzer(repo_path=str(repo_path))
    compatibility_table = analyzer.analyze()
    
    if args.output_dir:
        report_dir = Path(args.output_dir)
    else:
        report_dir = repo_path / "reports" / datetime.now().strftime("%Y-%m-%d")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    analyzer.export_to_markdown(report_dir / "openstack-compat-table.md")
    analyzer.export_to_csv(report_dir / "openstack-compat-table.csv")
    
    print(f"\n✅ Compatibility analysis complete! Found {len(compatibility_table)} compatibility checks.")
    print(f"📄 Reports exported to: {report_dir}")
    print(f"   - openstack-compat-table.md")
    print(f"   - openstack-compat-table.csv")
