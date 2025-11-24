#!/usr/bin/env python3
import os
import datetime
import requests

today = datetime.datetime.now().strftime("%Y-%m-%d")
webhook = os.getenv("TEAMS_WEBHOOK_URL")

if not webhook:
    print("⚠️ No Microsoft Teams webhook set. Skipping...")
    exit(0)

msg = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "Genestack Intelligence Update",
    "themeColor": "0076D7",
    "title": f"🧬 Genestack Intelligence Report — {today}",
    "text": (
        f"✔ Drift report generated\n"
        f"✔ Contributor heatmap updated\n"
        f"✔ All intelligence modules executed\n\n"
        f"📁 Location: `reports/{today}`"
    )
}

response = requests.post(webhook, json=msg)
if response.status_code not in (200, 204):
    print("❌ Error sending Teams notification:", response.text)
else:
    print("📨 Teams notification sent.")
