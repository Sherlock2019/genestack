import streamlit as st
import os, glob, subprocess, json, shlex, textwrap
from datetime import datetime
from typing import Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    return df.applymap(lambda val: wrap_text(val, width=width))

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
