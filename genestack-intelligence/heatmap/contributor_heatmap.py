#!/usr/bin/env python3
import subprocess, os, datetime, matplotlib.pyplot as plt
import pandas as pd

today = datetime.datetime.now().strftime("%Y-%m-%d")
outdir = f"reports/{today}"
os.makedirs(outdir, exist_ok=True)

def run(cmd): return subprocess.check_output(cmd, shell=True, text=True)

log = run("git shortlog -sn")

data = []
for line in log.splitlines():
    count, name = line.strip().split("\t")
    data.append((name, int(count)))

df = pd.DataFrame(data, columns=["name", "commits"])

plt.figure(figsize=(10,6))
plt.barh(df["name"], df["commits"])
plt.title("Genestack Contributor Heatmap")
plt.tight_layout()
plt.savefig(f"{outdir}/heatmap.png")

with open(f"{outdir}/heatmap.md", "w") as f:
    f.write(df.to_markdown())

print("✅ Heatmap generated.")
