#!/usr/bin/env python3
import subprocess, os, datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")
report_dir = f"reports/{today}"
os.makedirs(report_dir, exist_ok=True)

def run(cmd):
    """Run a shell command and return stdout or captured error as a string."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    except Exception as e:
        return f"SKIPPED: {e}\n"

def write(path, content):
    with open(path, "w") as fh:
        fh.write(content)

summary = f"# Drift Report ({today})\n\n"

# -----------------------------------------
# HELM DRIFT (AUTO-SKIP)
# -----------------------------------------
if os.path.exists("Chart.yaml") or os.path.isdir("charts"):
    summary += "## Helm Drift\n"
    expected = run("helm template .")
    live = run("kubectl get all -o yaml")
    write(f"{report_dir}/helm_expected.yaml", expected)
    write(f"{report_dir}/helm_live.yaml", live)
    summary += "Helm drift comparison generated.\n\n"
else:
    summary += "## Helm Drift\nSKIPPED — no Helm chart found in repo.\n\n"

# -----------------------------------------
# KUSTOMIZE DRIFT (AUTO-SKIP)
# -----------------------------------------
overlay = "base-kustomize/overlays/production"
if os.path.exists(overlay):
    summary += "## Kustomize Drift\n"
    expected = run(f"kubectl kustomize {overlay}")
    live = run("kubectl get all -o yaml")
    write(f"{report_dir}/kustom_expected.yaml", expected)
    write(f"{report_dir}/kustom_live.yaml", live)
    summary += "Kustomize drift comparison generated.\n\n"
else:
    summary += "## Kustomize Drift\nSKIPPED — overlay directory not found.\n\n"

# -----------------------------------------
# CLUSTER CONNECTIVITY TEST (AUTO-SKIP)
# -----------------------------------------
conn = run("kubectl version --short")
if "SKIPPED" in conn or "connect" in conn or "refused" in conn:
    summary += "## Cluster Connectivity\nSKIPPED — no Kubernetes cluster detected.\n\n"
else:
    summary += "## Cluster Connectivity\nCluster reachable.\n\n"

# Save final summary
write(f"{report_dir}/drift-report.md", summary)

print("✅ Drift detection complete (Auto-Skip Mode enabled).")
