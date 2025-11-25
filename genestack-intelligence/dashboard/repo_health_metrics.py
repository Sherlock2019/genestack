import subprocess
import statistics
import json
from datetime import datetime

# -------------------------------------------------------
# Helper: run shell command
# -------------------------------------------------------
def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


# -------------------------------------------------------
# KPI #1 — Commit Frequency
# -------------------------------------------------------
def get_commit_frequency():
    try:
        count = int(sh("git rev-list --count HEAD"))
        # Heuristic scaling to 0–100%
        score = min(100, (count / 2000) * 100)
        return round(score, 2), count
    except:
        return 0, 0


# -------------------------------------------------------
# KPI #2 — PR Review Velocity
# -------------------------------------------------------
# Logic:
# - find merge commits (those with "Merge pull request")
# - extract time difference between parent commits
# - compute average (scaled to 0–100)
def get_review_velocity():
    try:
        log = sh(
            "git log --merges --pretty='%ct %p' --grep='Merge pull request'"
        ).splitlines()

        deltas = []
        for line in log:
            parts = line.split()
            if len(parts) < 3:
                continue

            merge_ts = int(parts[0])
            parent_ts = int(sh(f"git show -s --pretty='%ct' {parts[2]}"))
            delta_hours = (merge_ts - parent_ts) / 3600
            deltas.append(delta_hours)

        if not deltas:
            return 10, None  # very slow / no PRs

        median_hours = statistics.median(deltas)
        # scale: 0–48h → 0–100 score
        score = max(0, min(100, (48 / median_hours) * 100))
        return round(score, 2), round(median_hours, 2)
    except:
        return 0, None


# -------------------------------------------------------
# KPI #3 — Churn Stability
# -------------------------------------------------------
def get_churn_stability():
    try:
        lines = sh("git log --pretty=tformat: --numstat").splitlines()
        additions, deletions = 0, 0

        for l in lines:
            parts = l.split()
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                additions += int(parts[0])
                deletions += int(parts[1])

        churn = additions + deletions

        # estimate total code size
        kloc = int(sh("git ls-files | xargs wc -l | tail -1").split()[0])
        if kloc == 0:
            return 0, 0

        churn_ratio = churn / kloc  # bigger = noisier
        score = max(0, min(100, (1 / churn_ratio) * 100)) if churn_ratio > 0 else 100

        return round(score, 2), churn
    except:
        return 0, 0


# -------------------------------------------------------
# Collect repo health metrics
# -------------------------------------------------------
def load_repo_health():
    commit_score, commit_count = get_commit_frequency()
    review_score, review_hours = get_review_velocity()
    churn_score, churn_ops = get_churn_stability()

    return {
        "Commit Frequency": {
            "pct": commit_score,
            "raw": commit_count
        },
        "Review Velocity": {
            "pct": review_score,
            "raw": review_hours
        },
        "Code Churn Stability": {
            "pct": churn_score,
            "raw": churn_ops
        }
    }
