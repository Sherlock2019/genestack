# Welcome to Genestack: Where Cloud Meets You

![Genestack](docs/assets/images/genestack.png)

Genestack — where Kubernetes and OpenStack tango in the cloud. Imagine a waltz between systems that deploy
what you need.

## Documentation

![Publishing](https://github.com/rackerlabs/genestack/actions/workflows/mkdocs.yaml/badge.svg?event=push)

Read the [Genestack Documentation](https://docs.rackspacecloud.com). The documentation was created to guide
through the process of building, operating, and consuming a cloud.

### Symphony of Simplicity

Genestack conducts this orchestra of tech with style. Operators play the score, managing the complexity with
a flick of their digital batons. They unify the chaos, making scaling and management a piece of cake. Think
of it like a conductor effortlessly guiding a cacophony into a symphony.

### Hybrid Hilarity

Our hybrid capabilities aren’t your regular circus act. Picture a shared OVN fabric — a communal network
where workers multitask like pros. Whether it’s computing, storing, or networking, they wear multiple
hats in a hyperconverged circus or a grand full-scale enterprise cloud extravaganza.

### The Secret Sauce: Kustomize & Helm

Genestack’s inner workings are a blend dark magic — crafted with [Kustomize](https://kustomize.io) and
[Helm](https://helm.sh). It’s like cooking with cloud. Want to spice things up? Tweak the
`kustomization.yaml` files or add those extra 'toppings' using Helm's style overrides. However, the
platform is ready to go with batteries included.

Genestack is making use of some homegrown solutions, community operators, and OpenStack-Helm. Everything
in Genestack comes together to form cloud in a new and exciting way; all built with opensource solutions
to manage cloud infrastructure in the way you need it.

## RXT Container Builds

![release-ceilometer](https://github.com/rackerlabs/genestack/actions/workflows/release-ceilometer.yaml/badge.svg?event=push)

![release-gnocchi](https://github.com/rackerlabs/genestack/actions/workflows/release-gnocchi.yaml/badge.svg?event=push)

![release-horizon-rxt](https://github.com/rackerlabs/genestack/actions/workflows/release-horizon-rxt.yml/badge.svg?event=push)

![release-keystone-rxt](https://github.com/rackerlabs/genestack/actions/workflows/release-keystone-rxt.yml/badge.svg?event=push)

![release-neutron-oslodb](https://github.com/rackerlabs/genestack/actions/workflows/release-neutron-oslodb.yaml/badge.svg?event=push)

![release-nova-oslodb](https://github.com/rackerlabs/genestack/actions/workflows/release-nova-oslodb.yaml/badge.svg?event=push)

![release-nova-uefi](https://github.com/rackerlabs/genestack/actions/workflows/release-nova-uefi.yml/badge.svg?event=push)

![release-octavia-ovn](https://github.com/rackerlabs/genestack/actions/workflows/release-octavia-ovn.yml/badge.svg?event=push)

---

## 🧬 Genestack Intelligence Dashboard — Repository Analytics (NEW)

The **Genestack Intelligence Dashboard** provides real-time engineering analytics,
repository health metrics, drift detection, release-cycle insights, and developer
productivity patterns.

This dashboard runs both **locally** and through **GitHub Actions** to deliver data-rich,
automatic insights into the Genestack platform.

### 🔥 What It Provides
- **Contributor Analytics** (heatmaps, weekly activity, ownership)
- **Branch Intelligence** (Top 10 active branches, stale branch detection)
- **Pull Request Insights** (last 10 PRs across all branches)
- **File Volatility** (hotspots, refactor candidates)
- **Helm/Kustomize Drift Detection** (auto-skip when no cluster is present)
- **AI Health Recommendations** (risk, trends, required actions)
- **Slack + Microsoft Teams Notifications**
- **One-click Streamlit Dashboard Interface**

---

## 📊 Dashboard Preview

<!-- INTELLIGENCE_DASHBOARD_START -->
<p align="center">
  <img src="docs/assets/intel_dashboard_preview.png?ts=20251124T121046Z" alt="Genestack Intelligence Dashboard" width="100%">
</p>
<!-- INTELLIGENCE_DASHBOARD_END -->

---

## 🚀 Start the Dashboard

```bash
./start.sh
```

Available at:

- **http://localhost:8600**
- **http://203.60.1.117:8600**

---

## 🧩 Directory Structure

```
genestack-intelligence/
├── dashboard/      # Streamlit dashboard UI
├── drift/          # Helm/Kustomize drift detection
├── heatmap/        # Contributor heatmap engine
├── notify/         # Slack/Teams notifier modules
└── .venv/          # Python environment
reports/
└── YYYY-MM-DD/     # Daily insights
```

---

## 🔔 GitHub Automation

| Badge | Workflow |
|-------|----------|
| ![Dashboard](https://img.shields.io/badge/Intel%20Dashboard-Auto--Build-blue) | Builds dashboard output |
| ![Drift](https://img.shields.io/badge/Drift%20Report-Auto--Check-orange) | Helm/Kustomize drift report |
| ![Weekly](https://img.shields.io/badge/Weekly%20Insights-Scheduled-green) | Weekly 00:00 insights |

These workflows:
- Update insights daily
- Regenerate drift reports
- Notify Slack/Teams
- Publish dashboards continuously

---

## 🛠 Local Development

```bash
cd genestack-intelligence
./local_run_all.sh
```

This runs:

- Heatmap generator
- Drift detector
- PR insights
- AI recommendations
- Slack/Teams notifications (if configured)

---

## 📡 Notifications (optional)

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
```

---

## 📘 Documentation

More details available under:

```
docs/community-insights.md
```

---

# 🎉 The Genestack Intelligence Dashboard elevates the development experience with clear visibility, analytics, and smart insights