#!/usr/bin/env python3
"""
OpenStack GitHub Version Resolver
Queries GitHub API to resolve actual versions from commit SHAs and determine release trains.
Works with Component Inventory Table.
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
import time

# GitHub API base URLs
GITHUB_API_BASE = "https://api.github.com"
OPENSTACK_ORG = "openstack"

# OpenStack release train mapping (as specified by user)
RELEASE_TRAIN_MAPPING = {
    "2025.1": "Caracal",
    "2024.2": "Dalmatian",
    "2024.1": "Bobcat",
    "2023.2": "Antelope",
    "2023.1": "Yoga",
}

# Component to GitHub repo mapping
COMPONENT_REPOS = {
    'keystone': 'keystone',
    'nova': 'nova',
    'neutron': 'neutron',
    'glance': 'glance',
    'cinder': 'cinder',
    'placement': 'placement',
    'heat': 'heat',
    'barbican': 'barbican',
    'octavia': 'octavia',
    'magnum': 'magnum',
    'masakari': 'masakari',
    'ceilometer': 'ceilometer',
    'gnocchi': 'gnocchi',
    'cloudkitty': 'cloudkitty',
    'ironic': 'ironic',
    'designate': 'designate',
    'zaqar': 'zaqar',
    'blazar': 'blazar',
    'freezer': 'freezer',
    'horizon': 'horizon',
    'skyline': 'skyline',
}

class OpenStackGitHubVersionResolver:
    def __init__(self, repo_path: str = "/root/genestack", github_token: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update({'Authorization': f'token {self.github_token}'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})
        self.version_cache = {}
        self.tag_cache = {}
        self.commit_cache = {}
        
    def extract_sha_from_version(self, version: str) -> Optional[str]:
        """Extract commit SHA from version string using specified pattern"""
        if not version:
            return None
        
        # Pattern: .*\+(?:[0-9a-f]{6,16})-(?P<sha>[0-9a-f]{7,16})$
        pattern = r".*\+(?:[0-9a-f]{6,16})-(?P<sha>[0-9a-f]{7,16})$"
        match = re.search(pattern, str(version))
        if match:
            return match.group('sha')
        
        return None
    
    def get_commit_info(self, service_name: str, sha: str) -> Optional[Dict]:
        """Query GitHub commits API"""
        if not sha or len(sha) < 7:
            return None
        
        cache_key = f"{service_name}:{sha}"
        if cache_key in self.commit_cache:
            return self.commit_cache[cache_key]
        
        repo_name = COMPONENT_REPOS.get(service_name.lower())
        if not repo_name:
            return None
        
        url = f"{GITHUB_API_BASE}/repos/{OPENSTACK_ORG}/{repo_name}/commits/{sha}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            # Handle rate limiting - wait and retry
            if response.status_code == 403:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"⚠️  Rate limit hit, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                commit_data = response.json()
                self.commit_cache[cache_key] = commit_data
                # Rate limiting: 60 requests/hour = ~1 request per minute
                time.sleep(1)
                return commit_data
            elif response.status_code == 404:
                # Commit not found
                self.commit_cache[cache_key] = None
                return None
        except Exception as e:
            print(f"Error querying commit {sha} for {service_name}: {e}")
        
        return None
    
    def get_all_tags(self, service_name: str) -> List[Dict]:
        """Fetch all tags for a service"""
        if service_name in self.tag_cache:
            return self.tag_cache[service_name]
        
        repo_name = COMPONENT_REPOS.get(service_name.lower())
        if not repo_name:
            return []
        
        url = f"{GITHUB_API_BASE}/repos/{OPENSTACK_ORG}/{repo_name}/tags"
        tags = []
        page = 1
        per_page = 200
        
        try:
            while True:
                params = {'page': page, 'per_page': per_page}
                response = self.session.get(url, params=params, timeout=10)
                
                # Handle rate limiting - wait and retry
                if response.status_code == 403:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"⚠️  Rate limit hit, waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code != 200:
                    break
                
                page_tags = response.json()
                if not page_tags:
                    break
                
                tags.extend(page_tags)
                
                # Check if there are more pages
                if len(page_tags) < per_page:
                    break
                
                page += 1
                # Rate limiting: 60 requests/hour = ~1 request per minute (conservative)
                time.sleep(1)
        
        except Exception as e:
            print(f"Error fetching tags for {service_name}: {e}")
        
        self.tag_cache[service_name] = tags
        return tags
    
    def is_ancestor(self, commit_sha: str, tag_sha: str, service_name: str) -> bool:
        """Check if tag_sha is an ancestor of commit_sha"""
        # For now, we'll do a simple comparison
        # In a full implementation, we'd need to query the commit tree
        # For this version, we'll check if the commit SHA matches the tag SHA
        # or if we can find the commit in the tag's history
        
        if commit_sha.startswith(tag_sha) or tag_sha.startswith(commit_sha):
            return True
        
        # Try to get commit info and check parents
        commit_info = self.get_commit_info(service_name, commit_sha)
        if commit_info:
            # Check if tag SHA is in parents
            parents = commit_info.get('parents', [])
            for parent in parents:
                parent_sha = parent.get('sha', '')
                if parent_sha.startswith(tag_sha) or tag_sha.startswith(parent_sha):
                    return True
        
        return False
    
    def find_ancestor_tag(self, service_name: str, commit_sha: str) -> Optional[Dict]:
        """Find tag whose commit SHA is ancestor of commit_sha"""
        tags = self.get_all_tags(service_name)
        
        if not tags:
            return None
        
        # Get commit info to get full SHA
        commit_info = self.get_commit_info(service_name, commit_sha)
        if not commit_info:
            return None
        
        full_commit_sha = commit_info.get('sha', commit_sha)
        
        # First, try exact match
        for tag in tags:
            tag_commit_sha = tag.get('commit', {}).get('sha', '')
            if tag_commit_sha == full_commit_sha or tag_commit_sha.startswith(commit_sha) or commit_sha.startswith(tag_commit_sha[:len(commit_sha)]):
                return tag
        
        # Then try to find ancestor by checking commit history
        # For simplicity, we'll find the most recent tag before this commit
        commit_date = commit_info.get('commit', {}).get('author', {}).get('date', '')
        
        if commit_date:
            # Sort tags by date and find the most recent one before commit
            sorted_tags = sorted(
                tags,
                key=lambda x: x.get('commit', {}).get('commit', {}).get('author', {}).get('date', ''),
                reverse=True
            )
            
            for tag in sorted_tags:
                tag_date = tag.get('commit', {}).get('commit', {}).get('author', {}).get('date', '')
                if tag_date and tag_date <= commit_date:
                    # Check if it's an ancestor
                    tag_sha = tag.get('commit', {}).get('sha', '')
                    if self.is_ancestor(full_commit_sha, tag_sha, service_name):
                        return tag
        
        # Fallback: return most recent tag
        if tags:
            return sorted(tags, key=lambda x: x.get('commit', {}).get('commit', {}).get('author', {}).get('date', ''), reverse=True)[0]
        
        return None
    
    def parse_release_train(self, version: str) -> Optional[str]:
        """Parse major.minor into OpenStack release train"""
        if not version:
            return None
        
        # Extract major.minor (e.g., 2025.1 from 2025.1.0 or 2025.1.2)
        match = re.search(r'(\d{4})\.(\d)', str(version))
        if match:
            major = match.group(1)
            minor = match.group(2)
            release_key = f"{major}.{minor}"
            return RELEASE_TRAIN_MAPPING.get(release_key)
        
        return None
    
    def get_release_notes_url(self, release_train: str, component: str) -> str:
        """Get release notes URL from releases.openstack.org"""
        # Find release key from train name
        release_key = None
        for key, train in RELEASE_TRAIN_MAPPING.items():
            if train.lower() == release_train.lower():
                release_key = key
                break
        
        if release_key:
            return f"https://releases.openstack.org/{release_key}/index.html"
        
        return f"https://releases.openstack.org/"
    
    def find_nearest_tag_for_release(self, service_name: str, target_release: str) -> Optional[str]:
        """Find nearest tag matching target release train"""
        tags = self.get_all_tags(service_name)
        
        if not tags:
            return None
        
        # Find release key from train name
        target_release_key = None
        for key, train in RELEASE_TRAIN_MAPPING.items():
            if train.lower() == target_release.lower():
                target_release_key = key
                break
        
        if not target_release_key:
            return None
        
        # Look for tags matching the release
        matching_tags = []
        for tag in tags:
            tag_name = tag.get('name', '').lstrip('v')
            parsed_train = self.parse_release_train(tag_name)
            if parsed_train and parsed_train.lower() == target_release.lower():
                matching_tags.append(tag)
        
        if matching_tags:
            # Return the most recent matching tag
            sorted_tags = sorted(
                matching_tags,
                key=lambda x: x.get('commit', {}).get('commit', {}).get('author', {}).get('date', ''),
                reverse=True
            )
            return sorted_tags[0].get('name', '').lstrip('v')
        
        return None
    
    def resolve_component_inventory(self, inventory_table: List[Dict]) -> List[Dict]:
        """Resolve versions for Component Inventory Table"""
        print("Resolving versions from GitHub (public API, no authentication required)...")
        print("Note: Using public API with 60 requests/hour limit. This may take a few minutes.")
        
        resolved = []
        errors = []
        
        for row in inventory_table:
            component = row.get('Component', '')
            version_in_repo = row.get('Version in Repo') or row.get('version', '')
            
            # Extract SHA using specified pattern
            sha = self.extract_sha_from_version(version_in_repo)
            
            if not sha:
                # Mark error and skip
                new_row = row.copy()
                new_row['error'] = "Invalid version format"
                new_row['Real OpenStack Version'] = "Unknown"
                new_row['Release Train'] = "Unknown"
                new_row['Compatibility Status'] = "❌ ERROR"
                new_row['Recommended Version'] = ""
                new_row['GitHub Commit URL'] = ""
                new_row['GitHub Tag URL'] = ""
                new_row['Release Notes URL'] = ""
                resolved.append(new_row)
                continue
            
            # Query GitHub commits API
            service_name = component.lower()
            commit_info = self.get_commit_info(service_name, sha)
            
            if not commit_info:
                # 404 - mark incompatible
                new_row = row.copy()
                new_row['Real OpenStack Version'] = "Unknown"
                new_row['Release Train'] = "Unknown"
                new_row['Compatibility Status'] = "❌ INCOMPATIBLE"
                new_row['Recommended Version'] = ""
                new_row['GitHub Commit URL'] = ""
                new_row['GitHub Tag URL'] = ""
                new_row['Release Notes URL'] = ""
                resolved.append(new_row)
                continue
            
            # Fetch tags and find ancestor
            tag_info = self.find_ancestor_tag(service_name, sha)
            
            real_version = "Unknown"
            release_train = "Unknown"
            tag_url = ""
            commit_url = commit_info.get('html_url', '')
            
            if tag_info:
                real_version = tag_info.get('name', '').lstrip('v')
                release_train = self.parse_release_train(real_version) or "Unknown"
                tag_commit_url = tag_info.get('commit', {}).get('html_url', '')
                if tag_commit_url:
                    tag_url = tag_commit_url
            
            release_notes_url = self.get_release_notes_url(release_train, component) if release_train != "Unknown" else ""
            
            new_row = row.copy()
            new_row['Real OpenStack Version'] = real_version
            new_row['Release Train'] = release_train
            new_row['Compatibility Status'] = "Pending"  # Will be set after all resolved
            new_row['Recommended Version'] = ""  # Will be set after compatibility check
            new_row['GitHub Commit URL'] = commit_url
            new_row['GitHub Tag URL'] = tag_url
            new_row['Release Notes URL'] = release_notes_url
            
            resolved.append(new_row)
        
        # Global compatibility check
        release_trains = [r['Release Train'] for r in resolved if r.get('Release Train') and r['Release Train'] != 'Unknown']
        
        if release_trains:
            # Find majority release
            train_counts = defaultdict(int)
            for train in release_trains:
                train_counts[train] += 1
            
            majority_release = max(train_counts.items(), key=lambda x: x[1])[0] if train_counts else None
            
            # Set compatibility status and recommendations
            for row in resolved:
                row_train = row.get('Release Train', 'Unknown')
                
                if row_train == 'Unknown':
                    row['Compatibility Status'] = "❌ ERROR"
                elif row_train == majority_release:
                    row['Compatibility Status'] = "✔ OK"
                else:
                    row['Compatibility Status'] = "❌ MISMATCH"
                    # Find nearest tag matching majority release
                    component = row.get('Component', '')
                    recommended = self.find_nearest_tag_for_release(component.lower(), majority_release)
                    if recommended:
                        row['Recommended Version'] = recommended
                    else:
                        row['Recommended Version'] = f"Use {majority_release} release train"
        
        return resolved
    
    def export_table(self, resolved: List[Dict], output_dir: Path):
        """Export resolved version table"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare table data with all columns
        table_data = []
        for r in resolved:
            table_data.append({
                'Component': r.get('Component', ''),
                'Version in Repo': r.get('Version in Repo') or r.get('version', ''),
                'Real OpenStack Version': r.get('Real OpenStack Version', 'Unknown'),
                'Release Train': r.get('Release Train', 'Unknown'),
                'Compatibility Status': r.get('Compatibility Status', ''),
                'Recommended Version': r.get('Recommended Version', ''),
                'GitHub Commit URL': r.get('GitHub Commit URL', ''),
                'GitHub Tag URL': r.get('GitHub Tag URL', ''),
                'Release Notes URL': r.get('Release Notes URL', ''),
                'Error': r.get('error', ''),
            })
        
        # Export CSV
        csv_path = output_dir / "openstack_github_resolved_versions.csv"
        fieldnames = ['Component', 'Version in Repo', 'Real OpenStack Version', 'Release Train',
                     'Compatibility Status', 'Recommended Version', 'GitHub Commit URL',
                     'GitHub Tag URL', 'Release Notes URL', 'Error']
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(table_data)
        
        # Export Markdown
        md_path = output_dir / "openstack_github_resolved_versions.md"
        with open(md_path, 'w') as f:
            f.write("# OpenStack Component Versions (GitHub Resolved)\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("| Component | Version in Repo | Real OpenStack Version | Release Train | ")
            f.write("Compatibility Status | Recommended Version | GitHub Commit URL | GitHub Tag URL | Release Notes URL |\n")
            f.write("|-----------|----------------|----------------------|---------------|")
            f.write("-------------------|-------------------|------------------|---------------|------------------|\n")
            
            for row in table_data:
                f.write(f"| {row['Component']} | {row['Version in Repo']} | {row['Real OpenStack Version']} | "
                       f"{row['Release Train']} | {row['Compatibility Status']} | {row['Recommended Version']} | "
                       f"[Commit]({row['GitHub Commit URL']}) | [Tag]({row['GitHub Tag URL']}) | "
                       f"[Release Notes]({row['Release Notes URL']}) |\n")
        
        # Export JSON
        json_path = output_dir / "openstack_github_resolved_versions.json"
        with open(json_path, 'w') as f:
            json.dump({
                'resolved_date': datetime.now().isoformat(),
                'components': resolved
            }, f, indent=2)
        
        print(f"✅ Exported resolved versions to {output_dir}")


if __name__ == "__main__":
    import argparse
    from openstack_repo_scanner import OpenStackRepoScanner
    
    parser = argparse.ArgumentParser(description="Resolve OpenStack versions from GitHub")
    parser.add_argument("--repo-path", default="/root/genestack", help="Path to repository")
    parser.add_argument("--github-token", help="GitHub token for API (optional, not required - public API works fine)")
    parser.add_argument("--output-dir", help="Output directory (default: reports/YYYY-MM-DD)")
    parser.add_argument("--inventory-file", help="Path to Component Inventory CSV file (optional)")
    args = parser.parse_args()
    
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        script_dir = Path(__file__).parent.parent
        repo_path = script_dir.resolve()
    
    # Load Component Inventory Table
    inventory_table = []
    
    if args.inventory_file and Path(args.inventory_file).exists():
        # Load from CSV file
        with open(args.inventory_file, 'r') as f:
            reader = csv.DictReader(f)
            inventory_table = list(reader)
        print(f"Loaded {len(inventory_table)} components from inventory file")
    else:
        # Scan repository using OpenStackRepoScanner
        print("Step 1: Scanning repository...")
        scanner = OpenStackRepoScanner(repo_path=str(repo_path))
        components = scanner.scan_repository()
        
        # Convert to inventory format
        for comp in components:
            inventory_table.append({
                'Component': comp.get('component', ''),
                'Version in Repo': comp.get('version_detected', ''),
                'version': comp.get('version_detected', ''),
                'Source Path': comp.get('source_file', ''),
            })
    
    # Resolve versions from GitHub
    print("\nStep 2: Resolving versions from GitHub...")
    resolver = OpenStackGitHubVersionResolver(repo_path=str(repo_path), github_token=args.github_token)
    resolved = resolver.resolve_component_inventory(inventory_table)
    
    # Export
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = repo_path / "reports" / datetime.now().strftime("%Y-%m-%d")
    
    resolver.export_table(resolved, output_dir)
    
    print(f"\n✅ Resolved {len(resolved)} component versions from GitHub")
    print(f"📄 Reports exported to: {output_dir}")
