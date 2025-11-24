# 🧬 Genestack Intelligence Dashboard  
**Repository: rackerlabs/genestack**  
**Purpose: Provide DevOps, SRE, Engineering Leads with real-time analytics and drift intelligence**  

---

## 🚀 Overview  
The **Genestack Intelligence Dashboard** transforms your Git repository into a fully visual intelligence platform.  
It consolidates:

- Code activity  
- Contributors & ownership  
- Branch health  
- File volatility  
- Heatmaps  
- Pull Request velocity  
- Kubernetes drift analysis (auto-skip mode)  
- Slack/Teams notifications  
- AI-generated risk & health insights  

Everything is continuously generated **locally** or by **GitHub Actions**.

---

# 🎯 Goals  
The dashboard exists to:

### ✔ Give developers & owners **fast visibility** into repository health  
### ✔ Detect infrastructure drift or configuration inconsistencies  
### ✔ Surface hidden risks (stale branches, volatile files, low PR velocity)  
### ✔ Help engineering leaders make **data-driven decisions**  
### ✔ Automate insights for Slack / Teams / weekly reporting

---

# 📁 Directory Structure

genestack-intelligence/
├── drift/ # Helm/K8s drift detection (auto-skip if no cluster)
├── heatmap/ # Contributor activity heatmap generator
├── dashboard/ # Streamlit UI app
├── notify/ # Slack + Teams notifications
└── .venv/ # Virtual environment

reports/
└── YYYY-MM-DD/ # Auto-generated insights per day

Accessible at:

- http://localhost:8600  
- http://203.60.1.117:8600  

---

# 🧬 Key Features

---

## 1️⃣ **Drift Detection Engine**  
Detects:

- Helm manifest drift  
- Kustomize overlay mismatches  
- Live cluster vs. source-of-truth differences  

If no Kubernetes cluster is present →  
✔ Auto-Skips cleanly  
✔ Still generates the report layout

Reports stored in:

reports/YYYY-MM-DD/drift-report.md

yaml
Copy code

---

## 2️⃣ **Contributor Intelligence**  
Includes:

### ✔ Pie Chart (Top Contributors)  
Shows contribution distribution for the top 10 contributors.

### ✔ Full-Width Heatmap  
Contributor vs week activity  
- Green = high activity  
- Blue = low  
- Highlights productivity & ownership patterns  

### ✔ Top 10 Most Active Contributors  
Automatically extracted with Git commands.

---

## 3️⃣ **Branch Intelligence**  
### ✔ Top 10 Most Active Branches  
With commit counts.  
Quickly reveals:

- Hot zones  
- Feature groups  
- Stale or abandoned branches  
- Rework areas  

---

## 4️⃣ **File Volatility Tracking**  
Shows:  
- Top 10 most modified files  
- Areas with bug-risk  
- Refactor candidates  
- Highly unstable modules  

---

## 5️⃣ **Pull Request Intelligence**  
### ✔ Last 10 PRs (merged)  
Each with:

| Commit | Title | Author | Date |
|--------|--------|--------|------|

Highlights:  
- PR velocity  
- Team synergy  
- Reviewer load  
- Changes merging across branches  

---

## 6️⃣ **AI-Generated Insights Panel**  
Automatically analyzes all metrics and creates recommendations.

Examples:

- ⚠️ “Some branches have zero commits — likely stale.”  
- 🔥 “Most volatile file: X with N changes.”  
- ⭐ “Top contributor: John Doe — 42 commits this cycle.”  
- 📉 “Low PR activity, development pace might be slowing.”  
- 📈 “High contributor activity — healthy repository.”  

The AI model is rules-based for now; can be upgraded to ML on request.

---

## 7️⃣ **Notifications**  
Dashboards support:

### ✔ Slack Incoming Webhooks  
### ✔ Microsoft Teams Message Cards

Set once:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/…. "
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/…"
On every dashboard run or GitHub Action:
→ Slack & Teams receive an update payload

🔧 Installation Requirements
Local setup:

nginx
Copy code
sudo apt install python3 python3-venv python3-pip graphviz git -y
start.sh auto-installs:

pandas

matplotlib

seaborn

tabulate

streamlit

🖥 Dashboard Components
🥧 Pie Chart — Contributor Distribution
Shows who owns most of the repo activity.

🔥 Heatmap — Contributor Activity Over Time
Easy detection of productivity trends
(or talent bottlenecks).

🌿 Top Branches
Quick status of active workstreams.

🗂 Volatile Files
High-risk assets visible instantly.

🔄 Latest Pull Requests
Highlights team collaboration speed.

🔮 AI Insights
Surfaces risks + recommendations.

🧭 Example Use Cases
Engineering Manager reviewing weekly repository health

SRE validating stability before big deployments

Platform team validating drift before/after changes

Architects detecting long-term hotspots

Contributors wanting visibility into overall activity

🚀 Where to Go Next
This dashboard can be extended with:

🔥 1. PR reviewer bottleneck detection
🔥 2. Commit trend forecasting (AI model)
🔥 3. ML-based risk scoring for commits
🔥 4. HTML/PDF weekly emailed reports
🔥 5. Integration with GitHub API for richer PR metadata
🔥 6. Directory-level change heatmaps
🔥 7. Genestack-specific module trends (frontend, charts, policies)
