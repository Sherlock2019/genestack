import streamlit as st
import os, glob, subprocess, json, shlex, textwrap
from datetime import datetime
from typing import Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
    PLOTLY_EXPRESS_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    PLOTLY_EXPRESS_AVAILABLE = False
    px = None
    go = None

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add dashboard directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))
try:
    from version_inventory import VersionInventory
    VERSION_INVENTORY_AVAILABLE = True
except ImportError:
    VERSION_INVENTORY_AVAILABLE = False

try:
    from bmw_repo_health_gauges import render_repo_health_gauges
    REPO_HEALTH_GAUGES_AVAILABLE = True
except ImportError:
    REPO_HEALTH_GAUGES_AVAILABLE = False

try:
    from theme_manager import get_theme, theme_switcher
    THEME_MANAGER_AVAILABLE = True
except ImportError:
    THEME_MANAGER_AVAILABLE = False
    def get_theme():
        # Default to light theme if theme_manager not available
        return {
            "bg": "#FFFFFF",
            "card": "#F7F9FC",
            "text": "#1A1A1A",
            "accent": "#007BFF",
            "accent_glow": "rgba(0, 123, 255, 0.35)",
            "good": "#28A745",
            "warn": "#FFC107",
            "bad": "#DC3545",
            "chart_bg": "#FFFFFF",
            "chart_grid": "#DDDDDD",
        }
    def theme_switcher():
        pass

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
    # page_title="Git-Dash-IntAIL",
    page_title="Genestack-dash-INTAIL",
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

def safe_percent(numerator, denominator):
    """Safely compute percentage, avoiding comma errors"""
    n = float(str(numerator).replace(",", ""))
    d = float(str(denominator).replace(",", ""))
    if d == 0:
        return 0.0
    return round((n / d) * 100, 1)

def mercedes_gauge(title, percent, current, total):
    """Create a Mercedes-style gauge component"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(percent),
        number={'suffix': "%", "font": {"size": 38, "color": "white"}},
        title={'text': f"<b>{title}</b><br>{current}/{total}", "font": {"size": 20, "color": "white"}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2ecc71", 'thickness': 0.28},
            'bgcolor': "#111",
            'borderwidth': 2,
            'bordercolor': "#222",
            'steps': [
                {'range': [0, percent], 'color': '#2ecc71'},
                {'range': [percent, 100], 'color': '#333'},
            ]
        }
    ))

    fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        height=300,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

def bmw_gauge(title, percent, current, total, theme=None):
    """Create a BMW M-Dashboard style gauge component using theme system"""
    if theme is None:
        theme = get_theme()
    
    color_good = theme["good"]
    color_warn = theme["warn"]
    color_bad = theme["bad"]
    
    # Build steps to cover full range 0-100 as background zones
    steps = [
        {"range": [0, 40], "color": color_bad},      # Bad band (0-40%)
        {"range": [40, 70], "color": color_warn},    # Warn band (40-70%)
        {"range": [70, 100], "color": color_good},    # Good band (70-100%)
    ]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(percent),
        number={
            "suffix": "%",
            "font": {"size": 46, "color": theme["text"], "family": "Segoe UI Semibold"}
        },
        title={
            "text": f"<b>{title}</b><br><span style='font-size:20px'>{current}/{total}</span>",
            "font": {"size": 22, "color": theme["text"]}
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": theme["text"],
                "tickwidth": 1,
                "ticks": "inside"
            },
            "bar": {"color": theme["accent"], "thickness": 0.28},
            "bgcolor": theme["bg"],
            "borderwidth": 0,

            # BMW M-Performance bands
            "steps": steps,

            # Redline indicator
            "threshold": {
                "line": {"color": theme["accent_glow"], "width": 5},
                "thickness": 0.9,
                "value": percent
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor=theme["chart_bg"],
        plot_bgcolor=theme["chart_bg"],
        height=350,
        margin=dict(l=20, r=20, t=80, b=20),
        font={'color': theme["text"], 'family': "Segoe UI"},
        xaxis_gridcolor=theme["chart_grid"],
        yaxis_gridcolor=theme["chart_grid"]
    )

    return fig

def stat_card(title, value, theme=None):
    """Create a themed stat card for KPI metrics"""
    if theme is None:
        theme = get_theme()
    st.markdown(
        f"""
        <div style="
            background:{theme['card']};
            padding:15px;
            border-radius:12px;
            box-shadow:0px 0px 12px {theme['accent_glow']};
            text-align:center;">
            <h4 style="color:{theme['text']}">{title}</h4>
            <div style="font-size:36px;color:{theme['accent']}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def load_branch_pr_stats():
    """Load branch PR/MR statistics from CSV or return fallback mock data"""
    try:
        df = pd.read_csv("reports/branch_pr_stats.csv")   # if auto-generated by pipeline
        return df
    except:
        # fallback mock values (replace automatically when real data exists)
        return pd.DataFrame([
            {"branch": "main", "prs": 142},
            {"branch": "release-2025.3", "prs": 88},
            {"branch": "installer-script-updates", "prs": 52},
            {"branch": "manila-driver-conf", "prs": 37},
            {"branch": "OSPC-1624-enable-ipsec", "prs": 32},
        ])

def top5_branch_pr_chart(df, theme=None):
    """Generate a horizontal bar chart for Top 5 Branches by PR/MR count"""
    if theme is None:
        theme = get_theme()
    
    # take top 5 by PR count
    df = df.sort_values("prs", ascending=False).head(5)

    fig = px.bar(
        df,
        x="prs",
        y="branch",
        orientation="h",
        title="Top 5 Branches — Pull / Merge Requests",
        color="prs",
        color_continuous_scale="Blues",
        text="prs",
    )

    fig.update_traces(textfont_size=14, textposition="outside")
    fig.update_layout(
        paper_bgcolor=theme["chart_bg"],
        plot_bgcolor=theme["chart_bg"],
        font=dict(color=theme["text"], size=14),
        height=420,
        margin=dict(l=20, r=20, t=70, b=20),
        xaxis_gridcolor=theme["chart_grid"],
        yaxis_gridcolor=theme["chart_grid"]
    )

    return fig

# Initialize theme switcher first (so dark_mode is set in session_state)
if THEME_MANAGER_AVAILABLE:
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False  # Default to light mode

# Get theme
theme = get_theme()

# Section title colors based on mode
is_dark = st.session_state.get("dark_mode", False) if THEME_MANAGER_AVAILABLE else False
section_title_color = "#00FFFF" if is_dark else "#006699"  # Neon blue in dark, IBM blue in light

