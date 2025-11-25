#!/usr/bin/env python3
"""
OpenStack Repository Scanner
Scans Git repository for ALL OpenStack component versions and performs compatibility analysis.
NO CLI commands - repository-only analysis.
"""

import os
import re
import json
import yaml
import csv
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from urllib.parse import urljoin
import html

try:
    from openstack_version_resolver import extract_version_from_chart_tag
    OPENSTACK_RESOLVER_AVAILABLE = True
except ImportError:
    OPENSTACK_RESOLVER_AVAILABLE = False

# Official OpenStack release mapping
OPENSTACK_RELEASES = {
    "2025.1": {"name": "Epoxy", "status": "current"},
    "2024.2": {"name": "Dalmatian", "status": "current"},
    "2024.1": {"name": "Caracal", "status": "current"},
    "2023.2": {"name": "Bobcat", "status": "maintained"},
    "2023.1": {"name": "Antelope", "status": "maintained"},
    "2022.0": {"name": "Zed", "status": "maintained"},
    "2021.0": {"name": "Yoga", "status": "EOL"},
    "2020.0": {"name": "Wallaby", "status": "EOL"},
}

# Component name patterns
COMPONENT_PATTERNS = {
    'keystone': r'keystone',
    'nova': r'nova',
    'neutron': r'neutron',
    'glance': r'glance',
    'cinder': r'cinder',
    'placement': r'placement',
    'heat': r'heat',
    'barbican': r'barbican',
    'octavia': r'octavia',
    'magnum': r'magnum',
    'masakari': r'masakari',
    'ceilometer': r'ceilometer',
    'gnocchi': r'gnocchi',
    'cloudkitty': r'cloudkitty',
    'ironic': r'ironic',
    'designate': r'designate',
    'zaqar': r'zaqar',
    'blazar': r'blazar',
    'freezer': r'freezer',
    'horizon': r'horizon',
    'skyline': r'skyline',
}

