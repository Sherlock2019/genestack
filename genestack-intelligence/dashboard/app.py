import streamlit as st
import os, glob, subprocess, json, shlex, textwrap
from datetime import datetime
from typing import Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from version_inventory import VersionInventory
    VERSION_INVENTORY_AVAILABLE = True
except ImportError:
    VERSION_INVENTORY_AVAILABLE = False

try:
    from openstack_compatibility import OpenStackCompatibilityAnalyzer
    COMPATIBILITY_ANALYZER_AVAILABLE = True
except ImportError:
    COMPATIBILITY_ANALYZER_AVAILABLE = False

try:
    from openstack_repo_scanner import OpenStackRepoScanner
    REPO_SCANNER_AVAILABLE = True
except ImportError:
    REPO_SCANNER_AVAILABLE = False

try:
    from openstack_github_version_resolver import OpenStackGitHubVersionResolver
    GITHUB_RESOLVER_AVAILABLE = True
except ImportError:
    GITHUB_RESOLVER_AVAILABLE = False

GITHUB_GREEN_PALETTE = ["#ebedf0", "#c6e48b", "#7bc96f", "#239a3b", "#196127"]

# ---------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="Genestack Intelligence Dashboard",
    layout="wide",
    page_icon="🧬"
)

# Ensure all tables wrap cell content so no horizontal scrolling is needed.
st.markdown(
    """
    <style>
        [data-testid="stDataFrame"] table {
            width: 100% !important;
        }
        [data-testid="stDataFrame"] td,
        [data-testid="stDataFrame"] th {
            white-space: normal !important;
            word-break: break-word !important;
        }
        [data-testid="stDataFrame"] [role="gridcell"],
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataEditor"] [role="gridcell"],
        [data-testid="stDataEditor"] [role="columnheader"] {
            white-space: normal !important;
            word-break: break-word !important;
            overflow-wrap: anywhere !important;
        }
        [data-testid="stDataEditor"] [contenteditable="true"] {
            white-space: normal !important;
            word-break: break-word !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def wrap_text(value: Any, width: int = 80) -> Any:
    if isinstance(value, str) and len(value) > width:
        return "\n".join(textwrap.wrap(value, width=width))
    return value

def wrap_dataframe_text(df: pd.DataFrame, width: int = 80) -> pd.DataFrame:
    return df.map(lambda val: wrap_text(val, width=width))

st.title("🧬 Genestack Intelligence Dashboard")
st.markdown("### Real-Time Repository Intelligence • Contributors • PR Insights • Drift Detection")

# ---------------------------------------------------
# Load latest report directory
# ---------------------------------------------------
reports = sorted(glob.glob("reports/*"), reverse=True)
if not reports:
    st.warning("No intelligence reports available. Run ./start.sh first.")
    st.stop()

latest = reports[0]
st.markdown(f"### 📅 Latest Report: **{os.path.basename(latest)}**")

# ---------------------------------------------------
# Utility: Run Git Command
# ---------------------------------------------------
def git(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except:
        return ""

# ---------------------------------------------------
# Extract Git Metrics
# ---------------------------------------------------

# 1. Contributors
contributors = git("git shortlog -sn --all")
contributors_list = [l.strip() for l in contributors.split("\n") if l.strip()]
contrib_df = pd.DataFrame(
    [l.split(maxsplit=1) for l in contributors_list[:10]],
    columns=["Commits", "Contributor"]
)
contrib_df["Commits"] = contrib_df["Commits"].astype(int)

# 2. Branch Commit Count
branches = git("git branch -r --format='%(refname:short)'").split("\n")
branch_data = []
for b in branches:
    if not b.strip():
        continue
    count = git(f"git rev-list --count {b}") or "0"
    branch_data.append([b, int(count)])
branch_df = pd.DataFrame(branch_data, columns=["Branch", "Commits"])
branch_df = branch_df.sort_values("Commits", ascending=False).head(10)

def branch_updated_files(branch_name: str) -> int:
    files_output = git(f"git log {branch_name} --pretty=format:'' --name-only")
    if not files_output:
        return 0
    files = {line.strip() for line in files_output.split("\n") if line.strip()}
    return len(files)

branch_df["Updated Files"] = branch_df["Branch"].apply(branch_updated_files)

def branch_top_files(branch_name: str, limit: int = 10) -> str:
    files_output = git(f"git log {branch_name} --pretty=format:'' --name-only")
    if not files_output:
        return ""
    counts = {}
    for line in files_output.split("\n"):
        file_path = line.strip()
        if not file_path:
            continue
        counts[file_path] = counts.get(file_path, 0) + 1
    top_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return ", ".join(f"{path} ({count})" for path, count in top_items)

branch_df["Top Modified Files"] = branch_df["Branch"].apply(branch_top_files)

def branch_latest_diff(branch_name: str, file_path: str | None = None, max_chars: int = 2000) -> str:
    """Return the most recent code diff for a file on the branch."""
    history_cmd = f"git log -2 --pretty=format:%H {shlex.quote(branch_name)}"
    if file_path:
        history_cmd += f" -- {shlex.quote(file_path)}"
    hashes = [line.strip() for line in git(history_cmd).split("\n") if line.strip()]
    if not hashes:
        return "No diff available"
    if len(hashes) == 1:
        diff_cmd = f"git show {shlex.quote(hashes[0])}"
        if file_path:
            diff_cmd += f" -- {shlex.quote(file_path)}"
    else:
        diff_cmd = f"git diff {shlex.quote(hashes[1])} {shlex.quote(hashes[0])}"
        if file_path:
            diff_cmd += f" -- {shlex.quote(file_path)}"
    diff_output = git(diff_cmd)
    if not diff_output:
        return "No diff available"
    diff_output = diff_output.strip()
    if len(diff_output) > max_chars:
        return diff_output[:max_chars] + "\n... (truncated)"
    return diff_output

def branch_recent_updates(branch_name: str, limit: int = 5) -> list[str]:
    log_output = git(
        f"git log {shlex.quote(branch_name)} -{limit} "
        "--pretty=format:'%ad — %h %s' --date=iso"
    )
    if not log_output:
        return []
    return [line.strip() for line in log_output.split("\n") if line.strip()]

def branch_file_details(branch_name: str, limit: int = 10):
    log_output = git(f"git log {branch_name} --pretty=format:'%ad||' --date=short --name-only")
    if not log_output:
        return []
    stats = {}
    current_date = None
    for line in log_output.split("\n"):
        entry = line.strip()
        if not entry:
            continue
        if entry.endswith("||"):
            current_date = entry[:-2]
            continue
        file_path = entry
        if not file_path:
            continue
        if file_path not in stats:
            stats[file_path] = {"count": 0, "last_date": current_date}
        stats[file_path]["count"] += 1
        # Keep the latest date
        if stats[file_path]["last_date"] is None or (current_date and current_date > stats[file_path]["last_date"]):
            stats[file_path]["last_date"] = current_date
    top_items = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)[:limit]
    return [
        {
            "Branch": branch_name,
            "File": path,
            "Changes": data["count"],
            "Last Change": data["last_date"] or "",
            "Latest Diff": branch_latest_diff(branch_name, path)
        }
        for path, data in top_items
    ]

branch_file_rows = []
for branch_name in branch_df["Branch"]:
    branch_file_rows.extend(branch_file_details(branch_name))

branch_files_detail_df = pd.DataFrame(branch_file_rows, columns=["Branch", "File", "Changes", "Last Change", "Latest Diff"])
branch_updates_map = {branch: branch_recent_updates(branch) for branch in branch_df["Branch"]}

COMMENT_COLUMN_CONFIG = {
    "User Comments": st.column_config.TextColumn(
        "User Comments",
        help="Add notes, owners, or follow-up tasks.",
        width="medium",
    )
}

def render_editable_table(df: pd.DataFrame, key: str, column_config: dict | None = None):
    display_df = df.copy()
    if "User Comments" not in display_df.columns:
        display_df["User Comments"] = ""
    display_df = wrap_dataframe_text(display_df)
    return st.data_editor(
        display_df,
        num_rows="dynamic",
        width="stretch",
        key=key,
        column_config=(column_config or {}) | COMMENT_COLUMN_CONFIG,
    )

# 3. Most Modified Files
changes = git("git log --name-only --pretty=format:'' | grep -v '^$' | sort | uniq -c | sort -nr")
file_lines = [l.strip() for l in changes.split("\n") if l.strip()][:10]
file_df = pd.DataFrame(
    [l.split(maxsplit=1) for l in file_lines],
    columns=["Changes", "File"]
)
file_df["Changes"] = file_df["Changes"].astype(int)

def analyze_file_risk(file_path: str, changes: int) -> dict:
    """Simple heuristic agent to flag risk, issues, and suggestions."""
    risk = []
    suggestion = []

    if changes > 100:
        risk.append("High churn (100+ edits)")
        suggestion.append("Stabilize design or break work into smaller modules.")
    elif changes > 50:
        risk.append("Moderate churn (50+ edits)")
        suggestion.append("Review for refactor opportunities.")

    lower = file_path.lower()
    if lower.endswith((".py", ".sh")):
        risk.append("Logic changes may lack regression tests")
        suggestion.append("Add or update automated tests covering recent code paths.")
    if lower.endswith((".yaml", ".yml", ".json", ".toml")) or "config" in lower:
        risk.append("Configuration drift risk")
        suggestion.append("Add validation checks and document config expectations.")
    if "docs" in lower or lower.endswith((".md", ".rst")):
        risk.append("Docs churn")
        suggestion.append("Ensure docs match latest product behavior.")
    if "infra" in lower or lower.endswith((".tf", ".kustomize")):
        risk.append("Infrastructure drift")
        suggestion.append("Run infra validation (terraform plan, kubectl diff, etc.).")

    if not risk:
        risk.append("Steady change")
        suggestion.append("Monitor but no immediate action needed.")

    return {
        "file": file_path,
        "changes": changes,
        "issues": ", ".join(risk),
        "suggestion": " ".join(suggestion)
    }

# ---------------------------------------------------
# Pull Requests (Last 10)
# ---------------------------------------------------
raw_prs = git("git log --merges --pretty=format:'%H|%an|%ad|%s' -10")
pr_rows = []
for row in raw_prs.split("\n"):
    if "|" not in row:
        continue
    commit, author, date, subject = row.split("|", 3)
    pr_rows.append([commit, subject, author, date])

pr_df = pd.DataFrame(pr_rows, columns=["Commit", "Title", "Author", "Date"])
if pr_df.empty:
    pr_df = pd.DataFrame(columns=["Commit", "Title", "Author", "Date"])

# ---------------------------------------------------
# KPI Summary Row
# ---------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Contributors", len(contrib_df))
col2.metric("Active Branches", len(branch_df))
col3.metric("Updated Files", len(file_df))
col4.metric("Recent PRs", len(pr_df))

# ---------------------------------------------------
# Pie Chart for Contributors
# ---------------------------------------------------
st.markdown("## 🥧 Contribution Distribution (Top Contributors)")
fig, ax = plt.subplots(figsize=(12, 6))
ax.pie(
    contrib_df["Commits"],
    labels=contrib_df["Contributor"],
    autopct='%1.1f%%',
    startangle=140
)
ax.axis('equal')
st.pyplot(fig)

# ---------------------------------------------------
# Complete Component Version Inventory (Replaces OpenStack Component Versions)
# ---------------------------------------------------
st.markdown("## 📦 Complete Component Version Inventory")

# Initialize session state for scan
if 'run_scan' not in st.session_state:
    st.session_state['run_scan'] = False

# Check for existing report first
report_dir = Path("reports") / datetime.now().strftime("%Y-%m-%d")
inventory_file = report_dir / "component-inventory.md"
inventory_csv = report_dir / "component-inventory.csv"

# Load existing inventory if available
inventory_loaded = False
inv_df = None

if inventory_csv.exists():
    try:
        inv_df = pd.read_csv(inventory_csv)
        # Ensure Comments column exists
        if 'Comments' not in inv_df.columns:
            inv_df['Comments'] = ''
        inventory_loaded = True
        st.success(f"📄 Loaded existing inventory: {len(inv_df)} components found")
    except Exception as e:
        pass

if VERSION_INVENTORY_AVAILABLE:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Scan Repository for All Component Versions")
        st.caption("Scans Helm charts, Kustomize, containers, OpenStack services, Python packages, Ansible roles, CI/CD workflows, and more.")
    with col2:
        if st.button("🔄 Run New Scan", type="primary"):
            st.session_state['run_scan'] = True
    
    if st.session_state.get('run_scan', False):
        with st.spinner("Scanning repository... This may take a few minutes."):
            try:
                repo_path = os.getcwd()
                scanner = VersionInventory(repo_path=repo_path)
                inventory = scanner.scan_all()
                
                if inventory:
                    # Convert to DataFrame
                    inv_df = pd.DataFrame(inventory)
                    inventory_loaded = True
                    st.session_state['run_scan'] = False
                    st.success(f"✅ Scan complete! Found {len(inv_df)} components.")
                    
                    # Auto-save to reports
                    report_dir.mkdir(parents=True, exist_ok=True)
                    scanner.export_to_markdown(report_dir / "component-inventory.md")
                    scanner.export_to_csv(report_dir / "component-inventory.csv")
            except Exception as e:
                st.error(f"Error scanning repository: {str(e)}")
                st.exception(e)
                st.session_state['run_scan'] = False
else:
    st.warning("⚠️ Version inventory scanner not available. Ensure version_inventory.py is in the genestack-intelligence directory.")

# Display inventory if available
if inventory_loaded and inv_df is not None and not inv_df.empty:
    # Filter for OpenStack services by default, but allow viewing all
    st.markdown("### Component Inventory Table")
    
    # Determine default filter - prefer OpenStack services if available
    all_types = sorted([str(x) for x in inv_df['Type'].unique() if pd.notna(x)])
    has_openstack = any('openstack' in str(t).lower() for t in all_types)
    default_types = ['openstack-service', 'openstack-service-image'] if has_openstack and 'openstack-service' in all_types else all_types
    
    # Display with filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.multiselect(
            "Filter by Type",
            options=all_types,
            default=default_types if isinstance(default_types, list) else all_types
        )
    with col2:
        search_term = st.text_input("🔍 Search Component", "")
    with col3:
        show_all = st.checkbox("Show All Types", value=not has_openstack)
        if show_all:
            type_filter = all_types
    
    # Apply filters
    filtered_df = inv_df[inv_df['Type'].isin(type_filter)]
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Component'].str.contains(search_term, case=False, na=False) |
            filtered_df['Source Path'].str.contains(search_term, case=False, na=False) |
            filtered_df['Notes'].astype(str).str.contains(search_term, case=False, na=False)
        ]
    
    # Display table with editable Comments column
    if not filtered_df.empty:
        # Ensure Comments column exists
        if 'Comments' not in filtered_df.columns:
            filtered_df['Comments'] = ''
        if 'Comments' not in inv_df.columns:
            inv_df['Comments'] = ''
        
        # Use data_editor for editable Comments column
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=600,
            column_config={
                "Comments": st.column_config.TextColumn(
                    "Comments",
                    help="Add your comments here",
                    width="large"
                )
            },
            disabled=["Component", "Type", "Version in Repo", "OpenStack Software Version", "Latest Upstream Version", 
                     "OpenStack Release Name", "Compatibility", "Recommended Upstream", "Source Path", "Notes"],
            key="inventory_editor"
        )
        
        # Save button for Comments
        if st.button("💾 Save Comments", key="save_inventory_comments"):
            # Update the full dataframe with edited comments
            if 'Comments' in edited_df.columns:
                # Map edited comments back to full inventory
                for idx, row in edited_df.iterrows():
                    # Find matching row in inv_df
                    mask = (inv_df['Component'] == row['Component']) & (inv_df['Type'] == row['Type'])
                    if mask.any():
                        inv_df.loc[mask, 'Comments'] = row.get('Comments', '')
                
                # Save to CSV
                csv_path = report_dir / "component-inventory.csv"
                inv_df.to_csv(csv_path, index=False)
                st.success("✅ Comments saved successfully!")
        
        # Statistics
        st.markdown("### 📊 Inventory Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Components", len(inv_df))
        with col2:
            st.metric("Component Types", len(inv_df['Type'].unique()))
        with col3:
            outdated = len(inv_df[inv_df['Latest Upstream Version'].notna() & 
                                   (inv_df['Latest Upstream Version'] != inv_df['Version in Repo']) &
                                   (~inv_df['Latest Upstream Version'].astype(str).str.contains('N/A', case=False, na=False))])
            st.metric("Potentially Outdated", outdated)
        with col4:
            with_latest = len(inv_df[inv_df['Latest Upstream Version'].notna() & 
                                       (~inv_df['Latest Upstream Version'].astype(str).str.contains('N/A', case=False, na=False))])
            st.metric("With Latest Info", with_latest)
        
        # Export options
        st.markdown("### 💾 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            csv = inv_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full CSV",
                data=csv,
                file_name=f"component-inventory-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col2:
            filtered_csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered CSV",
                data=filtered_csv,
                file_name=f"component-inventory-filtered-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("No components match the current filters.")
elif not inventory_loaded:
    st.info("💡 Click '🔄 Run New Scan' to generate a complete component version inventory, or ensure a previous scan exists in the reports directory.")

# ---------------------------------------------------
# OpenStack Repository Scanner (Comprehensive)
# ---------------------------------------------------
st.markdown("## 🔍 OpenStack Repository Component Scanner")

# Initialize session state
if 'run_repo_scan' not in st.session_state:
    st.session_state['run_repo_scan'] = False
if 'scrape_releases' not in st.session_state:
    st.session_state['scrape_releases'] = False

# Check for existing reports
repo_inventory_csv = report_dir / "openstack_repo_compatibility.csv"
repo_inventory_json = report_dir / "openstack_repo_inventory.json"
recommended_stack_json = report_dir / "openstack_recommended_stack.json"

repo_scan_loaded = False
repo_table_df = None
recommended_stack = None

if repo_inventory_csv.exists():
    try:
        repo_table_df = pd.read_csv(repo_inventory_csv)
        # Ensure Comments column exists
        if 'Comments' not in repo_table_df.columns:
            repo_table_df['Comments'] = ''
        repo_scan_loaded = True
        st.success(f"📄 Loaded existing repository scan: {len(repo_table_df)} components")
    except Exception as e:
        pass

if recommended_stack_json.exists():
    try:
        with open(recommended_stack_json, 'r') as f:
            recommended_stack = json.load(f)
    except Exception as e:
        pass

if REPO_SCANNER_AVAILABLE:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### Scan Repository for OpenStack Components")
        st.caption("Recursively scans ALL files for OpenStack component versions. NO CLI required - repository-only analysis.")
    with col2:
        scrape_check = st.checkbox("Scrape OpenStack Releases", value=False, help="Fetch latest release data from releases.openstack.org")
    with col3:
        if st.button("🔄 Run Repository Scan", type="primary"):
            st.session_state['run_repo_scan'] = True
            st.session_state['scrape_releases'] = scrape_check
    
    if st.session_state.get('run_repo_scan', False):
        with st.spinner("Scanning repository and analyzing compatibility... This may take a few minutes."):
            try:
                repo_path = os.getcwd()
                scanner = OpenStackRepoScanner(repo_path=repo_path)
                
                # Scrape if requested
                if st.session_state.get('scrape_releases', False):
                    with st.spinner("Scraping OpenStack release data..."):
                        scanner.scrape_openstack_releases()
                
                # Scan repository
                components = scanner.scan_repository()
                
                # Analyze compatibility
                table = scanner.analyze_compatibility()
                
                if table:
                    repo_table_df = pd.DataFrame(table)
                    repo_scan_loaded = True
                    st.session_state['run_repo_scan'] = False
                    st.success(f"✅ Scan complete! Found {len(components)} component versions, {len(table)} compatibility checks.")
                    
                    # Auto-save to reports
                    report_dir.mkdir(parents=True, exist_ok=True)
                    scanner.export_reports(table, report_dir)
                    
                    # Load recommended stack
                    if recommended_stack_json.exists():
                        with open(recommended_stack_json, 'r') as f:
                            recommended_stack = json.load(f)
            except Exception as e:
                st.error(f"Error scanning repository: {str(e)}")
                st.exception(e)
                st.session_state['run_repo_scan'] = False
else:
    st.warning("⚠️ Repository scanner not available. Ensure openstack_repo_scanner.py is in the genestack-intelligence directory.")

# Display recommended stack if available
if recommended_stack:
    st.markdown("### 📊 Recommended Stack")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Recommended Release", recommended_stack.get('recommended_release_name', 'Unknown'))
    with col2:
        st.metric("Components", recommended_stack.get('components_count', 0))
    with col3:
        st.metric("Issues Found", recommended_stack.get('issues_found', 0))
    with col4:
        releases = len(recommended_stack.get('release_distribution', {}))
        st.metric("Release Series", releases)
    
    st.info(f"💡 **Recommendation**: {recommended_stack.get('recommendation', 'N/A')}")

# Display compatibility table if available
if repo_scan_loaded and repo_table_df is not None and not repo_table_df.empty:
    st.markdown("### Component Compatibility Table")
    
    # Display with filters
    col1, col2, col3 = st.columns(3)
    with col1:
        # Filter out NaN and convert to string for sorting
        unique_issues = [str(x) for x in repo_table_df['Compatibility Issues'].unique() if pd.notna(x)]
        issue_filter = st.multiselect(
            "Filter by Issues",
            options=sorted(unique_issues),
            default=sorted(unique_issues)
        )
    with col2:
        # Filter out NaN and convert to string for sorting
        unique_releases = [str(x) for x in repo_table_df['Mapped Release'].unique() if pd.notna(x)]
        release_filter = st.multiselect(
            "Filter by Release",
            options=sorted(unique_releases),
            default=sorted(unique_releases)
        )
    with col3:
        search_term = st.text_input("🔍 Search Component", "", key="repo_search")
    
    # Apply filters - handle NaN values
    filtered_repo_df = repo_table_df[
        (repo_table_df['Compatibility Issues'].astype(str).isin(issue_filter)) &
        (repo_table_df['Mapped Release'].astype(str).isin(release_filter))
    ]
    if search_term:
        filtered_repo_df = filtered_repo_df[
            filtered_repo_df['Component'].str.contains(search_term, case=False, na=False) |
            filtered_repo_df['File'].str.contains(search_term, case=False, na=False) |
            filtered_repo_df['Compatibility Issues'].astype(str).str.contains(search_term, case=False, na=False)
        ]
    
    # Color code by issues
    def highlight_issues(row):
        issues = str(row['Compatibility Issues']).upper()
        if 'ERROR' in issues or 'MISMATCH' in issues or 'EOL' in issues:
            return ['background-color: #ffcccc'] * len(row)  # Red
        elif 'WARNING' in issues or 'MIXED' in issues:
            return ['background-color: #fff4cc'] * len(row)  # Yellow
        elif issues == 'OK':
            return ['background-color: #ccffcc'] * len(row)  # Green
        return [''] * len(row)
    
    # Display table with editable Comments column
    if not filtered_repo_df.empty:
        # Ensure Comments column exists
        if 'Comments' not in filtered_repo_df.columns:
            filtered_repo_df['Comments'] = ''
        
        # Use data_editor for editable Comments column
        edited_df = st.data_editor(
            filtered_repo_df,
            use_container_width=True,
            hide_index=True,
            height=600,
            column_config={
                "Comments": st.column_config.TextColumn(
                    "Comments",
                    help="Add your comments here",
                    width="large"
                )
            },
            disabled=["Component", "Version Detected", "Real Version", "File", "Mapped Release", "Compatibility Issues", "Recommended Stack"],
            key="repo_compatibility_editor"
        )
        
        # Save button for Comments
        if st.button("💾 Save Comments", key="save_repo_comments"):
            # Update the full dataframe with edited comments
            if 'Comments' in edited_df.columns:
                for idx, row in edited_df.iterrows():
                    if idx in repo_table_df.index:
                        repo_table_df.at[idx, 'Comments'] = row.get('Comments', '')
                
                # Save to CSV
                csv_path = report_dir / "openstack_repo_compatibility.csv"
                repo_table_df.to_csv(csv_path, index=False)
                st.success("✅ Comments saved successfully!")
        
        # Statistics
        st.markdown("### 📊 Scan Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ok_count = len(repo_table_df[repo_table_df['Compatibility Issues'].astype(str) == 'OK'])
            st.metric("✅ OK", ok_count)
        with col2:
            warning_count = len(repo_table_df[repo_table_df['Compatibility Issues'].astype(str).str.contains('MIXED|WARNING', case=False, na=False)])
            st.metric("⚠️ Warnings", warning_count)
        with col3:
            error_count = len(repo_table_df[repo_table_df['Compatibility Issues'].astype(str).str.contains('ERROR|MISMATCH|EOL', case=False, na=False)])
            st.metric("❌ Errors", error_count)
        with col4:
            st.metric("Total Components", len(repo_table_df))
        
        # Show summary
        if error_count > 0:
            st.error(f"🚨 **{error_count} compatibility error(s) found!** Review the table above for details.")
        if warning_count > 0:
            st.warning(f"⚠️ **{warning_count} compatibility warning(s) found.** Review recommended.")
        if error_count == 0 and warning_count == 0:
            st.success("✅ **All compatibility checks passed!**")
        
        # Export options
        st.markdown("### 💾 Export Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            csv_data = repo_table_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"openstack-repo-compat-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col2:
            if repo_inventory_json.exists():
                with open(repo_inventory_json, 'r') as f:
                    json_data = f.read()
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"openstack-repo-inventory-{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        with col3:
            filtered_csv = filtered_repo_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered CSV",
                data=filtered_csv,
                file_name=f"openstack-repo-filtered-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("No components match the current filters.")
elif not repo_scan_loaded:
    st.info("💡 Click '🔄 Run Repository Scan' to scan the repository for all OpenStack component versions and compatibility issues.")

# ---------------------------------------------------
# GitHub Version Resolution (Resolve Real Versions from GitHub)
# ---------------------------------------------------
st.markdown("## 🔗 GitHub Version Resolution")

# Initialize session state
if 'resolve_github_versions' not in st.session_state:
    st.session_state['resolve_github_versions'] = False

# Check for existing resolved versions
github_resolved_csv = report_dir / "openstack_github_resolved_versions.csv"
github_resolved_json = report_dir / "openstack_github_resolved_versions.json"

github_resolved_loaded = False
github_resolved_df = None

if github_resolved_csv.exists():
    try:
        github_resolved_df = pd.read_csv(github_resolved_csv)
        github_resolved_loaded = True
        st.success(f"📄 Loaded existing GitHub-resolved versions: {len(github_resolved_df)} components")
    except Exception as e:
        pass

if GITHUB_RESOLVER_AVAILABLE:
    st.markdown("### Resolve Real Versions from GitHub")
    st.caption("Extracts commit SHAs from Component Inventory Table, queries GitHub API to find actual tags/versions, and determines release train compatibility. Works without authentication (60 requests/hour limit).")
    
    # Check if Component Inventory is available
    if inventory_loaded and inv_df is not None and not inv_df.empty:
        if st.button("🔗 Resolve from GitHub", type="primary"):
            st.session_state['resolve_github_versions'] = True
    else:
        st.info("⚠️ Component Inventory Table required. Please run '🔄 Run New Scan' in the Component Version Inventory section first.")
    
    if st.session_state.get('resolve_github_versions', False):
        with st.spinner("Resolving versions from GitHub API... This may take several minutes due to rate limits."):
            try:
                repo_path = os.getcwd()
                
                # Use Component Inventory Table
                if inventory_loaded and inv_df is not None and not inv_df.empty:
                    # Convert DataFrame to list of dicts
                    inventory_table = inv_df.to_dict('records')
                    
                    # Resolve from GitHub (no token - uses public API)
                    resolver = OpenStackGitHubVersionResolver(repo_path=repo_path, github_token=None)
                    resolved = resolver.resolve_component_inventory(inventory_table)
                    
                    if resolved:
                        # Convert to DataFrame with new columns
                        github_resolved_df = pd.DataFrame(resolved)
                        github_resolved_loaded = True
                        st.session_state['resolve_github_versions'] = False
                        st.success(f"✅ Resolved {len(resolved)} component versions from GitHub")
                        
                        # Auto-save
                        report_dir.mkdir(parents=True, exist_ok=True)
                        resolver.export_table(resolved, report_dir)
                else:
                    st.error("Component Inventory Table not available. Please run a scan first.")
                    st.session_state['resolve_github_versions'] = False
            except Exception as e:
                st.error(f"Error resolving versions from GitHub: {str(e)}")
                st.exception(e)
                st.session_state['resolve_github_versions'] = False
                if "rate limit" in str(e).lower() or "403" in str(e):
                    st.warning("⚠️ GitHub API rate limit exceeded (60 requests/hour for unauthenticated). The resolver will retry with delays. For faster resolution, you can set GITHUB_TOKEN environment variable, but it's not required.")
else:
    if not GITHUB_RESOLVER_AVAILABLE:
        st.warning("⚠️ GitHub version resolver not available. Ensure openstack_github_version_resolver.py is in the genestack-intelligence directory.")

# Display resolved versions if available
if github_resolved_loaded and github_resolved_df is not None and not github_resolved_df.empty:
    st.markdown("### GitHub-Resolved Version Table")
    
    # Display with filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=sorted([str(x) for x in github_resolved_df['Compatibility Status'].unique() if pd.notna(x)]),
            default=sorted([str(x) for x in github_resolved_df['Compatibility Status'].unique() if pd.notna(x)])
        )
        with col2:
            train_filter = st.multiselect(
                "Filter by Release Train",
                options=sorted([str(x) for x in github_resolved_df['Release Train'].unique() if pd.notna(x) and str(x) != 'Unknown']),
                default=sorted([str(x) for x in github_resolved_df['Release Train'].unique() if pd.notna(x) and str(x) != 'Unknown'])
            )
    with col3:
        search_term = st.text_input("🔍 Search Component", "", key="github_search")
    
    # Apply filters
    filtered_github_df = github_resolved_df[
        (github_resolved_df['Compatibility Status'].astype(str).isin(status_filter)) &
        (github_resolved_df['Release Train'].astype(str).isin(train_filter))
    ]
    if search_term:
        filtered_github_df = filtered_github_df[
            filtered_github_df['Component'].str.contains(search_term, case=False, na=False) |
            filtered_github_df['Real OpenStack Version'].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_github_df['Version in Repo'].astype(str).str.contains(search_term, case=False, na=False)
        ]
    
    # Display table with all new columns
    if not filtered_github_df.empty:
        # Select columns to display
        display_columns = ['Component', 'Version in Repo', 'Real OpenStack Version', 
                          'Release Train', 'Compatibility Status', 'Recommended Version',
                          'GitHub Commit URL', 'GitHub Tag URL', 'Release Notes URL']
        
        # Filter to only show columns that exist
        available_columns = [col for col in display_columns if col in filtered_github_df.columns]
        display_df = filtered_github_df[available_columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Statistics
        st.markdown("### 📊 Resolution Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            compatible_count = len(github_resolved_df[github_resolved_df['Compatibility Status'].astype(str).str.contains('✔', na=False)])
            st.metric("✔ Compatible", compatible_count)
        with col2:
            incompatible_count = len(github_resolved_df[github_resolved_df['Compatibility Status'].astype(str).str.contains('❌', na=False)])
            st.metric("❌ Incompatible", incompatible_count)
        with col3:
            unique_trains = len([x for x in github_resolved_df['Release Train'].unique() if pd.notna(x) and str(x) != 'Unknown'])
            st.metric("Release Trains", unique_trains)
        with col4:
            st.metric("Total Components", len(github_resolved_df))
        
        # Show summary
        if incompatible_count > 0:
            st.error(f"🚨 **{incompatible_count} incompatible component(s) found!** Review recommended versions.")
        if compatible_count == len(github_resolved_df):
            st.success("✅ **All components are compatible!**")
        
        # Export options
        st.markdown("### 💾 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            csv_data = github_resolved_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"openstack-github-resolved-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col2:
            if github_resolved_json.exists():
                with open(github_resolved_json, 'r') as f:
                    json_data = f.read()
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"openstack-github-resolved-{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
    else:
        st.warning("No components match the current filters.")
elif not github_resolved_loaded:
    st.info("💡 Click '🔗 Resolve from GitHub' to query GitHub API for actual component versions and release trains. Works without authentication (public API, 60 requests/hour).")

# ---------------------------------------------------
# OpenStack Compatibility Analysis (Legacy)
# ---------------------------------------------------
st.markdown("## 🔍 OpenStack Compatibility Analysis (Detailed)")

# Initialize session state
if 'run_compat_analysis' not in st.session_state:
    st.session_state['run_compat_analysis'] = False

# Check for existing compatibility report
compat_file = report_dir / "openstack-compat-table.md"
compat_csv = report_dir / "openstack-compat-table.csv"

compat_loaded = False
compat_df = None

if compat_csv.exists():
    try:
        compat_df = pd.read_csv(compat_csv)
        compat_loaded = True
        st.success(f"📄 Loaded existing compatibility analysis: {len(compat_df)} checks")
    except Exception as e:
        pass

if COMPATIBILITY_ANALYZER_AVAILABLE:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Analyze OpenStack Component Compatibility")
        st.caption("Checks release alignment, API microversions, container image alignment, Python library compatibility, and Kubernetes API compatibility.")
    with col2:
        if st.button("🔄 Run Compatibility Analysis", type="primary"):
            st.session_state['run_compat_analysis'] = True
    
    if st.session_state.get('run_compat_analysis', False):
        with st.spinner("Analyzing OpenStack compatibility... This may take a minute."):
            try:
                repo_path = os.getcwd()
                analyzer = OpenStackCompatibilityAnalyzer(repo_path=repo_path)
                compatibility_table = analyzer.analyze()
                
                if compatibility_table:
                    compat_df = pd.DataFrame(compatibility_table)
                    compat_loaded = True
                    st.session_state['run_compat_analysis'] = False
                    st.success(f"✅ Analysis complete! Found {len(compat_df)} compatibility checks.")
                    
                    # Auto-save to reports
                    report_dir.mkdir(parents=True, exist_ok=True)
                    analyzer.export_to_markdown(report_dir / "openstack-compat-table.md")
                    analyzer.export_to_csv(report_dir / "openstack-compat-table.csv")
            except Exception as e:
                st.error(f"Error analyzing compatibility: {str(e)}")
                st.exception(e)
                st.session_state['run_compat_analysis'] = False
else:
    st.warning("⚠️ Compatibility analyzer not available. Ensure openstack_compatibility.py is in the genestack-intelligence directory.")

# Display compatibility table if available
if compat_loaded and compat_df is not None and not compat_df.empty:
    st.markdown("### Compatibility Status Table")
    
    # Color code by status
    def color_status(val):
        if val == "OK":
            return 'background-color: #ccffcc'  # Green
        elif val == "WARNING":
            return 'background-color: #fff4cc'  # Yellow
        elif val == "ERROR":
            return 'background-color: #ffcccc'  # Red
        return ''
    
    # Apply styling
    styled_compat_df = compat_df.style.applymap(color_status, subset=['Status'])
    
    # Display with filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=['OK', 'WARNING', 'ERROR'],
            default=['ERROR', 'WARNING', 'OK']
        )
    with col2:
        search_term = st.text_input("🔍 Search Component", "", key="compat_search")
    
    # Apply filters
    filtered_compat_df = compat_df[compat_df['Status'].isin(status_filter)]
    if search_term:
        filtered_compat_df = filtered_compat_df[
            filtered_compat_df['Component'].str.contains(search_term, case=False, na=False) |
            filtered_compat_df['Notes'].astype(str).str.contains(search_term, case=False, na=False)
        ]
    
    # Display table
    if not filtered_compat_df.empty:
        # Create styled version for display
        display_df = filtered_compat_df.copy()
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Statistics
        st.markdown("### 📊 Compatibility Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ok_count = len(compat_df[compat_df['Status'] == 'OK'])
            st.metric("✅ OK", ok_count, delta=None)
        with col2:
            warning_count = len(compat_df[compat_df['Status'] == 'WARNING'])
            st.metric("⚠️ Warnings", warning_count, delta=None)
        with col3:
            error_count = len(compat_df[compat_df['Status'] == 'ERROR'])
            st.metric("❌ Errors", error_count, delta=None)
        with col4:
            total_checks = len(compat_df)
            st.metric("Total Checks", total_checks)
        
        # Show summary
        if error_count > 0:
            st.error(f"🚨 **{error_count} compatibility error(s) found!** Review the table above for details.")
        if warning_count > 0:
            st.warning(f"⚠️ **{warning_count} compatibility warning(s) found.** Review recommended.")
        if error_count == 0 and warning_count == 0:
            st.success("✅ **All compatibility checks passed!**")
        
        # Export options
        st.markdown("### 💾 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            csv = compat_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full CSV",
                data=csv,
                file_name=f"openstack-compat-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col2:
            filtered_csv = filtered_compat_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered CSV",
                data=filtered_csv,
                file_name=f"openstack-compat-filtered-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("No compatibility checks match the current filters.")
elif not compat_loaded:
    st.info("💡 Click '🔄 Run Compatibility Analysis' to analyze OpenStack component compatibility, or ensure a previous analysis exists in the reports directory.")

# ---------------------------------------------------
# Top 10 Modified Files per Branch (Surfaced near top for screenshot)
# ---------------------------------------------------
st.markdown("## 🗂 Top 10 Modified Files per Branch")
if branch_files_detail_df.empty:
    st.info("No file change data available for the selected branches.")
else:
    branch_files_display = branch_files_detail_df.copy()
    branch_files_display["Changes"] = branch_files_display["Changes"].astype(int)
    render_editable_table(branch_files_display, key="modified_files_table")

# ---------------------------------------------------
# GitHub-style Contribution Calendar (tabular with bars)
# ---------------------------------------------------
st.markdown("## 🔥 GitHub-Style Contribution Calendar (Last 12 Months)")

calendar_raw = git("git log --pretty=format:'%an|%ad' --date=short")
calendar_records = []
for line in calendar_raw.split("\n"):
    if "|" not in line:
        continue
    author, date_str = line.split("|", 1)
    calendar_records.append([author.strip(), date_str.strip(), 1])

if calendar_records:
    calendar_df = pd.DataFrame(calendar_records, columns=["author", "date", "commits"])
    calendar_df["date"] = pd.to_datetime(calendar_df["date"])

    end_date = pd.Timestamp.today().normalize()
    start_date = end_date - pd.Timedelta(days=365)
    calendar_df = calendar_df[(calendar_df["date"] >= start_date) & (calendar_df["date"] <= end_date)]

    if calendar_df.empty:
        st.info("No commit activity found for the last 12 months.")
    else:
        calendar_df["week"] = calendar_df["date"].dt.to_period("W")
        week_range = pd.period_range(start=start_date.to_period("W"), end=end_date.to_period("W"), freq="W")

        weekly = calendar_df.groupby(["author", "week"])["commits"].sum().unstack(fill_value=0)
        weekly = weekly.reindex(columns=week_range, fill_value=0)
        weekly["total"] = weekly.sum(axis=1)
        weekly = weekly.sort_values("total", ascending=False).drop(columns=["total"])

        week_labels = [period.start_time.strftime("%Y-%m-%d") for period in weekly.columns]
        display_df = weekly.copy().astype(int)
        display_df.columns = week_labels

        bar_color = "#2563eb"
        styled_calendar = (
            display_df.style
            .format("{:.0f}")
            .bar(axis=1, color=bar_color)
        )
        st.dataframe(styled_calendar, width="stretch")
else:
    st.info("No commit history found to build the calendar.")

# ---------------------------------------------------
# Tables Section
# ---------------------------------------------------
st.markdown("## 🌿 Top 10 Active Branches")
render_editable_table(branch_df, key="top_branches_table")

st.markdown("## 🔄 Last 10 PRs (Merged)")
if pr_df.empty:
    st.info("No merged PR history available.")
else:
    render_editable_table(pr_df, key="pr_table")

# ---------------------------------------------------
# AI Analysis (Mockup) — Top File Trends & Risks
# ---------------------------------------------------
st.markdown("## 🤖 AI Analysis (Mockup) — Top Modified Files & Issue Trends")
st.caption("Real AI agent analysis coming soon. All tables are editable for team notes.")

ai_insights = []
insights_df = pd.DataFrame()

if file_df.empty:
    st.info("No file change data to analyze.")
else:
    ai_insights = [analyze_file_risk(row["File"], row["Changes"]) for _, row in file_df.iterrows()]
    insights_df = pd.DataFrame(ai_insights)
    insights_df.rename(columns={"file": "File", "changes": "Changes", "issues": "Issues", "suggestion": "Suggested Action"}, inplace=True)
    insights_df["Changes"] = insights_df["Changes"].astype(int)
    render_editable_table(insights_df, key="ai_insights_table")

    issue_records = []
    for _, row in insights_df.iterrows():
        for issue in [item.strip() for item in row["Issues"].split(",")]:
            if issue:
                issue_records.append({"Issue": issue, "File": row["File"]})

    st.markdown("### Issue Trend Summary")
    if issue_records:
        issue_df = pd.DataFrame(issue_records)
        issue_summary_df = (
            issue_df.groupby("Issue")
            .agg(
                Files_Concerned=("File", lambda x: ", ".join(sorted(set(x)))),
                Files_Impacted=("File", "nunique"),
            )
            .reset_index()
        )
        render_editable_table(issue_summary_df, key="issue_summary_table")
    else:
        st.info("No issue trends detected yet.")

    st.markdown("### Suggested Actions")
    suggested_actions_df = insights_df[["File", "Suggested Action"]]
    render_editable_table(suggested_actions_df, key="suggested_actions_table")

# ---------------------------------------------------
# Engineering Risk Summary
# ---------------------------------------------------
st.markdown("## 🧾 Engineering Risk & Update Summary")

summary_rows = []
risk_lookup = {}
if not insights_df.empty:
    risk_lookup = insights_df.set_index("File").to_dict("index")

for _, branch_row in branch_df.iterrows():
    branch_name = branch_row["Branch"]
    branch_files = branch_files_detail_df[branch_files_detail_df["Branch"] == branch_name]
    top_file = branch_files.iloc[0]["File"] if not branch_files.empty else ""
    top_changes = int(branch_files.iloc[0]["Changes"]) if not branch_files.empty else 0
    risk_entry = risk_lookup.get(top_file, {})
    risk_notes = risk_entry.get("Issues", "No risk signals")
    updates = branch_updates_map.get(branch_name, [])
    summary_rows.append(
        {
            "Branch": branch_name,
            "Commits": branch_row["Commits"],
            "Updated Files": branch_row.get("Updated Files", 0),
            "Most Changed File": top_file,
            "File Changes": top_changes,
            "Risk Notes": risk_notes,
            "Recent Updates (Last 5)": " | ".join(updates) if updates else "No recent history",
        }
    )

if summary_rows:
    summary_df = pd.DataFrame(summary_rows)
    render_editable_table(summary_df, key="risk_summary_table")
else:
    st.info("No branch summary data available.")

if not insights_df.empty:
    riskiest = insights_df.sort_values("Changes", ascending=False).iloc[0]
    st.markdown(
        f"**Top Risky File to Check:** `{riskiest['File']}` — {riskiest['Issues']} (suggested: {riskiest['Suggested Action']})"
    )

# ---------------------------------------------------
# AI Insights
# ---------------------------------------------------
st.markdown("## 🔮 AI Suggested Insights")

insights = []

# Stale branches
stale = branch_df[branch_df["Commits"] == 0]
if not stale.empty:
    insights.append("⚠️ Some branches have **zero commits** — likely stale.")

# Overactive developer
top_dev = contrib_df.iloc[0]
insights.append(f"⭐ **Top contributor** this cycle: **{top_dev['Contributor']}** with {top_dev['Commits']} commits.")

# Most volatile file
volatile = file_df.iloc[0]
insights.append(f"🔥 Most frequently modified file: **{volatile['File']}** ({volatile['Changes']} changes).")

# Few PRs recently
if len(pr_df) < 3:
    insights.append("📉 Low PR activity — development pace might be slowing.")

for i in insights:
    st.markdown(f"- {i}")

st.success("Dashboard loaded successfully.")