st.markdown(
    f"""
    <style>
        body {{
            background-color: {theme['bg']} !important;
            color: {theme['text']} !important;
        }}
        .stApp {{
            background-color: {theme['bg']} !important;
        }}
        .block-container {{
            padding-top: 1rem;
            background-color: {theme['bg']} !important;
        }}
        div[data-testid="stMetricValue"] {{
            color: {theme['accent']} !important;
        }}
        /* macOS-inspired colorful table styling */
        table {{
            background: linear-gradient(135deg, {theme['card']} 0%, {theme['card']} 100%) !important;
            color: {theme['text']} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08) !important;
            border-collapse: separate !important;
            border-spacing: 0 !important;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
            padding: 12px 16px !important;
            border: none !important;
            position: relative !important;
        }}
        th:first-child {{
            border-top-left-radius: 12px !important;
        }}
        th:last-child {{
            border-top-right-radius: 12px !important;
        }}
        td {{
            color: {theme['text']} !important;
            padding: 10px 16px !important;
            border-bottom: 1px solid rgba(102, 126, 234, 0.1) !important;
            transition: all 0.2s ease !important;
        }}
        tr:nth-child(even) td {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
        }}
        tr:nth-child(odd) td {{
            background: linear-gradient(135deg, rgba(240, 147, 251, 0.03) 0%, rgba(102, 126, 234, 0.03) 100%) !important;
        }}
        tr:hover td {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
            transform: scale(1.01) !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
        }}
        tr:last-child td:first-child {{
            border-bottom-left-radius: 12px !important;
        }}
        tr:last-child td:last-child {{
            border-bottom-right-radius: 12px !important;
        }}
        .stDataFrame {{
            background: linear-gradient(135deg, {theme['card']} 0%, {theme['card']} 100%) !important;
            border-radius: 12px !important;
            padding: 8px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        }}
        /* Additional macOS-style enhancements */
        [data-testid="stDataFrame"] {{
            border-radius: 12px !important;
            overflow: hidden !important;
        }}
        [data-testid="stDataFrame"] table {{
            border-radius: 12px !important;
        }}
        [data-testid="stDataFrame"] th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }}
        [data-testid="stDataFrame"] tr:nth-child(even) {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
        }}
        [data-testid="stDataFrame"] tr:nth-child(odd) {{
            background: linear-gradient(135deg, rgba(240, 147, 251, 0.03) 0%, rgba(102, 126, 234, 0.03) 100%) !important;
        }}
        [data-testid="stDataFrame"] tr:hover {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
        }}
        [data-testid="stDataEditor"] {{
            border-radius: 12px !important;
            overflow: hidden !important;
        }}
        [data-testid="stDataEditor"] table {{
            border-radius: 12px !important;
        }}
        [data-testid="stDataEditor"] th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }}
        [data-testid="stDataEditor"] tr:nth-child(even) {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
        }}
        [data-testid="stDataEditor"] tr:nth-child(odd) {{
            background: linear-gradient(135deg, rgba(240, 147, 251, 0.03) 0%, rgba(102, 126, 234, 0.03) 100%) !important;
        }}
        [data-testid="stDataEditor"] tr:hover {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
        }}
        /* Section titles - neon blue in dark mode, IBM blue in light mode (no glow) */
        h1, h2, h3, h4, h5, h6 {{
            color: {section_title_color} !important;
        }}
        /* Markdown headers */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
            color: {section_title_color} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Header with theme switcher
col_title, col_theme = st.columns([4, 1])
with col_title:
    # st.title("🧬 Git-Dash-IntAIL")
    st.title("🧬 Genestack-dash-INTAIL")
    st.markdown("### Real-Time Repository Intelligence • Contributors • PR Insights • Drift Detection")
with col_theme:
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    if THEME_MANAGER_AVAILABLE:
        theme_switcher()
    else:
        st.info("Theme manager not available")

# ---------------------------------------------------
# Load latest report directory
# ---------------------------------------------------
repo_path = st.session_state.get('current_repo_path', os.getcwd())
reports_pattern = os.path.join(repo_path, "reports", "*")
reports = sorted(glob.glob(reports_pattern), reverse=True)

if reports:
    latest = reports[0]
    st.markdown(f"### 📅 Latest Report: **{os.path.basename(latest)}**")
else:
    st.info("ℹ️ No pre-generated reports found. Analyzing repository in real-time...")

# ---------------------------------------------------
# Repository Manager
# ---------------------------------------------------
try:
    from repo_manager import get_repo_path, cleanup_repos
    REPO_MANAGER_AVAILABLE = True
except ImportError:
    REPO_MANAGER_AVAILABLE = False
    def get_repo_path(repo_url=None):
        return os.getcwd()
    def cleanup_repos():
        pass

# Initialize repo path in session state
if 'current_repo_path' not in st.session_state:
    st.session_state['current_repo_path'] = os.getcwd()

# ---------------------------------------------------
# Utility: Run Git Command
# ---------------------------------------------------
def git(cmd, repo_path=None):
    """Run git command in specified repo path"""
    if repo_path is None:
        repo_path = st.session_state.get('current_repo_path', os.getcwd())
    try:
        return subprocess.check_output(
            cmd, 
            shell=True, 
            text=True, 
            cwd=repo_path
        ).strip()
    except:
        return ""

# Initialize session state for repo URL
if 'git_repo_url' not in st.session_state:
    # Try to get from git config first
    detected_url = git("git config --get remote.origin.url")
    if not detected_url:
        detected_url = git("git remote get-url origin")
    if not detected_url:
        # Fallback to known repository URL
        detected_url = "https://github.com/rackerlabs/genestack"
    
    # Clean up the URL
    if detected_url:
        if detected_url.startswith("git@"):
            detected_url = detected_url.replace(":", "/").replace("git@", "https://")
        elif detected_url.startswith("git://"):
            detected_url = detected_url.replace("git://", "https://")
        if detected_url.endswith(".git"):
            detected_url = detected_url[:-4]
    
    st.session_state['git_repo_url'] = detected_url

# Git Repository URL Input
st.markdown("### 🔗 Git Repository URL")
col1, col2 = st.columns([3, 1])
with col1:
    user_repo_url = st.text_input(
        "Enter Git Repository URL to analyze",
        value=st.session_state['git_repo_url'],
        placeholder="https://github.com/rackerlabs/genestack",
        help="Enter any Git repository URL (GitHub, GitLab, etc.) to analyze. The app will use this repository for all analysis.",
        key="repo_url_input"
    )
with col2:
    if st.button("🔍 Analyze This Repo", type="primary"):
        if user_repo_url:
            # Clean up the URL
            cleaned_url = user_repo_url.strip()
            if cleaned_url.startswith("git@"):
                cleaned_url = cleaned_url.replace(":", "/").replace("git@", "https://")
            elif cleaned_url.startswith("git://"):
                cleaned_url = cleaned_url.replace("git://", "https://")
            if cleaned_url.endswith(".git"):
                cleaned_url = cleaned_url[:-4]
            
            # Get the repo path (will clone if needed)
            repo_path = get_repo_path(cleaned_url)
            
            # Update session state
            st.session_state['git_repo_url'] = cleaned_url
            st.session_state['current_repo_path'] = repo_path
            
            st.success(f"✅ Now analyzing: {cleaned_url}")
            st.rerun()

# Display current repository URL
current_repo_url = st.session_state.get('git_repo_url', '')
if current_repo_url:
    st.markdown(f"**📦 Currently Analyzing:** [{current_repo_url}]({current_repo_url})")

# Display README
repo_path = st.session_state.get('current_repo_path', os.getcwd())
readme_path = Path(repo_path) / "README.md"
if readme_path.exists():
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        with st.expander("📖 Repository README", expanded=False):
            st.markdown(readme_content)
    except Exception as e:
        st.info(f"Could not load README: {str(e)}")

# ---------------------------------------------------
# Extract Git Metrics
# ---------------------------------------------------

# Initialize insights_df early (used in moved sections)
insights_df = pd.DataFrame()

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

# Top 3 Contributors - Medals & Thank You
st.markdown("### 🏆 Top Contributors Recognition")
st.markdown("#### 🙏 **Thank You for Your Outstanding Contributions!**")

if not contrib_df.empty and len(contrib_df) >= 3:
    top_3_contributors = contrib_df.head(3)
    
    # Create medals display
    medal_col1, medal_col2, medal_col3 = st.columns(3)
    
    with medal_col1:
        # Gold Medal - 1st Place
        contributor_1 = top_3_contributors.iloc[0]
        st.markdown(f"<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.markdown(f"## 🥇 **GOLD MEDAL**")
        st.markdown(f"### **{contributor_1['Contributor']}**")
        st.markdown(f"#### **{contributor_1['Commits']:,} commits**")
        st.markdown(f"</div>", unsafe_allow_html=True)
        if PLOTLY_AVAILABLE:
            fig_gold = go.Figure(go.Indicator(
                mode = "number+gauge",
                value = contributor_1['Commits'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Total Commits", 'font': {'size': 18, 'color': '#FFD700'}},
                number = {'font': {'size': 60, 'color': '#FFD700', 'family': 'Arial Black'}},
                gauge = {
                    'axis': {'range': [None, contrib_df['Commits'].max() * 1.2], 'tickcolor': '#FFD700'},
                    'bar': {'color': "#FFD700", 'thickness': 0.4},
                    'bgcolor': "white",
                    'borderwidth': 3,
                    'bordercolor': "#FFD700",
                    'steps': [
                        {'range': [0, contrib_df['Commits'].max() * 0.5], 'color': "#f0f0f0"},
                        {'range': [contrib_df['Commits'].max() * 0.5, contrib_df['Commits'].max()], 'color': "#d0d0d0"}
                    ]
                }
            ))
            fig_gold.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_gold, use_container_width=True)
    
    with medal_col2:
        # Silver Medal - 2nd Place
        contributor_2 = top_3_contributors.iloc[1]
        st.markdown(f"<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%); border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.markdown(f"## 🥈 **SILVER MEDAL**")
        st.markdown(f"### **{contributor_2['Contributor']}**")
        st.markdown(f"#### **{contributor_2['Commits']:,} commits**")
        st.markdown(f"</div>", unsafe_allow_html=True)
        if PLOTLY_AVAILABLE:
            fig_silver = go.Figure(go.Indicator(
                mode = "number+gauge",
                value = contributor_2['Commits'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Total Commits", 'font': {'size': 18, 'color': '#C0C0C0'}},
                number = {'font': {'size': 60, 'color': '#C0C0C0', 'family': 'Arial Black'}},
                gauge = {
                    'axis': {'range': [None, contrib_df['Commits'].max() * 1.2], 'tickcolor': '#C0C0C0'},
                    'bar': {'color': "#C0C0C0", 'thickness': 0.4},
                    'bgcolor': "white",
                    'borderwidth': 3,
                    'bordercolor': "#C0C0C0",
                    'steps': [
                        {'range': [0, contrib_df['Commits'].max() * 0.5], 'color': "#f0f0f0"},
                        {'range': [contrib_df['Commits'].max() * 0.5, contrib_df['Commits'].max()], 'color': "#d0d0d0"}
                    ]
                }
            ))
            fig_silver.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_silver, use_container_width=True)
    
    with medal_col3:
        # Bronze Medal - 3rd Place
        contributor_3 = top_3_contributors.iloc[2]
        st.markdown(f"<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.markdown(f"## 🥉 **BRONZE MEDAL**")
        st.markdown(f"### **{contributor_3['Contributor']}**")
        st.markdown(f"#### **{contributor_3['Commits']:,} commits**")
        st.markdown(f"</div>", unsafe_allow_html=True)
        if PLOTLY_AVAILABLE:
            fig_bronze = go.Figure(go.Indicator(
                mode = "number+gauge",
                value = contributor_3['Commits'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Total Commits", 'font': {'size': 18, 'color': '#CD7F32'}},
                number = {'font': {'size': 60, 'color': '#CD7F32', 'family': 'Arial Black'}},
                gauge = {
                    'axis': {'range': [None, contrib_df['Commits'].max() * 1.2], 'tickcolor': '#CD7F32'},
                    'bar': {'color': "#CD7F32", 'thickness': 0.4},
                    'bgcolor': "white",
                    'borderwidth': 3,
                    'bordercolor': "#CD7F32",
                    'steps': [
                        {'range': [0, contrib_df['Commits'].max() * 0.5], 'color': "#f0f0f0"},
                        {'range': [contrib_df['Commits'].max() * 0.5, contrib_df['Commits'].max()], 'color': "#d0d0d0"}
                    ]
                }
            ))
            fig_bronze.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bronze, use_container_width=True)
    
    # Detailed breakdown table for top 3 contributors
    st.markdown("### 📊 Detailed Contribution Breakdown")
    
    def get_contributor_stats(contributor_name):
        """Get detailed stats for a contributor: branches and files"""
        # Escape contributor name for shell command
        escaped_name = contributor_name.replace("'", "'\\''")
        
        # Get branches they contributed to
        branch_stats = {}
        for branch in branch_df['Branch'].head(10):  # Check top 10 branches
            try:
                branch_escaped = shlex.quote(branch)
                branch_commits = git(f"git log {branch_escaped} --author='{escaped_name}' --pretty=format:'%H' 2>/dev/null | wc -l")
                commit_count = int(branch_commits.strip()) if branch_commits.strip().isdigit() else 0
                if commit_count > 0:
                    branch_stats[branch] = commit_count
            except:
                pass
        
        # Get files they modified most
        file_stats = {}
        try:
            all_files_cmd = f"git log --author='{escaped_name}' --pretty=format:'' --name-only 2>/dev/null | grep -v '^$' | sort | uniq -c | sort -nr | head -10"
            all_files = git(all_files_cmd)
            if all_files:
                for line in all_files.split('\n')[:10]:
                    if line.strip():
                        parts = line.strip().split(maxsplit=1)
                        if len(parts) == 2:
                            try:
                                count = int(parts[0])
                                file_path = parts[1]
                                if file_path and file_path.strip():
                                    file_stats[file_path] = count
                            except:
                                pass
        except:
            pass
        
        return branch_stats, file_stats
    
    # Create detailed breakdown table
    breakdown_rows = []
    for rank, (idx, contributor_row) in enumerate(top_3_contributors.iterrows(), 1):
        contributor_name = contributor_row['Contributor']
        total_commits = contributor_row['Commits']
        
        branch_stats, file_stats = get_contributor_stats(contributor_name)
        
        # Top branches
        top_branches = sorted(branch_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        top_branches_str = ", ".join([f"{branch} ({count})" for branch, count in top_branches]) if top_branches else "N/A"
        
        # Top files
        top_files = sorted(file_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        top_files_str = ", ".join([f"{file} ({count})" for file, count in top_files]) if top_files else "N/A"
        
        medal = "🥇 Gold" if rank == 1 else "🥈 Silver" if rank == 2 else "🥉 Bronze"
        
        breakdown_rows.append({
            'Medal': medal,
            'Contributor': contributor_name,
            'Total Commits': f"{total_commits:,}",
            'Top Branches': top_branches_str,
            'Top Files': top_files_str
        })
    
    breakdown_df = pd.DataFrame(breakdown_rows)
    st.dataframe(
        breakdown_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Medal": st.column_config.TextColumn("Medal", width="small"),
            "Contributor": st.column_config.TextColumn("Contributor", width="medium"),
            "Total Commits": st.column_config.TextColumn("Total Commits", width="small"),
            "Top Branches": st.column_config.TextColumn("Top Branches", width="large"),
            "Top Files": st.column_config.TextColumn("Top Files", width="large")
        }
    )
    
    st.markdown("---")
    
    # Copy of sections moved here from "What Now ?" section
    # BMW Repo Health Gauges - Real Git-based KPIs
    if REPO_HEALTH_GAUGES_AVAILABLE and PLOTLY_AVAILABLE:
        try:
            render_repo_health_gauges(theme=theme)
        except Exception as e:
            st.error(f"Error rendering repo health gauges: {str(e)}")
            st.info("Falling back to basic metrics display...")
    else:
        st.info("Repo health gauges not available. Install required dependencies.")
    
    st.markdown("---")
    
    # Top 5 Contributors Table
    st.markdown("### 👥 Top 5 Contributors")
    if not contrib_df.empty:
        top_5_contributors = contrib_df.head(5).copy()
        top_5_contributors['Rank'] = range(1, len(top_5_contributors) + 1)
        top_5_contributors_display = top_5_contributors[['Rank', 'Contributor', 'Commits']].copy()
        top_5_contributors_display.columns = ['Rank', 'Contributor', 'Commits']
        top_5_contributors_display['Commits'] = top_5_contributors_display['Commits'].apply(lambda x: f"{x:,}")
        st.dataframe(
            top_5_contributors_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "Contributor": st.column_config.TextColumn("Contributor", width="large"),
                "Commits": st.column_config.TextColumn("Commits", width="medium")
            }
        )
    else:
        st.info("No contributor data available.")
    
    # Top Active Branches Table
    st.markdown("### 🌿 Top 5 Active Branches")
    if not branch_df.empty:
        top_5_branches = branch_df.head(5).copy()
        top_5_branches['Rank'] = range(1, len(top_5_branches) + 1)
        top_5_branches_display = top_5_branches[['Rank', 'Branch', 'Commits', 'Updated Files']].copy()
        top_5_branches_display.columns = ['Rank', 'Branch', 'Commits', 'Files Updated']
        top_5_branches_display['Commits'] = top_5_branches_display['Commits'].apply(lambda x: f"{x:,}")
        top_5_branches_display['Files Updated'] = top_5_branches_display['Files Updated'].apply(lambda x: f"{x:,}")
        st.dataframe(
            top_5_branches_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "Branch": st.column_config.TextColumn("Branch", width="large"),
                "Commits": st.column_config.TextColumn("Commits", width="medium"),
                "Files Updated": st.column_config.TextColumn("Files Updated", width="medium")
            }
        )
    else:
        st.info("No branch data available.")
    
    # Top 5 Branches by Pull/Merge Requests Chart
    st.markdown("### 🔀 Top 5 Branches — Pull / Merge Requests")
    if PLOTLY_AVAILABLE and PLOTLY_EXPRESS_AVAILABLE:
        try:
            branch_pr_df = load_branch_pr_stats()
            fig_branch_pr = top5_branch_pr_chart(branch_pr_df, theme=theme)
            st.plotly_chart(fig_branch_pr, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering PR/MR chart: {str(e)}")
            st.info("Falling back to table view...")
            branch_pr_df = load_branch_pr_stats()
            st.dataframe(branch_pr_df.head(5), use_container_width=True, hide_index=True)
    else:
        st.info("Plotly Express not available for PR/MR chart visualization.")
        # Fallback to table view
        branch_pr_df = load_branch_pr_stats()
        st.dataframe(branch_pr_df.head(5), use_container_width=True, hide_index=True)
    
    # Top Moving Parts and Updates Table
    st.markdown("### 🔥 Top Moving Parts & Updates")
    if not file_df.empty:
        top_5_files = file_df.head(5).copy()
        top_5_files['Rank'] = range(1, len(top_5_files) + 1)
        
        # Merge with AI insights if available
        try:
            has_insights = not insights_df.empty
        except (NameError, AttributeError):
            has_insights = False
        
        if has_insights:
            top_5_files_display = top_5_files[['Rank', 'File', 'Changes']].copy()
            top_5_files_display['Changes'] = top_5_files_display['Changes'].apply(lambda x: f"{x:,}")
            
            # Add AI insights columns
            issues_list = []
            recommendations_list = []
            for idx, row in top_5_files.iterrows():
                file_path = row['File']
                file_insights = insights_df[insights_df['File'] == file_path]
                if not file_insights.empty:
                    insight = file_insights.iloc[0]
                    issues_list.append(insight.get('Issues', 'No issues detected'))
                    recommendations_list.append(insight.get('Suggested Action', 'No specific action'))
                else:
                    issues_list.append('No analysis available')
                    recommendations_list.append('No recommendation')
            
            top_5_files_display['Issues'] = issues_list
            top_5_files_display['Recommendation'] = recommendations_list
            top_5_files_display.columns = ['Rank', 'File', 'Changes', 'Issues', 'Recommendation']
        else:
            top_5_files_display = top_5_files[['Rank', 'File', 'Changes']].copy()
            top_5_files_display['Changes'] = top_5_files_display['Changes'].apply(lambda x: f"{x:,}")
            top_5_files_display.columns = ['Rank', 'File', 'Changes']
        
        # Build column config dynamically
        column_config = {
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "File": st.column_config.TextColumn("File", width="large"),
            "Changes": st.column_config.TextColumn("Changes", width="medium")
        }
        if 'Issues' in top_5_files_display.columns:
            column_config["Issues"] = st.column_config.TextColumn("Issues", width="large")
        if 'Recommendation' in top_5_files_display.columns:
            column_config["Recommendation"] = st.column_config.TextColumn("Recommendation", width="large")
        
        st.dataframe(
            top_5_files_display,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
    else:
        st.info("No file change data available.")
    
    st.markdown("---")
    
    # Copy of sections moved here from main sections
    # Top 10 Modified Files per Branch
    st.markdown("### 🗂 Top 10 Modified Files per Branch")
    if branch_files_detail_df.empty:
        st.info("No file change data available for the selected branches.")
    else:
        branch_files_display = branch_files_detail_df.copy()
        branch_files_display["Changes"] = branch_files_display["Changes"].astype(int)
        render_editable_table(branch_files_display, key="modified_files_table_moved")
    
    # GitHub-style Contribution Calendar
    st.markdown("### 🔥 GitHub-Style Contribution Calendar (Last 12 Months)")
    
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
    
    # Top 10 Active Branches
    st.markdown("### 🌿 Top 10 Active Branches")
    render_editable_table(branch_df, key="top_branches_table_moved")
    
    # Last 10 PRs (Merged)
    st.markdown("### 🔄 Last 10 PRs (Merged)")
    if pr_df.empty:
        st.info("No merged PR history available.")
    else:
        render_editable_table(pr_df, key="pr_table_moved")
    
    st.markdown("---")
else:
    if not contrib_df.empty:
        st.info(f"🏆 **Thank you to all contributors!** Currently showing {len(contrib_df)} contributor(s).")
    else:
        st.info("No contributor data available for recognition.")

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
        # Ensure Comments column exists and convert to string type
        if 'Comments' not in inv_df.columns:
            inv_df['Comments'] = ''
        else:
            # Convert Comments column to string, replacing NaN/None with empty string
            inv_df['Comments'] = inv_df['Comments'].fillna('').astype(str).replace('nan', '').replace('None', '')
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
        # Ensure Comments column exists and convert to string type
        if 'Comments' not in filtered_df.columns:
            filtered_df['Comments'] = ''
        else:
            # Convert Comments column to string, replacing NaN/None with empty string
            filtered_df['Comments'] = filtered_df['Comments'].fillna('').astype(str).replace('nan', '').replace('None', '')
        if 'Comments' not in inv_df.columns:
            inv_df['Comments'] = ''
        else:
            # Convert Comments column to string, replacing NaN/None with empty string
            inv_df['Comments'] = inv_df['Comments'].fillna('').astype(str).replace('nan', '').replace('None', '')
        
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
        # Ensure Comments column exists and convert to string type
        if 'Comments' not in repo_table_df.columns:
            repo_table_df['Comments'] = ''
        else:
            # Convert Comments column to string, replacing NaN/None with empty string
            repo_table_df['Comments'] = repo_table_df['Comments'].fillna('').astype(str).replace('nan', '').replace('None', '')
        # Ensure Review Comment column exists and convert to string type
        if 'Review Comment' not in repo_table_df.columns:
            repo_table_df['Review Comment'] = ''
        else:
            # Convert Review Comment column to string, replacing NaN/None with empty string
            repo_table_df['Review Comment'] = repo_table_df['Review Comment'].fillna('').astype(str).replace('nan', '').replace('None', '')
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
                    # Ensure Review Comment column exists and is string type
                    if 'Review Comment' not in repo_table_df.columns:
                        repo_table_df['Review Comment'] = ''
                    else:
                        repo_table_df['Review Comment'] = repo_table_df['Review Comment'].fillna('').astype(str).replace('nan', '').replace('None', '')
                    # Ensure Comments column exists and is string type
                    if 'Comments' not in repo_table_df.columns:
                        repo_table_df['Comments'] = ''
                    else:
                        repo_table_df['Comments'] = repo_table_df['Comments'].fillna('').astype(str).replace('nan', '').replace('None', '')
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
        # Ensure Comments column exists and convert to string type
        if 'Comments' not in filtered_repo_df.columns:
            filtered_repo_df['Comments'] = ''
        else:
            # Convert Comments column to string, replacing NaN/None with empty string
            filtered_repo_df['Comments'] = filtered_repo_df['Comments'].fillna('').astype(str).replace('nan', '').replace('None', '')
        
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
        
        # Errors and Warnings Review Table
        if error_count > 0 or warning_count > 0:
            st.markdown("### 📋 Errors and Warnings Requiring Review")
            
            # Filter for errors and warnings only
            issues_df = repo_table_df[
                (repo_table_df['Compatibility Issues'].astype(str).str.contains('ERROR|MISMATCH|EOL|MIXED|WARNING', case=False, na=False)) &
                (repo_table_df['Compatibility Issues'].astype(str) != 'OK')
            ].copy()
            
            if not issues_df.empty:
                # Ensure Review Comment column exists and convert to string type
                if 'Review Comment' not in issues_df.columns:
                    issues_df['Review Comment'] = ''
                else:
                    issues_df['Review Comment'] = issues_df['Review Comment'].fillna('').astype(str).replace('nan', '').replace('None', '')
                if 'Review Comment' not in repo_table_df.columns:
                    repo_table_df['Review Comment'] = ''
                else:
                    repo_table_df['Review Comment'] = repo_table_df['Review Comment'].fillna('').astype(str).replace('nan', '').replace('None', '')
                
                # Select relevant columns for display
                display_columns = ['Component', 'Version Detected', 'Real Version', 'File', 
                                 'Mapped Release', 'Compatibility Issues', 'Recommended Stack', 'Review Comment']
                
                # Filter to only show columns that exist
                available_columns = [col for col in display_columns if col in issues_df.columns]
                issues_display_df = issues_df[available_columns].copy()
                
                # Sort by severity (errors first, then warnings)
                def severity_sort(row):
                    issues = str(row.get('Compatibility Issues', '')).upper()
                    if 'ERROR' in issues or 'MISMATCH' in issues or 'EOL' in issues:
                        return 0  # Errors first
                    elif 'WARNING' in issues or 'MIXED' in issues:
                        return 1  # Warnings second
                    return 2
                
                issues_display_df['_sort_order'] = issues_display_df.apply(severity_sort, axis=1)
                issues_display_df = issues_display_df.sort_values('_sort_order').drop(columns=['_sort_order'])
                
                # Use data_editor for editable Review Comment column
                edited_issues_df = st.data_editor(
                    issues_display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=600,
                    column_config={
                        "Review Comment": st.column_config.TextColumn(
                            "Review Comment",
                            help="Add review notes, assign owners, or track follow-up actions",
                            width="large"
                        ),
                        "Component": st.column_config.TextColumn(
                            "Component",
                            width="medium"
                        ),
                        "Compatibility Issues": st.column_config.TextColumn(
                            "Compatibility Issues",
                            width="medium"
                        ),
                        "File": st.column_config.TextColumn(
                            "File",
                            width="medium"
                        )
                    },
                    disabled=[col for col in available_columns if col != 'Review Comment'],
                    key="errors_warnings_review_editor"
                )
                
                # Save button for Review Comments
                if st.button("💾 Save Review Comments", key="save_errors_warnings_comments"):
                    # Update the full dataframe with edited review comments
                    if 'Review Comment' in edited_issues_df.columns:
                        # Map edited comments back to full repo_table_df
                        for idx, row in edited_issues_df.iterrows():
                            # Find matching row in repo_table_df
                            mask = (
                                (repo_table_df['Component'] == row['Component']) &
                                (repo_table_df['File'] == row.get('File', '')) &
                                (repo_table_df['Compatibility Issues'].astype(str) == str(row.get('Compatibility Issues', '')))
                            )
                            if mask.any():
                                repo_table_df.loc[mask, 'Review Comment'] = row.get('Review Comment', '')
                        
                        # Save to CSV
                        csv_path = report_dir / "openstack_repo_compatibility.csv"
                        repo_table_df.to_csv(csv_path, index=False)
                        st.success("✅ Review comments saved successfully!")
                
                # Show breakdown by severity
                st.markdown("#### Breakdown by Severity")
                col1, col2 = st.columns(2)
                with col1:
                    issues_errors = len(issues_df[issues_df['Compatibility Issues'].astype(str).str.contains('ERROR|MISMATCH|EOL', case=False, na=False)])
                    st.metric("❌ Errors Requiring Review", issues_errors)
                with col2:
                    issues_warnings = len(issues_df[issues_df['Compatibility Issues'].astype(str).str.contains('MIXED|WARNING', case=False, na=False)])
                    st.metric("⚠️ Warnings Requiring Review", issues_warnings)
        
        # Incompatibilities and Reviews Table (HIDDEN)
        # st.markdown("### 📋 Incompatibilities and Reviews Needed")
        # 
        # # Filter for errors and warnings only
        # incompat_df = repo_table_df[
        #     (repo_table_df['Compatibility Issues'].astype(str).str.contains('ERROR|MISMATCH|EOL|MIXED|WARNING', case=False, na=False)) &
        #     (repo_table_df['Compatibility Issues'].astype(str) != 'OK')
        # ].copy()
        # 
        # if not incompat_df.empty:
        #     # Ensure Review Comment column exists
        #     if 'Review Comment' not in incompat_df.columns:
        #         incompat_df['Review Comment'] = ''
        #     if 'Review Comment' not in repo_table_df.columns:
        #         repo_table_df['Review Comment'] = ''
        #     
        #     # Select relevant columns for display
        #     display_columns = ['Component', 'Version Detected', 'Real Version', 'File', 
        #                      'Mapped Release', 'Compatibility Issues', 'Recommended Stack']
        #     if 'Review Comment' not in display_columns:
        #         display_columns.append('Review Comment')
        #     
        #     # Filter to only show columns that exist
        #     available_columns = [col for col in display_columns if col in incompat_df.columns]
        #     incompat_display_df = incompat_df[available_columns].copy()
        #     
        #     # Use data_editor for editable Review Comment column
        #     edited_incompat_df = st.data_editor(
        #         incompat_display_df,
        #         use_container_width=True,
        #         hide_index=True,
        #         height=600,
        #         column_config={
        #             "Review Comment": st.column_config.TextColumn(
        #                 "Review Comment",
        #                 help="Add review notes, assign owners, or track follow-up actions",
        #                 width="large"
        #             ),
        #             "Component": st.column_config.TextColumn(
        #                 "Component",
        #                 width="medium"
        #             ),
        #             "Compatibility Issues": st.column_config.TextColumn(
        #                 "Compatibility Issues",
        #                 width="medium"
        #             ),
        #             "File": st.column_config.TextColumn(
        #                 "File",
        #                 width="medium"
        #             )
        #         },
        #         disabled=[col for col in available_columns if col != 'Review Comment'],
        #         key="incompatibilities_editor"
        #     )
        #     
        #     # Save button for Review Comments
        #     if st.button("💾 Save Review Comments", key="save_incompat_comments"):
        #         # Update the full dataframe with edited review comments
        #         if 'Review Comment' in edited_incompat_df.columns:
        #             # Map edited comments back to full repo_table_df
        #             for idx, row in edited_incompat_df.iterrows():
        #                 # Find matching row in repo_table_df
        #                 mask = (
        #                     (repo_table_df['Component'] == row['Component']) &
        #                     (repo_table_df['File'] == row.get('File', '')) &
        #                     (repo_table_df['Compatibility Issues'].astype(str) == str(row.get('Compatibility Issues', '')))
        #                 )
        #                 if mask.any():
        #                     repo_table_df.loc[mask, 'Review Comment'] = row.get('Review Comment', '')
        #             
        #             # Save to CSV
        #             csv_path = report_dir / "openstack_repo_compatibility.csv"
        #             repo_table_df.to_csv(csv_path, index=False)
        #             st.success("✅ Review comments saved successfully!")
        #     
        #     # Show breakdown by severity
        #     st.markdown("#### Breakdown by Severity")
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         incompat_errors = len(incompat_df[incompat_df['Compatibility Issues'].astype(str).str.contains('ERROR|MISMATCH|EOL', case=False, na=False)])
        #         st.metric("❌ Errors Requiring Review", incompat_errors)
        #     with col2:
        #         incompat_warnings = len(incompat_df[incompat_df['Compatibility Issues'].astype(str).str.contains('MIXED|WARNING', case=False, na=False)])
        #         st.metric("⚠️ Warnings Requiring Review", incompat_warnings)
        # else:
        #     st.info("✅ No incompatibilities found! All components are compatible.")
        
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
# OpenStack Compatibility Analysis (Legacy) - HIDDEN
# ---------------------------------------------------
# st.markdown("## 🔍 OpenStack Compatibility Analysis (Detailed)")
# 
# # Initialize session state
# if 'run_compat_analysis' not in st.session_state:
#     st.session_state['run_compat_analysis'] = False
# 
# # Check for existing compatibility report
# compat_file = report_dir / "openstack-compat-table.md"
# compat_csv = report_dir / "openstack-compat-table.csv"
# 
# compat_loaded = False
# compat_df = None
# 
# if compat_csv.exists():
#     try:
#         compat_df = pd.read_csv(compat_csv)
#         compat_loaded = True
#         st.success(f"📄 Loaded existing compatibility analysis: {len(compat_df)} checks")
#     except Exception as e:
#         pass
# 
# if COMPATIBILITY_ANALYZER_AVAILABLE:
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         st.markdown("### Analyze OpenStack Component Compatibility")
#         st.caption("Checks release alignment, API microversions, container image alignment, Python library compatibility, and Kubernetes API compatibility.")
#     with col2:
#         if st.button("🔄 Run Compatibility Analysis", type="primary"):
#             st.session_state['run_compat_analysis'] = True
#     
#     if st.session_state.get('run_compat_analysis', False):
#         with st.spinner("Analyzing OpenStack compatibility... This may take a minute."):
#             try:
#                 repo_path = os.getcwd()
#                 analyzer = OpenStackCompatibilityAnalyzer(repo_path=repo_path)
#                 compatibility_table = analyzer.analyze()
#                 
#                 if compatibility_table:
#                     compat_df = pd.DataFrame(compatibility_table)
#                     compat_loaded = True
#                     st.session_state['run_compat_analysis'] = False
#                     st.success(f"✅ Analysis complete! Found {len(compat_df)} compatibility checks.")
#                     
#                     # Auto-save to reports
#                     report_dir.mkdir(parents=True, exist_ok=True)
#                     analyzer.export_to_markdown(report_dir / "openstack-compat-table.md")
#                     analyzer.export_to_csv(report_dir / "openstack-compat-table.csv")
#             except Exception as e:
#                 st.error(f"Error analyzing compatibility: {str(e)}")
#                 st.exception(e)
#                 st.session_state['run_compat_analysis'] = False
# else:
#     st.warning("⚠️ Compatibility analyzer not available. Ensure openstack_compatibility.py is in the genestack-intelligence directory.")
# 
# # Display compatibility table if available
# if compat_loaded and compat_df is not None and not compat_df.empty:
#     st.markdown("### Compatibility Status Table")
#     
#     # Color code by status
#     def color_status(val):
#         if val == "OK":
#             return 'background-color: #ccffcc'  # Green
#         elif val == "WARNING":
#             return 'background-color: #fff4cc'  # Yellow
#         elif val == "ERROR":
#             return 'background-color: #ffcccc'  # Red
#         return ''
#     
#     # Apply styling
#     styled_compat_df = compat_df.style.applymap(color_status, subset=['Status'])
#     
#     # Display with filters
#     col1, col2 = st.columns(2)
#     with col1:
#         status_filter = st.multiselect(
#             "Filter by Status",
#             options=['OK', 'WARNING', 'ERROR'],
#             default=['ERROR', 'WARNING', 'OK']
#         )
#     with col2:
#         search_term = st.text_input("🔍 Search Component", "", key="compat_search")
#     
#     # Apply filters
#     filtered_compat_df = compat_df[compat_df['Status'].isin(status_filter)]
#     if search_term:
#         filtered_compat_df = filtered_compat_df[
#             filtered_compat_df['Component'].str.contains(search_term, case=False, na=False) |
#             filtered_compat_df['Notes'].astype(str).str.contains(search_term, case=False, na=False)
#         ]
#     
#     # Display table
#     if not filtered_compat_df.empty:
#         # Create styled version for display
#         display_df = filtered_compat_df.copy()
#         
#         st.dataframe(
#             display_df,
#             use_container_width=True,
#             hide_index=True,
#             height=600
#         )
#         
#         # Statistics
#         st.markdown("### 📊 Compatibility Statistics")
#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             ok_count = len(compat_df[compat_df['Status'] == 'OK'])
#             st.metric("✅ OK", ok_count, delta=None)
#         with col2:
#             warning_count = len(compat_df[compat_df['Status'] == 'WARNING'])
#             st.metric("⚠️ Warnings", warning_count, delta=None)
#         with col3:
#             error_count = len(compat_df[compat_df['Status'] == 'ERROR'])
#             st.metric("❌ Errors", error_count, delta=None)
#         with col4:
#             total_checks = len(compat_df)
#             st.metric("Total Checks", total_checks)
#         
#         # Show summary
#         if error_count > 0:
#             st.error(f"🚨 **{error_count} compatibility error(s) found!** Review the table above for details.")
#         if warning_count > 0:
#             st.warning(f"⚠️ **{warning_count} compatibility warning(s) found.** Review recommended.")
#         if error_count == 0 and warning_count == 0:
#             st.success("✅ **All compatibility checks passed!**")
#         
#         # Export options
#         st.markdown("### 💾 Export Options")
#         col1, col2 = st.columns(2)
#         with col1:
#             csv = compat_df.to_csv(index=False)
#             st.download_button(
#                 label="📥 Download Full CSV",
#                 data=csv,
#                 file_name=f"openstack-compat-{datetime.now().strftime('%Y%m%d')}.csv",
#                 mime="text/csv"
#             )
#         with col2:
#             filtered_csv = filtered_compat_df.to_csv(index=False)
#             st.download_button(
#                 label="📥 Download Filtered CSV",
#                 data=filtered_csv,
#                 file_name=f"openstack-compat-filtered-{datetime.now().strftime('%Y%m%d')}.csv",
#                 mime="text/csv"
#             )
#     else:
#         st.warning("No compatibility checks match the current filters.")
# elif not compat_loaded:
#     st.info("💡 Click '🔄 Run Compatibility Analysis' to analyze OpenStack component compatibility, or ensure a previous analysis exists in the reports directory.")

# ---------------------------------------------------
# Top 10 Modified Files per Branch (COMMENTED OUT - MOVED TO TOP MOVING PARTS & UPDATES)
# ---------------------------------------------------
# st.markdown("## 🗂 Top 10 Modified Files per Branch")
# if branch_files_detail_df.empty:
#     st.info("No file change data available for the selected branches.")
# else:
#     branch_files_display = branch_files_detail_df.copy()
#     branch_files_display["Changes"] = branch_files_display["Changes"].astype(int)
#     render_editable_table(branch_files_display, key="modified_files_table")

# ---------------------------------------------------
# GitHub-style Contribution Calendar (COMMENTED OUT - MOVED TO TOP MOVING PARTS & UPDATES)
# ---------------------------------------------------
# st.markdown("## 🔥 GitHub-Style Contribution Calendar (Last 12 Months)")
# 
# calendar_raw = git("git log --pretty=format:'%an|%ad' --date=short")
# calendar_records = []
# for line in calendar_raw.split("\n"):
#     if "|" not in line:
#         continue
#     author, date_str = line.split("|", 1)
#     calendar_records.append([author.strip(), date_str.strip(), 1])
# 
# if calendar_records:
#     calendar_df = pd.DataFrame(calendar_records, columns=["author", "date", "commits"])
#     calendar_df["date"] = pd.to_datetime(calendar_df["date"])
# 
#     end_date = pd.Timestamp.today().normalize()
#     start_date = end_date - pd.Timedelta(days=365)
#     calendar_df = calendar_df[(calendar_df["date"] >= start_date) & (calendar_df["date"] <= end_date)]
# 
#     if calendar_df.empty:
#         st.info("No commit activity found for the last 12 months.")
#     else:
#         calendar_df["week"] = calendar_df["date"].dt.to_period("W")
#         week_range = pd.period_range(start=start_date.to_period("W"), end=end_date.to_period("W"), freq="W")
# 
#         weekly = calendar_df.groupby(["author", "week"])["commits"].sum().unstack(fill_value=0)
#         weekly = weekly.reindex(columns=week_range, fill_value=0)
#         weekly["total"] = weekly.sum(axis=1)
#         weekly = weekly.sort_values("total", ascending=False).drop(columns=["total"])
# 
#         week_labels = [period.start_time.strftime("%Y-%m-%d") for period in weekly.columns]
#         display_df = weekly.copy().astype(int)
#         display_df.columns = week_labels
# 
#         bar_color = "#2563eb"
#         styled_calendar = (
#             display_df.style
#             .format("{:.0f}")
#             .bar(axis=1, color=bar_color)
#         )
#         st.dataframe(styled_calendar, width="stretch")
# else:
#     st.info("No commit history found to build the calendar.")
# 
# # ---------------------------------------------------
# # Tables Section (COMMENTED OUT - MOVED TO TOP MOVING PARTS & UPDATES)
# # ---------------------------------------------------
# st.markdown("## 🌿 Top 10 Active Branches")
# render_editable_table(branch_df, key="top_branches_table")
# 
# st.markdown("## 🔄 Last 10 PRs (Merged)")
# if pr_df.empty:
#     st.info("No merged PR history available.")
# else:
#     render_editable_table(pr_df, key="pr_table")

# ---------------------------------------------------
# AI Analysis (Mockup) — Top File Trends & Risks (COMMENTED OUT - MOVED TO SO WHAT : AI FINDINGS)
# ---------------------------------------------------
# st.markdown("## 🤖 AI Analysis (Mockup) — Top Modified Files & Issue Trends")
# st.caption("Real AI agent analysis coming soon. All tables are editable for team notes.")
# 
# ai_insights = []
# insights_df = pd.DataFrame()
# 
# if file_df.empty:
#     st.info("No file change data to analyze.")
# else:
#     ai_insights = [analyze_file_risk(row["File"], row["Changes"]) for _, row in file_df.iterrows()]
#     insights_df = pd.DataFrame(ai_insights)
#     insights_df.rename(columns={"file": "File", "changes": "Changes", "issues": "Issues", "suggestion": "Suggested Action"}, inplace=True)
#     insights_df["Changes"] = insights_df["Changes"].astype(int)
#     render_editable_table(insights_df, key="ai_insights_table")
# 
#     issue_records = []
#     for _, row in insights_df.iterrows():
#         for issue in [item.strip() for item in row["Issues"].split(",")]:
#             if issue:
#                 issue_records.append({"Issue": issue, "File": row["File"]})
# 
#     st.markdown("### Issue Trend Summary")
#     if issue_records:
#         issue_df = pd.DataFrame(issue_records)
#         issue_summary_df = (
#             issue_df.groupby("Issue")
#             .agg(
#                 Files_Concerned=("File", lambda x: ", ".join(sorted(set(x)))),
#                 Files_Impacted=("File", "nunique"),
#             )
#             .reset_index()
#         )
#         render_editable_table(issue_summary_df, key="issue_summary_table")
#     else:
#         st.info("No issue trends detected yet.")
# 
#     st.markdown("### Suggested Actions")
#     suggested_actions_df = insights_df[["File", "Suggested Action"]]
#     render_editable_table(suggested_actions_df, key="suggested_actions_table")

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
# SO WHAT : AI Findings
# ---------------------------------------------------
st.markdown("## 🔍 SO WHAT : AI Findings")

# AI Analysis (Mockup) — Top Modified Files & Issue Trends
st.markdown("### 🤖 AI Analysis (Mockup) — Top Modified Files & Issue Trends")
st.caption("Real AI agent analysis coming soon. All tables are editable for team notes.")

# Compute AI insights if not already done
if file_df.empty:
    st.info("No file change data to analyze.")
else:
    # Only compute if insights_df is empty (not already computed)
    if insights_df.empty:
        ai_insights = [analyze_file_risk(row["File"], row["Changes"]) for _, row in file_df.iterrows()]
        insights_df = pd.DataFrame(ai_insights)
        insights_df.rename(columns={"file": "File", "changes": "Changes", "issues": "Issues", "suggestion": "Suggested Action"}, inplace=True)
        insights_df["Changes"] = insights_df["Changes"].astype(int)
    
    render_editable_table(insights_df, key="ai_insights_table_moved")

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
        render_editable_table(issue_summary_df, key="issue_summary_table_moved")
    else:
        st.info("No issue trends detected yet.")

    st.markdown("### Suggested Actions")
    suggested_actions_df = insights_df[["File", "Suggested Action"]]
    render_editable_table(suggested_actions_df, key="suggested_actions_table_moved")

# ---------------------------------------------------
# What Now ? - Recommended Actions and Key Insights
# ---------------------------------------------------
st.markdown("## ❓ What Now ?")

# Gauges for Key Metrics - Mercedes Style Big Gauges (COMMENTED OUT - MOVED TO DETAILED CONTRIBUTION BREAKDOWN)
# st.markdown("### 📊 Key Metrics Overview (Mercedes-Style Gauges)")
# 
# # Compute actual percentages from metrics
# top5_files_percent = 0
# top5_files_current = 0
# top5_files_total = 0
# 
# top5_contrib_percent = 0
# top5_contrib_current = 0
# top5_contrib_total = 0
# 
# top5_branches_percent = 0
# top5_branches_current = 0
# top5_branches_total = 0
# 
# # Calculate Top 5 Files percentage
# if not file_df.empty:
#     top5_files_total = file_df['Changes'].sum()
#     top5_files_current = file_df.head(5)['Changes'].sum()
#     if top5_files_total > 0:
#         top5_files_percent = round((top5_files_current / top5_files_total) * 100, 1)
# 
# # Calculate Top 5 Contributors percentage
# if not contrib_df.empty:
#     top5_contrib_total = contrib_df['Commits'].sum()
#     top5_contrib_current = contrib_df.head(5)['Commits'].sum()
#     if top5_contrib_total > 0:
#         top5_contrib_percent = round((top5_contrib_current / top5_contrib_total) * 100, 1)
# 
# # Calculate Top 5 Branches percentage
# if not branch_df.empty:
#     top5_branches_total = branch_df['Commits'].sum()
#     top5_branches_current = branch_df.head(5)['Commits'].sum()
#     if top5_branches_total > 0:
#         top5_branches_percent = round((top5_branches_current / top5_branches_total) * 100, 1)
# 
# # Render the 3 Mercedes-style gauges in 3 columns
# if PLOTLY_AVAILABLE:
#     col1, col2, col3 = st.columns(3)
#     
#     with col1:
#         if top5_files_total > 0:
#             st.plotly_chart(
#                 mercedes_gauge("Top 5 Files", top5_files_percent, int(top5_files_current), int(top5_files_total)),
#                 use_container_width=True
#             )
#         else:
#             st.info("No file data")
#     
#     with col2:
#         if top5_contrib_total > 0:
#             st.plotly_chart(
#                 mercedes_gauge("Top 5 Contributors", top5_contrib_percent, int(top5_contrib_current), int(top5_contrib_total)),
#                 use_container_width=True
#             )
#         else:
#             st.info("No contributor data")
#     
#     with col3:
#         if top5_branches_total > 0:
#             st.plotly_chart(
#                 mercedes_gauge("Top 5 Branches", top5_branches_percent, int(top5_branches_current), int(top5_branches_total)),
#                 use_container_width=True
#             )
#         else:
#             st.info("No branch data")
# else:
#     # Fallback to simple metrics if plotly not available
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         if top5_files_total > 0:
#             st.metric("Top 5 Files", f"{top5_files_percent:.1f}%", f"{int(top5_files_current):,}/{int(top5_files_total):,} changes")
#         else:
#             st.info("No file data")
#     with col2:
#         if top5_contrib_total > 0:
#             st.metric("Top 5 Contributors", f"{top5_contrib_percent:.1f}%", f"{int(top5_contrib_current):,}/{int(top5_contrib_total):,} commits")
#         else:
#             st.info("No contributor data")
#     with col3:
#         if top5_branches_total > 0:
#             st.metric("Top 5 Branches", f"{top5_branches_percent:.1f}%", f"{int(top5_branches_current):,}/{int(top5_branches_total):,} commits")
#         else:
#             st.info("No branch data")
# 
# st.markdown("---")
# 
# # Top 5 Contributors Table (COMMENTED OUT - MOVED TO DETAILED CONTRIBUTION BREAKDOWN)
# # st.markdown("### 👥 Top 5 Contributors")
# # if not contrib_df.empty:
# #     top_5_contributors = contrib_df.head(5).copy()
# #     top_5_contributors['Rank'] = range(1, len(top_5_contributors) + 1)
# #     top_5_contributors_display = top_5_contributors[['Rank', 'Contributor', 'Commits']].copy()
# #     top_5_contributors_display.columns = ['Rank', 'Contributor', 'Commits']
# #     top_5_contributors_display['Commits'] = top_5_contributors_display['Commits'].apply(lambda x: f"{x:,}")
# #     st.dataframe(
# #         top_5_contributors_display,
# #         use_container_width=True,
# #         hide_index=True,
# #         column_config={
# #             "Rank": st.column_config.NumberColumn("Rank", width="small"),
# #             "Contributor": st.column_config.TextColumn("Contributor", width="large"),
# #             "Commits": st.column_config.TextColumn("Commits", width="medium")
# #         }
# #     )
# # else:
# #     st.info("No contributor data available.")
# 
# # Top Active Branches Table (COMMENTED OUT - MOVED TO DETAILED CONTRIBUTION BREAKDOWN)
# # st.markdown("### 🌿 Top 5 Active Branches")
# # if not branch_df.empty:
# #     top_5_branches = branch_df.head(5).copy()
# #     top_5_branches['Rank'] = range(1, len(top_5_branches) + 1)
# #     top_5_branches_display = top_5_branches[['Rank', 'Branch', 'Commits', 'Updated Files']].copy()
# #     top_5_branches_display.columns = ['Rank', 'Branch', 'Commits', 'Files Updated']
# #     top_5_branches_display['Commits'] = top_5_branches_display['Commits'].apply(lambda x: f"{x:,}")
# #     top_5_branches_display['Files Updated'] = top_5_branches_display['Files Updated'].apply(lambda x: f"{x:,}")
# #     st.dataframe(
# #         top_5_branches_display,
# #         use_container_width=True,
# #         hide_index=True,
# #         column_config={
# #             "Rank": st.column_config.NumberColumn("Rank", width="small"),
# #             "Branch": st.column_config.TextColumn("Branch", width="large"),
# #             "Commits": st.column_config.TextColumn("Commits", width="medium"),
# #             "Files Updated": st.column_config.TextColumn("Files Updated", width="medium")
# #         }
# #     )
# # else:
# #     st.info("No branch data available.")
# 
# # Top Moving Parts and Updates Table (COMMENTED OUT - MOVED TO DETAILED CONTRIBUTION BREAKDOWN)
# # st.markdown("### 🔥 Top Moving Parts & Updates")
# # if not file_df.empty:
# #     top_5_files = file_df.head(5).copy()
# #     top_5_files['Rank'] = range(1, len(top_5_files) + 1)
# #     
# #     # Merge with AI insights if available
# #     if not insights_df.empty:
# #         top_5_files_display = top_5_files[['Rank', 'File', 'Changes']].copy()
# #         top_5_files_display['Changes'] = top_5_files_display['Changes'].apply(lambda x: f"{x:,}")
# #         
# #         # Add AI insights columns
# #         issues_list = []
# #         recommendations_list = []
# #         for idx, row in top_5_files.iterrows():
# #             file_path = row['File']
# #             file_insights = insights_df[insights_df['File'] == file_path]
# #             if not file_insights.empty:
# #                 insight = file_insights.iloc[0]
# #                 issues_list.append(insight.get('Issues', 'No issues detected'))
# #                 recommendations_list.append(insight.get('Suggested Action', 'No specific action'))
# #             else:
# #                 issues_list.append('No analysis available')
# #                 recommendations_list.append('No recommendation')
# #         
# #         top_5_files_display['Issues'] = issues_list
# #         top_5_files_display['Recommendation'] = recommendations_list
# #         top_5_files_display.columns = ['Rank', 'File', 'Changes', 'Issues', 'Recommendation']
# #     else:
# #         top_5_files_display = top_5_files[['Rank', 'File', 'Changes']].copy()
# #         top_5_files_display['Changes'] = top_5_files_display['Changes'].apply(lambda x: f"{x:,}")
# #         top_5_files_display.columns = ['Rank', 'File', 'Changes']
# #     
# #     # Build column config dynamically
# #     column_config = {
# #         "Rank": st.column_config.NumberColumn("Rank", width="small"),
# #         "File": st.column_config.TextColumn("File", width="large"),
# #         "Changes": st.column_config.TextColumn("Changes", width="medium")
# #     }
# #     if 'Issues' in top_5_files_display.columns:
# #         column_config["Issues"] = st.column_config.TextColumn("Issues", width="large")
# #     if 'Recommendation' in top_5_files_display.columns:
# #         column_config["Recommendation"] = st.column_config.TextColumn("Recommendation", width="large")
# #     
# #     st.dataframe(
# #         top_5_files_display,
# #         use_container_width=True,
# #         hide_index=True,
# #         column_config=column_config
# #     )
# # else:
# #     st.info("No file change data available.")

# Recommended Actions Table
st.markdown("### ✅ Recommended Actions")
recommended_actions_rows = []

# Actions from AI analysis
try:
    has_insights = not insights_df.empty
except (NameError, AttributeError):
    has_insights = False

if has_insights:
    for idx, row in insights_df.head(10).iterrows():
        file_path = row.get('File', 'Unknown')
        suggestion = row.get('Suggested Action', 'No specific action')
        changes = row.get('Changes', 0)
        recommended_actions_rows.append({
            'Priority': 'High' if changes > 100 else 'Medium' if changes > 50 else 'Low',
            'File': file_path,
            'Changes': changes,
            'Action': suggestion
        })

# Additional system-level actions
stale = branch_df[branch_df["Commits"] == 0]
if not stale.empty:
    recommended_actions_rows.append({
        'Priority': 'Medium',
        'File': 'System',
        'Changes': len(stale),
        'Action': f'Review stale branches: {len(stale)} branch(es) with zero commits — consider cleanup.'
    })

if len(pr_df) < 3:
    recommended_actions_rows.append({
        'Priority': 'Medium',
        'File': 'System',
        'Changes': len(pr_df),
        'Action': 'Low PR activity detected — development pace might be slowing. Consider reviewing blockers.'
    })

if not contrib_df.empty:
    top_dev = contrib_df.iloc[0]
    recommended_actions_rows.append({
        'Priority': 'Low',
        'File': 'System',
        'Changes': top_dev['Commits'],
        'Action': f"Recognize top contributor: {top_dev['Contributor']} with {top_dev['Commits']} commits this cycle."
    })

if not file_df.empty:
    volatile = file_df.iloc[0]
    recommended_actions_rows.append({
        'Priority': 'High',
        'File': volatile['File'],
        'Changes': volatile['Changes'],
        'Action': f"Review high-churn file: {volatile['File']} has {volatile['Changes']} changes — consider refactoring or stabilization."
    })

# Display as table
if recommended_actions_rows:
    actions_df = pd.DataFrame(recommended_actions_rows)
    # Convert Priority to numeric for proper sorting (High=3, Medium=2, Low=1)
    priority_map = {'High': 3, 'Medium': 2, 'Low': 1}
    actions_df['_priority_sort'] = actions_df['Priority'].map(priority_map)
    # Store original Changes as numeric for sorting
    actions_df['_changes_numeric'] = pd.to_numeric(actions_df['Changes'], errors='coerce')
    actions_df = actions_df.sort_values(['_priority_sort', '_changes_numeric'], ascending=[False, False])
    actions_df = actions_df.drop(columns=['_priority_sort', '_changes_numeric'])
    # Format Changes for display
    actions_df['Changes'] = actions_df['Changes'].apply(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) and not pd.isna(x) else str(x))
    
    st.dataframe(
        actions_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Priority": st.column_config.TextColumn("Priority", width="small"),
            "File": st.column_config.TextColumn("File", width="medium"),
            "Changes": st.column_config.TextColumn("Changes", width="small"),
            "Action": st.column_config.TextColumn("Action", width="large")
        }
    )
else:
    st.info("No specific actions recommended at this time.")

st.success("Dashboard loaded successfully.")