class OpenStackRepoScanner:
    def __init__(self, repo_path: str = "/root/genestack"):
        self.repo_path = Path(repo_path)
        self.components = []
        self.release_counts = defaultdict(int)
        self.scraped_release_data = {}
        
    def scan_repository(self) -> List[Dict]:
        """Recursively scan repository for OpenStack component versions"""
        print("Scanning repository for OpenStack component versions...")
        
        # Files to scan
        scan_patterns = [
            "**/Chart.yaml",
            "**/values.yaml",
            "**/*-helm-overrides.yaml",
            "**/kustomization.yaml",
            "**/*.yaml",
            "**/Dockerfile",
            "**/Containerfile",
            "**/Dockerfile.*",
            "**/Containerfile.*",
            "**/requirements.txt",
            "**/.github/workflows/*.yml",
            "**/.github/workflows/*.yaml",
        ]
        
        # Also scan helm-chart-versions.yaml specifically
        self._scan_file(self.repo_path / "helm-chart-versions.yaml")
        
        # Scan all matching files
        for pattern in scan_patterns:
            for file_path in self.repo_path.glob(pattern):
                if file_path.is_file() and '.git' not in str(file_path):
                    self._scan_file(file_path)
        
        # Remove duplicates and consolidate
        self._consolidate_components()
        
        return self.components
    
    def _scan_file(self, file_path: Path):
        """Scan a single file for OpenStack component versions"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Scan for version patterns
                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    
                    # Check for component names
                    for component, pattern in COMPONENT_PATTERNS.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            version = self._extract_version_from_line(line, component)
                            if version:
                                context_start = max(0, line_num - 3)
                                context_end = min(len(lines), line_num + 4)
                                context = '\n'.join(lines[context_start:context_end])
                                
                                self.components.append({
                                    'component': component,
                                    'version_detected': version,
                                    'source_file': str(file_path.relative_to(self.repo_path)),
                                    'source_line': line_num,
                                    'version_context': context,
                                    'raw_line': line.strip()
                                })
        except Exception as e:
            pass
    
    def _extract_version_from_line(self, line: str, component: str) -> Optional[str]:
        """Extract version from a line of text"""
        # Pattern 1: appVersion: "2025.1.2"
        match = re.search(r'appVersion\s*[:=]\s*["\']?([\d\.]+[^"\'\s]*)["\']?', line, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 2: version: "2024.2.186"
        match = re.search(r'version\s*[:=]\s*["\']?([\d\.]+[^"\'\s]*)["\']?', line, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 3: image: ...:2024.1-latest or tag: 2025.1
        match = re.search(r'(?:image|tag)\s*[:=]\s*.*?[:]?([\d]{4}\.[\d](?:[\.\d]+)?(?:[-+][\w]+)?)', line, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 4: component_version: "2024.1"
        match = re.search(rf'{component}[_-]?version\s*[:=]\s*["\']?([\d\.]+[^"\'\s]*)["\']?', line, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 5: openstack_version: "2025.1"
        match = re.search(r'openstack[_-]?version\s*[:=]\s*["\']?([\d\.]+[^"\'\s]*)["\']?', line, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 6: Direct version in component context (e.g., nova: 2024.2.555)
        match = re.search(rf'{component}\s*[:=]\s*([\d]{{4}}\.[\d](?:[\.\d]+)?(?:[-+][\w]+)?)', line, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def _consolidate_components(self):
        """Consolidate duplicate component entries"""
        component_map = {}
        
        for comp in self.components:
            key = (comp['component'], comp['version_detected'])
            if key not in component_map:
                component_map[key] = comp
            else:
                # Merge sources
                existing = component_map[key]
                if comp['source_file'] not in existing.get('source_files', []):
                    if 'source_files' not in existing:
                        existing['source_files'] = [existing['source_file']]
                    existing['source_files'].append(comp['source_file'])
        
        self.components = list(component_map.values())
    
    def map_to_release(self, version: str) -> Tuple[Optional[str], Optional[str]]:
        """Map version to OpenStack release"""
        if not version:
            return None, None
        
        # Extract major.minor (e.g., 2025.1 from 2025.1.2+cdd5e6c55)
        match = re.search(r'(\d{4})\.(\d)', str(version))
        if match:
            year = int(match.group(1))
            minor = int(match.group(2))
            release_key = f"{year}.{minor}"
            
            if release_key in OPENSTACK_RELEASES:
                return release_key, OPENSTACK_RELEASES[release_key]['name']
        
        # Try approximate matching
        for release_key, info in OPENSTACK_RELEASES.items():
            if release_key in str(version):
                return release_key, info['name']
        
        return None, None
    
    def analyze_compatibility(self) -> List[Dict]:
        """Analyze compatibility and build final table"""
        print("Analyzing compatibility...")
        
        # Map all components to releases
        for comp in self.components:
            release_key, release_name = self.map_to_release(comp['version_detected'])
            comp['mapped_release'] = release_key
            comp['mapped_release_name'] = release_name
            
            if release_key:
                self.release_counts[release_key] += 1
        
        # Determine dominant release
        dominant_release = max(self.release_counts.items(), key=lambda x: x[1])[0] if self.release_counts else None
        
        # Build compatibility table
        table = []
        for comp in self.components:
            issues = self._check_compatibility(comp, dominant_release)
            recommended = self._get_recommended_stack(comp, dominant_release)
            
            # Extract real version (formatted) if resolver is available
            real_version = "Unknown"
            if OPENSTACK_RESOLVER_AVAILABLE:
                version_detected = comp.get('version_detected', '')
                if version_detected:
                    full_version, numeric, release, formatted = extract_version_from_chart_tag(version_detected)
                    if formatted:
                        real_version = formatted
            
            table.append({
                'Component': comp['component'],
                'Version Detected': comp['version_detected'],
                'Real Version': real_version,
                'File': comp.get('source_files', [comp['source_file']])[0] if isinstance(comp.get('source_files'), list) else comp['source_file'],
                'Mapped Release': comp.get('mapped_release_name', 'Unknown'),
                'Compatibility Issues': issues,
                'Recommended Stack': recommended,
                'Comments': ''  # Editable comments column
            })
        
        return table
    
    def _check_compatibility(self, comp: Dict, dominant_release: Optional[str]) -> str:
        """Check for compatibility issues"""
        issues = []
        
        release_key = comp.get('mapped_release')
        release_name = comp.get('mapped_release_name')
        
        if not release_key:
            return "VERSION_UNMAPPABLE"
        
        # Check 1: EOL status
        release_info = OPENSTACK_RELEASES.get(release_key, {})
        if release_info.get('status') == 'EOL':
            issues.append("UNSUPPORTED (EOL)")
        
        # Check 2: Major release mismatch with dominant
        if dominant_release and release_key != dominant_release:
            issues.append(f"MAJOR_RELEASE_MISMATCH (target: {OPENSTACK_RELEASES.get(dominant_release, {}).get('name', dominant_release)})")
        
        # Check 3: Mixed series
        if len(self.release_counts) > 1:
            other_releases = [k for k in self.release_counts.keys() if k != release_key]
            if other_releases:
                issues.append(f"MIXED_RELEASES ({', '.join([OPENSTACK_RELEASES.get(r, {}).get('name', r) for r in other_releases])})")
        
        # Check 4: Core service mismatches
        component = comp['component']
        if component in ['nova', 'neutron', 'keystone', 'glance', 'cinder', 'placement']:
            core_releases = [c.get('mapped_release') for c in self.components 
                           if c['component'] in ['nova', 'neutron', 'keystone', 'glance', 'cinder', 'placement'] 
                           and c.get('mapped_release')]
            if len(set(core_releases)) > 1:
                issues.append("CORE_SERVICE_MISMATCH")
        
        # Check 5: Placement/Nova specific
        if component == 'placement':
            nova_comps = [c for c in self.components if c['component'] == 'nova']
            if nova_comps:
                nova_release = nova_comps[0].get('mapped_release')
                if nova_release and release_key != nova_release:
                    issues.append("PLACEMENT/NOVA_MISMATCH")
        
        if not issues:
            return "OK"
        
        return "; ".join(issues)
    
    def _get_recommended_stack(self, comp: Dict, dominant_release: Optional[str]) -> str:
        """Get recommended stack for component"""
        release_key = comp.get('mapped_release')
        release_name = comp.get('mapped_release_name')
        
        if not dominant_release:
            if release_name:
                return f"{release_name} ({release_key})"
            return "Unknown"
        
        dominant_name = OPENSTACK_RELEASES.get(dominant_release, {}).get('name', dominant_release)
        
        if release_key == dominant_release:
            return f"{dominant_name} ({dominant_release}) — Fully compatible"
        else:
            # List all detected releases
            all_releases = [f"{OPENSTACK_RELEASES.get(r, {}).get('name', r)} ({r})" 
                          for r in self.release_counts.keys()]
            return f"Unify to {dominant_name} ({dominant_release}). Mixed releases detected: {', '.join(all_releases)}"
    
    def scrape_openstack_releases(self) -> Dict:
        """Scrape OpenStack release information from official website"""
        print("Scraping OpenStack release data from releases.openstack.org...")
        
        scraped_data = {}
        
        try:
            # Try to get main releases page
            url = "https://releases.openstack.org/"
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                content = response.text
                
                # Extract release information
                for release_key, info in OPENSTACK_RELEASES.items():
                    release_name = info['name']
                    # Look for release in content
                    if release_name.lower() in content.lower() or release_key in content:
                        # Try to get detailed info for each release
                        release_url = f"https://releases.openstack.org/{release_key}/"
                        try:
                            release_response = requests.get(release_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                            if release_response.status_code == 200:
                                release_content = release_response.text
                                # Extract component versions if available
                                component_versions = {}
                                for comp in COMPONENT_PATTERNS.keys():
                                    # Look for component version patterns
                                    pattern = rf'{comp}[:\s]+([\d\.]+)'
                                    matches = re.findall(pattern, release_content, re.IGNORECASE)
                                    if matches:
                                        component_versions[comp] = matches[0]
                                
                                scraped_data[release_key] = {
                                    **info,
                                    'url': release_url,
                                    'component_versions': component_versions,
                                    'scraped': True
                                }
                            else:
                                scraped_data[release_key] = {
                                    **info,
                                    'url': release_url,
                                    'scraped': False
                                }
                        except:
                            scraped_data[release_key] = {
                                **info,
                                'scraped': False
                            }
                
                self.scraped_release_data = scraped_data
                print(f"✅ Scraped data for {len(scraped_data)} releases")
                return scraped_data
        except Exception as e:
            print(f"Warning: Could not scrape release data: {e}")
            # Return static data as fallback
            self.scraped_release_data = OPENSTACK_RELEASES.copy()
            return OPENSTACK_RELEASES.copy()
        
        return scraped_data
    
    def export_reports(self, table: List[Dict], output_dir: Path):
        """Export all report formats"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. JSON inventory
        inventory_data = {
            'scan_date': datetime.now().isoformat(),
            'repository_path': str(self.repo_path),
            'components': self.components,
            'release_distribution': dict(self.release_counts),
            'scraped_release_data': self.scraped_release_data
        }
        
        with open(output_dir / "openstack_repo_inventory.json", 'w') as f:
            json.dump(inventory_data, f, indent=2)
        
        # 2. Markdown table
        with open(output_dir / "openstack_repo_inventory.md", 'w') as f:
            f.write("# OpenStack Repository Component Inventory\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Repository: {self.repo_path}\n\n")
            
            if self.release_counts:
                f.write("## Release Distribution\n\n")
                for release_key, count in sorted(self.release_counts.items(), key=lambda x: x[1], reverse=True):
                    release_name = OPENSTACK_RELEASES.get(release_key, {}).get('name', release_key)
                    f.write(f"- **{release_name} ({release_key})**: {count} components\n")
                f.write("\n")
            
            f.write("## Component Inventory\n\n")
            f.write("| Component | Version Detected | Real Version | File | Mapped Release | Compatibility Issues | Recommended Stack | Comments |\n")
            f.write("|-----------|------------------|--------------|------|----------------|---------------------|-------------------|----------|\n")
            
            for row in table:
                f.write(f"| {row['Component']} | {row['Version Detected']} | {row.get('Real Version', 'Unknown')} | {row['File']} | "
                       f"{row['Mapped Release']} | {row['Compatibility Issues']} | {row['Recommended Stack']} | {row.get('Comments', '')} |\n")
        
        # 3. CSV compatibility table
        with open(output_dir / "openstack_repo_compatibility.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Component', 'Version Detected', 'Real Version', 'File', 
                                                   'Mapped Release', 'Compatibility Issues', 'Recommended Stack', 'Comments'])
            writer.writeheader()
            writer.writerows(table)
        
        # 4. Recommended stack JSON
        dominant_release = max(self.release_counts.items(), key=lambda x: x[1])[0] if self.release_counts else None
        recommended_stack = {
            'recommended_release': dominant_release,
            'recommended_release_name': OPENSTACK_RELEASES.get(dominant_release, {}).get('name') if dominant_release else None,
            'release_distribution': dict(self.release_counts),
            'components_count': len(table),
            'issues_found': len([r for r in table if r['Compatibility Issues'] != 'OK']),
            'recommendation': self._get_overall_recommendation(dominant_release)
        }
        
        with open(output_dir / "openstack_recommended_stack.json", 'w') as f:
            json.dump(recommended_stack, f, indent=2)
    
    def _get_overall_recommendation(self, dominant_release: Optional[str]) -> str:
        """Get overall recommendation"""
        if not dominant_release:
            return "Unable to determine recommended release. Review component versions manually."
        
        dominant_name = OPENSTACK_RELEASES.get(dominant_release, {}).get('name', dominant_release)
        
        if len(self.release_counts) == 1:
            return f"All components are aligned to {dominant_name} ({dominant_release}). Deployment is compatible."
        else:
            releases_list = ', '.join([f"{OPENSTACK_RELEASES.get(r, {}).get('name', r)}" 
                                     for r in self.release_counts.keys()])
            return f"Mixed releases detected: {releases_list}. Recommend unifying all components to {dominant_name} ({dominant_release}) for compatibility. See https://releases.openstack.org/{dominant_release}/"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan repository for OpenStack component versions")
    parser.add_argument("--repo-path", default="/root/genestack", help="Path to repository")
    parser.add_argument("--output-dir", help="Output directory (default: reports/YYYY-MM-DD)")
    parser.add_argument("--scrape", action="store_true", help="Scrape OpenStack release website")
    args = parser.parse_args()
    
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        script_dir = Path(__file__).parent.parent
        repo_path = script_dir.resolve()
    
    scanner = OpenStackRepoScanner(repo_path=str(repo_path))
    
    # Scrape if requested
    if args.scrape:
        scanner.scrape_openstack_releases()
    
    # Scan repository
    components = scanner.scan_repository()
    
    # Analyze compatibility
    table = scanner.analyze_compatibility()
    
    # Export reports
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = repo_path / "reports" / datetime.now().strftime("%Y-%m-%d")
    
    scanner.export_reports(table, output_dir)
    
    print(f"\n✅ Scan complete! Found {len(components)} component versions.")
    print(f"📄 Reports exported to: {output_dir}")
    print(f"   - openstack_repo_inventory.json")
    print(f"   - openstack_repo_inventory.md")
    print(f"   - openstack_repo_compatibility.csv")
    print(f"   - openstack_recommended_stack.json")
