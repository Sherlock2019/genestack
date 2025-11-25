#!/usr/bin/env python3
"""
OpenStack Version Resolver
Converts Helm chart tags into real OpenStack release names using official metadata.
"""

import re
import json
import requests
from typing import Optional, Tuple
from pathlib import Path

# Official OpenStack releases metadata
OPENSTACK_SERIES_URL = "https://releases.openstack.org/_releases/releases.json"

# Cache for series data
_SERIES_CACHE = None

def load_openstack_series():
    """Load OpenStack release series from official metadata (cached)"""
    global _SERIES_CACHE
    
    if _SERIES_CACHE is not None:
        return _SERIES_CACHE
    
    # Try to fetch from API (only once)
    try:
        response = requests.get(OPENSTACK_SERIES_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Format: { "antelope": { "releases": [{"version": "2023.1", ...}], ... }, ... }
        series = {}
        for name, entry in data.items():
            if "releases" in entry and entry["releases"]:
                # Get the latest release for this series
                latest = entry["releases"][-1]
                version = latest.get("version", "")
                if version:
                    series[name] = {
                        "version": version,
                        "name": name.title(),
                        "status": latest.get("status", "unknown")
                    }
        
        _SERIES_CACHE = series
        return series
    except Exception:
        # API not available - use fallback mapping (cache it immediately)
        _SERIES_CACHE = {
            "epoxy": {"version": "2025.1", "name": "Epoxy", "status": "current"},
            "dalmatian": {"version": "2024.2", "name": "Dalmatian", "status": "current"},
            "caracal": {"version": "2024.1", "name": "Caracal", "status": "current"},
            "bobcat": {"version": "2023.2", "name": "Bobcat", "status": "maintained"},
            "antelope": {"version": "2023.1", "name": "Antelope", "status": "maintained"},
            "zed": {"version": "2022.0", "name": "Zed", "status": "maintained"},
            "yoga": {"version": "2021.0", "name": "Yoga", "status": "EOL"},
        }
        return _SERIES_CACHE


def extract_version_from_chart_tag(tag: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Convert Helm chart tag → OpenStack version.
    
    Example:
    - 2024.2.396 → full_version: 2024.2.396, numeric: 2024.2, release: 'Dalmatian', formatted: 'dalmatian v396'
    - 2023.1.105 → full_version: 2023.1.105, numeric: 2023.1, release: 'Antelope', formatted: 'antelope v105'
    - 2025.1.2+abcd → full_version: 2025.1.2, numeric: 2025.1, release: 'Epoxy', formatted: 'epoxy v1.2'
    - 2024.2.396+gfd123-628a320c → full_version: 2024.2.396, numeric: 2024.2, release: 'Dalmatian', formatted: 'dalmatian v396'
    
    Returns:
        Tuple of (full_version, numeric_version, release_name, formatted_version) or (None, None, None, None) if not found
    """
    if not tag:
        return None, None, None, None
    
    tag_str = str(tag)
    
    # Extract full version (before + or -): 2024.2.396, 2025.1.2, 2024.2, etc.
    full_match = re.match(r"(\d{4}\.\d(?:\.\d+)?)", tag_str)
    if not full_match:
        return None, None, None, None
    
    full_version = full_match.group(1)
    
    # Extract major.minor for release train mapping
    numeric_match = re.match(r"(\d{4}\.\d)", full_version)
    if not numeric_match:
        return None, None, None, None
    
    numeric_version = numeric_match.group(1)

    # Load series once (cached) and map numeric version → OpenStack release name
    series = load_openstack_series()
    release_name = None
    release_name_lower = None
    
    for name, details in series.items():
        if details.get("version") == numeric_version:
            release_name = details.get("name", name.title())
            release_name_lower = name.lower()  # Use lowercase for formatted version
            break
    
    # If not found in series, try reverse lookup by version pattern
    if not release_name:
        # Fallback mapping
        fallback_map = {
            "2025.1": ("Epoxy", "epoxy"),
            "2024.2": ("Dalmatian", "dalmatian"),
            "2024.1": ("Caracal", "caracal"),
            "2023.2": ("Bobcat", "bobcat"),
            "2023.1": ("Antelope", "antelope"),
            "2022.0": ("Zed", "zed"),
            "2021.0": ("Yoga", "yoga"),
        }
        result = fallback_map.get(numeric_version)
        if result:
            release_name, release_name_lower = result
    
    # Format as: {release_train} v{minor.patch}
    formatted_version = None
    if release_name_lower:
        # Extract minor.patch: 2024.2.396 → 2.396, 2025.1.2 → 1.2
        version_parts = full_version.split('.')
        if len(version_parts) >= 3:
            # Has patch version: 2024.2.396 → v2.396
            minor_patch = f"{version_parts[1]}.{version_parts[2]}"
            formatted_version = f"{release_name_lower} v{minor_patch}"
        elif len(version_parts) == 2:
            # Only minor version: 2025.1 → v1
            minor_version = version_parts[1]
            formatted_version = f"{release_name_lower} v{minor_version}"
    
    return full_version, numeric_version, release_name, formatted_version


def get_release_status(numeric_version: str) -> Optional[str]:
    """Get release status (current, maintained, EOL)"""
    series = load_openstack_series()
    
    for name, details in series.items():
        if details.get("version") == numeric_version:
            return details.get("status", "unknown")
    
    return None


if __name__ == "__main__":
    # Test the resolver
    test_tags = [
        "2024.2.396+gfd123",
        "2024.2.396+gfd123-628a320c",
        "2023.1.105",
        "2025.1+abcd",
        "2024.1-latest",
        "invalid-tag"
    ]
    
    print("Testing OpenStack Version Resolver:")
    print("=" * 60)
    for tag in test_tags:
        numeric, release = extract_version_from_chart_tag(tag)
        status = get_release_status(numeric) if numeric else None
        print(f"Tag: {tag:35} → Version: {numeric or 'N/A':8} Release: {release or 'N/A':12} Status: {status or 'N/A'}")
